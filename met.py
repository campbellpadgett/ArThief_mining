import csv







# MET related 

def csv_helper(csv_file: str):

    with open(csv_file) as csv_file_opened:

        csv_reader = csv.reader(csv_file_opened, delimiter=',')
        row_number = 0
        types = {}

        key_terms = ['Paintings', 'Photographs|Prints',
                     'Paintings-Decorative', 'Photographs']

        max_rows = input('how many rows should we traverse? ')

        for row in csv_reader:

            classification = row[45]
            isPublicDomain = row[3]

            if row_number == int(max_rows):
                break

            if classification not in key_terms:
                continue

            if isPublicDomain == False:
                continue

            # idx = 0
            print(row)
            row_number += 1

            # for col in row:
            #     print(col, idx)
            #     idx += 1

            # if classification not in types:
            #     types[classification] = 0

            # types[classification] += 1


if __name__ == '__main__':
    csv_helper('MetObjects.csv')
