import time
from typing import NoReturn
from utils import csv_traverse, create_new_csv, rjk_processor
import asyncio




def rjk() -> NoReturn:

    source = 'RJK'
    original_file = '../rijk/202001-rma-csv-collection.csv'
    key_object_type_terms = ['schilderij']

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

    print(len(csv_rows))
    print('--------------------------------------')
    start = time.time()
    asyncio.run(create_new_csv(filename='rjk.csv',
                rows=csv_rows, desired_data=desired_rjk_data, csv_processor=rjk_processor))
    end = time.time()
    print(f'searched {len(csv_rows)} links in {end - start} seconds')


if __name__ == '__main__':
    rjk()