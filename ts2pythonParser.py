#!/usr/bin/env python3

"""ts2python.py - compiles Typescript dataclasses to Python
        TypedDicts <https://www.python.org/dev/peps/pep-0589/>

Copyright 2021  by Eckhart Arnold (arnold@badw.de)
                Bavarian Academy of Sciences and Humanities (badw.de)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied.  See the License for the specific language governing
permissions and limitations under the License.
"""

#######################################################################
#
# SYMBOLS SECTION - Can be edited. Changes will be preserved.
#
#######################################################################

import datetime
import keyword
from functools import partial, lru_cache
import os
import sys
from typing import Tuple, List, Union, Any, Callable, Set, Dict, Sequence, \
    Optional


try:
    scriptpath = os.path.abspath(os.path.dirname(__file__))
except NameError:
    scriptpath = ''
if scriptpath not in sys.path:
    sys.path.append(scriptpath)

try:
    import regex as re
except ImportError:
    import re

from DHParser.compile import Compiler, compile_source, Junction, full_compile
from DHParser.configuration import set_config_value, get_config_value, get_config_values, \
    access_presets, finalize_presets, set_preset_value, get_preset_value, NEVER_MATCH_PATTERN, \
    get_config_values, read_local_config
from DHParser import dsl
from DHParser.dsl import recompile_grammar, never_cancel
from DHParser.ebnf import grammar_changed
from DHParser.error import ErrorCode, Error, canonical_error_strings, has_errors, NOTICE, \
    WARNING, ERROR, FATAL
from DHParser.log import start_logging, suspend_logging, resume_logging
from DHParser.nodetree import Node, WHITESPACE_PTYPE, TOKEN_PTYPE, RootNode, Path, pick_from_path
from DHParser.parse import Grammar, PreprocessorToken, Whitespace, Drop, AnyChar, Parser, \
    Lookbehind, Lookahead, Alternative, Pop, Text, Synonym, Counted, Interleave, INFINITE, ERR, \
    Option, NegativeLookbehind, OneOrMore, RegExp, Retrieve, Series, Capture, TreeReduction, \
    ZeroOrMore, Forward, NegativeLookahead, Required, CombinedParser, Custom, mixin_comment, \
    last_value, matching_bracket, optional_last_value, SmartRE
from DHParser.pipeline import create_parser_junction, create_preprocess_junction, \
    create_junction, PseudoJunction, full_pipeline, end_points
from DHParser.preprocess import nil_preprocessor, PreprocessorFunc, PreprocessorResult, \
    gen_find_include_func, preprocess_includes, make_preprocessor, chain_preprocessors
from DHParser.stringview import StringView
from DHParser.toolkit import is_filename, load_if_file, cpu_count, RX_NEVER_MATCH, \
    ThreadLocalSingletonFactory, expand_table, md5, as_list, static
from DHParser.trace import set_tracer, resume_notices_on, trace_history
from DHParser.transform import is_empty, remove_if, TransformationDict, TransformerFunc, \
    transformation_factory, remove_children_if, move_fringes, normalize_whitespace, \
    is_anonymous, name_matches, reduce_single_child, replace_by_single_child, replace_or_reduce, \
    remove_whitespace, replace_by_children, remove_empty, remove_tokens, flatten, all_of, \
    any_of, transformer, merge_adjacent, collapse, collapse_children_if, transform_result, \
    remove_children, remove_content, remove_brackets, change_name, remove_anonymous_tokens, \
    keep_children, is_one_of, not_one_of, content_matches, apply_if, peek, \
    remove_anonymous_empty, keep_nodes, traverse_locally, strip, lstrip, rstrip, \
    replace_content_with, forbid, assert_content, remove_infix_operator, add_error, error_on, \
    left_associative, lean_left, node_maker, has_descendant, neg, has_ancestor, insert, \
    positions_of, replace_child_names, add_attributes, delimit_children, merge_connected, \
    has_attr, has_parent, has_children, has_child, apply_unless, apply_ifelse, traverse, \
    TransformerCallable
from DHParser import parse as parse_namespace__


version = "0.8.0"


#######################################################################
#
# PREPROCESSOR SECTION - Can be edited. Changes will be preserved.
#
#######################################################################

# To capture includes, replace the NEVER_MATCH_PATTERN
# by a pattern with group "name" here, e.g. r'\input{(?P<name>.*)}'
RE_INCLUDE = NEVER_MATCH_PATTERN
RE_COMMENT = '(?:\\/\\/.*)|(?:\\/\\*(?:.|\\n)*?\\*\\/)'



def ts2pythonTokenizer(original_text) -> Tuple[str, List[Error]]:
    # Here, a function body can be filled in that adds preprocessor tokens
    # to the source code and returns the modified source.
    return original_text, []

# def preprocessor_factory() -> PreprocessorFunc:
#     # below, the second parameter must always be the same as ts2pythonGrammar.COMMENT__!
#     find_next_include = gen_find_include_func(RE_INCLUDE, '(?:\\/\\/.*)|(?:\\/\\*(?:.|\\n)*?\\*\\/)')
#     include_prep = partial(preprocess_includes, find_next_include=find_next_include)
#     tokenizing_prep = make_preprocessor(ts2pythonTokenizer)
#     return chain_preprocessors(include_prep, tokenizing_prep)
#
#
# get_preprocessor = ThreadLocalSingletonFactory(preprocessor_factory)

preprocessing: PseudoJunction = create_preprocess_junction(
    ts2pythonTokenizer, RE_INCLUDE, RE_COMMENT)


#######################################################################
#
# PARSER SECTION - Don't edit! CHANGES WILL BE OVERWRITTEN!
#
#######################################################################

