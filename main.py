import asyncio
import json
import typing

import httpx
from loguru import logger

from typing_ import ServerResponse
from taskpool import TaskPoolExecutor
from colors import closest_color

RgbTuple = tuple[int, int, int]

TARGET_COLORS: set[RgbTuple] = set()

colors_storage: dict[str, int] = {}


class ResponseError(Exception):
    pass


class ColorPickedError(Exception):
    pass


async def pick_color(web_session: httpx.AsyncClient, color_id: int, tick: int):
    resp = await web_session.post('/art/factory/pick', data={'num': color_id, 'tick': tick})
    resp = ServerResponse(resp.text)
    # if not resp.success:
    #     print(resp.to_dict())


async def check_and_get_colors(web_session: httpx.AsyncClient):
    async with TaskPoolExecutor(3) as executor:
        last_tick = 0
        while True:
            resp = ServerResponse(
                (await web_session.post('/art/factory/generate', data={'Content-Type': 'multipart/form-data'})).text)

            if resp.info.tick == last_tick:
                await asyncio.sleep(0)
                continue

            for i in range(1, 4):
                await executor.put(pick_color(web_session, color_id=i, tick=resp.info.tick))

            last_tick = resp.info.tick

            colors_info = await web_session.post('/art/colors/list', data={'Content-Type': 'multipart/form-data'})
            print(colors_info.text)

            await asyncio.sleep(0)


@logger.catch()
async def main():
    async with httpx.AsyncClient(
            base_url='http://api.datsart.dats.team/',
            headers={'Authorization': 'Bearer 643d26392556f643d263925571'}
    ) as web_client:
        await take_info(web_client)
        # await check_and_get_colors(web_client)
        # используем дату, если мы хотим какую-то хуйню передать и она динамическая
        # data = {'imageId': '2'}
        # resp: httpx.Response = await web_client.post(
        #     '/art/colors/list',
        #     headers={'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'}
        #     # headers={'Content-Disposition': 'form-data; imageId="2"'}
        #     # data=data
        # )
        #
        # print(resp.status_code)
        # print(resp.text)
        # if resp.status_code != 200:
        #     # print(resp.text)
        #     raise ResponseError()
        #
        # with open('.temp.json', 'w') as f:
        #     json.dump(resp.json(), f, indent=2, ensure_ascii=False)
        #
        # color_list = resp.json()["response"]
        # red, black = closest_color(color_list)
        # print(f'самый красный: {red}\nсамый чёрн: {black}')
        # resp: ServerResponse = ServerResponse(resp.text)
        # print(resp.info.tick)
        #
        # await asyncio.gather(asyncio.create_task(check_and_get_colors(web_client)))


@logger.catch()
async def check_position(web_client: httpx.AsyncClient):
    # await check_and_get_colors(web_client)

    data = {"id": "1682103745449907326"}
    resp: httpx.Response = await web_client.post(
        '/art/state/queue',
        data=data
    )

    print(resp.status_code)
    print(resp.text)
    if resp.status_code != 200:
        print(resp.text)
        raise ResponseError()


@logger.catch()
async def take_info(web_client: httpx.AsyncClient):
    resp: httpx.Response = await web_client.post(
        '/art/stage/info',
    )
    return resp


asyncio.run(main())
