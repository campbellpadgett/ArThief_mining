from cgi import test
import csv
from typing import NoReturn
from utils import csv_traverse
from requests import get




def met() -> NoReturn:

    source = 'MET'
    original_file = '../MET/MetObjects.csv'
    key_object_type_terms = ['Paintings', 'Paintings-Decorative']

    artworks = csv_traverse(original_file, key_object_type_terms, source)

    

    # test_artwork = artworks[0]

    test_artwork = ['2009.224', 'False', 'True', 'True', '35155', '374', 'Arms and Armor', '2009', 'Painting', 'Guidobaldo II della Rovere, Duke of Urbino (1514–1574), With his  Armor by Filippo Negroli', 'Italian', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'ca. 1580–85', '1555', '1610', 'Oil on copper', '5 1/2 x 4 in. (14 x 10.2 cm); frame: 7 1/8 x 4 7/8 in. (18.1 x 12.5 cm)', 'Purchase, Arthur Ochs Sulzberger Gift, 2009', '', '', '', '',
                    '', '', '', '', '', '', '', 'Paintings', '', 'http://www.metmuseum.org/art/collection/search/35155', 'https://www.wikidata.org/wiki/Q56042443', '', 'Metropolitan Museum of Art, New York, NY', 'Armor|Men|Portraits', 'http://vocab.getty.edu/page/aat/300226591|http://vocab.getty.edu/page/aat/300025928|http://vocab.getty.edu/page/aat/300015637', 'https://www.wikidata.org/wiki/Q20793164|https://www.wikidata.org/wiki/Q8441|https://www.wikidata.org/wiki/Q134307']
    

    # for idx in range(len(test_artwork)):
    #     print(test_artwork[idx], idx)

    object_id = test_artwork[4]
    res = get(f'https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}')

    primaryImage, primaryImageSmall = res.json()['primaryImage'], res.json()['primaryImageSmall']

    print(primaryImage, primaryImageSmall)

    




if __name__ == '__main__':
    met()
