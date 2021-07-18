# ccscore
Avaliador automático de coesão para o Português.

Este repositório traz os códigos utilizados na dissertação Avaliação e Valoração Automática da Coesão de Textos Dissertativos.

Diretórios:

- ccscore: código do avaliador de coesão
- cogroo: ferramenta CoGrOO de correção ortográfica e gramatical, executada em modo servidor. (https://github.com/cogroo/cogroo4)
- CORP: ferramenta CORP de resolução de correferências executada em modo desktop (https://www.inf.pucrs.br/linatural/wordpress/recursos-e-ferramentas/corp-coreference-resolution-for-portuguese/)
- dicionários: dicionário testados para busca de palavras
- examples: exemplos de utilização da ferramenta
- experimentos: notebook ipython com as etapas de execução dos experimentos
- notebooks: noteboks ipython de caráter mais genérico, com tarefas como criação e organização da base de textos
- scripts: scripts shell de execução de ferramentas externas como o CoGrOO e o container da DBSpedia Spotlight

Para criar o ambiente de execução:

* usando pip: pip install -r requirements.txt

* usando conda: conda env create -f environment.yaml



Citações:

CORP: 

E. B. Fonseca, V. Sesti, A. Antonitsch, A. A. Vanin, and R. Vieira. Corp – uma abordagem baseada em regras e conhecimento semântico para a resolução de correferências. Linguamatica, 9(1):3–18, 2017

CoGrOO:

KINOSHITA, Jorge; SALVADOR, L. d N.; MENEZES, C. E. D. Cogroo–um corretor gramatical para a língua portuguesa, acoplável ao openoffice. In: Proc. of Latin American Informatics Conf., Cali, Colombia. 2005. p. 53.


