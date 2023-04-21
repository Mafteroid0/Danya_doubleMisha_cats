import asyncio
import json
from pathlib import Path

import httpx
from loguru import logger

from typing_ import ServerResponse
from taskpool import TaskPoolExecutor

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
        while True:
            resp = ServerResponse(
                (await web_session.post('/art/factory/generate', data={'Content-Type': 'multipart/form-data'})).text)
            # print(resp.response.to_dict())
            for i in range(1, 4):
                await executor.put(pick_color(web_session, color_id=i, tick=resp.info.tick))
            await asyncio.sleep(1)


@logger.catch()
async def main():
    async with httpx.AsyncClient(
            base_url='http://api.datsart.dats.team/',
            headers={'Authorization': 'Bearer 643d26392556f643d263925571'}
    ) as web_client:
        # await check_and_get_colors(web_client)

        data = {"angleHorizontal": "0",
                "angleVertical": "30",
                "power": "500",
                "colors[9428803]": "1",
                "colors[4936479]": "1",

                }
        resp: httpx.Response = await web_client.post(
            '/art/ballista/shoot',
            data=data
        )

        print(resp.status_code)
        print(resp.text)
        if resp.status_code != 200:
            print(resp.text)
            raise ResponseError()

        # color1 = hex_convert(resp.json()["response"]["1"]["color"])
        # red = (194, 39, 45)
        # black = (36, 36, 36)
        # color_list = resp.json()["response"]
        # print("colorlist", color_list)

        with open('.temp.json', 'w') as f:
            json.dump(resp.json(), f, indent=2, ensure_ascii=False)

        # mix_colors(red,)
        # mix_colors(black, )
        resp: ServerResponse = ServerResponse(resp.text)
        print(resp.info.tick)

        await asyncio.gather(asyncio.create_task(check_and_get_colors(web_client)))


@logger.catch()
async def check_position():
    async with httpx.AsyncClient(
            base_url='http://api.datsart.dats.team/',
            headers={'Authorization': 'Bearer 643d26392556f643d263925571'}
    ) as web_client:
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
async def take_info():
    async with httpx.AsyncClient(
            base_url='http://api.datsart.dats.team/',
            headers={'Authorization': 'Bearer 643d26392556f643d263925571'}
    ) as web_client:
        # await check_and_get_colors(web_client)

        resp: httpx.Response = await web_client.post(
            '/art/stage/info',
        )

        print(resp.status_code)
        print(resp.text)
        if resp.status_code != 200:
            print(resp.text)
            raise ResponseError()


# asyncio.run(main())
# asyncio.run(check_position())
# asyncio.run(take_info())
# TODO: Сделать функции с вводом параметров
# TODO: Добавить цикл main.data.power = i inrange(0, 1000, 10) который берёт случайную краску со склада и стеляет (отправляет запрос) Нужно будет посмотреть при каких параметрах происходят попадания