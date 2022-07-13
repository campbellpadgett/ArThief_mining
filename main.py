from utils import chi_processor
from rjk import rjk
from met import met
from logger import start_msg











def main():

    start_msg('CHI: 1, MET: 2, or RJK: 3')
    source = input('Which source will we convert? ')
    
    if source == '1':
        chi_processor()
    elif source == '2':
        met()
    elif source =='3':
        rjk()
    else:
        raise Exception('input was either not entered or had additional digits')



if __name__ == '__main__':
    main()