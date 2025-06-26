from typing import TypedDict, NotRequired, Optional, TypeVar, Callable, Any, List, Generic

class Test_RegisterWebviewViewProviderOptions_0_WebviewOptions_0(TypedDict):
    retainContextWhenHidden: NotRequired[bool]


class Test_RegisterWebviewViewProviderOptions_0(TypedDict):
    webviewOptions: NotRequired[Test_RegisterWebviewViewProviderOptions_0_WebviewOptions_0]


class Test:

    def registerWebviewViewProvider(self, viewId: str, provider: 'WebviewViewProvider', options: Optional[
        Test_RegisterWebviewViewProviderOptions_0] = None) -> 'Disposable':
        pass

T = TypeVar('T')

class Event(Generic[T]):

    def __call__(self, listener: Callable[[T], Any], thisArgs: Optional[Any] = None,
                 disposables: Optional[List['Disposable']] = None) -> 'Disposable':
        pass
