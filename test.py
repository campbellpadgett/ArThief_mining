from typing import Callable, Dict, List, NoReturn
import csv 
import time
import glob
import json
from termcolor import colored

artwork_types_folder = '/Users/campbellpadgett/Downloads/artic-api-data/json/artwork-types'


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
    print(colored('[LOG]', 'blue'), len(artwork_files), f'files inside directory')
    new_painting_count = url_count = 0

    with open('chi.csv', mode='w') as file:
        writer = csv.writer(file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Title', 'Artist', 'Natiionality', 'Artist Bio',
                        'Era', 'Medium', 'Source', 'Image Small', 'Image Large'])

        print(colored('[LOG]', 'blue'), f'{"chi.csv"} created')

        for artwork_file in artwork_files:
            row = file_explorer(artwork_file, chi_url_generator)
            url_count += 1

            if row is not None:
                writer.writerow(row)
                new_painting_count += 1
                print(colored('[COUNT]', 'yellow'), f'{len(artwork_files) - url_count} files left')

    end = time.time()
    print(colored('[COMPLETE]', 'green'),
          f'searched and extracted {len(artwork_files)} files in {end - start} seconds, {new_painting_count} new urls')


# if __name__ == '__main__':


#     # ts = Translator()
#     # trans = ts.translate('hello', src='en', dest='ko').text()
#     # print(colored('[LOG]', 'blue'), 'length of csv_rows: ', len(csv_rows))
#     print(colored('[START]', 'green'))
    # print('--------------------------------------')
    # main()
    # asyncio.run(create_tanslated_csv(filename='rjk_translated.csv',
    #             rows=csv_rows, csv_processor=translate_processor))
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(create_tanslated_csv)
    # print(colored('[COMPLETE]', 'green'), f'searched and extracted {len(csv_rows)} links in {end - start} seconds')


# if __name__ == '__main__':

#     # a = ['a', 'b', 'c']
#     # print(get_row_indicies(a))

#     # key_terms = ['Paintings', 'Paintings-Decorative']
#     # csv_traverse('../MET/MetObjects.csv', key_terms, 'MET')

#     source = 'RJK'
#     # original_file = '../MET/MetObjects.csv'
#     original_file = '../rijk/202001-rma-csv-collection.csv'
#     key_object_type_terms = ['schilderij']
#     # desired_met_data = {
#     #     'title': 9,
#     #     'artist': 18,
#     #     'artist_nationality': 22,
#     #     'artist_display_bio': 19,
#     #     'culture': 10,
#     #     'era': 11,
#     #     'gender': 25,
#     #     'nation': 38,
#     #     'medium': 31,
#     #     'source': 50,
#     #     'date_of_release': 28,
#     #     'image_link': 4
#     # }

#     desired_rjk_data = {
#         'title': 9,
#         'artist': 18,
#         'artist_nationality': 22,
#         'artist_display_bio': 19,
#         'culture': 10,
#         'era': 11,
#         'gender': 25,
#         'nation': 38,
#         'medium': 31,
#         'source': 50,
#         'date_of_release': 28,
#         'image_link': 4
#     }

#     # csv_rows = csv_traverse(original_file, key_object_type_terms, source)

#     print(colored('[START]', 'green'))

#     csv_rows = []
#     with open('rjk.csv') as csv_file_opened:
#         print(colored('[LOG]', 'blue'), 'opened rjk.csv')
#         csv_reader = csv.reader(csv_file_opened, delimiter=',')
#         count = 0
#         for row in csv_reader:
#             if count == 0:
#                 count += 1
#                 continue
#             csv_rows.append(row)

#     print(colored('[LOG]', 'blue'), len(csv_rows), 'rows to be processed')
#     print('--------------------------------------')
#     start = time.time()
#     # asyncio.run(create_new_csv(filename='rjk.csv',
#     #             rows=csv_rows, desired_data=desired_rjk_data, csv_processor=rjk_processor))
#     asyncio.run(create_tanslated_csv(filename='rjk_translated.csv',
#                 rows=csv_rows, csv_processor=translate_processor))
#     end = time.time()
#     print('--------------------------------------')
#     print(colored('[COMPLETE]', 'green'),
#           f'translated {len(csv_rows)} links in {end - start} seconds')
