import asyncio
import json
from pathlib import Path

import httpx
from loguru import logger

from typing_ import ServerResponse
from color_conventer import hex_convert, mix_colors
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
    if not resp.success:
        print(resp.to_dict())


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

        data = {'imageId': '2'}
        resp: httpx.Response = await web_client.post(
            '/art/colors/list',
            headers={'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'}
            # headers={'Content-Disposition': 'form-data; imageId="2"'}
            # data=data
        )

        print(resp.status_code)
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


asyncio.run(main())
