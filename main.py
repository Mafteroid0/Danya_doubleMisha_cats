import asyncio
import json
from pathlib import Path

import httpx
from loguru import logger

from typing_ import ServerResponse


temp_json_file = Path('.temp.json')


class ResponseError(Exception):
    pass


@logger.catch()
async def main():
    async with httpx.AsyncClient(
            base_url='http://api.datsart.dats.team/',
            headers={'Authorization': 'Bearer 643d26392556f643d263925571'}
    ) as web_client:
        resp: httpx.Response = await web_client.post(
            '/art/stage/next',
            headers={'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'}
        )

        print(resp.text)
        if resp.status_code != 200:
            raise ResponseError()

        with open('.temp.json', 'w') as f:
            json.dump(resp.json(), f, indent=2)

        resp: ServerResponse = ServerResponse(resp.text)
        print(resp.info.tick)


asyncio.run(main())
