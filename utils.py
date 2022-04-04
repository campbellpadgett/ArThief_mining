import csv
from typing import Callable, List, Dict, NoReturn
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
        elif source == "RJK":
            class_idx, isPub_idx = 3, 6

        for row in csv_reader:

            classification = row[class_idx]
            isPublicDomain = row[isPub_idx]

            if classification not in key_terms or isPublicDomain == False or isPublicDomain== '':
                continue
            
            print(row)
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



def filter_for_rjk_fields(json_data: str, image_link: str) -> List[str]:
    """Takes in RJK json data and returns row for csv"""

    title = json_data['artObject']['title']
    artist = json_data['artObject']['principalMakers'][0]['name']
    artist_nationality = json_data['artObject']['principalMakers'][0]['nationality']
    artist_display_bio = json_data['artObject']['principalMakers'][0]['labelDesc']
    culture = json_data['artObject']['language']
    era = json_data['artObject']['dating']['presentingDate']
    # gender = json_data['artObject']['dating']['presentingDate']
    nation = json_data['artObject']['productionPlaces'][0]
    medium = json_data['artObject']['physicalMedium']
    source = 'Rijksmuseum'
    date_of_release = json_data['artObject']['dating']['presentingDate']
    image_link = image_link

    return [title, artist, artist_nationality,
            artist_display_bio,
            culture,
            era,
            nation,
            medium,
            source,
            date_of_release,
            image_link]


async def rjk_processor(row: str, session: aiohttp.ClientSession, pause: bool, desired_data: Dict[str, int], writer: Callable):
    """Takes a row from the Rijksstudio csv file and makes a get request with the url stored 
    in it. Then stores new url and desired data in new csv row"""


    object_number, image = row[0], row[6]
    url = f'https://www.rijksmuseum.nl/api/nl/collection/{object_number}?key=RDOovp6Y'
    print('url prepared: ', url)
    
    async with session.get(url, allow_redirects=False) as response:
        print('sending request now', url)
        # per instructions of met api
        if pause:
            print('_________limit hit. Pausing for 1.3 seconds_________')
            time.sleep(1.3)

        result = await response.json()
        new_line = filter_for_rjk_fields(result, image)

        print(f'Storing {image}, {url}')
        writer.writerow(new_line)


async def met_processor(row: str, session: aiohttp.ClientSession, pause: bool, desired_data: Dict[str, int], writer: Callable):
    """Takes a row from the MET csv file and makes a get request with the url stored 
    in it. Then stores new url and desired data in new csv row"""

    new_line = []
    for key in desired_data:
        new_line.append(row[desired_data[key]])

    url = f'https://collectionapi.metmuseum.org/public/collection/v1/objects/{row[desired_data["image_link"]]}'

    async with session.get(url, allow_redirects=False) as response:
        # per instructions of met api
        if pause:
            print('_________limit hit. Pausing for 1.3 seconds_________')
            time.sleep(1.3)

        result = await response.json()
        primaryImage, primaryImageSmall = result['primaryImage'], result['primaryImageSmall']

        if result['isPublicDomain']:
            print(f'Storing {primaryImage}, {url}')
            new_line.append(primaryImage)
            new_line.append(primaryImageSmall)
            writer.writerow(new_line)


async def create_new_csv(filename: str, rows: list[str], desired_data: Dict[str, int], 
                            csv_processor: Callable[[str, aiohttp.ClientSession, int, Dict[str, int], Callable], NoReturn]):
    """Takes rows of csv data and persists them to new csv using the process_csv_entry function
    and the event loop from asyncio and aiohttp"""

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh Intel Mac OS X 10.15 rv: 98.0) Gecko/20100101 Firefox/98.0"
    }
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl=ssl_context, limit=10)

    with open(filename, mode='w') as test_file:
        writer = csv.writer(test_file, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Title', 'Artist', 'Natiionality', 'Artist Bio', 'Culture', 'Era', 'Gender', 'Nation', 'Medium', 'Source', 'DOR', 'Image'])

        async with aiohttp.ClientSession(connector=conn, headers=headers) as session:
            tasks, rows_traversed = [], 0
            for row in rows:
                pause = False
                if rows_traversed > 75:
                    pause, rows_traversed = True, 0
                task = asyncio.ensure_future(csv_processor(
                    row=row, session=session, pause=pause, desired_data=desired_data, writer=writer))
                tasks.append(task)
                rows_traversed += 1
            await asyncio.gather(*tasks, return_exceptions=True)
            




            
if __name__ == '__main__':

    # a = ['a', 'b', 'c']
    # print(get_row_indicies(a))

    # key_terms = ['Paintings', 'Paintings-Decorative']
    # csv_traverse('../MET/MetObjects.csv', key_terms, 'MET')

    source = 'RJK'
    # original_file = '../MET/MetObjects.csv'
    original_file = '../rijk/202001-rma-csv-collection.csv'
    key_object_type_terms = ['schilderij']
    # desired_met_data = {
    #     'title': 9,
    #     'artist': 18,
    #     'artist_nationality': 22,
    #     'artist_display_bio': 19,
    #     'culture': 10,
    #     'era': 11,
    #     'gender': 25,
    #     'nation': 38,
    #     'medium': 31,
    #     'source': 50,
    #     'date_of_release': 28,
    #     'image_link': 4
    # }

    desired_rjk_data = {
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

    print(len(csv_rows[:100]))
    print('--------------------------------------')
    start = time.time()
    asyncio.run(create_new_csv(filename='rjk.csv',
                rows=csv_rows[:100], desired_data=desired_rjk_data, csv_processor=rjk_processor))
    end = time.time()
    print(f'searched {len(csv_rows[:100])} links in {end - start} seconds')
