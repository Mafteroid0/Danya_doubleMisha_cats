import asyncio

import httpx


async def main():
    async with httpx.AsyncClient(
            base_url='http://api.datsart.dats.team/',
            headers={'Authorization': 'Bearer 643d26392556f643d263925571'}
    ) as web_client:
        resp: httpx.Response = await web_client.post(
            '/art/stage/next',
            headers={'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'}
        )
        print(resp.json())


asyncio.run(main())