class ts2pythonGrammar(Grammar):
    r"""Parser for a ts2python source file.
    """
    arg_list = Forward()
    declaration = Forward()
    declarations_block = Forward()
    document = Forward()
    function = Forward()
    generic_type = Forward()
    literal = Forward()
    type = Forward()
    types = Forward()
    source_hash__ = "e4be941365df870eeba2f0e17eb636f3"
    early_tree_reduction__ = CombinedParser.MERGE_TREETOPS
    disposable__ = re.compile('(?:_array_ellipsis$|_top_level_assignment$|_quoted_identifier$|DOT$|INT$|_reserved$|NEG$|FRAC$|EXP$|_keyword$|EOF$|_top_level_literal$|_namespace$|_part$)')
    static_analysis_pending__ = []  # type: List[bool]
    parser_initialization__ = ["upon instantiation"]
    COMMENT__ = r'(?://.*)\n?|(?:/\*(?:.|\n)*?\*/) *\n?'
    comment_rx__ = re.compile(COMMENT__)
    WHITESPACE__ = r'\s*'
    WSP_RE__ = mixin_comment(whitespace=WHITESPACE__, comment=COMMENT__)
    wsp__ = Whitespace(WSP_RE__)
    dwsp__ = Drop(Whitespace(WSP_RE__, keep_comments=True))
    EOF = Drop(SmartRE(f'(?!.)', '!/./'))
    EXP = Option(SmartRE(f'(?P<:Text>E|e)(?:(?P<:Text>\\+|\\-)?)([0-9]+)', '`E`|`e` [`+`|`-`] /[0-9]+/'))
    DOT = Text(".")
    FRAC = Option(Series(DOT, RegExp('[0-9]+')))
    NEG = Text("-")
    INT = Series(Option(NEG), SmartRE(f'([1-9][0-9]+|[0-9])', '/[1-9][0-9]+/|/[0-9]/'))
    _reserved = Drop(SmartRE(f'(?P<:Text>true|false)', '`true`|`false`'))
    _part = RegExp('(?!\\d)\\w+')
    identifier = Series(NegativeLookahead(_reserved), _part, dwsp__)
    name = Series(NegativeLookahead(_reserved), _part, ZeroOrMore(Series(Text("."), _part)), dwsp__)
    _quoted_identifier = Alternative(identifier, Series(Series(Drop(Text('"')), dwsp__), identifier, Series(Drop(Text('"')), dwsp__), mandatory=2), Series(Series(Drop(Text("\'")), dwsp__), identifier, Series(Drop(Text("\'")), dwsp__), mandatory=2))
    variable = Synonym(name)
    basic_type = SmartRE(f'(?P<:Text>object|array|string|number|boolean|null|integer|uinteger|decimal|unknown|any|void)(?P<comment__>{WSP_RE__})', '`object`|`array`|`string`|`number`|`boolean`|`null`|`integer`|`uinteger`|`decimal`|`unknown`|`any`|`void` ~')
    key = Alternative(identifier, Series(Series(Drop(Text('"')), dwsp__), identifier, Series(Drop(Text('"')), dwsp__)))
    association = Series(key, Series(Drop(Text(":")), dwsp__), literal, mandatory=1)
    object = Series(Series(Drop(Text("{")), dwsp__), Option(Series(association, ZeroOrMore(Series(Series(Drop(Text(",")), dwsp__), association)))), Option(Series(Drop(Text(",")), dwsp__)), Series(Drop(Text("}")), dwsp__))
    array = Series(Series(Drop(Text("[")), dwsp__), Option(Series(literal, ZeroOrMore(Series(Series(Drop(Text(",")), dwsp__), literal)))), Series(Drop(Text("]")), dwsp__))
    string = SmartRE(f'("[^"\\n]*")(?P<comment__>{WSP_RE__})|(\'[^\'\\n]*\')(?P<comment__>{WSP_RE__})', '/"[^"\\n]*"/ ~|/\'[^\'\\n]*\'/ ~')
    boolean = SmartRE(f'(?P<:Text>true|false)(?P<comment__>{WSP_RE__})', '`true`|`false` ~')
    number = Series(INT, FRAC, EXP, dwsp__)
    integer = Series(INT, SmartRE(f'(?![.Ee])', '!/[.Ee]/'), dwsp__)
    type_name = Synonym(name)
    _top_level_literal = Drop(Synonym(literal))
    _array_ellipsis = Drop(Series(literal, ZeroOrMore(Series(Series(Drop(Text(",")), dwsp__), literal))))
    assignment = Series(variable, Series(Drop(Text("=")), dwsp__), Alternative(literal, variable), Option(Series(Drop(Text(";")), dwsp__)))
    _top_level_assignment = Drop(Synonym(assignment))
    const = Series(Option(Series(Drop(Text("export")), dwsp__)), Series(Drop(Text("const")), dwsp__), declaration, Option(Series(Series(Drop(Text("=")), dwsp__), Alternative(literal, identifier))), Option(Series(Drop(Text(";")), dwsp__)), mandatory=2)
    item = Series(_quoted_identifier, Option(Series(Series(Drop(Text("=")), dwsp__), literal)))
    enum = Series(Option(Series(Drop(Text("export")), dwsp__)), Series(Drop(Text("enum")), dwsp__), identifier, Series(Drop(Text("{")), dwsp__), item, ZeroOrMore(Series(Series(Drop(Text(",")), dwsp__), item)), Option(Series(Drop(Text(",")), dwsp__)), Series(Drop(Text("}")), dwsp__), mandatory=3)
    keyof = Series(Text("keyof"), dwsp__)
    optional = Series(Text("?"), dwsp__)
    readonly = Series(Text("readonly"), dwsp__)
    func_type = Series(Option(Series(Drop(Text("new")), dwsp__)), Series(Drop(Text("(")), dwsp__), Option(arg_list), Series(Drop(Text(")")), dwsp__), Series(Drop(Text("=>")), dwsp__), types)
    extends = Series(SmartRE(f'(?:extends)(?P<comment__>{WSP_RE__})|(?:implements)(?P<comment__>{WSP_RE__})', '"extends"|"implements"'), Alternative(generic_type, type_name), ZeroOrMore(Series(Series(Drop(Text(",")), dwsp__), Alternative(generic_type, type_name))))
    index_signature = Series(Option(readonly), Series(Drop(Text("[")), dwsp__), identifier, Alternative(Series(Drop(Text(":")), dwsp__), Series(Option(Series(Drop(Text("in")), dwsp__)), keyof), Series(Drop(Text("in")), dwsp__)), type, Series(Drop(Text("]")), dwsp__), Option(optional))
    map_signature = Series(index_signature, Series(Drop(Text(":")), dwsp__), types)
    mapped_type = Series(Series(Drop(Text("{")), dwsp__), map_signature, Option(Series(Drop(Text(";")), dwsp__)), Series(Drop(Text("}")), dwsp__))
    extends_type = Series(Series(Drop(Text("extends")), dwsp__), Option(keyof), Alternative(basic_type, type_name, mapped_type))
    declarations_tuple = Series(Series(Drop(Text("[")), dwsp__), declaration, ZeroOrMore(Series(Series(Drop(Text(",")), dwsp__), declaration)), Series(Drop(Text("]")), dwsp__))
    type_tuple = Series(Series(Drop(Text("[")), dwsp__), types, ZeroOrMore(Series(Series(Drop(Text(",")), dwsp__), types)), Series(Drop(Text("]")), dwsp__))
    indexed_type = Series(type_name, Series(Drop(Text("[")), dwsp__), Alternative(type_name, literal), Series(Drop(Text("]")), dwsp__))
    array_type = Alternative(basic_type, generic_type, type_name, Series(Series(Drop(Text("(")), dwsp__), types, Series(Drop(Text(")")), dwsp__)), type_tuple, declarations_block)
    array_types = Synonym(array_type)
    array_of = Series(array_types, Series(Drop(Text("[]")), dwsp__))
    equals_type = Series(Series(Drop(Text("=")), dwsp__), Alternative(basic_type, type_name))
    parameter_type = Series(Option(readonly), Alternative(array_of, basic_type, generic_type, indexed_type, Series(type_name, Option(extends_type), Option(equals_type)), declarations_block, type_tuple, declarations_tuple))
    parameter_types = Series(Option(Series(Drop(Text("|")), dwsp__)), parameter_type, ZeroOrMore(Series(Series(Drop(Text("|")), dwsp__), parameter_type)))
    type_parameters = Series(Series(Drop(Text("<")), dwsp__), parameter_types, ZeroOrMore(Series(Series(Drop(Text(",")), dwsp__), parameter_types)), Series(Drop(Text(">")), dwsp__), mandatory=1)
    type_alias = Series(Option(Series(Drop(Text("export")), dwsp__)), Series(Drop(Text("type")), dwsp__), identifier, Option(type_parameters), Series(Drop(Text("=")), dwsp__), types, Option(Series(Drop(Text(";")), dwsp__)), mandatory=2)
    alias = Synonym(identifier)
    wildcard = Series(Series(Drop(Text("*")), dwsp__), Series(Drop(Text("as")), dwsp__), alias)
    intersection = Series(type, OneOrMore(Series(Series(Drop(Text("&")), dwsp__), type, mandatory=1)))
    symbol = Series(Option(Series(Drop(Text("type")), dwsp__)), identifier, Option(Series(Series(Drop(Text("as")), dwsp__), alias)))
    interface = Series(Option(Series(Drop(Text("export")), dwsp__)), Option(Series(Drop(Text("declare")), dwsp__)), SmartRE(f'(?:interface)(?P<comment__>{WSP_RE__})|(?:class)(?P<comment__>{WSP_RE__})', '"interface"|"class"'), identifier, Option(type_parameters), Option(extends), declarations_block, Option(Series(Drop(Text(";")), dwsp__)), mandatory=3)
    namespace = Series(Option(Series(Drop(Text("export")), dwsp__)), Series(Drop(Text("namespace")), dwsp__), identifier, Series(Drop(Text("{")), dwsp__), ZeroOrMore(Alternative(interface, type_alias, enum, const, Series(declaration, Option(Series(Drop(Text(";")), dwsp__))), Series(function, Option(Series(Drop(Text(";")), dwsp__))))), Series(Drop(Text("}")), dwsp__), mandatory=2)
    static = Series(Text("static"), dwsp__)
    virtual_enum = Series(Option(Series(Drop(Text("export")), dwsp__)), Series(Drop(Text("namespace")), dwsp__), identifier, Series(Drop(Text("{")), dwsp__), ZeroOrMore(Alternative(interface, type_alias, enum, const, Series(declaration, Option(Series(Drop(Text(";")), dwsp__))))), Series(Drop(Text("}")), dwsp__))
    qualifiers = Interleave(readonly, static, Series(Drop(Text('public')), dwsp__), Series(Drop(Text('protected')), dwsp__), Series(Drop(Text('private')), dwsp__), repetitions=[(0, 1), (0, 1), (0, 1), (0, 1), (0, 1)])
    _keyword = Drop(SmartRE(f'(?P<:Text>readonly|function|const|public|private|protected)(?!\\w)', '`readonly`|`function`|`const`|`public`|`private`|`protected` !/\\w/'))
    special = Series(Series(Drop(Text("[")), dwsp__), name, Series(Drop(Text("]")), dwsp__), Series(Drop(Text("(")), dwsp__), Option(arg_list), Series(Drop(Text(")")), dwsp__), Option(Series(Series(Drop(Text(":")), dwsp__), types)), mandatory=4)
    argument = Series(identifier, Option(optional), Option(Series(Series(Drop(Text(":")), dwsp__), types)))
    arg_tail = Series(Series(Drop(Text("...")), dwsp__), identifier, Option(Series(Series(Drop(Text(":")), dwsp__), Alternative(array_of, generic_type))))
    symList = Series(Series(Drop(Text("{")), dwsp__), symbol, ZeroOrMore(Series(Series(Drop(Text(",")), dwsp__), symbol)), Series(Drop(Text("}")), dwsp__))
    importList = Series(Alternative(symList, identifier), ZeroOrMore(Series(Series(Drop(Text(",")), dwsp__), Alternative(symList, identifier))))
    Import = Series(Series(Drop(Text("import")), dwsp__), Option(Series(Alternative(wildcard, importList), Series(Drop(Text("from")), dwsp__))), string)
    module = Series(Series(Drop(Text("declare")), dwsp__), Series(Drop(Text("module")), dwsp__), _quoted_identifier, Series(Drop(Text("{")), dwsp__), document, Series(Drop(Text("}")), dwsp__))
    _namespace = Alternative(virtual_enum, namespace)
    literal.set(Alternative(integer, number, boolean, string, array, object))
    generic_type.set(Series(type_name, type_parameters))
    type.set(Series(Option(readonly), Alternative(array_of, basic_type, generic_type, indexed_type, Series(type_name, NegativeLookahead(Text("("))), Series(Series(Drop(Text("(")), dwsp__), types, Series(Drop(Text(")")), dwsp__)), mapped_type, declarations_block, type_tuple, declarations_tuple, literal, func_type)))
    types.set(Series(Option(Series(Drop(Text("|")), dwsp__)), Alternative(intersection, type), ZeroOrMore(Series(Series(Drop(Text("|")), dwsp__), Alternative(intersection, type)))))
    arg_list.set(Series(Alternative(Series(argument, ZeroOrMore(Series(Series(Drop(Text(",")), dwsp__), argument)), Option(Series(Series(Drop(Text(",")), dwsp__), arg_tail))), arg_tail), Option(Series(Drop(Text(",")), dwsp__))))
    function.set(Alternative(Series(Option(Series(Option(Series(Drop(Text("export")), dwsp__)), qualifiers, Option(Series(Drop(Text("function")), dwsp__)), NegativeLookahead(_keyword), identifier, Option(optional), Option(type_parameters))), Series(Drop(Text("(")), dwsp__), Option(arg_list), Series(Drop(Text(")")), dwsp__), Option(Series(Series(Drop(Text(":")), dwsp__), types)), mandatory=2), special))
    declaration.set(Series(Option(Series(Drop(Text("export")), dwsp__)), qualifiers, Option(SmartRE(f'(?:let)(?P<comment__>{WSP_RE__})|(?:var)(?P<comment__>{WSP_RE__})', '"let"|"var"')), NegativeLookahead(_keyword), identifier, Option(optional), NegativeLookahead(Text("(")), Option(Series(Series(Drop(Text(":")), dwsp__), types))))
    declarations_block.set(Series(Series(Drop(Text("{")), dwsp__), Option(Series(Alternative(function, declaration), ZeroOrMore(Series(Option(SmartRE(f'(?:;)(?P<comment__>{WSP_RE__})|(?:,)(?P<comment__>{WSP_RE__})', '";"|","')), Alternative(function, declaration))), Option(SmartRE(f'(?:;)(?P<comment__>{WSP_RE__})|(?:,)(?P<comment__>{WSP_RE__})', '";"|","')))), Option(Series(map_signature, Option(SmartRE(f'(?:;)(?P<comment__>{WSP_RE__})|(?:,)(?P<comment__>{WSP_RE__})', '";"|","')))), Series(Drop(Text("}")), dwsp__)))
    document.set(Series(dwsp__, ZeroOrMore(Alternative(interface, type_alias, _namespace, enum, const, module, _top_level_assignment, _array_ellipsis, _top_level_literal, Series(Import, Option(Series(Drop(Text(";")), dwsp__))), Series(function, Option(Series(Drop(Text(";")), dwsp__))), Series(declaration, Option(Series(Drop(Text(";")), dwsp__)))))))
    root = Series(document, EOF)
    resume_rules__ = {'interface': [re.compile(r'(?=export|$)')],
                      'type_alias': [re.compile(r'(?=export|$)')],
                      'enum': [re.compile(r'(?=export|$)')],
                      'const': [re.compile(r'(?=export|$)')],
                      'declaration': [re.compile(r'(?=export|$)')],
                      '_top_level_assignment': [re.compile(r'(?=export|$)')],
                      '_top_level_literal': [re.compile(r'(?=export|$)')],
                      'module': [re.compile(r'(?=export|$)')]}
    root__ = root
    
