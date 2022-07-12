import csv
from typing import Callable, List, Dict, NoReturn
import aiohttp
import asyncio
import ssl
import time
import certifi
from googletrans import Translator
from termcolor import colored
import settings
import glob
import json

def csv_traverse(csv_file: str, key_terms: List[str], source: str) -> List:

    """Used to take a csv file and filter out non-painting 
    or non-Photo related artworks, returns results"""

    traversed_csv = []
    start = time.time()
    with open(csv_file) as csv_file_opened:

        csv_reader = csv.reader(csv_file_opened, delimiter=',')

        if source == 'MET':
            class_idx, isPub_idx, title_idx = 45, 3, 9
        elif source == "RJK":
            class_idx, isPub_idx = 3, 6


        for row in csv_reader:

            classification = row[class_idx]
            isPublicDomain = row[isPub_idx]
            title = row[title_idx]

            if (classification not in key_terms or isPublicDomain == False 
                or isPublicDomain== '' 
                or title ==''):
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


def folder_explorer(dir: str) -> List[str]:
    '''Takes a directory path and returns an array of all files in that directory'''

    print(colored('[LOG]', 'blue'), f'opening dir: {dir} with folder_explorer')
    json_files = glob.glob(dir + '/**/*.json', recursive=True)

    return json_files


def chi_url_generator(data: Dict[str, str]) -> Dict[str, str] or NoReturn:
    '''Takes json file and extracts CHI urls from it'''

    accessable = (data['is_public_domain']
                  and data['artwork_type_title'] == 'Painting'
                  and data['image_id'] is not None)

    if accessable:
        imageID = data['image_id']
        large = f'https://www.artic.edu/iiif/2/{imageID}/full/1686,/0/default.jpg'
        small = f'https://www.artic.edu/iiif/2/{imageID}/full/843,/0/default.jpg'
        nameAndBio = data['artist_display'].split()
        nameAndBio = ' '.join(nameAndBio)

        return [
            data['title'], nameAndBio, data['place_of_origin'],
            nameAndBio, data['date_display'], data['medium_display'],
            data['credit_line'], large, small
        ]


def file_explorer(file: str, data_extractor: Callable[[List[str]], Dict[str, str] or NoReturn]) -> List[str]:
    '''Takes a file and a data_extractor. Returns data'''

    f = open(file, 'r')
    data = json.load(f)
    f.close()

    data = data_extractor(data)

    return data


def chi_processor():
    start = time.time()

    artwork_dir = '/Users/campbellpadgett/Desktop/art/API Stuff'
    artwork_files = folder_explorer(artwork_dir)
    print(colored('[LOG]', 'blue'), len(
        artwork_files), f'files inside directory')
    new_painting_count = url_count = 0

    with open('chi.csv', mode='w') as file:
        writer = csv.writer(file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Title', 'Artist', 'Natiionality', 'Artist Bio',
                        'Era', 'Medium', 'Source', 'Image Small', 'Image Large'])

        print(colored('[LOG]', 'blue'), f'{"chi.csv"} created')

        for artwork_file in artwork_files:
            row = file_explorer(artwork_file, chi_url_generator)

            # if title is empty, don't presist
            if row[0] == '' or row[0] is None:
                continue

            url_count += 1

            if row is not None:
                writer.writerow(row)
                new_painting_count += 1
                print(colored('[COUNT]', 'yellow'),
                      f'{len(artwork_files) - url_count} files left')

    end = time.time()
    print(colored('[COMPLETE]', 'green'),
          f'searched and extracted {len(artwork_files)} files in {end - start} seconds, {new_painting_count} new urls')



def filter_for_rjk_fields(json_data: str, image_link: str) -> List[str] or None:
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

    if title == '':
        return None
        

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
    
    async with session.get(url, allow_redirects=False) as response:
        # per instructions of met api
        if pause:
            print(colored('[PAUSE]', 'yellow'),
                  '_____limit reached, pausing 1 second_____')
            time.sleep(1)

        result = await response.json()
        new_line = filter_for_rjk_fields(result, image)

        if new_line is None:
            return

        print(colored('[LOG]', 'blue'), f'Storing {image}, {url}')
        writer.writerow(new_line)


async def translate_processor(row: List[str], pause: bool, session: aiohttp.ClientSession, writer: Callable, count: int, length: int):

    title_idx, bio_idx, nation_idx, medium_idx = 0, 3, 6, 7
    text = [row[title_idx], row[bio_idx], row[nation_idx], row[medium_idx]]

    params = {"q": f'{text}', "target": 'en'}
    # print(colored('[SENDING TRANSLATION]', 'magenta'), f'{row[title_idx]}')

    async with session.post(url=settings.url, params=params) as response:
        if pause:
            print(colored('[RUNNING]', 'yellow'), f'{length - count} rows left to translate')
            time.sleep(0.3)

        translated_texts: List[str] = await response.json()
        translation: List[str]

        # removing the quotes and array charecters from google translate api
        translations = translated_texts['data']['translations'][0]['translatedText']
        quote_removed = translations.replace("&quot;", "")
        front_bar_removed = quote_removed.replace("&#39;", "'")
        back_bar_removed = front_bar_removed.replace('[', "")
        combined_translation = back_bar_removed.replace(']', "")
        comma_striped_translation = combined_translation.replace("'", "")

        translation = comma_striped_translation.split(',')
        # print(translation)
        # print(colored(f'[TRANSLATION]:', 'magenta'), f'{translation[0]}')

        title, nation, medium = translation[0], translation[3], translation[4]
        bio = translation[1] + ',' + translation[2]

        new_row = [title,
                   row[1],
                   row[2],
                   bio,
                   row[4],
                   row[5],
                   nation,
                   medium,
                   row[8],
                   row[9],
                   row[10]]

        writer.writerow(new_row)


async def create_tanslated_csv(filename: str, rows: list[str], csv_processor: Callable[[str, bool, Callable], NoReturn]):

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh Intel Mac OS X 10.15 rv: 98.0) Gecko/20100101 Firefox/98.0"
    }
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl=ssl_context, limit=10)

    with open(filename, mode='w') as file:
        writer = csv.writer(file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Title', 'Artist', 'Nationality', 'Artist Bio', 'Culture',
                        'Era', 'Nation', 'Medium', 'Source', 'DOR', 'Image'])

        count = 1
        length = len(rows)

        async with aiohttp.ClientSession(connector=conn, headers=headers) as session:
            tasks, rows_traversed = [], 0
            for row in rows:
                pause = False
                if rows_traversed > 50:
                    pause, rows_traversed = True, 0
                task = asyncio.ensure_future(csv_processor(
                    row=row, pause=pause, session=session, writer=writer, count=count, length=length))
                tasks.append(task)
                count += 1
                rows_traversed += 1
            await asyncio.gather(*tasks, return_exceptions=True)


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

    with open(filename, mode='w') as file:
        writer = csv.writer(file, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Title', 'Artist', 'Natiionality', 'Artist Bio', 'Culture', 'Era', 'Gender', 'Nation', 'Medium', 'Source', 'DOR', 'Image'])

        print(colored('[LOG]', 'blue'), f'{filename} created')

        async with aiohttp.ClientSession(connector=conn, headers=headers) as session:
            tasks, rows_traversed = [], 0
            for row in rows:
                pause = False
                if rows_traversed > 55:
                    pause, rows_traversed = True, 0
                task = asyncio.ensure_future(csv_processor(
                    row=row, session=session, pause=pause, desired_data=desired_data, writer=writer))
                tasks.append(task)
                rows_traversed += 1
            await asyncio.gather(*tasks, return_exceptions=True)
            