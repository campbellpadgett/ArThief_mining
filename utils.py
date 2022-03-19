import csv
from typing import List, Dict
import aiohttp
import asyncio
import ssl
import time
import certifi

def csv_traverse(csv_file: str, key_terms: List[str], source: str) -> List:

    """Used to take a csv file and filter out non-painting 
    or non-Photo related artworks, returns results"""

    traversed_csv = []
    start = time.time()
    with open(csv_file) as csv_file_opened:

        csv_reader = csv.reader(csv_file_opened, delimiter=',')

        if source == 'MET':
            class_idx, isPub_idx = 45, 3

        for row in csv_reader:

            classification = row[class_idx]
            isPublicDomain = row[isPub_idx]

            if classification not in key_terms or isPublicDomain == False:
                continue
            
            traversed_csv.append(row)
        
        end = time.time()
        print(f'traversed {len(traversed_csv)} rows in {end - start} seconds')
        return traversed_csv
        # print(traversed_csv[:5])
        # print(type(traversed_csv))




def get_row_indicies(row: List[str]) -> List[str]:
    
    """Used to show the row values and their corrisponding indicies.
        Should be first row of CSV file"""

    row_values = []
    idx = 0
    
    for value in row:
        row_values.append(f'{value} {idx}')
        idx += 1

    return row_values





async def process_csv_entry(row: str, session: aiohttp.ClientSession, count: int, desired_data: Dict[str, int], writer: csv.writer):
    """Takes a row from a csv file and makes a get request with the url stored 
    in it. Then stores new url and desired data in new csv row"""

    count += 1
    if count > 70:
        time.sleep(1.1)
        count = 0

    new_line = []
    for key in desired_data:
        new_line.append(row[desired_data[key]])

    url = f'https://collectionapi.metmuseum.org/public/collection/v1/objects/{row[desired_met_data["image_link"]]}'

    async with session.get(url, allow_redirects=False) as response:
        result = await response.json()
        primaryImage, primaryImageSmall = result['primaryImage'], result['primaryImageSmall']

        print(f'Storing {primaryImage}, {primaryImageSmall}...')
        new_line.append(primaryImage)
        new_line.append(primaryImageSmall)
        writer.writerow(new_line)


async def create_new_csv(filename: str, rows: list[str], desired_data: Dict[str, int]):
    """Takes rows of csv data and persists them to new csv using the process_csv_entry function
    and the event loop from asyncio and aiohttp"""

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh Intel Mac OS X 10.15 rv: 98.0) Gecko/20100101 Firefox/98.0"
    }
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl=ssl_context, limit=10)

    with open(filename, mode='w') as test_file:
        met_writer = csv.writer(test_file, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        met_writer.writerow(['Title', 'Artist'])

        async with aiohttp.ClientSession(connector=conn, headers=headers) as session:
            tasks = []
            count = 0
            for row in rows:
                task = asyncio.ensure_future(process_csv_entry(
                    row=row, session=session, count=count, desired_data=desired_data, writer=met_writer))
                tasks.append(task)
            await asyncio.gather(*tasks, return_exceptions=True)





            
if __name__ == '__main__':

    # a = ['a', 'b', 'c']
    # print(get_row_indicies(a))

    # key_terms = ['Paintings', 'Paintings-Decorative']
    # csv_traverse('../MET/MetObjects.csv', key_terms, 'MET')

    source = 'MET'
    original_file = '../MET/MetObjects.csv'
    key_object_type_terms = ['Paintings', 'Paintings-Decorative']
    desired_met_data = {
        'title': 9,
        'artist': 18,
        'artist_nationality': 22,
        'artist_display_bio': 19,
        'culture': 10,
        'era': 11,
        'gender': 25,
        'nation': 38,
        'medium': 31,
        'source': 50,
        'date_of_release': 28,
        'image_link': 4
    }
    
    csv_rows = csv_traverse(original_file, key_object_type_terms, source)

    print(len(csv_rows[:26]))
    print('--------------------------------------')
    start = time.time()
    asyncio.run(create_new_csv(filename='met.csv', rows=csv_rows[:26], desired_data=desired_met_data))
    end = time.time()
    print(f'searched {len(csv_rows[:26])} links in {end - start} seconds')