parsing: PseudoJunction = create_parser_junction(ts2pythonGrammar)
get_grammar = parsing.factory # for backwards compatibility, only


#######################################################################
#
# AST SECTION - Can be edited. Changes will be preserved.
#
#######################################################################

SPECIAL_FUNCTIONS = {"Symbol.iterator": "__iter__"}

def convert_special_function(p: Path):
    node = p[-1]
    assert node.name == "special"
    identifier = node['name']
    identifier.name = "identifier"
    identifier.result = SPECIAL_FUNCTIONS.get(identifier.content, "__unknown__")

def add_flags(p: Path):
    p[0].attr['keep_comments'] = get_config_value('ts2python.KeepMultilineComments', False)

def clear_flags(p: Path):
    p[0].attr = dict()

ts2python_AST_transformation_table = {
    # AST Transformations for the ts2python-grammar
    # "<": flatten,
    "<<<": add_flags,
    ":Text": change_name('TEXT'),
    "comment__": remove_if(lambda p: p[-1].content.rfind('\n') < 0 \
                                     or not p[0].get_attr('keep_comments', True)),
    "special": [apply_if(add_error("Unknown special function"),
                         lambda p: p[-1]['name'].content not in SPECIAL_FUNCTIONS),
                convert_special_function],
    "function": apply_if(reduce_single_child, has_child('special')),
    "alias": reduce_single_child,
    "*": move_fringes(lambda p: p[-1].name == "comment__"),
    ">>>": clear_flags
}


def ts2pythonTransformer() -> TransformerCallable:
    """Creates a transformation function that does not share state with other
    threads or processes."""
    return static(partial(transformer,
        transformation_table=ts2python_AST_transformation_table.copy(),
        src_stage='cst', dst_stage='ast'))

ASTTransformation: Junction = Junction(
    'cst', ThreadLocalSingletonFactory(ts2pythonTransformer), 'ast')

#######################################################################
#
# COMPILER SECTION - Can be edited. Changes will be preserved.
#
#######################################################################

def dump_configuration() -> str:
    return f"""[ts2python]
RenderAnonymous = {get_config_value('ts2python.RenderAnonymous', 'local')}
UseEnum = {get_config_value('ts2python.UseEnum', True)}
UsePostponedEvaluation = {get_config_value('ts2python.UsePostponedEvaluation', True)}
UseTypeUnion = {get_config_value('ts2python.UseTypeUnion', False)}
UseExplicitTypeAlias = {get_config_value('ts2python.UseExplicitTypeAlias', False)}
UseTypeParameters = {get_config_value('ts2python.UseTypeParameters', False)}
UseLiteralType = {get_config_value('ts2python.UseLiteralType', False)}
UseVariadicGenerics = {get_config_value('ts2python.UseVariadicGenerics', False)}
UseNotRequired = {get_config_value('ts2python.UseNotRequired', False)}
AllowReadOnly = {get_config_value('ts2python.AllowReadOnly', False)}
AssumeDeferredEvaluation = {get_config_value('ts2python.AssumeDeferredEvaluation', False)}
KeepMultilineComments = {get_config_value('ts2python.KeepMultilineComments', False)}"""


def required_python_version(ts2python_cfg: Dict[str, bool],
                            purpose: str = "compatibility") -> Tuple[int, int]:
    assert purpose in ("compatibility", "features")
    min_version = (3, 7)
    if ts2python_cfg.get('ts2python.UseLiteralType', False):
        min_version = (3, 8)
    if ts2python_cfg.get('ts2python.UseTypeUnion', False):
        min_version = (3, 10)
    elif ts2python_cfg.get('ts2python.UseExplicitTypeAlias', False):
        min_version = (3, 10)
    if ts2python_cfg.get('ts2python.UseVariadicGenerics', False):
        min_version = (3, 11)
    elif ts2python_cfg.get('ts2python.UseNotRequired', False) \
            and purpose == "features":
        min_version = (3, 11)
    if ts2python_cfg.get('ts2python.UseTypeParameters', False):
        min_version = (3, 12)
    if ts2python_cfg.get('ts2python.AllowReadOnly', False) \
            and purpose == "features":
        min_version = (3, 13)
    if ts2python_cfg.get('ts2python.AssumeDeferredEvaluation', False):
        min_version = (3, 14)
    # Neither UseReadOnly nor UseNotRequired place any demand on the
    # Python version, because:
    # ReadOnly can be defined as Union for Python-version < 3.13
    # NotRequired can be defined as Optional for Python-version < 3.11
    return min_version


def set_compatibility_level(version_info: Tuple[int, ...] = (3, 7),
                            config_or_preset: str = "preset"):
    if config_or_preset == "preset":
        set_value = set_preset_value
    else:
        assert config_or_preset == "config"
        set_value = set_config_value
    if not version_info >= (3, 7):
        print('Compatibility version must be >= 3.7')
        sys.exit(1)
    if version_info >= (3, 8):
        set_value('ts2python.UseLiteralType', True, allow_new_key=True)
    if version_info >= (3, 10):
        set_value('ts2python.UseTypeUnion', True, allow_new_key=True)
        if version_info < (3, 12):
            set_value('ts2python.UseExplicitTypeAlias', True, allow_new_key=True)
    if version_info >= (3, 11):
        set_value('ts2python.UseNotRequired', True, allow_new_key=True)
        set_value('ts2python.UseVariadicGenerics', True, allow_new_key=True)
    if version_info >= (3, 12):
        set_value('ts2python.UseTypeParameters', True, allow_new_key=True)
    if version_info >= (3, 13):
        set_value('ts2python.AllowReadOnly', True, allow_new_key=True)
    if version_info >= (3, 14):
        set_value('ts2python.AssumeDeferredEvaluation', True, allow_new_key=True)




def source_hash(source_text: str) -> str:
    try:
        with open(__file__, 'r', encoding='utf-8') as f:
            script = f.read()
    except (FileNotFoundError, IOError):
        script = "source of ts2pythonParser.py not found!?"
    return md5(source_text, script, dump_configuration())


GENERAL_IMPORTS = """
import sys
from enum import Enum, IntEnum"""


TYPE_IMPORTS_37 = """from typing import Union, Optional, Any, Generic, TypeVar, Callable, List, \\
    Iterable, Iterator, Tuple, Dict, Awaitable
"""


TYPE_IMPORTS_311 = """from typing import Union, Optional, Any, Generic, TypeVar, Callable, List, \\
    Iterable, Iterator, Tuple, Dict, TypedDict, NotRequired, Literal, TypeAlias, \\
    Awaitable, Self
try:
    from typing import ReadOnly
except ImportError:
    ReadOnly = Union
"""

TYPE_IMPORTS_313 = """from typing import Union, Optional, Any, Generic, TypeVar, Callable, List, \\
    Iterable, Iterator, Tuple, Dict, TypedDict, NotRequired, Literal, ReadOnly, Awaitable
"""

TYPEDDICT_IMPORTS_37 = """
try:
    from ts2python.typeddict_shim import TypedDict, GenericTypedDict, NotRequired, Literal, \\
        ReadOnly, TypeAlias
    # Override typing.TypedDict for Runtime-Validation
except ImportError:
    print("Module ts2python.typeddict_shim not found. Only coarse-grained " 
          "runtime type-validation of TypedDicts possible")
    try:
        from typing import TypedDict, Literal
    except ImportError:
        try:
            from ts2python.typing_extensions import TypedDict, Literal
        except ImportError:
            print(f'Please install the "typing_extensions" module via the shell '
                  f'command "# pip install typing_extensions" before running '
                  f'{__file__} with Python-versions <= 3.8!')
    try:
        from typing_extensions import NotRequired, ReadOnly, TypeAlias
    except ImportError:
        NotRequired = Optional
        ReadOnly = Union
        TypeAlias = Any
    GenericMeta = type
    class _GenericTypedDictMeta(GenericMeta):
        def __new__(cls, name, bases, ns, total=True):
            return type.__new__(_GenericTypedDictMeta, name, (dict,), ns)
        __call__ = dict
    GenericTypedDict = _GenericTypedDictMeta('TypedDict', (dict,), {})
    GenericTypedDict.__module__ = __name__"""

TYPE_IMPORTS_MAPPING = {(3, 13): [TYPE_IMPORTS_313],
                        (3, 11): [TYPE_IMPORTS_311],
                        (3,  9): [TYPE_IMPORTS_37, TYPEDDICT_IMPORTS_37],
                        (3,  7): [TYPE_IMPORTS_37, TYPEDDICT_IMPORTS_37]}

FUNCTOOLS_IMPORTS = """
try:
    from ts2python.singledispatch_shim import singledispatch, singledispatchmethod
except ImportError:
    print("ts2python.singledispatch_shim not found! @singledispatch-annotation"          
          " imported from functools may cause NameErrors on forward-referenced"
          " types.")
    try:
        from functools import singledispatch, singledispatchmethod
    except ImportError:
        print(f"functools.singledispatchmethod does not exist in Python Version "
              f"{sys.version}. This module may therefore fail to run if "
              f"singledispatchmethod is needed, anywhere!")     
"""


PROMISE_LIKE_CLASS_312 = """class PromiseLike[T]:
    def then(self, onfullfilled: Optional[Callable], onrejected: Optional[Callable]) -> Self:
        pass
"""

PROMISE_LIKE_CLASS_37 = """PromiseLike = Iterable  # Admittedly, a very poor hack"""


def to_typename(varname: str) -> str:
    # assert varname[-1:] != '_' or keyword.iskeyword(varname[:-1]), varname  # and varname[0].islower()
    return varname[0].upper() + varname[1:] + '_'


