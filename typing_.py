from typing import overload

from types_ import FriendlyDict


class ResponseInfo(FriendlyDict):
    m: int
    t: float
    c: int
    tick: int
    ns: int


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


class Queue(FriendlyDict):
    id: int


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


class ResponseField(FriendlyDict):
    stage: Stage
    images: list[Image]
    selectedImage: ShortImage
    canvas: Canvas
    stats: Stats
    queue: Queue
    stage: Stage
    images: list[Image]


class ServerResponse(FriendlyDict):
    success: bool
    status: int
    info: ResponseInfo
    response: ResponseField


RgbTuple = tuple[int, int, int]
