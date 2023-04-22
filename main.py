import asyncio
import json

import httpx
from loguru import logger
from podbor_params import shoot_calulating
from taskpool import TaskPoolExecutor
from typing_ import RgbTuple
from typing_ import ServerResponse
from colors import mix_colors

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

            await asyncio.sleep(0)


async def shoot(web_session: httpx.AsyncClient, horizontal: int, vertical: int, power: int):
    async with TaskPoolExecutor(2) as executor:  #
        colors_info = ServerResponse(
            (await web_session.post('/art/colors/list', data={'Content-Type': 'multipart/form-data'})).text)
        color = [*colors_info.response.keys()][0]
        shoot_resp = ServerResponse(
            (
                await web_session.post(
                    '/art/ballista/shoot',
                    data={
                        'angleHorizontal': horizontal,
                        'angleVertical': vertical,
                        'power': power,
                        f'colors[{color}]': 1
                    }
                )
            ).text
        )
        # print(shoot_resp)
        # print('id =', shoot_resp.response.queue.id)
        await asyncio.sleep(1)
        # resp = await wait_for_shoot_info(web_session, shoot_resp.response.queue.id)


async def wait_for_shoot_info(web_session: httpx.AsyncClient, shoot_id: int):
    while True:
        resp = ServerResponse(
            (await web_session.post('/art/state/queue', data={'id': shoot_id}))
            .text
        )

        resp = ServerResponse(
            (await web_session.post('/art/state/queue', data={'id': shoot_id}))
            .text
        )

        if resp.respone is None or resp.response == [None]:
            await asyncio.sleep(0)
            continue
        break
    return resp


async def color_thing(web_session: httpx.AsyncClient):
    print("122\n", mix_colors((0, 12, 45), (120, 50, 11)))


#1 1682144585168121910


# TODO: Добавить цикл main.data.power = i inrange(0, 1000, 10) который берёт случайную краску со склада и стеляет (отправляет запрос) Нужно будет посмотреть при каких параметрах происходят попадания


@logger.catch()
async def main():
    async with httpx.AsyncClient(
            base_url='http://api.datsart.dats.team/',
            headers={'Authorization': 'Bearer 643d26392556f643d263925571'}
    ) as web_session:
        # await shoot(web_session, 1, 1, 500)
        # for vertical in range(30, 101, 10):
        #     for power in range(1, 1001, 10):
        #         oldshoots, oldMisses, oldMissesPartially = await take_info(web_session)

                x, y = 155, 137
                radius, horisontal = shoot_calulating(x, y)
                pwr = (radius * 78.9281) / 564
                await shoot(web_session, horisontal, 1, pwr) # 42.09 - 42.1
                #78.9281 - край
        #         shoots, Misses, MissesPartially = await take_info(web_session)
        #
        #         if MissesPartially - oldMissesPartially == 1:
        #             print("попал частично!")
        #             print(f'vertical: {vertical}\nhorizontal: 1\npower: {power}')
        #         elif shoots - oldshoots != (Misses - oldMisses):
        #             print("попал полностью!")
        #             print(f'vertical: {vertical}\nhorizontal: 1\npower: {power}')
        #         print('-----------------------')
                # else:
                #     print("не попал")

        # print(take_info)



@logger.catch()
async def check_position(web_session: httpx.AsyncClient):
    # await check_and_get_colors(web_session)

    data = {"id": "1682103745449907326"}
    resp: httpx.Response = await web_session.post(
        '/art/state/queue',
        data=data
    )

    if resp.status_code != 200:
        print(resp.text)
        raise ResponseError()


@logger.catch()
async def take_info(web_session: httpx.AsyncClient):
    resp = ServerResponse(
        (await web_session.post('/art/stage/info'))
        .text
    )

    # return resp
    return resp.response.stats.shoots, resp.response.stats.shootsMisses, resp.response.stats.shootsMissesPartially

    # TODO: Добавить цикл main.data.power = i inrange(0, 1000, 10) который берёт случайную краску со склада и стеляет (отправляет запрос) Нужно будет посмотреть при каких параметрах происходят попадания


asyncio.run(main())

# TODO: Сделать функции с вводом параметров
# TODO: Добавить цикл main.data.power = i inrange(0, 1000, 10) который берёт случайную краску со склада и стеляет (отправляет запрос) Нужно будет посмотреть при каких параметрах происходят попадания