def to_varname(typename: str) -> str:
    assert typename[0].isupper() or typename[-1:] == '_', typename
    return typename[0].lower() + (typename[1:-1] if typename[-1:] == '_' else typename[1:])


def to_dict(declarations: str) -> str:
    r"""Converts a sequence of declarations to a dictionary.
    Example::

        >>> decls = "name: str\nversion: int"
        >>> print(to_dict(decls))
        {"name": str, "version": int}
    """
    entries = declarations.split('\n')
    for i in range(len(entries)):
        k = entries[i].find(":")
        assert k >= 0
        entries[i] = f'"{entries[i][:k]}"{entries[i][k:]}'
    return "".join(["{", ", ".join(entries), "}"])


def is_qualified(name: str) -> bool:
    """Returns True if the given type-name is qualified, e.g.::

        >>> is_qualified("T")
        False
        >>> is_qualified("ReadOnly[T]")
        True
    """
    return name[-1:] == ']'


def strip_qualifier(qualified_name: str) -> str:
    """Removes qualifiers from type names, e.g.::

        >>> qualified_name = "ReadOnly[T]"
        >>> strip_qualifier(qualified_name)
        'T'
    """
    while True:
        a = qualified_name.find('[')
        b = qualified_name.rfind(']')
        if a >= 0:
            assert b >= 0, f"unmatched brackets in {qualified_name}"
            qualified_name = qualified_name[a + 1:b]
        else:
            assert b < 0, f"unmatched brackets in {qualified_name}"
            return qualified_name


def strip_type_parameters(objname: str) -> str:
    """Removes Type-Parameters from object name, e.g.::

        >>> strip_type_parameters("Mapping_0[K, V]")
        'Mapping_0'
        >>> strip_type_parameters("Mapping_0[K[X, Y], V]")
        'Mapping_0'
        >>> strip_type_parameters("Mapping_0[K, V[T[A, B]]]")
        'Mapping_0'
    """
    if objname[-1:] == ']':
        b = len(objname) - 1
        a = b
        while b >= a:
            a = objname.rfind('[', 0, a)
            b = objname.rfind(']', 0, b)
        return objname[:a]
    return objname


NOT_YET_IMPLEMENTED_WARNING = ErrorCode(310)
UNSUPPORTED_WARNING = ErrorCode(320)

TYPE_NAME_SUBSTITUTION = {
    'object': 'Dict',
    'array': 'List',
    'string': 'str',
    'number': 'float',
    'decimal': 'float',
    'integer': 'int',
    'uinteger': 'int',
    'boolean': 'bool',
    'null': 'None',
    'undefined': 'None',
    'unknown': 'Any',
    'any': 'Any',
    'void': 'None',

    'PromiseLike': 'PromiseLike',
    'IterableIterator': 'Iterator',
    'Array': 'List',
    'Record': 'Dict',
    'ReadonlyArray': 'List',
    'Uint32Array': 'List[int]',
    'Error': 'Exception',
    'RegExp': 'str' }


