#!/usr/bin/env python3

"""ts2python.py - compiles typescript dataclasses to Python
        TypedDicts <https://www.python.org/dev/peps/pep-0589/>

Copyright 2021  by Eckhart Arnold (arnold@badw.de)
                Bavarian Academy of Sciences an Humanities (badw.de)

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
from functools import partial
import os
import sys
from typing import Tuple, List, Union, Any, Callable, Set, Dict


try:
    scriptpath = os.path.dirname(__file__)
except NameError:
    scriptpath = ''
dhparser_parentdir = os.path.abspath(os.path.join(scriptpath, '..', 'DHParser'))
if scriptpath not in sys.path:
    sys.path.append(scriptpath)
if dhparser_parentdir not in sys.path:
    sys.path.append(dhparser_parentdir)

try:
    import regex as re
except ImportError:
    import re
from DHParser import start_logging, suspend_logging, resume_logging, is_filename, load_if_file, \
    Grammar, Compiler, nil_preprocessor, PreprocessorToken, Whitespace, Drop, AnyChar, \
    Lookbehind, Lookahead, Alternative, Pop, Text, Synonym, Counted, Interleave, INFINITE, \
    Option, NegativeLookbehind, OneOrMore, RegExp, Retrieve, Series, Capture, TreeReduction, \
    ZeroOrMore, Forward, NegativeLookahead, Required, CombinedParser, mixin_comment, \
    compile_source, grammar_changed, last_value, matching_bracket, PreprocessorFunc, is_empty, \
    remove_if, Node, TransformerCallable, TransformationDict, transformation_factory, traverse, \
    remove_children_if, normalize_whitespace, is_anonymous, matches_re, \
    reduce_single_child, replace_by_single_child, replace_or_reduce, remove_whitespace, \
    replace_by_children, remove_empty, remove_tokens, flatten, all_of, any_of, \
    merge_adjacent, collapse, collapse_children_if, transform_content, WHITESPACE_PTYPE, \
    TOKEN_PTYPE, remove_children, remove_content, remove_brackets, change_tag_name, \
    remove_anonymous_tokens, keep_children, is_one_of, not_one_of, has_content, apply_if, peek, \
    remove_anonymous_empty, keep_nodes, traverse_locally, strip, lstrip, rstrip, \
    transform_content, replace_content_with, forbid, assert_content, remove_infix_operator, \
    add_error, error_on, recompile_grammar, left_associative, lean_left, set_config_value, \
    get_config_value, node_maker, access_thread_locals, access_presets, PreprocessorResult, \
    finalize_presets, ErrorCode, RX_NEVER_MATCH, set_tracer, resume_notices_on, \
    trace_history, has_descendant, neg, has_ancestor, optional_last_value, insert, \
    positions_of, replace_tag_names, add_attributes, delimit_children, merge_connected, \
    has_attr, has_parent, ThreadLocalSingletonFactory, Error, canonical_error_strings, \
    has_errors, ERROR, FATAL, set_preset_value, get_preset_value, NEVER_MATCH_PATTERN, \
    gen_find_include_func, preprocess_includes, make_preprocessor, chain_preprocessors, \
    pick_from_context, json_dumps, RootNode, get_config_values, md5, StringView


#######################################################################
#
# PREPROCESSOR SECTION - Can be edited. Changes will be preserved.
#
#######################################################################

RE_INCLUDE = NEVER_MATCH_PATTERN
# To capture includes, replace the NEVER_MATCH_PATTERN 
# by a pattern with group "name" here, e.g. r'\input{(?P<name>.*)}'


def ts2pythonTokenizer(original_text) -> Tuple[str, List[Error]]:
    # Here, a function body can be filled in that adds preprocessor tokens
    # to the source code and returns the modified source.
    return original_text, []


def preprocessor_factory() -> PreprocessorFunc:
    # below, the second parameter must always be the same as ts2pythonGrammar.COMMENT__!
    find_next_include = gen_find_include_func(RE_INCLUDE, '(?:\\/\\/.*)|(?:\\/\\*(?:.|\\n)*?\\*\\/)')
    include_prep = partial(preprocess_includes, find_next_include=find_next_include)
    tokenizing_prep = make_preprocessor(ts2pythonTokenizer)
    return chain_preprocessors(include_prep, tokenizing_prep)


get_preprocessor = ThreadLocalSingletonFactory(preprocessor_factory, ident=1)


#######################################################################
#
# PARSER SECTION - Don't edit! CHANGES WILL BE OVERWRITTEN!
#
#######################################################################

class ts2pythonGrammar(Grammar):
    r"""Parser for a ts2python source file.
    """
    declaration = Forward()
    declarations_block = Forward()
    index_signature = Forward()
    literal = Forward()
    type = Forward()
    types = Forward()
    source_hash__ = "911f656dfd6f3897be668f4aca5ad608"
    disposable__ = re.compile('INT$|NEG$|FRAC$|DOT$|EXP$|EOF$|_array_ellipsis$|_top_level_assignment$|_top_level_literal$|_quoted_identifier$')
    static_analysis_pending__ = []  # type: List[bool]
    parser_initialization__ = ["upon instantiation"]
    COMMENT__ = r'(?:\/\/.*)|(?:\/\*(?:.|\n)*?\*\/)'
    comment_rx__ = re.compile(COMMENT__)
    WHITESPACE__ = r'\s*'
    WSP_RE__ = mixin_comment(whitespace=WHITESPACE__, comment=COMMENT__)
    wsp__ = Whitespace(WSP_RE__)
    dwsp__ = Drop(Whitespace(WSP_RE__))
    EOF = Drop(NegativeLookahead(RegExp('.')))
    EXP = Option(Series(Alternative(Text("E"), Text("e")), Option(Alternative(Text("+"), Text("-"))), RegExp('[0-9]+')))
    DOT = Text(".")
    FRAC = Option(Series(DOT, RegExp('[0-9]+')))
    NEG = Text("-")
    INT = Series(Option(NEG), Alternative(RegExp('[1-9][0-9]+'), RegExp('[0-9]')))
    identifier = Series(RegExp('(?!\\d)\\w+'), dwsp__)
    variable = Series(identifier, ZeroOrMore(Series(Text("."), identifier)))
    basic_type = Series(Alternative(Text("object"), Text("array"), Text("string"), Text("number"), Text("boolean"), Text("null"), Text("integer"), Text("uinteger"), Text("decimal"), Text("unknown"), Text("any")), dwsp__)
    name = Alternative(identifier, Series(Series(Drop(Text('"')), dwsp__), identifier, Series(Drop(Text('"')), dwsp__)))
    association = Series(name, Series(Drop(Text(":")), dwsp__), literal)
    object = Series(Series(Drop(Text("{")), dwsp__), Option(Series(association, ZeroOrMore(Series(Series(Drop(Text(",")), dwsp__), association)))), Option(Series(Drop(Text(",")), dwsp__)), Series(Drop(Text("}")), dwsp__))
    array = Series(Series(Drop(Text("[")), dwsp__), Option(Series(literal, ZeroOrMore(Series(Series(Drop(Text(",")), dwsp__), literal)))), Series(Drop(Text("]")), dwsp__))
    string = Alternative(Series(RegExp('"[^"\\n]*"'), dwsp__), Series(RegExp("'[^'\\n]*'"), dwsp__))
    number = Series(INT, FRAC, EXP, dwsp__)
    integer = Series(INT, NegativeLookahead(RegExp('[.Ee]')), dwsp__)
    type_parameter = Series(Series(Drop(Text("<")), dwsp__), identifier, Series(Drop(Text(">")), dwsp__))
    _top_level_literal = Drop(Synonym(literal))
    _array_ellipsis = Drop(Series(literal, Drop(ZeroOrMore(Drop(Series(Series(Drop(Text(",")), dwsp__), literal))))))
    assignment = Series(variable, Series(Drop(Text("=")), dwsp__), Alternative(literal, variable), Series(Drop(Text(";")), dwsp__))
    _top_level_assignment = Drop(Synonym(assignment))
    const = Series(Option(Series(Drop(Text("export")), dwsp__)), Series(Drop(Text("const")), dwsp__), declaration, Series(Drop(Text("=")), dwsp__), Alternative(literal, identifier), Series(Drop(Text(";")), dwsp__), mandatory=2)
    _quoted_identifier = Alternative(identifier, Series(Series(Drop(Text('"')), dwsp__), identifier, Series(Drop(Text('"')), dwsp__), mandatory=2), Series(Series(Drop(Text("\'")), dwsp__), identifier, Series(Drop(Text("\'")), dwsp__), mandatory=2))
    item = Series(_quoted_identifier, Option(Series(Series(Drop(Text("=")), dwsp__), literal)))
    enum = Series(Option(Series(Drop(Text("export")), dwsp__)), Series(Drop(Text("enum")), dwsp__), identifier, Series(Drop(Text("{")), dwsp__), item, ZeroOrMore(Series(Series(Drop(Text(",")), dwsp__), item)), Option(Series(Drop(Text(",")), dwsp__)), Series(Drop(Text("}")), dwsp__), mandatory=3)
    extends = Series(Series(Drop(Text("extends")), dwsp__), identifier, ZeroOrMore(Series(Series(Drop(Text(",")), dwsp__), identifier)))
    map_signature = Series(index_signature, Series(Drop(Text(":")), dwsp__), types)
    mapped_type = Series(Series(Drop(Text("{")), dwsp__), map_signature, Option(Series(Drop(Text(";")), dwsp__)), Series(Drop(Text("}")), dwsp__))
    type_tuple = Series(Series(Drop(Text("[")), dwsp__), type, ZeroOrMore(Series(Series(Drop(Text(",")), dwsp__), type)), Series(Drop(Text("]")), dwsp__))
    type_name = Synonym(identifier)
    array_of = Series(Alternative(basic_type, Series(Series(Drop(Text("(")), dwsp__), types, Series(Drop(Text(")")), dwsp__)), type_name), Series(Drop(Text("[]")), dwsp__))
    interface = Series(Option(Series(Drop(Text("export")), dwsp__)), Series(Drop(Text("interface")), dwsp__), identifier, Option(type_parameter), Option(extends), declarations_block, mandatory=2)
    type_alias = Series(Option(Series(Drop(Text("export")), dwsp__)), Series(Drop(Text("type")), dwsp__), identifier, Series(Drop(Text("=")), dwsp__), types, Series(Drop(Text(";")), dwsp__), mandatory=2)
    namespace = Series(Option(Series(Drop(Text("export")), dwsp__)), Series(Drop(Text("namespace")), dwsp__), identifier, Series(Drop(Text("{")), dwsp__), ZeroOrMore(Alternative(interface, type_alias, enum, const, Series(declaration, Series(Drop(Text(";")), dwsp__)))), Series(Drop(Text("}")), dwsp__), mandatory=2)
    optional = Series(Text("?"), dwsp__)
    qualifier = Series(Text("readonly"), dwsp__)
    literal.set(Alternative(integer, number, string, array, object))
    type.set(Alternative(array_of, basic_type, type_name, Series(Series(Drop(Text("(")), dwsp__), types, Series(Drop(Text(")")), dwsp__)), mapped_type, declarations_block, type_tuple, literal))
    types.set(Series(type, ZeroOrMore(Series(Series(Drop(Text("|")), dwsp__), type))))
    index_signature.set(Series(Series(Drop(Text("[")), dwsp__), identifier, Alternative(Series(Drop(Text(":")), dwsp__), Series(Series(Drop(Text("in")), dwsp__), Series(Drop(Text("keyof")), dwsp__))), type, Series(Drop(Text("]")), dwsp__)))
    declaration.set(Series(Option(qualifier), identifier, Option(optional), Option(Series(Series(Drop(Text(":")), dwsp__), types))))
    declarations_block.set(Series(Series(Drop(Text("{")), dwsp__), Option(Series(declaration, ZeroOrMore(Series(Option(Series(Drop(Text(";")), dwsp__)), declaration)), Option(Series(Series(Drop(Text(";")), dwsp__), map_signature)), Option(Series(Drop(Text(";")), dwsp__)))), Series(Drop(Text("}")), dwsp__)))
    document = Series(dwsp__, ZeroOrMore(Alternative(interface, type_alias, namespace, enum, const, Series(declaration, Series(Drop(Text(";")), dwsp__)), _top_level_assignment, _array_ellipsis, _top_level_literal)), EOF)
    root__ = TreeReduction(document, CombinedParser.MERGE_TREETOPS)
    

_raw_grammar = ThreadLocalSingletonFactory(ts2pythonGrammar, ident=1)

def get_grammar() -> ts2pythonGrammar:
    grammar = _raw_grammar()
    if get_config_value('resume_notices'):
        resume_notices_on(grammar)
    elif get_config_value('history_tracking'):
        set_tracer(grammar, trace_history)
    try:
        if not grammar.__class__.python_src__:
            grammar.__class__.python_src__ = get_grammar.python_src__
    except AttributeError:
        pass
    return grammar
    
def parse_ts2python(document, start_parser = "root_parser__", *, complete_match=True):
    return get_grammar()(document, start_parser, complete_match)


#######################################################################
#
# AST SECTION - Can be edited. Changes will be preserved.
#
#######################################################################

ts2python_AST_transformation_table = {
    # AST Transformations for the ts2python-grammar
    # "<": flatten,
    ":Text": change_tag_name('TEXT')
    # "*": replace_by_single_child
}


def ts2pythonTransformer() -> TransformerCallable:
    """Creates a transformation function that does not share state with other
    threads or processes."""
    return partial(traverse, transformation_table=ts2python_AST_transformation_table.copy())


get_transformer = ThreadLocalSingletonFactory(ts2pythonTransformer, ident=1)


def transform_ts2python(cst):
    get_transformer()(cst)


#######################################################################
#
# COMPILER SECTION - Can be edited. Changes will be preserved.
#
#######################################################################


GENERAL_IMPORTS = """
import sys
from enum import Enum, IntEnum
from typing import Union, List, Tuple, Optional, Dict, Any, Generic, TypeVar
"""

TYPEDDICT_IMPORTS = """
try:
    from ts2python.json_validation import TypedDict, GenericTypedDict, \
        NotRequired, Literal
    # Overwrite typing.TypedDict for Runtime-Validation
