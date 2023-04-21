from types_ import FriendlyDict


class ResponseInfo(FriendlyDict):
    m: int
    t: float
    c: int
    tick: int
    ns: int


class StageInfo(FriendlyDict):
    id: int
    num: int
    name: str
    description: str


class Image(FriendlyDict):
    id: int
    url: str
    grage: int
    width: int
    height: int


class ResponseField(FriendlyDict):
    stage: StageInfo
    images: list[Image]


class ServerResponse(FriendlyDict):
    success: bool
    status: int
    info: ResponseInfo