class ts2pythonCompiler(Compiler):
    """Compiler for the abstract-syntax-tree of a ts2python source file.
    """

    def reset(self):
        super().reset()
        self.additional_imports = ''
        self.require_singledispatch = False
        self.base_class_name = "TypedDict"
        self.render_anonymous = get_config_value('ts2python.RenderAnonymous', 'local')
        if self.render_anonymous not in ('type', 'functional', 'local', 'toplevel'):
            raise ValueError(
                f'Illegal value "{self.render_anonymous}" for '
                f'ts2python.RenderAnonymous. Must be one of "type", '
                f'"functional", "local", "toplevel".')
        ts2python_cfg = get_config_values('ts2python.*')
        self.use_enums = ts2python_cfg.get('ts2python.UseEnum', True)
        self.use_postponed_evaluation = ts2python_cfg.get('ts2python.UsePostponedEvaluation', False)
        self.use_type_union = ts2python_cfg.get('ts2python.UseTypeUnion', False)
        self.use_explicit_type_alias = ts2python_cfg.get('ts2python.UseExplicitTypeAlias', False)
        self.use_type_parameters = ts2python_cfg.get('ts2python.UseTypeParameters', False)
        if self.use_type_parameters:
            self.use_explicit_type_alias = False
        self.use_literal_type = ts2python_cfg.get('ts2python.UseLiteralType', False)
        self.use_variadic_generics = ts2python_cfg.get('ts2python.UseVariadicGenerics', False)
        self.use_not_required = ts2python_cfg.get('ts2python.UseNotRequired', False)
        self.allow_read_only = ts2python_cfg.get('ts2python.AllowReadOnly', False)
        self.assume_deferred_evaluation = ts2python_cfg.get('ts2python.AssumeDeferredEvaluation', False)
        self.keep_comments = ts2python_cfg.get('ts2python.KeepMultilineComments', False)
        self.compatibility_level = required_python_version(ts2python_cfg, "compatibility")
        self.feature_level = required_python_version(ts2python_cfg, "features")
        if self.use_type_parameters and not self.use_variadic_generics:
            raise ValueError(
                'Configuration flag UseTypeParameters can only be set to True '
                'if UseVariadicGenerics is also set to True!')

        self.overloaded_type_names: Set[str] = set()
        self.known_types: List[Dict[str, str]] = [
            {'Union': 'Union', 'List': 'List', 'Tuple': 'Tuple', 'Optional': 'Optional',
             'Dict': 'Dict', 'Set': 'Set', 'Any': 'Any', 'Generic': 'Generic',
             'Coroutine': 'Coroutine', 'list': 'list', 'tuple': 'tuple', 'dict': 'dict',
             'set': 'set', 'frozenset': 'frozenset', 'int': 'int', 'float': 'float',
             'str': 'str', 'None': 'None'}]
        self.local_classes: List[List[str]] = [[]]
        self.base_classes: Dict[str, List[str]] = {}
        self.typed_dicts: Set[str] = {'TypedDict'}  # names of classes that are TypedDicts
        # self.default_values: Dict = {}
        # self.referred_objects: Dict = {}
        self.basic_type_aliases: Set[str] = set()
        self.obj_name: List[str] = ['TOPLEVEL_']
        self.scope_type: List[str] = ['']
        self.optional_keys: List[List[str]] = [[]]
        self.func_name: str = ''  # name of the current functions header or ''
        self.func_type_parameters: str = ''  # type parameters of the current function header, if any
        self.strip_type_from_const = False


    def compile(self, node) -> str:
        result = super().compile(node)
        if isinstance(result, str):
            return result
        raise TypeError(f"Compilation of {node.name} yielded a result of "
                        f"type {str(type(result))} and not str as expected!")

    def is_toplevel(self) -> bool:
        return self.obj_name == ['TOPLEVEL_']

    def get_known_type(self, typename: str, value: str = "") -> str:
        i = typename.find('[')
        if i >= 0:  typename = typename[:i]  # for example, reduces List[str] to List
        for type_dict in self.known_types:
            if typename in type_dict:
                return type_dict[typename]
        return value

    def add_to_known_types(self, node, typename: str, kind: str):
        if typename in self.known_types[-1] and not is_qualified(kind):
            self.tree.new_error(
                node, f'{node.name} {typename} has already been defined earlier as '
                f'{self.known_types[-1][typename]}!', WARNING)
        self.known_types[-1][typename] = kind

    def prepare(self, root: Node) -> None:
        type_aliases = {nd['identifier'].content for nd in root.select_children('type_alias')}
        namespaces = {nd['identifier'].content for nd in root.select_children('namespace')}
        self.overloaded_type_names = type_aliases & namespaces
        self.tree.stage = 'py'
        return None

    def finalize(self, python_code: Any) -> Any:
        chksum = f'source_hash__ = "{source_hash(self.tree.source)}"'
        if self.tree.name == 'root':
            for py_version, type_imports in TYPE_IMPORTS_MAPPING.items():
                if self.compatibility_level >= py_version:
                    break
            else:
                raise ValueError(f'Illegal minimal Python version {self.compatibility_level}')
            c_major, c_minor = self.compatibility_level
            # f_major, f_minor = self.feature_level
            code_blocks = [f'# Generated by ts2python version {version} '
                           f'on {datetime.datetime.now()}\n# compatibility level: '
                           f'Python {c_major}.{c_minor} and above\n',
                           # f'# feature level: Python {f_major}.{f_minor}\n',
                           'from __future__ import annotations' if
                           self.use_postponed_evaluation else '',
                           GENERAL_IMPORTS] \
                + type_imports \
                + ([FUNCTOOLS_IMPORTS] if self.require_singledispatch else []) \
                + [self.additional_imports, chksum, '\n##### BEGIN OF ts2python generated code\n']
        else:
            code_blocks = []
        code_blocks.append(python_code)
        if self.tree.name == 'root':
            code_blocks.append('\n##### END OF ts2python generated code\n')
        cooked = '\n\n'.join(code_blocks)
        cooked = re.sub(' +(?=\n)', '', cooked)
        return re.sub(r'\n\n\n+', '\n\n\n', cooked)

    def on_EMPTY__(self, node) -> str:
        return ''

    def on_ZOMBIE__(self, node) -> str:
        self.tree.new_error(node,
            "Malformed syntax-tree! Possibly caused by a parsing error.")
        return ""
        # raise ValueError('Malformed syntax-tree!')

    def on_comment__(self, node) -> str:
        assert node.content.rfind("\n") >= 0  # inline comments should have been removed
        if self.keep_comments:
            comment = node.content
            multiline = True if re.match(' *\n', comment) else False
            comment = comment.strip()
            comment = re.sub(r'/\*+\s*|\s*\*/|//[ \t]*', '', comment)
            comment = re.sub(r'(?:\n|^)[ \t]*\* ?', '\n', comment).lstrip()
            lines = comment.split('\n')
            for i in range(len(lines)):
                line = lines[i].strip()
                lines[i] = "# " + line if line else ''
            comment = '\n'.join(lines)
            return f"\n{comment}" if multiline else comment
        return ""

    def on_root(self, node) -> str:
        assert len(node.children) == 1
        return self.compile(node.children[0])

    def on_document(self, node) -> str:
        if 'module' in node and isinstance(node['module'], Sequence) > 1:
            self.tree.new_error(
                node, 'Transpiling more than a single ambient module '
                'is not yet implemented! Only the first ambient module will '
                'be transpiled for now.', NOT_YET_IMPLEMENTED_WARNING)
            return self.compile(node['module'][0]['document'])
        self.mark_overloaded_functions(node)
        return '\n\n'.join(self.compile(child) for child in node.children
                           if child.name != 'declaration')

    def on_module(self, node) -> str:
        name = self.compile(node['identifier'])
        return self.compile(node['document'])

    def on_Import(self, node) -> str:
        return ""  # For now, ignore imports

    def on_symbol(self, node) -> str:
        return ""  # For the time being

    def render_class_header(self, name: str,
                            base_classes: str,
                            force_base_class: str = '',
                            generic_types: str = '') -> str:
        assert name
        optional_key_list = self.optional_keys[-1]
        base_class_name = (force_base_class or self.base_class_name).strip()
        tps = generic_types if self.use_type_parameters else ''
        if base_class_name == 'TypedDict':
            total = not bool(optional_key_list) or self.use_not_required
            if base_classes:
                td_name = 'TypedDict' if (self.use_variadic_generics or
                                          base_classes.find('Generic[') < 0) \
                                      else 'GenericTypedDict'
                if self.use_not_required or total:
                    return f"class {name}{tps}({base_classes}, {td_name}):\n"
                else:
                    return f"class {name}{tps}({base_classes}, "\
                           f"{td_name}, total={total}):\n"
            else:
                tps = generic_types if self.use_type_parameters else ''
                if self.use_not_required or total:
                    return f"class {name}{tps}(TypedDict):\n"
                else:
                    return f"class {name}{tps}(TypedDict, total={total}):\n"
        else:
            if base_classes:
                if base_class_name:
                    return f"class {name}{tps}({base_classes}, {base_class_name}):\n"
                else:
                    return f"class {name}{tps}({base_classes}):\n"
            else:
                if base_class_name:
                    return f"class {name}{tps}({base_class_name}):\n"
                else:
                    return f"class {name}{tps}:\n"

    def render_local_classes(self) -> str:
        self.func_name = ''
        classes = self.local_classes[-1]
        return '\n'.join(lc for lc in classes) + '\n' if classes else ''

    def process_type_parameters(self, node: Node) -> Tuple[str, str]:
        tps = ''
        preface = ''
        try:
            tp = self.compile(node['type_parameters'])
            tpl_qualified = [p.replace("'", "") for p in tp.split(', ')]  # may contain "ReadOnly[...]"
            tpl = [strip_qualifier(p) for p in tpl_qualified]
            tps = '[' + ', '.join(p for p in tpl) + ']'
            if self.use_type_parameters:
                preface = ''
            else:
                preface = ''.join(f"{p} = TypeVar('{p}')\n"
                                  for p in tpl if not self.get_known_type(p))
            for q, p in zip(tpl_qualified, tpl):
                self.add_to_known_types(node, p, q if is_qualified(q) else '[]')
        except KeyError:
            pass
        return tps, preface

    def on_interface(self, node) -> str:
        name = self.compile(node['identifier'])
        self.obj_name.append(name)
        self.scope_type.append('interface')
        self.local_classes.append([])
        self.optional_keys.append([])
        if self.use_type_parameters:  self.known_types.append(dict())
        tps, preface = self.process_type_parameters(node)
        preface += '\n'
        preface += node.get_attr('preface', '')
        if not self.use_type_parameters:  self.known_types.append(dict())
        base_class_list = []
        try:
            base_class_list = self.bases(node['extends'])
            base_classes = ', '.join(base_class_list)  # self.compile(node['extends'])
            if self.local_classes[-1]:
                preface += self.render_local_classes() + '\n'
                self.local_classes[-1] = []
            if tps and not self.use_variadic_generics:
                base_classes += f", Generic{tps}"
        except KeyError:
            base_classes = f"Generic{tps}" \
                if (tps and not self.use_type_parameters
                    and (not self.use_variadic_generics
                         or 'function' in node['declarations_block']))\
                else ''
        if any(bc not in self.typed_dicts for bc in base_class_list):
            force_base_class = ' '
        elif 'function' in node['declarations_block']:
            force_base_class = ' '  # do not derive from TypeDict
        else:
            force_base_class = ''
            self.typed_dicts.add(name)
        decls_block = node['declarations_block']
        save_render_anonymous = self.render_anonymous
        if force_base_class:
            self.render_anonymous = "local"
            decls_block.attr['no_typed_dict'] = True
        decls = self.compile(decls_block)
        interface = self.render_class_header(name, base_classes, force_base_class, tps)
        self.base_classes[name] = base_class_list
        if self.base_class_name == "TypedDict" and self.render_anonymous == "toplevel":
            interface = self.render_local_classes() + '\n' + interface
        else:
            interface += ('    ' + self.render_local_classes().replace('\n', '\n    ')).rstrip(' ')
        self.render_anonymous = save_render_anonymous
        self.optional_keys.pop()
        self.local_classes.pop()
        self.known_types.pop()
        self.add_to_known_types(node, name, 'interface')
        self.scope_type.pop()
        self.obj_name.pop()
        return preface + interface + '    ' + decls.replace('\n', '\n    ')

    # def on_type_parameter(self, node) -> str:  # OBSOLETE, see on_type_parameters()
    #     return self.compile(node['identifier'])

    @lru_cache(maxsize=4)
    def bases(self, node) -> List[str]:
        assert node.name == 'extends'
        bases = [self.compile(nd) for nd in node.children]
        return [TYPE_NAME_SUBSTITUTION.get(bc, bc) for bc in bases]

    def on_extends(self, node) -> str:
        return ', '.join(self.bases(node))

    def on_type_alias(self, node) -> str:
        alias = self.compile(node['identifier'])
        if all(typ[0].name in ('basic_type', 'literal')
               for typ in node.select('type')):
            self.basic_type_aliases.add(alias)
        self.obj_name.append(alias)
        if alias not in self.overloaded_type_names:
            if self.use_type_parameters:  self.known_types.append(dict())
            tps, preface = self.process_type_parameters(node)
            if not self.use_type_parameters:
                if self.use_explicit_type_alias:
                    tps = ": TypeAlias"
                else:
                    tps = ''
            if self.known_types[-1].get(alias, '') \
                    in ('namespace', 'enum', 'virtual_enum'):
                preface = ('# commented out, because there is already an '
                           'enumeration with the same name\n# ' + preface)
            else:
                self.add_to_known_types(node, alias, 'type_alias')
            self.local_classes.append([])
            self.optional_keys.append([])
            types = self.compile(node['types'])
            preface += self.render_local_classes()
            self.optional_keys.pop()
            self.local_classes.pop()
            if self.use_type_parameters:  self.known_types.pop()
            code = preface + ("type " if self.use_type_parameters else "") \
                   + f"{alias}{tps} = {types}"
            # there follows a hack to avoid failure on type unions of
            # stringified type aliases and real types
            if not self.use_type_parameters \
                    and types[-1:] == "'" and alias in self.known_types[-1]:
                del self.known_types[-1][alias]
        else:
            code = ''
        if node[-1].name == 'comment__':
            code += '\n\n' + self.compile(node[-1])
        self.obj_name.pop()
        return code

    def mark_overloaded_functions(self, scope: Node):
        is_interface = self.scope_type[-1] in ('interface', 'namespace')
        first_use: Dict[str, Node] = dict()
        try:
            for func_decl in as_list(scope['function']):
                name = func_decl['identifier'].content
                if keyword.iskeyword(name):
                    name += '_'
                if name in first_use:
                    first_use[name].attr['decorator'] = \
                        '@singledispatchmethod' if is_interface \
                        else '@singledispatch'
                    func_decl.attr['decorator'] = f'@{name}.register'
                    self.require_singledispatch = True
                else:
                    first_use[name] = func_decl
        except KeyError:
            pass  # no functions in declarations block

    def on_declarations_tuple(self, node) -> str:
        return self.on_declarations_block(node)

    def on_declarations_block(self, node) -> str:
        self.mark_overloaded_functions(node)
        # declarations = '\n'.join(self.compile(nd) for nd in node
        #                          if nd.name in ('declaration', 'function'))
        if node.get_attr('no_typed_dict', False):
            for nd in node.children:
                if 'optional' in nd:
                    nd.attr['force_optional'] = True
        raw_decls = [self.compile(nd) for nd in node
                     if nd.name in ('declaration', 'function', 'comment__')]
        declarations = '\n'.join(d for d in raw_decls if d)
        return declarations or "pass"

    def on_declaration(self, node) -> str:
        identifier = self.compile(node['identifier'])
        self.obj_name.append(to_typename(identifier))
        T = self.compile_type_expression(node, node['types']) \
            if 'types' in node else 'Any'
        typename = self.obj_name.pop()
        if T[0:5] == 'class':
            self.local_classes[-1].append(T)
            T = typename  # substitute typename for type
        if 'optional' in node:
            self.optional_keys[-1].append(identifier)
            T = f"Optional[{T}]" if node.get_attr('force_optional', False) \
                else f"NotRequired[{T}]"
        if self.is_toplevel() and bool(self.local_classes[-1]):
            preface = self.render_local_classes()
            self.local_classes.pop()
            self.optional_keys.pop()
            return preface + f"{identifier}: {T}"
        return f"{identifier}: {T}"

    def on_function(self, node) -> str:
        is_constructor = False
        if 'identifier' in node:
            name = self.compile(node["identifier"])
            self.func_name = name
            if name == 'constructor' and self.scope_type[-1] == 'interface':
                name = self.obj_name[-1] + 'Constructor'
                is_constructor = True
        else:  # anonymous function
            name = "__call__"
        if self.use_type_parameters:  self.known_types.append(dict())
        tps, preface = self.process_type_parameters(node)
        if preface and not self.is_toplevel():
            self.local_classes[-1].insert(0, preface)
            preface = ''
        if not self.use_type_parameters:  tps = ''
        self.func_type_parameters = tps
        try:
            arguments = self.compile(node['arg_list'])
            if self.scope_type[-1] == 'interface':
                arguments = 'self, ' + arguments
        except KeyError:
            arguments = 'self' if self.scope_type[-1] == 'interface' else ''
        try:
            return_type = self.compile(node['types'])
        except KeyError:
            return_type = 'Any'
        if self.use_type_parameters:  self.known_types.pop()
        decorator = node.get_attr('decorator', '')
        fallback = ""
        type_error = "raise TypeError(f'First argument {arg1} of single-dispatch " \
                     "function/method {name} has illegal type {type(arg1)}')"
        if decorator:
            if decorator == "@singledispatch":
                fallback = f"\n{preface}@singledispatch\ndef {name}{tps}(arg1) -> {return_type}:" \
                           f"\n    {type_error}\n"
                decorator = f"@{name}.register"
            elif decorator == "@singledispatchmethod":
                fallback = f"\n{preface}@singledispatchmethod\ndef {name}{tps}(self, arg1) -> {return_type}:" \
                           f"\n    {type_error}\n"
                decorator = f"@{name}.register"
            else:  assert decorator.endswith('.register')
            name = '_'
            decorator += '\n'
        pyfunc = f"{decorator}def {name}{tps}({arguments}) -> {return_type}:\n    pass"
        if is_constructor:
            interface = pick_from_path(self.path, 'interface', reverse=True)
            assert interface
            interface.attr['preface'] = ''.join([
                interface.get_attr('preface', ''), f"\n{preface}{pyfunc}", '\n'])
            return ''
        else:
            return f"{fallback}\n{preface if not fallback else ''}{pyfunc}"

    def on_arg_list(self, node) -> str:
        breadcrumb = '/'.join(nd.name for nd in self.path)
        if breadcrumb.rfind('func_type') > breadcrumb.rfind('function'):
            arg_list = [self.compile(nd) for nd in node.children]
            if any(arg[0:1] == '*' for arg in arg_list):
                return '...'
            return ', '.join(re.sub(r'^\w+\s*:\s*', '', arg) for arg in arg_list)
        return ', '.join(self.compile(nd) for nd in node.children)

    def on_arg_tail(self, node):
        argname = self.compile(node["identifier"])
        if 'array_of' in node:
            self.obj_name.append(to_typename(argname))
            type = self.compile(node['array_of'])[5:-1]
            self.obj_name.pop()
            return f'*{argname}: {type}'
        else:
            return '*' + argname

    def on_argument(self, node) -> str:
        argname = self.compile(node["identifier"])
        if 'types' in node:
            self.obj_name.append(to_typename(argname))
            types = self.compile_type_expression(node, node['types'])
            self.obj_name.pop()
            if 'optional' in node:
                types = f'Optional[{types}] = None'
            return f'{argname}: {types}'
        else:
            return f'{argname} = None' if 'optional' in node else argname

    def on_optional(self, node):
        assert False, "This method should never have been called!"

    def on_index_signature(self, node) -> str:
        if "keyof" in node:
            self.tree.new_error(node,
                "ts2Python cannot infer 'keyof'-types. Any-type returned.",
                UNSUPPORTED_WARNING)
            return "Optional[Any]" if node[-1].name == 'optional' else "Any"
            # return self.compile(node["identifier"])  # should Any be returned, here?
        else:
            typ = self.compile(node['type'])
            return f'Optional[{typ}]' if node[-1].name == 'optional' else typ

    def render_union(self, preface, union) -> str:
        if self.use_type_union or len(union) <= 1:
            # if any(typ[0:1] in ('"', "'") for typ in union):
            if any(typ[0:1] in ('"', "'") for typ in union)\
                    or (not self.use_type_parameters and
                        (not all(self.get_known_type(typ) for typ in union) \
                         and pick_from_path(self.path, 'type_alias'))):
                union = [typ.replace("'", '').replace('"', '') for typ in union]
                return f"{preface}'{' | '.join(union)}'"
            else:
                return preface + ' | '.join(union)
        else:
            return preface + f"Union[{', '.join(union)}]"

    def readonly_decl(self) -> bool:
        for i in range(len(self.path) - 2, -1, -1):
            decl = self.path[i]
            if decl.name == 'types':
                break
            if decl.name == 'declaration':
                if i >= 0 and self.path[i-1].name == 'declarations_block' \
                        and 'function' in self.path[i-1]:
                    break
                qualifiers = decl.get('qualifiers', None)
                if qualifiers and 'readonly' in qualifiers:
                    return True
        return False

    def on_types(self, node) -> str:
        union = []
        i = 0
        obj_name_stub = '' if self.is_toplevel() else self.obj_name[-1]
        fname = self.func_name[:1].upper() + self.func_name[1:]
        ftps = self.func_type_parameters
        for nd in node.children:
            n = obj_name_stub.rfind('_')
            ending = strip_type_parameters(obj_name_stub)[n + 1:]
            if n >= 0 and (not ending or ending.isdecimal()):
                obj_name_stub = obj_name_stub[:n]
            self.obj_name[-1] = fname + obj_name_stub + '_' + str(i) + ftps
            save = self.func_name
            self.func_name = ""
            typ = self.compile_type_expression(node, nd)
            self.func_name = save
            if typ not in union:
                union.append(typ)
                i += 1
            self.obj_name[-1] = obj_name_stub or 'TOPLEVEL_'
        for i in range(len(union)):
            typ = union[i]
            if typ[0:5] == 'class':
                k = typ.rfind('\nclass')
                m = re.match(r"class\s*(\w+)(\[\w+(?:,\s*\w+)*])?[\w(){},' =]*\s*:", typ[k + 1:])
                assert m, typ
                cname = m.group(1)
                self.local_classes[-1].append(typ)
                union[i] = cname
        if self.is_toplevel():
            preface = self.render_local_classes()
        else:
            preface = ''
        if self.use_literal_type and \
                any(nd[0].name == 'literal' for nd in node.children):
            if all(nd[0].name == 'literal' for nd in node.children):
                result = f"Literal[{', '.join(typ for typ in union)}]"
            else:
                new_union = []
                literal_package = []
                for i, nd in enumerate(node.children):
                    if nd[0].name == 'literal':
                        literal_package.append(union[i])
                    else:
                        if literal_package:
                            new_union.append(f"Literal[{', '.join(l for l in literal_package)}]")
                            literal_package = []
                        new_union.append(union[i])
                if literal_package:
                    new_union.append(f"Literal[{', '.join(l for l in literal_package)}]")
                result = self.render_union(preface, new_union)
        else:
            result = self.render_union(preface, union)
        return f"ReadOnly[{result}]" if self.allow_read_only and self.readonly_decl() \
            else result

    def render_declarations(self, decls: str) -> str:
        if self.base_class_name != "TypedDict" or self.render_anonymous == "local":
            return ''.join([self.render_class_header(self.obj_name[-1], '') + "    ",
                            self.render_local_classes().replace('\n', '\n    '),
                            decls.replace('\n', '\n    ')])
        elif self.render_anonymous == "toplevel":
            # the magic marker "TOPLEVEL_" should not be part of the class-name,
            # but make sure that there is always a name, even in a testing-context
            # that does not start at top-level. Thus, the or-clause in class_name.
            names = [strip_type_parameters(name) for name in self.obj_name[1:-1]] \
                    + [self.obj_name[-1]]
            class_name = '_'.join(names) or self.obj_name[0]
            return ''.join([self.render_local_classes(),
                            self.render_class_header(class_name, '') + "    ",
                            decls.replace('\n', '\n    ')])
        elif self.render_anonymous == "functional":
            return f'TypedDict("{self.obj_name[-1]}", {to_dict(decls)})'
        else:
            assert self.render_anonymous == "type"
            return f'TypedDict[{to_dict(decls)}]'

    def on_type(self, node) -> str:
        num_children = len(node.children)
        assert 1 <= num_children <= 2
        readonly = node[0].name == 'readonly'
        assert readonly or num_children == 1
        typ = node[1] if readonly else node[0]
        readonly = readonly or self.readonly_decl()
        if typ.name in ('declarations_block', 'declarations_tuple'):
            self.local_classes.append([])
            self.optional_keys.append([])
            decls = self.compile(typ)
            result = self.render_declarations(decls)
            self.optional_keys.pop()
            self.local_classes.pop()
        elif typ.name == 'literal':
            literal_typ = typ[0].name
            if self.use_literal_type:
                result = self.compile(typ)
            elif literal_typ == 'array':
                result = 'List'
            elif literal_typ == 'object':
                result = 'Dict'
            elif literal_typ in ('number', 'integer'):
                literal = self.compile(typ)
                try:
                    _ = int(literal)
                    result = 'int'
                except ValueError:
                    result = 'str'
            elif literal_typ == 'boolean':
                result = 'bool'
            else:
                assert literal_typ == 'string', literal_typ
                _ = self.compile(typ)
                result = 'str'
        else:
            result = self.compile(typ)
        if self.allow_read_only and \
                (readonly or self.get_known_type(result)[:9] == "ReadOnly["):
            return f"ReadOnly[{result}]"
        else:
            return result


    def on_type_tuple(self, node):
        return 'Tuple[' + ', '.join(self.compile(nd) for nd in node) + ']'

    def on_mapped_type(self, node) -> str:
        return self.compile(node['map_signature'])

    def on_map_signature(self, node) -> str:
        return "Dict[%s, %s]" % (self.compile(node['index_signature']),
                                 self.compile(node['types']))

    def on_indexed_type(self, node) -> str:
        assert node[0].name == "type_name"
        self.tree.new_error(node,
            'ts2Python cannot determine index types. Any-type returned.',
            UNSUPPORTED_WARNING)
        return "Any"
        # return self.on_type_name(node[0])

    def on_func_type(self, node) -> str:
        if 'arg_list' in node:
            arg_list = self.compile(node["arg_list"])
            if  arg_list == "..." or arg_list.find('= None') >= 0 \
                    or arg_list.find('*') >= 0:
                # See https://docs.python.org/3/library/typing.html#typing.Callable
                args = '...'
            else:
                args = f'[{arg_list}]'
        else:
            args = '[]'
        types = self.compile(node["types"])
        return f'Callable[{args}, {types}]'

    def on_intersection(self, node) -> str:
        # ignore intersection
        self.tree.new_error(node,
            'Type intersections are not yet implemented. Any-type returned.',
            NOT_YET_IMPLEMENTED_WARNING)
        return "Any"

    def on_virtual_enum(self, node) -> str:
        name = self.compile(node['identifier'])
        if self.known_types[-1].get(name, '') == 'type_alias':
            # silently overwrite type_alias
            self.known_types[-1][name] = 'virtual_enum'
        else:
            self.add_to_known_types(node, name, 'virtual_enum')
        save = self.strip_type_from_const
        if all(child.name == 'const' for child in node.children[1:]):
            if all(nd['literal'][0].name == 'integer'
                   for nd in node.select_children('const') if 'literal' in nd):
                header = f'class {name}(IntEnum):'
            else:
                header =  f'class {name}(Enum):'
            self.strip_type_from_const = True
        else:
            header = ''
        namespace = []
        for child in node.children[1:]:
            namespace.append(self.compile(child))
        if not header:
            header = self.render_class_header(name, '')[:-1]  # leave out the trailing "\n"
            # self.optional_keys.pop()?
        namespace.insert(0, header)
        self.strip_type_from_const = save
        return '\n    '.join(namespace)

    def on_namespace(self, node) -> str:
        # errmsg = "Transpilation of namespaces that contain more than just " \
        #          "constant definitions has not yet been implemented."
        # self.tree.new_error(node, errmsg, NOT_YET_IMPLEMENTED_WARNING)
        # return "# " + errmsg
        name = self.compile(node['identifier'])
        self.add_to_known_types(node, name, 'namespace')
        declarations = [f'class {name}:']
        assert len(node.children) >= 2
        self.mark_overloaded_functions(node)
        self.obj_name.append(name)
        self.scope_type.append('namespace')
        self.local_classes.append([])
        self.optional_keys.append([])
        self.known_types.append(dict())
        self.mark_overloaded_functions(node)
        declaration = self.compile(node[1])
        declaration = declaration.lstrip('\n')
        declarations.extend(declaration.split('\n'))
        for nd in node[2:]:
            declaration = self.compile(nd)
            declarations.extend(declaration.split('\n'))
        local_classes = self.render_local_classes()
        if self.render_anonymous != 'toplevel':
            if local_classes:
                declarations.insert(1, local_classes.replace('\n', '\n    '))
            result = '\n    '.join(declarations)
        else:
            if local_classes:
                result = ''.join([local_classes, '\n',
                                  '\n    '.join(declarations)])
            else:
                result = '\n    '.join(declarations)
        self.known_types.pop()
        self.add_to_known_types(node, name, 'namespace')
        self.local_classes.pop()
        self.optional_keys.pop()
        self.scope_type.pop()
        self.obj_name.pop()
        return result

    def on_enum(self, node) -> str:
        if self.use_enums:
            if all(nd['literal'][0].name == 'integer' for
                   nd in node.select_children('item') if 'literal' in nd):
                base_class = '(IntEnum)'
            else:
                base_class = '(Enum)'
        else:
            base_class = ''
        name = self.compile(node['identifier'])
        self.add_to_known_types(node, name, 'enum')
        enum = ['class ' + name + base_class + ':']
        for item in node.select_children('item'):
            enum.append(self.compile(item))
        return '\n    '.join(enum)

    def on_item(self, node) -> str:
        if len(node.children) == 1:
            identifier = self.compile(node[0])
            if self.use_enums:
                return identifier + ' = enum.auto()'
            else:
                return identifier + ' = ' + repr(identifier)
        else:
            return self.compile(node['identifier']) + ' = ' + self.compile(node['literal'])

    def on_const(self, node) -> str:
        if 'literal' in node or 'identifier' in node:
            if self.strip_type_from_const:
                return self.compile(node['declaration']['identifier']) \
                       + ' = ' + self.compile(node[-1])
            else:
                return self.compile(node['declaration']) + ' = ' + self.compile(node[-1])
        else:
            # const without assignment, e.g. "export const version: string;"
            return self.compile(node['declaration'])

    def on_assignment(self, node) -> str:
        return self.compile(node['variable']) + ' = ' + self.compile(node[1])

    def on_literal(self, node) -> str:
        assert len(node.children) == 1
        return self.compile(node[0])

    def on_integer(self, node) -> str:
        return node.content

    def on_number(self, node) -> str:
        return node.content

    def on_boolean(self, node) -> str:
        return {'true': 'True', 'false': 'False'}[node.content]

    def on_string(self, node) -> str:
        return node.content

    def on_array(self, node) -> str:
        return '[' + \
               ', '.join(self.compile(nd) for nd in node.children) + \
               ']'

    def on_object(self, node) -> str:
        return '{\n    ' + \
               ',\n    '.join(self.compile(nd) for nd in node.children) + \
               '\n}'

    def on_association(self, node) -> str:
        return f'"{self.compile(node["key"])}": ' + self.compile(node['literal'])

    def on_key(self, node) -> str:
        return node.content

    def on_basic_type(self, node) -> str:
        return TYPE_NAME_SUBSTITUTION[node.content]

    def on_generic_type(self, node) -> str:
        type_name = node['type_name']
        if type_name.content == 'PromiseLike' \
                and 'PromiseLike' not in self.known_types \
                and 'PromiseLike' not in self.obj_name:  # a hack for a special case
            interface = pick_from_path(self.path, 'interface')  # a hack for a special case
            if not interface or not interface['identifier'].content == 'PromiseLike':
                if self.compatibility_level >= (3, 12):
                    promiselike_def = PROMISE_LIKE_CLASS_312
                else:
                    promiselike_def = PROMISE_LIKE_CLASS_37
                self.local_classes[-1].append(promiselike_def)
                self.known_types[-1]['PromiseLike']= 'PromiseLike'
        base_type = self.compile(type_name)
        parameters = self.compile(node['type_parameters'])
        if parameters == 'None':
            return base_type
        else:
            return f'{base_type}[{parameters}]'

    def on_type_parameters(self, node) -> str:
        type_parameters = [self.compile(nd) for nd in node.children]
        return ', '.join(type_parameters)

    def on_parameter_types(self, node) -> str:
        return self.on_types(node)

    def on_parameter_type(self, node) -> str:
        if len(node.children) > 1 and node[0].name != 'readonly':
            node.result = (node[0],)  # ignore extends_type and equals_type for now
        return self.on_type(node)

    def on_extends_type(self, node) -> str:
        # TODO: generate TypeVar with restrictions
        self.tree.new_error(node, "restrictied generics not yet implemented",
                            NOT_YET_IMPLEMENTED_WARNING)
        return ""

    def on_equals_type(self, node) -> str:
        # TODO: generate TypeVar with restrictions
        self.tree.new_error(node, "restrictied generics not yet implemented",
                            NOT_YET_IMPLEMENTED_WARNING)
        return ""

    def on_type_name(self, node) -> str:
        name = self.compile(node['name'])
        return TYPE_NAME_SUBSTITUTION.get(name, name)

    def compile_type_expression(self, node, type_node) -> str:
        unknown_types = set(tn.content for tn in node.select('type_name')
                            if not self.get_known_type(tn.content))
        type_expression = self.compile(type_node)
        if self.assume_deferred_evaluation or self.use_postponed_evaluation:
            type_expression = type_expression.replace("'", "")
        else:
            for typ in unknown_types:
                rx = re.compile(r"(?:(?<=[^\w'])|^)" + typ + r"(?:(?=[^\w'])|$)")
                segments = type_expression.split("'")
                for i in range(0, len(segments), 2):
                    segments[i] = rx.sub(f"'{typ}'", segments[i])
                type_expression = "'".join(segments)
                # type_expression = rx.sub(f"'{typ}'", type_expression)
            if type_expression[0:1] == "'":
                type_expression = ''.join(["'", type_expression.replace("'", ""), "'"])
        return type_expression

    def on_array_of(self, node) -> str:
        assert len(node.children) == 1
        element_type = self.compile_type_expression(node, node[0])
        return 'List[' + element_type + ']'

    def on_array_types(self, node) -> str:
        return self.on_types(node)

    def on_array_type(self, node) -> str:
        return self.on_type(node)

    def on_qualifiers(self, node):
        assert False, ('Qualifiers should be ignored and this method should '
                       'never be called! "readonly" will be taken care by '
                       'on_type().')

    def on_variable(self, node) -> str:
        return self.compile(node['name'])

    def on_name(self, node):
        return '.'.join((name + '_' if keyword.iskeyword(name) else name)
                        for name in node.content.split('.'))

    def on_identifier(self, node) -> str:
        identifier = node.content
        if keyword.iskeyword(identifier):
            identifier += '_'
        return identifier