except ImportError:
    # print("Module ts2python.json_validation not found. Only " 
    #       "coarse-grained type-validation of TypedDicts possible")
    try:
        from typing import TypedDict, Literal
    except ImportError:
        try:
            from ts2python.typing_extensions import TypedDict, Literal
        except ImportError:
            print(f'Please install the "typing_extensions" module via the shell '
                  f'command "# pip install typing_extensions" before running '
                  f'{__file__} with Python-versions <= 3.7!')
    try:
        from typing_extensions import NotRequired
    except ImportError:
        NotRequired = Optional
    if sys.version_info >= (3, 7, 0):  GenericMeta = type
    else:
        from typing import GenericMeta
    class _GenericTypedDictMeta(GenericMeta):
        def __new__(cls, name, bases, ns, total=True):
            return type.__new__(_GenericTypedDictMeta, name, (dict,), ns)
        __call__ = dict
    GenericTypedDict = _GenericTypedDictMeta('TypedDict', (dict,), {})
    GenericTypedDict.__module__ = __name__   
"""

PEP655_IMPORTS = """
"""


def to_typename(varname: str) -> str:
    assert varname[-1:] != '_' or keyword.iskeyword(varname[:-1]), varname  # and varname[0].islower()
    return varname[0].upper() + varname[1:] + '_'


def to_varname(typename: str) -> str:
    assert typename[0].isupper() or typename[-1:] == '_', typename
    return typename[0].lower() + (typename[1:-1] if typename[-1:] == '_' else typename[1:])


class ts2pythonCompiler(Compiler):
    """Compiler for the abstract-syntax-tree of a ts2python source file.
    """

    def reset(self):
        super().reset()
        bcn = get_config_value('ts2python.BaseClassName', 'TypedDict')
        i = bcn.rfind('.')
        if i >= 0:
            self.additional_imports = f'\nfrom {bcn[:i]} import {bcn[i + 1:]}\n'
            bcn = bcn[i + 1:]
        else:
            self.additional_imports = ''
        self.base_class_name = bcn
        self.class_decorator = get_config_value('ts2python.ClassDecorator', '').strip()
        if self.class_decorator:
            if self.class_decorator[0] != '@':
                self.class_decorator = '@' + self.class_decorator
            self.class_decorator += '\n'
        self.use_enums = get_config_value('ts2python.UseEnum', True)
        self.use_type_union = get_config_value('ts2python.UseTypeUnion', False)
        self.use_literal_type = get_config_value('ts2python.UseLiteralType', True)
        self.use_not_required = get_config_value('ts2python.UseNotRequired', False)

        self.overloaded_type_names: Set[str] = set()
        self.known_types: Set[str] = set()
        self.local_classes: List[List[str]] = [[]]
        self.base_classes: Dict[str, List[str]] = {}
        # self.default_values: Dict = {}
        # self.referred_objects: Dict = {}
        self.basic_type_aliases: Set[str] = set()
        self.obj_name: List[str] = ['TOPLEVEL_']
        self.optional_keys: List[List[str]] = [[]]
        self.strip_type_from_const = False

    def compile(self, node) -> str:
        result = super().compile(node)
        if isinstance(result, str):
            return result
        raise TypeError(f"Compilation of {node.tag_name} yielded a result of "
                        f"type {str(type(result))} and not str as expected!")

    def is_toplevel(self) -> bool:
        return self.obj_name == ['TOPLEVEL_']

    def qualified_obj_name(self, pos: int=0, varname: bool=False) -> str:
        obj_name = self.obj_name[1:] if len(self.obj_name) > 1 else self.obj_name
        if pos < 0:  obj_name = obj_name[:pos]
        if varname:  obj_name = obj_name[:-1] + [to_varname(obj_name[-1])]
        return '.'.join(obj_name)

    def prepare(self, root: Node) -> None:
        type_aliases = {nd['identifier'].content for nd in root.select_children('type_alias')}
        namespaces = {nd['identifier'].content for nd in root.select_children('namespace')}
        self.overloaded_type_names = type_aliases & namespaces
        return None

    def finalize(self, python_code: Any) -> Any:
        chksum = f'source_hash__ = "{md5(self.tree.source)}"'
        if self.tree.tag_name == 'document':
            code_blocks = [
                f'# Generated by ts2python on {datetime.datetime.now()}\n',
                GENERAL_IMPORTS, TYPEDDICT_IMPORTS, self.additional_imports,
                chksum, '\n##### BEGIN OF LSP SPECS\n'
            ]
            if self.base_class_name == 'TypedDict':
                code_blocks.append(PEP655_IMPORTS)
        else:
            code_blocks = []
        code_blocks.append(python_code)
        if self.tree.tag_name == 'document':
            code_blocks.append('\n##### END OF LSP SPECS\n')
        cooked = '\n\n'.join(code_blocks)
        return re.sub(r'\n\n+', '\n\n\n', cooked)

    def on_EMPTY__(self, node) -> str:
        return ''

    def on_ZOMBIE__(self, node):
        raise ValueError('Malformed syntax-tree!')

    def on_document(self, node) -> str:
        return '\n\n'.join(self.compile(child) for child in node.children
                           if child.tag_name != 'declaration')

    def render_class_header(self, name: str, base_classes: str) -> str:
        optional_key_list = self.optional_keys.pop()
        decorator = self.class_decorator
        if self.base_class_name == 'TypedDict':
            total = not bool(optional_key_list) or self.use_not_required
            if base_classes:
                if base_classes.find('Generic[') >= 0:
                    td_name = 'GenericTypedDict'
                else:
                    td_name = 'TypedDict'
                if self.use_not_required:
                    return decorator + \
                           f"class {name}({base_classes}, {td_name}):\n"
                else:
                    return decorator + f"class {name}({base_classes}, "\
                           f"{td_name}, total={total}):\n"
            else:
                if self.use_not_required:
                    return decorator + f"class {name}(TypedDict):\n"
                else:
                    return decorator + \
                           f"class {name}(TypedDict, total={total}):\n"
        else:
            if base_classes:
                return decorator + \
                       f"class {name}({base_classes}, {self.base_class_name}):\n"
            else:
                return decorator + f"class {name}({self.base_class_name}):\n"

    def render_local_classes(self) -> str:
        if self.local_classes[-1]:
            classes = self.local_classes.pop()
            return '\n'.join(lc for lc in classes) + '\n'
        else:
            self.local_classes.pop()
            return ''

    def on_interface(self, node) -> str:
        name = self.compile(node['identifier'])
        self.obj_name.append(name)
        self.local_classes.append([])
        self.optional_keys.append([])
        try:
            tp = self.compile(node['type_parameter'])
            preface = f"{tp} = TypeVar('{tp}')\n\n"
        except KeyError:
            tp = ''
            preface = ''
        base_class_list = []
        try:
            base_classes = self.compile(node['extends'])
            for bc in node['extends'].children:
                base_class_list.append(bc.content)
            if tp:
                base_classes += f", Generic[{tp}]"
        except KeyError:
            base_classes = f"Generic[{tp}]" if tp else ''
        decls = self.compile(node['declarations_block'])
        interface = self.render_class_header(name, base_classes)
        self.base_classes[name] = base_class_list
        interface += ('    ' + self.render_local_classes().replace('\n', '\n    ')).rstrip(' ')
        self.known_types.add(name)
        self.obj_name.pop()
        return preface + interface + '    ' + decls.replace('\n', '\n    ')

    def on_type_parameter(self, node) -> str:
        return self.compile(node['identifier'])

    def on_extends(self, node) -> str:
        return ', '.join(self.compile(nd) for nd in node.children)

    def on_type_alias(self, node) -> str:
        alias = self.compile(node['identifier'])
        if all(typ[0].tag_name in ('basic_type', 'literal') for typ in node.select('type')):
            self.basic_type_aliases.add(alias)
        self.obj_name.append(alias)
        if alias not in self.overloaded_type_names:
            self.known_types.add(alias)
            self.local_classes.append([])
            self.optional_keys.append([])
            types = self.compile(node['types'])
            preface = self.render_local_classes()
            code = preface + f"{alias} = {types}"
        else:
            code = ''
        self.obj_name.pop()
        return code

    def on_declarations_block(self, node) -> str:
        declarations = '\n'.join(self.compile(nd) for nd in node
                                 if nd.tag_name == 'declaration')
        return declarations or "pass"

    def on_declaration(self, node) -> str:
        identifier = self.compile(node['identifier'])
        self.obj_name.append(to_typename(identifier))
        T = self.compile(node['types']) if 'types' in node else 'Any'
        typename = self.obj_name.pop()
        if T[0:5] == 'class':
            self.local_classes[-1].append(T)
            T = typename  # substitute typename for type
        if 'optional' in node:
            self.optional_keys[-1].append(identifier)
            if self.use_not_required:
                T = f"NotRequired[{T}]"
            else:
                if T.startswith('Union['):
                    if T.find('None') < 0:
                        T = T[:-1] + ', None]'
                elif T.find('|') >= 0:
                    if T.find('None') < 0:
                        T += '|None'
                else:
                    T = f"Optional[{T}]"
        if self.is_toplevel() and T[0:5] == 'class':
            preface = self.render_local_classes()
            self.local_classes.append([])
            self.optional_keys.append([])
            return preface + f"{identifier}:{to_typename(identifier)}"
        return f"{identifier}: {T}"

    def on_optional(self, node):
        assert False, "This method should never have been called!"

    def on_index_signature(self, node) -> str:
        return self.compile(node['type'])

    def on_types(self, node) -> str:
        if len(node.children) == 1:
            return self.compile(node[0])
        else:
            assert len(node.children) > 1
            union = []
            i = 0
            for nd in node.children:
                obj_name_stub = self.obj_name[-1]
                delim = '' if self.obj_name[-1][-1:] == '_' else '_'
                self.obj_name[-1] = self.obj_name[-1] + delim + str(i)
                typ = self.compile(nd)
                if typ not in union:
                    union.append(typ)
                    i += 1
                self.obj_name[-1] = obj_name_stub
            for i in range(len(union)):
                typ = union[i]
                if typ[0:5] == 'class':
                    cname = re.match(r"class\s*(\w+)[\w(){},' =]*\s*:", typ).group(1)
                    self.local_classes[-1].append(typ)
                    union[i] = cname
            if self.is_toplevel():
                preface = self.render_local_classes()
                self.local_classes.append([])
                self.optional_keys.append([])
            else:
                preface = ''
            if self.use_literal_type and \
                    any(nd[0].tag_name == 'literal' for nd in node.children):
                assert all(nd[0].tag_name == 'literal' for nd in node.children)
                return f"Literal[{', '.join(union)}]"
            elif self.use_type_union:
                return preface + '|'.join(union)
            else:
                if len(union) == 1:
                    return preface + union[0]
                return preface + f"Union[{', '.join(union)}]"

    def on_type(self, node) -> str:
        assert len(node.children) == 1
        typ = node[0]
        if typ.tag_name == 'declarations_block':
            self.local_classes.append([])
            self.optional_keys.append([])
            decls = self.compile(typ)
            return ''.join([self.render_class_header(self.obj_name[-1], '') + "    ",
                             self.render_local_classes().replace('\n', '\n    '),
                             decls.replace('\n', '\n    ')])   # maybe add one '\n'?
            # return 'Dict'
        elif typ.tag_name == 'literal':
            literal_typ = typ[0].tag_name
            if self.use_literal_type:
                return self.compile(typ)
            elif literal_typ == 'array':
                return 'List'
            elif literal_typ == 'object':
                return 'Dict'
            elif literal_typ in ('number', 'integer'):
                literal = self.compile(typ)
                try:
                    _ = int(literal)
                    return 'int'
                except ValueError:
                    return 'str'
            else:
                assert literal_typ == 'string', literal_typ
                literal = self.compile(typ)
                return 'str'
        else:
            return self.compile(typ)

    def on_type_tuple(self, node):
        return 'Tuple[' + ', '.join(self.compile(nd) for nd in node) + ']'

    def on_mapped_type(self, node) -> str:
        return self.compile(node['map_signature'])

    def on_map_signature(self, node) -> str:
        return "Dict[%s, %s]" % (self.compile(node['index_signature']),
                                 self.compile(node['types']))

    def on_namespace(self, node) -> str:
        name = self.compile(node['identifier'])
        if name in self.known_types:  return ''
        self.known_types.add(name)
        save = self.strip_type_from_const
        if all(child.tag_name == 'const' for child in node.children[1:]):
            if all(nd['literal'][0].tag_name == 'integer'
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
        namespace.insert(0, header)
        self.strip_type_from_const = save
        return '\n    '.join(namespace)

    def on_enum(self, node) -> str:
        if self.use_enums:
            if all(nd['literal'][0].tag_name == 'integer' for
                   nd in node.select_children('item') if 'literal' in nd):
                base_class = '(IntEnum)'
            else:
                base_class = '(Enum)'
        else:
            base_class = ''
        name = self.compile(node['identifier'])
        self.known_types.add(name)
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
        if self.strip_type_from_const:
            return self.compile(node['declaration']['identifier']) \
                   + ' = ' + self.compile(node[-1])
        else:
            return self.compile(node['declaration']) + ' = ' + self.compile(node[-1])

    def on_assignment(self, node) -> str:
        return self.compile(node['variable']) + ' = ' + self.compile(node[1])

    def on_literal(self, node) -> str:
        assert len(node.children) == 1
        return self.compile(node[0])

    def on_integer(self, node) -> str:
        return node.content

    def on_number(self, node) -> str:
        return node.content

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
        return f'"{self.compile(node["name"])}": ' + self.compile(node['literal'])

    def on_name(self, node) -> str:
        return node.content

    def on_basic_type(self, node) -> str:
        python_basic_types = {'object': 'Dict',
                              'array': 'List',
                              'string': 'str',
                              'number': 'float',
                              'decimal': 'float',
                              'integer': 'int',
                              'uinteger': 'int',
                              'boolean': 'bool',
                              'null': 'None',
                              'unknown': 'Any',
                              'any': 'Any'}
        return python_basic_types[node.content]

    def on_type_name(self, node) -> str:
        name = self.compile(node['identifier'])
        if name not in self.known_types:
            name = "'" + name + "'"
        return name

    def on_array_of(self, node) -> str:
        assert len(node.children) == 1
        name = self.compile(node[0])
        if node[0].tag_name == 'identifier' and name not in self.known_types:
            name = "'" + name + "'"
        return 'List[' + name + ']'

    def on_qualifier(self, node):
        assert False, "Qualifiers should be ignored and this method should never be called!"

    def on_variable(self, node) -> str:
        return node.content

    def on_identifier(self, node) -> str:
        identifier = node.content
        if keyword.iskeyword(identifier):
            identifier += '_'
        return identifier


get_compiler = ThreadLocalSingletonFactory(ts2pythonCompiler, ident=1)


def compile_ts2python(ast):
    return get_compiler()(ast)


#######################################################################
#
# END OF DHPARSER-SECTIONS
#
#######################################################################

RESULT_FILE_EXTENSION = ".sxpr"  # Change this according to your needs!


def compile_src(source: str) -> Tuple[Any, List[Error]]:
    """Compiles ``source`` and returns (result, errors)."""
    result_tuple = compile_source(source, get_preprocessor(), get_grammar(), get_transformer(),
                                  get_compiler())
    return result_tuple[:2]  # drop the AST at the end of the result tuple


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


def process_file(source: str, result_filename: str = '') -> str:
    """Compiles the source and writes the serialized results back to disk,
    unless any fatal errors have occurred. Error and Warning messages are
    written to a file with the same name as `result_filename` with an
    appended "_ERRORS.txt" or "_WARNINGS.txt" in place of the name's
    extension. Returns the name of the error-messages file or an empty
    string, if no errors of warnings occurred.
    """
    source_filename = source if is_filename(source) else ''
    if os.path.isfile(result_filename):
        with open(result_filename, 'r', encoding='utf-8') as f:
            result = f.read()
        if source_filename == source:
            with open(source_filename, 'r', encoding='utf-8') as f:
                source = f.read()
        m = re.search('source_hash__ *= *"([a-z0-9]*)"', result)
        if m.groups()[-1] == md5(source):
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


def batch_process(file_names: List[str], out_dir: str,
                  *, submit_func: Callable = None,
                  log_func: Callable = None) -> List[str]:
    """Compiles all files listed in filenames and writes the results and/or
    error messages to the directory `our_dir`. Returns a list of error
    messages files.
    """
    error_list =  []

    def gen_dest_name(name):
        return os.path.join(out_dir, os.path.splitext(os.path.basename(name))[0] \
                                     + RESULT_FILE_EXTENSION)

    def run_batch(submit_func: Callable):
        nonlocal error_list
        err_futures = []
        for name in file_names:
            dest_name = gen_dest_name(name)
            err_futures.append(submit_func(process_file, name, dest_name))
        for file_name, err_future in zip(file_names, err_futures):
            error_filename = err_future.result()
            if log_func:
                log_func('Compiling "%s"' % file_name)
            if error_filename:
                error_list.append(error_filename)

    if submit_func is None:
        import concurrent.futures
        from DHParser.toolkit import instantiate_executor
        with instantiate_executor(get_config_value('batch_processing_parallelization'),
                                  concurrent.futures.ProcessPoolExecutor) as pool:
            run_batch(pool.submit)
    else:
        run_batch(submit_func)
    return error_list


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
    grammar = get_grammar()
    transformer = get_transformer()
    compiler = get_compiler()
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


def main():
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
    parser.add_argument('files', nargs='+')
    parser.add_argument('-D', '--debug', action='store_const', const='debug',
                        help='Store debug information in LOGS subdirectory')
    parser.add_argument('-o', '--out', nargs=1, default=['out'],
                        help='Output directory for batch processing')
    parser.add_argument('-v', '--verbose', action='store_const', const='verbose',
                        help='Verbose output')
    parser.add_argument('--singlethread', action='store_const', const='singlethread',
                        help='Run batch jobs in a single thread (recommended only for debugging)')
    parser.add_argument('-c', '--compatibility', nargs=1, action='extend', type=str,
                        help='Minimal required python version (must be >= 3.6)')
    parser.add_argument('-b', '--base', nargs=1, action='extend', type=str,
                        help='Base class name, e.g. TypedDict (default) or BaseModel (pydantic)')
    parser.add_argument('-d', '--decorator', nargs=1, action='extend', type=str,
                        help="addes the given decorator ")
    parser.add_argument('-p', '--peps', nargs='+', action='extend', type=str,
                        help='Assume Python-PEPs, e.g. 655 or ~655')

    args = parser.parse_args()
    file_names, out, log_dir = args.files, args.out[0], ''

    workdir = file_names[0] if os.path.isdir(file_names[0]) else os.path.dirname(file_names[0])
    from DHParser.configuration import read_local_config
    read_local_config(os.path.join(workdir, 'ts2python/ts2pythonParser.ini'))

    if args.debug or args.compatibility or args.base or args.decorator or args.peps:
        access_presets()
        if args.debug is not None:
            log_dir = 'LOGS'
            set_preset_value('history_tracking', True)
            set_preset_value('resume_notices', True)
            set_preset_value('log_syntax_trees', frozenset(['cst', 'ast']))  # don't use a set literal, here
        if args.compatibility:
            version_info = tuple(int(part) for part in args.compatibility[0].split('.'))
            if version_info >= (3, 10):
                set_preset_value('ts2python.UseTypeUnion', True, allow_new_key=True)
        if args.base:  set_preset_value('ts2python.BaseClassName', args.base[0].strip())
        if args.decorator:  set_preset_value('ts2python.ClassDecorator', args.decorator[0].strip())
        if args.peps:
            args_peps = [pep.strip() for pep in args.peps]
            all_peps = {'435', '584', '604', '655', '~435', '~584', '~604', '~655'}
            if not all(pep in all_peps for pep in args_peps):
                print(f'Unsupported PEPs specified: {args_peps}\n'
                      'Allowed PEP arguments are:\n'
                      '  435  - use Enums (Python 3.4)\n'
                      '  604  - use type union (Python 3.10)\n'
                      '  584  - use Literal type (Python 3.8)\n'
                      '  655  - use NotRequired instead of Optional\n')
                sys.exit(1)
            for pep in args_peps:
                kwargs= {'value': pep[0] != '~', 'allow_new_key': True}
                if pep == '435':  set_preset_value('ts2python.UseEnum', **kwargs)
                if pep == '584':  set_preset_value('ts2python.UseLiteralType', **kwargs)
                if pep == '604':  set_preset_value('ts2python.TypeUnion', **kwargs)
                if pep == '655':  set_preset_value('ts2python.UseNotRequired', **kwargs)
        finalize_presets()
        _ = get_config_values('ts2python.*')  # fill config value cache

    start_logging(log_dir)

    if args.singlethread:
        set_config_value('batch_processing_parallelization', False)

    def echo(message: str):
        if args.verbose:
            print(message)

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
        error_file = process_file(file_names[0], file_names[0][:-3] + '.py')
        if error_file:
            with open(error_file, 'r', encoding='utf-8') as f:
                print(f.read())
        # result, errors = compile_src(file_names[0])
        #
        # if errors:
        #     for err_str in canonical_error_strings(errors):
        #         print(err_str)
        #     if has_errors(errors, ERROR):
        #         sys.exit(1)
        #
        # dest_name = file_names[0][:-3] + '.py'
        # with open(file_names[0][:-3] + '.py', 'w', encoding='utf-8') as f:
        #     f.write(result)
        #  print(result.serialize(how='default' if args.xml is None else 'xml')
        #        if isinstance(result, Node) else result)

if __name__ == "__main__":
    main()
