import aiohttp
import asyncio
import ssl
import certifi
import requests


met = f'https://collectionapi.metmuseum.org/public/collection/v1/objects/35155'

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh Intel Mac OS X 10.15 rv: 98.0) Gecko/20100101 Firefox/98.0"
}


async def main():


    # res = requests.get(met)
    # print(res.request.headers)

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl=ssl_context)

    async with aiohttp.ClientSession(connector=conn, headers=headers) as session:
        async with session.get(met) as res:
            # print(res.status)
            print(await res.json())
        # async with session.get(met) as response:
        #     print(response)

            # print("Status:", response.status)
            # print("Content-type:", response.headers['content-type'])

            # # res = await response
            # html = await response.text()
            # print(html)
            # print(res['primaryImage'])

loop = asyncio.get_event_loop()
loop.run_until_complete(main())



if __name__ == '__main__':
    main()