compiling: Junction = create_junction(
    ts2pythonCompiler, "ast", "py")


#######################################################################
#
# Processing-Pipeline
#
#######################################################################

# Add your own stages to the junctions and target-lists, below
# (See DHParser.compile for a description of junctions)

# ADD YOUR OWN POST-PROCESSING-JUNCTIONS HERE:
junctions = set([ASTTransformation, compiling])

# put your targets of interest, here. A target is the name of result (or stage)
# of any transformation, compilation or postprocessing step after parsing.
# Serializations of the stages listed here will be written to disk when
# calling process_file() or batch_process() and also appear in test-reports.
targets = end_points(junctions)
# alternative: targets = set([compiling.dst])

# provide a set of those stages for which you would like to see the output
# in the test-report files, here. (AST is always included)
test_targets = set(j.dst for j in junctions)
# alternative: test_targets = targets

# add one or more serializations for those targets that are node-trees
serializations = expand_table(dict([('*', ['sxpr'])]))

#######################################################################
#
# END OF DHPARSER-SECTIONS
#
#######################################################################

RESULT_FILE_EXTENSION = ".py"  # Change this according to your needs!


def compile_src(source: str, target: str = "py") -> Tuple[Any, List[Error]]:
    """Compiles ``source`` and returns (result, errors)."""
    results = full_pipeline(source, preprocessing.factory, parsing.factory,
                           junctions, {target})
    return results[target]


