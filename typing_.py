from types_ import FriendlyDict


class ResponseInfo(FriendlyDict):
    m: int
    t: float
    c: int
    tick: int | None = None
    ns: int | None = None


class Stage(FriendlyDict):
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


class GetNextStageResponseField(FriendlyDict):
    stage: Stage
    images: list[Image]


class Queue(FriendlyDict):
    id: int


class StartNextStageResponseField(FriendlyDict):
    queue: Queue


class ShortImage(FriendlyDict):
    id: int
    url: str
    grade: int


class Canvas(FriendlyDict):
    url: str


class Stats(FriendlyDict):
    userStageId: int
    userId: int
    lastLogId: int
    commandCount: int
    grade: int
    pixels: int
    pixelsMisses: int
    shoots: int
    shootsMisses: int
    shootsMissesPartially: int


class GetActualInfoStageResponseField(FriendlyDict):
    stage: Stage
    images: list[Image]
    selectedImage: ShortImage
    canvas: Canvas
    stats: Stats


class ServerResponse(FriendlyDict):
    success: bool
    status: int
    info: ResponseInfo
    response: GetNextStageResponseField | StartNextStageResponseField | GetActualInfoStageResponseField
