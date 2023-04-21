import asyncio
import json
from pathlib import Path

import httpx
from loguru import logger

from typing_ import ServerResponse
from color_conventer import hex_convert

temp_json_file = Path('.temp.json')


class ResponseError(Exception):
    pass


@logger.catch()
async def main():
    async with httpx.AsyncClient(
            base_url='http://api.datsart.dats.team/',
            headers={'Authorization': 'Bearer 643d26392556f643d263925571'}
    ) as web_client:
        data = {'imageId': '2'}
        resp: httpx.Response = await web_client.post(
            '/art/factory/generate',
            headers={'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'}
            # headers={'Content-Disposition': 'form-data; imageId="2"'}
            # data=data
        )

        print(resp.status_code)
        if resp.status_code != 200:
            print(resp.text)
            raise ResponseError()

        with open('.temp.json', 'w+') as f:
            json.dump(resp.json(), f, indent=2, ensure_ascii=False)

        color1 = hex_convert(resp.json()['response']['1']['color'])
        color2 = hex_convert(resp.json()['response']['2']['color'])
        color3 = hex_convert(resp.json()['response']['3']['color'])
        resp: ServerResponse = ServerResponse(resp.text)
        print(resp.info.tick)


asyncio.run(main())