def serialize_result(result: Any) -> Union[str, bytes]:
    """Serialization of result. REWRITE THIS, IF YOUR COMPILATION RESULT
    IS NOT A TREE OF NODES.
    """
    if isinstance(result, Node):
        return result.serialize(how='default' if RESULT_FILE_EXTENSION != '.xml' else 'xml')
    elif isinstance(result, (str, StringView)):
        return result
    else:
        return repr(result)


def process_file(source: str, out_dir: str = '') -> str:
    """Compiles the source and writes the serialized results back to disk,
    unless any fatal errors have occurred. Error and Warning messages are
    written to a file with the same name as `result_filename` with an
    appended "_ERRORS.txt" or "_WARNINGS.txt" in place of the name's
    extension. Returns the name of the error-messages file or an empty
    string, if no errors of warnings occurred.
    """
    source_filename = source if is_filename(source) else ''
    if source_filename:
        result_filename = os.path.join(out_dir,
            os.path.splitext(os.path.basename(source_filename))[0]
            + RESULT_FILE_EXTENSION)
    else:
        result_filename = os.path.join(out_dir, "out.py")
    if os.path.isfile(result_filename):
        with open(result_filename, 'r', encoding='utf-8') as f:
            result = f.read()
        if source_filename == source:
            with open(source_filename, 'r', encoding='utf-8') as f:
                source = f.read()
        m = re.search(r'source_hash__ *= *"([\w.!? ]*)"', result)
        if m and m.groups()[-1] == source_hash(source):
            return ''  # no re-compilation necessary, because source hasn't changed
    result, errors = compile_src(source)
    if not has_errors(errors, FATAL):
        if os.path.abspath(source_filename) != os.path.abspath(result_filename):
            with open(result_filename, 'w', encoding='utf-8') as f:
                f.write(serialize_result(result))
        else:
            errors.append(Error('Source and destination have the same name "%s"!'
                                % result_filename, 0, FATAL))
    if errors:
        err_ext = '_ERRORS.txt' if has_errors(errors, ERROR) else '_WARNINGS.txt'
        err_filename = os.path.splitext(result_filename)[0] + err_ext
        with open(err_filename, 'w') as f:
            f.write('\n'.join(canonical_error_strings(errors)))
        return err_filename
    return ''


