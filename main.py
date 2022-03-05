from chicago import chicago
from rjk import rjk
from met import met












def main():

    print('Chicago, MET, or RJK')
    source = input('Which source will we convert? ')
    
    if source == 'Chicago':
        chicago()
    elif source == 'MET':
        met()
    elif source =='RJK':
        rjk()
    else:
        raise Exception('input was either misspelled or not typed')

    pass



if __name__ == '__main__':
    main()