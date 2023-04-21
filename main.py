import asyncio

import httpx


async def main():
    web_client = httpx.AsyncClient(
        base_url='http://api.datsart.dats.team/',
        headers={'Authorization': 'Bearer 643d26392556f643d263925571'}
    )


asyncio.run(main())
