import argparse
from os import path
from system import exit
from cohesion_analyser import CohesionAnalyzer


if __name__ == '__main__':
    '''
    Call this program to analyse just one essay file 
    '''
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='Essay file that contains the text to be analysed')
    args = parser.parse_args()

    if path.isfile(args.input):
        try:
            linhas_arq = []
            with open(args.input, 'r') as f:
                linhas_arq = f.readlines()

            texto = "\n".join(linhas_arq)
        except IOError:
            print(f"Error trying to open file {args.input}")

        # Call cohesion analyzer
        cohesion_analyzer = CohesionAnalyzer()

        # Get the results
        cohesion_analyzer.analyze(texto)
        cohesion_analyzer.results()

    else:
        print("Invalid path for input file")
        exit(0)
