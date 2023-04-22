import asyncio
import json
import math

import httpx
from loguru import logger
from PIL import Image
from io import BytesIO
from podbor_params import shoot_calulating
from taskpool import TaskPoolExecutor
from typing_ import RgbTuple
from typing_ import ServerResponse
from colors import mix_colors, match_colors_combination, distance

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


async def shoot(web_session: httpx.AsyncClient, x: int, y: int, color: RgbTuple, width: int = 1):  # надо передать в tuple и список хуярить если цветов нескл
    async with TaskPoolExecutor(2) as executor:
        # color = match_colors_combination(target_pixel, color_list.response, weight=1)
        radius, horizontal = shoot_calulating(x, y, width)
        power = (radius * 78.9281) / 564  # await shoot(web_session, horisontal, 1, pwr)  # 42.09 - 42.1
        # 78.9281 - крайawait shoot(web_session, horizontal=horizontal, vertical=1, power=pwr, factory_color=color)

        # colors_info = ServerResponse(
        #     (await web_session.post('/art/colors/list', data={'Content-Type': 'multipart/form-data'})).text)
        # color = [*colors_info.response.keys()][0]
        shoot_resp = ServerResponse(
            (
                await web_session.post(
                    '/art/ballista/shoot',
                    data={
                        'angleHorizontal': horizontal,
                        'angleVertical': 1,
                        'power': power,
                        f'colors[{color}]': 1
                    }
                )
            ).text
        )
        print(shoot_resp)
        # print('id =', shoot_resp.response.queue.id)
        await asyncio.sleep(0.25)
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


async def analyze_shoot(web_session: httpx.AsyncClient):
    img = httpx.get("http://s.datsart.dats.team/game/image/shared/2.png")  # картинка к которой мы стремиися
    perfect_img = Image.open(BytesIO(img.content))
    canvas = "http://s.datsart.dats.team/game/canvas/238/108.png"  # наша картинка
    resp = httpx.get(canvas)
    img = Image.open(BytesIO(resp.content))
    color_list = []
    _ = asyncio.create_task(update_color_list(web_session, color_list))
    for x in range(250):
        for y in range(250):
            await asyncio.sleep(0)
            pixel_color_canvas = img.getpixel((x, y))  # собираем с нашей картинки пиксель
            target_pixel = perfect_img.getpixel((x, y))  # собираем с нужной картинки пиксель
            d = distance(target_pixel, pixel_color_canvas)
            if pixel_color_canvas == (255, 255, 255) and d < 0.1:
                continue  # похуй это белый пиксель похуй похуй похуй мне эй
            if d > 0.27:  # пиксели разные, надо красить. 0.07471591718924561 - дистанция между белым нужного и белым нашего канваса
                print(color_list)

                color = match_colors_combination(target_pixel, color_list.response, weight=1)
                radius, horizontal = shoot_calulating(x, y)
                pwr = (radius * 78.9281) / 564
                # await shoot(web_session, horisontal, 1, pwr)  # 42.09 - 42.1
                # 78.9281 - край
                await shoot(web_session, horizontal=horizontal, vertical=1, power=pwr, factory_color=color)


async def update_color_list(web_session, color_list):
    while True:
        color_list += await get_pots(web_session)
        print("128")
        await asyncio.sleep(1)
        color_list.clear()


# TODO: Добавить цикл main.data.power = i inrange(0, 1000, 10) который берёт случайную краску со склада и стеляет (отправляет запрос) Нужно будет посмотреть при каких параметрах происходят попадания


@logger.catch()
async def main():
    async with httpx.AsyncClient(
            base_url='http://api.datsart.dats.team/',
            headers={'Authorization': 'Bearer 643d26392556f643d263925571'}
    ) as web_session:
        await analyze_shoot(web_session)


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


async def get_pots(web_session: httpx.AsyncClient):
    resp = ServerResponse((await web_session.post('/art/colors/list')).text)
    return resp


asyncio.run(main())

# TODO: Сделать функции с вводом параметров
# TODO: Добавить цикл main.data.power = i inrange(0, 1000, 10) который берёт случайную краску со склада и стеляет (отправляет запрос) Нужно будет посмотреть при каких параметрах происходят попадания
