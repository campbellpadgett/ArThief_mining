import csv
import time
from datetime import datetime
from typing import NoReturn
from utils import csv_traverse, create_new_csv
import asyncio





def met() -> NoReturn:

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

    artworks = csv_traverse(original_file, key_object_type_terms, source)
    
    print('--------------------------------------')
    print(len(artworks[:26]))
    
    start = time.time()
    asyncio.run(create_new_csv(filename='met.csv', rows=artworks, desired_data=desired_met_data))
    end = time.time()

    print('--------------------------------------')
    print(f'Wrote {len(artworks[:26])} new rows in {end - start} seconds')




if __name__ == '__main__':
    met()