def _process_file(args: Tuple[str, str]) -> str:
    return process_file(*args)


def batch_process(file_names: List[str], out_dir: str,
                  *, submit_func: Callable = None,
                  log_func: Callable = None,
                  cancel_func: Callable = never_cancel) -> List[str]:
    """Compiles all files listed in filenames and writes the results and/or
    error messages to the directory `our_dir`. Returns a list of error
    messages files.
    """
    return dsl.batch_process(file_names, out_dir, _process_file,
        submit_func=submit_func, log_func=log_func, cancel_func=cancel_func)


INSPECT_TEMPLATE = """<h2>{testname}</h2>
<h3>Test source</h3>
<div style="background-color: cornsilk;">
<code style="white-space: pre-wrap;">{test_source}
</code>
</div>
<h3>AST</h3>
<div style="background-color: antiquewhite;">
<code style="white-space: pre-wrap;">{ast_str}
</code>
</div>
<h3>Python</h3>
<div style="background-color: yellow;">
<code style="white-space: pre-wrap;">{code}
</code>
</div>
"""


def inspect(test_file_path: str):
    assert test_file_path[-4:] == '.ini'
    from DHParser.testing import unit_from_file
    test_unit = unit_from_file(test_file_path, additional_stages={'py'})
    grammar = parsing.factory
    transformer = ASTTransformation.factory
    compiler = compiling.factory
    results = []
    for parser in test_unit:
        for testname, test_source in test_unit[parser].get('match', dict()).items():
            ast = grammar(test_source, parser)
            transformer(ast)
            ast_str = ast.as_tree()
            code = compiler(ast)
            results.append(INSPECT_TEMPLATE.format(
                testname=testname,
                test_source=test_source.replace('<', '&lt;').replace('>', '&gt;'),
                ast_str=ast_str.replace('<', '&lt;').replace('>', '&gt;'),
                code=code.replace('<', '&lt;').replace('>', '&gt;')))
    test_file_name = os.path.basename(test_file_path)
    results_str = '\n        '.join(results)
    html = f'''<!DOCTYPE html>\n<html>
    <head><meta charset="utf-8"><title>{test_file_name}</title></head>
    <body>
        <h1>{test_file_name}</h1>
        {results_str}\n</body>\n</html>'''
    destdir = os.path.join(os.path.dirname(test_file_path), "REPORT")
    if not os.path.exists(destdir):  os.mkdir(destdir)
    destpath = os.path.join(destdir, test_file_name[:-4] + '.html')
    with open(destpath, 'w', encoding='utf-8') as f:
        f.write(html)
    import webbrowser
    webbrowser.open('file://' + destpath if sys.platform == "darwin" else destpath)


def main(called_from_app=False):
    # recompile grammar if needed
    script_path = os.path.abspath(__file__)
    script_name = os.path.basename(script_path)
    if script_name.endswith('Parser.py'):
        base_path = script_path[:-9]
    else:
        base_path = os.path.splitext(script_path)[0]
    grammar_path = base_path + '.ebnf'
    parser_update = False

    def notify():
        global parser_update
        parser_update = True
        print('recompiling ' + grammar_path)

    if os.path.exists(grammar_path) and os.path.isfile(grammar_path):
        if not recompile_grammar(grammar_path, script_path, force=False, notify=notify):
            error_file = base_path + '_ebnf_ERRORS.txt'
            with open(error_file, encoding="utf-8") as f:
                print(f.read())
            sys.exit(1)
        elif parser_update:
            print(os.path.basename(__file__) + ' has changed. '
                  'Please run again in order to apply updated compiler')
            sys.exit(0)
    else:
        print('Could not check whether grammar requires recompiling, '
              'because grammar was not found at: ' + grammar_path)

    from argparse import ArgumentParser
    parser = ArgumentParser(description="Parses a ts2python-file and shows its syntax-tree.")
    parser.add_argument('files', nargs='*' if called_from_app else '+')
    parser.add_argument('-D', '--debug', action='store_const', const='debug',
                        help='Store debug information in LOGS subdirectory')
    parser.add_argument('-o', '--out', nargs=1, default=['ts2python_output'],
                        help='Output directory for batch processing')
    parser.add_argument('-v', '--verbose', action='store_const', const='verbose',
                        help='Verbose output')
    parser.add_argument('--singlethread', action='store_const', const='singlethread',
                        help='Run batch jobs in a single thread (recommended only for debugging)')
    parser.add_argument('-c', '--compatibility', nargs=1, action='extend', type=str,
                        help='Minimal required python version (must be >= 3.7)')
    parser.add_argument('-a', '--anonymous', nargs=1, action='extend', type=str,
                        help='How to render anonymous interfaces: "local" (default), '
                             '"toplevel", "functional", "type"')
    parser.add_argument('-p', '--peps', nargs=1, action='extend', type=str,
                        help='Assume or ignore Python-PEPs, e.g. "655,~705" assume NotRequired '
                             '(PEP 655), but ignore ReadOnly (PEP 705)')
    parser.add_argument('-k', '--comments', action='store_const', const="comments",
                        help="Preserve (multiline) comments")

    args = parser.parse_args()
    file_names, out, log_dir = args.files, args.out[0], ''

    read_local_config(os.path.join(scriptpath, 'ts2pythonConfig.ini'))

    if args.debug or args.compatibility or args.peps or args.anonymous:
        access_presets()
        if args.debug is not None:
            log_dir = 'LOGS'
            set_preset_value('history_tracking', True)
            set_preset_value('resume_notices', True)
            set_preset_value('log_syntax_trees', frozenset(['cst', 'ast']))  # don't use a set literal, here
        if args.compatibility:
            version_info = tuple(int(part) for part in args.compatibility[0].split('.'))
            set_compatibility_level(version_info, "preset")
        if args.anonymous:  set_preset_value('ts2python.RenderAnonymous', args.anonymous[0].strip())
        if args.peps:
            args_peps = [pep.strip() for pep in args.peps[0].split(',')]
            all_peps = { '435',  '563',  '584',  '586',  '604', '613',
                         '646',  '649',  '655',  '695',  '705',  '749',
                        '~435', '~563', '~584', '~586', '~604', '~613',
                        '~646', '~649', '~655', '~695', '~705', '~749'}
            if not all(pep in all_peps for pep in args_peps):
                print(f'Unsupported PEPs specified: {args_peps}\n'
                      'Allowed PEP arguments are:\n'
                      '  435  - use Enums (Python 3.4)\n'
                      '  563  - use postponed evaluation (Python 3.7)\n'
                      '  584 or 586  - use Literal type (Python 3.8)\n'
                      '  604  - use type union (Python 3.10)\n'
                      '  613  - use explicit type alias (Python 3.10 - 3.11)\n'
                      '  646  - use variadic Generics (Python 3.11)\n'
                      '  649 or 749 - assume deferred type evaluation (Python 3.14)\n'
                      '  655  - use NotRequired instead of Optional (Python3.11)\n'
                      '  695  - use type parameters (Python 3.12)\n'
                      '  705  - allow ReadOnly (Python 3.13)\n')
                sys.exit(1)
            for pep in args_peps:
                kwargs= {'value': pep[0] != '~', 'allow_new_key': True}
                if pep == '435':  set_preset_value('ts2python.UseEnum', **kwargs)
                if pep == '563':  set_preset_value('ts2python.UsePostponedEvaluation', **kwargs)
                if pep in ('586', '584'):  set_preset_value('ts2python.UseLiteralType', **kwargs)
                if pep == '604':  set_preset_value('ts2python.TypeUnion', **kwargs)
                if pep == '613':  set_preset_value('ts2python.UseExplicitTypeAlias', **kwargs)
                if pep == '646':  set_preset_value('tsPython.UseVariadicGenerics', **kwargs)
                if pep == '655':  set_preset_value('ts2python.UseNotRequired', **kwargs)
                if pep == '695':  set_preset_value('ts2python.UseTypeParameters', **kwargs)
                if pep == '705':  set_preset_value('ts2python.AllowReadOnly', **kwargs)
                if pep in ('649', '749'):  set_preset_value('ts2python.AssumeDeferredEvaluation', **kwargs)
        if args.comments: set_preset_value('ts2python.KeepMultilineComments', True)
        finalize_presets()
        # _ = get_config_values('ts2python.*')  # fill config value cache

    start_logging(log_dir)

    if args.singlethread:
        set_config_value('batch_processing_parallelization', False)

    def echo(message: str):
        if args.verbose:
            print(message)

    if called_from_app and not file_names:  return False

    batch_processing = True
    if len(file_names) == 1:
        if os.path.isdir(file_names[0]):
            dir_name = file_names[0]
            echo('Processing all files in directory: ' + dir_name)
            file_names = [os.path.join(dir_name, fn) for fn in os.listdir(dir_name)
                          if os.path.isfile(os.path.join(dir_name, fn))]
        elif not ('-o' in sys.argv or '--out' in sys.argv):
            batch_processing = False

    if batch_processing:
        if not os.path.exists(out):
            os.mkdir(out)
        elif not os.path.isdir(out):
            print('Output directory "%s" exists and is not a directory!' % out)
            sys.exit(1)
        error_files = batch_process(file_names, out, log_func=print if args.verbose else None)
        if error_files:
            category = "ERRORS" if any(f.endswith('_ERRORS.txt') for f in error_files) \
                else "warnings"
            print("There have been %s! Please check files:" % category)
            print('\n'.join(error_files))
            if category == "ERRORS":
                sys.exit(1)

    elif file_names[0][-4:] == '.ini':
        inspect(file_names[0])

    else:
        assert file_names[0].lower().endswith('.ts')
        error_file = process_file(file_names[0], '.')
        if error_file:
            with open(error_file, 'r', encoding='utf-8') as f:
                print(f.read())

if __name__ == "__main__":
    main()
