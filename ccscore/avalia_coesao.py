import argparse
from os import path
from system import exit
from cohesion_analyser import CohesionAnalyzer



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='Arquivo contendo texto a ser analisado')
    args = parser.parse_args()

    if path.isfile(args.input):
        try:
            linhas_arq = []
            with open(args.input, 'r') as f:
                linhas_arq = f.readlines()

            texto = "\n".join(linhas_arq)
        except IOError:
            print("Erro")

        # Call cohesion analyzer
        cohesion_analyzer = CohesionAnalyzer()

        # Get the results
        cohesion_analyzer.analyze(texto)
        cohesion_analyzer.results()

    else:
        print("Caminho inválido para o arquivo de entrada")
        exit(0)
