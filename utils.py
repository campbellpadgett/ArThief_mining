import csv
from typing import List, NoReturn, Tuple









def csv_traverse(csv_file: str, key_terms: List[str], source: str) -> List:

    """Used to take a csv file and filter out non-painting 
    or non-Photo related artworks, returns results"""

    traversed_csv = []
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





            
# if __name__ == '__main__':

    # a = ['a', 'b', 'c']

    # print(get_row_indicies(a))

    # key_terms = ['Paintings', 'Paintings-Decorative']

    # csv_traverse('../MET/MetObjects.csv', key_terms, 'MET')
