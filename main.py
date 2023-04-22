import asyncio
import json

import httpx
from loguru import logger

from taskpool import TaskPoolExecutor
from typing_ import RgbTuple
from typing_ import ServerResponse

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


async def shoot(web_session: httpx.AsyncClient, horizontal: int, vertical: int, power: int):
    async with TaskPoolExecutor(2) as executor:  # бля заюзать бы его если б не слип 50 чтобы приходил респонс не ноне
        colors_info = ServerResponse(
            (await web_session.post('/art/colors/list', data={'Content-Type': 'multipart/form-data'})).text)
        print("dd", colors_info.response)
        color = [*colors_info.response.keys()][0]
        # print(color)
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
        print('id =', [shoot_resp.response.queue.id])

        resp = await wait_for_shoot_info(web_session, shoot_resp.response.queue.id)

        print("77", resp)
        if resp.response.status != 0 or resp.response.status != 10:

            angleHor = resp.response.dto.shot.angleHorizontal
            angleVer = resp.response.dto.shot.angleVertical
            Power = resp.response.dto.shot.power

            if resp.response.stats.status == 200:
                print(f"АХУЕТЬЬ РАКЕТА НАХУЙ ПОЛЕТЕЛА!!!!\n")
                with open('.temp.json', 'w+') as f:
                    existing_json = json.load(f)
                    existing_json.append(resp.response)
                    json.dump(existing_json, f, indent=2, ensure_ascii=False)
            else:
                print('промах при:')
            print(f'horizontal: {angleHor}\nvertical: {angleVer}\npower: {Power}\n')
        else:
            await asyncio.sleep(0)

    print("93", resp)


async def wait_for_shoot_info(web_session: httpx.AsyncClient, shoot_id: int):
    while True:
        resp = ServerResponse(
            (await web_session.post('/art/state/queue', data={'id': shoot_id}))
            .text
        )

        # print(resp.to_dict())

        if resp.respone is None or resp.response == [None]:
            await asyncio.sleep(0)
            continue
        break
    return resp

# 1682144585168121910


# TODO: Добавить цикл main.data.power = i inrange(0, 1000, 10) который берёт случайную краску со склада и стеляет (отправляет запрос) Нужно будет посмотреть при каких параметрах происходят попадания


@logger.catch()
async def main():
    async with httpx.AsyncClient(
            base_url='http://api.datsart.dats.team/',
            headers={'Authorization': 'Bearer 643d26392556f643d263925571'}
    ) as web_session:


        await shoot(web_session, 0, 66, 460)

        await take_info(web_session)

        # resp = await web_session.post('/art/colors/list')
        # # resp = ServerResponse(resp.text)
        #
        # with open('.temp.json', 'w') as f:
        #     json.dump(resp.json(), f, indent=2, ensure_ascii=False)
        # await check_and_get_colors(web_session) data={'num': color_id, 'tick': tick
        # используем дату, если мы хотим какую-то хуйню передать и она динамическая
        # data = {'imageId': '2'}
        # resp: httpx.Response = await web_session.post(
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
        # await asyncio.gather(asyncio.create_task(check_and_get_colors(web_session)))


@logger.catch()
async def check_position(web_session: httpx.AsyncClient, id):
    # await check_and_get_colors(web_session)

    data = {"id": f"{id}"}
    resp: httpx.Response = await web_session.post(
        '/art/state/queue',
        data=data
    )

    print(resp.status_code)
    print(resp.text)
    if resp.status_code != 200:
        print(resp.text)
        raise ResponseError()


@logger.catch()
async def take_info(web_session: httpx.AsyncClient):
    resp: httpx.Response = await web_session.post(
        '/art/stage/info',
    )
    with open('.temp.json', 'w') as f:
        json.dump(resp.json(), f, indent=2, ensure_ascii=False)
    print(resp)
    return resp

    # TODO: Добавить цикл main.data.power = i inrange(0, 1000, 10) который берёт случайную краску со склада и стеляет (отправляет запрос) Нужно будет посмотреть при каких параметрах происходят попадания


asyncio.run(main())

# TODO: Сделать функции с вводом параметров
# TODO: Добавить цикл main.data.power = i inrange(0, 1000, 10) который берёт случайную краску со склада и стеляет (отправляет запрос) Нужно будет посмотреть при каких параметрах происходят попадания
