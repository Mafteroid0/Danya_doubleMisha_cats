import asyncio
import json
from pathlib import Path
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

            # colors_info = await web_session.post('/art/colors/list', data={'Content-Type': 'multipart/form-data'})
            # print('boom')

            await asyncio.sleep(0)

async def shoot(web_session: httpx.AsyncClient):
    async with TaskPoolExecutor(2) as executor: #бля заюзать бы его если б не слип 50 чтобы приходил респонс не ноне
        colors_info = ServerResponse((await web_session.post('/art/colors/list', data={'Content-Type': 'multipart/form-data'})).text)
        # print("dd", colors_info.response)
        for horizontal in range(1, 91, 2):
            for vertical in range(1, 91, 2):
                for power in range(1, 1001, 5):
                    for color in colors_info.response:
                        data = {
                            'angleHorizontal': horizontal,
                            'angleVertical': vertical,
                            'power': power,
                             f'colors[{color}]': 1
                        }
                        resp = ServerResponse(
                            (await web_session.post('/art/ballista/shoot', data=data)).text)
                        data = {
                            'id': resp.response.queue.id,
                        }
                        print('id=',resp.response.queue.id)

                        while True:
                            resp = ServerResponse(
                                (await web_session.post('/art/state/queue', data=data)).text)
                            if resp.respone == None:
                                await asyncio.sleep(5)
                                continue
                            print("77", resp)
                            if resp.response.status != 0 or resp.response.status != 10:
                                angleHor = resp.response.dto.shot.angleHorizontal
                                angleVer = resp.response.dto.shot.angleVertical
                                Power = resp.response.dto.shot.power
                                if resp.response.stats.status == 20:
                                    print(f"АХУЕТЬЬ РАКЕТА НАХУЙ ПОЛЕТЕЛА!!!!\n")
                                    with open('.temp.json', 'w+') as f:
                                        existing_json = json.load(f)
                                        existing_json.append(resp.response)
                                        json.dump(existing_json, f, indent=2, ensure_ascii=False)

                                else:
                                    print('промах при:')
                                print(f'horizontal: {angleHor}\nvertical: {angleVer}\npower: {Power}\n')
                                break
                            else:
                                await asyncio.sleep(2)


        print("93", resp)
    # TODO: Добавить цикл main.data.power = i inrange(0, 1000, 10) который берёт случайную краску со склада и стеляет (отправляет запрос) Нужно будет посмотреть при каких параметрах происходят попадания


@logger.catch()
async def main():
    async with httpx.AsyncClient(
            base_url='http://api.datsart.dats.team/',
            headers={'Authorization': 'Bearer 643d26392556f643d263925571'}
    ) as web_client:
        await shoot(web_client)
        # resp = await web_client.post('/art/colors/list')
        # # resp = ServerResponse(resp.text)
        #
        # with open('.temp.json', 'w') as f:
        #     json.dump(resp.json(), f, indent=2, ensure_ascii=False)
        # await check_and_get_colors(web_client) data={'num': color_id, 'tick': tick
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



    # TODO: Добавить цикл main.data.power = i inrange(0, 1000, 10) который берёт случайную краску со склада и стеляет (отправляет запрос) Нужно будет посмотреть при каких параметрах происходят попадания


asyncio.run(main())

# TODO: Сделать функции с вводом параметров
# TODO: Добавить цикл main.data.power = i inrange(0, 1000, 10) который берёт случайную краску со склада и стеляет (отправляет запрос) Нужно будет посмотреть при каких параметрах происходят попадания