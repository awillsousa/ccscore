# ccscore

##Avaliador Automático de Coesão

Este programa foi desenvolvido como parte do trabalho de mestrado, Avaliação Automática de Coesão Textual, desenvolvido por A. Willian Sousa para o Programa de Pós-graduação em Informática (PPgInf) da Universidade Federal do Paraná (UFPR).

##Funcionamento

O programa determina um valor de coesão em uma escala de 0-2, considerando os elementos coesivos, entidades e cadeias de referências encontradas no texto. 

A etiquetagem dos textos, utilizados nos experimentos, foi feita por meio da biblioteca Spacy (versão 2.3.1) e do parser PALAVRAS. A principal utilização do PALAVRAS, foi para obtenção de rótulos semânticos para os elementos constituintes dos textos. 

### Informações das pastas

#### ccscore
Aqui está o código-fonte do software de avaliação de coesão.

#### dicionários
Aqui temos dois objetos contendo listas de palavras e suas funções. A palavras e funções foram obtidas dos dicionários disponibilizados pelos Projeto Unitex-PB ( http://www.nilc.icmc.usp.br/nilc/projects/unitex-pb/web/dicionarios.html). 

Foram criados dois objetos:

<ul>
<li>Um dicionário (OrderedDict): usando a palavra como chave, contendo dados de forma canônica, função, flexão, gênero, número  e pessoa</li>
<li>Uma lista (List): contêm apenas as palavras</li>
</ul>

O uso desses objetos dessa forma, exigem uma boa quantidade de memória para que possam ser carregados em memória; mais de  GB.

#### docs

Documentaçã do software

#### examples

Exemplos de uso do ccscore

#### notebooks

Vários arquivos de Jupyter Notebooks (.ipynb), contendo os passos para a realização de atividades como obtenção da base de redações, criação de base de conhecimento, exportação da base de redações, correção e análise de textos, dentre outros. 

#### scripts

Scripts bash para execução de tarefas. 

#### experimentos

Contém as informações e os resultados dos experimentos realizados na dissertação. Um bom local para inciar se o objetivo for reproduzir os experimentos do trabalho de mestrado.

### Avaliação Automática

< INSERIR COMANDO PARA EXECUTAR A AVALIAÇÃO DE UM TEXTO >

### Ferramentas Utilizadas

Para conseguir executar cada uma das etapas do processo de avaliação de coesão, várias ferramentas, estudos, projetos e recursos foram utilizados, de forma total ou parcial. 

<ul>
<li>Spacy</li>
<li>Parser PALAVRAS</li>
<li>Dicionários Unitex-PB</li>
<li>Corretor Ortográfico CoGrOO</li>
<li>CORP para anotação de correferências</li>
<li>OpenWordNet-PT</li>
<li>spacy-ann-linker</li>
<li>stanford-corenlp</li>
<li>Biblioteca de Inferência Infernal</li>
</ul>


### Como citar este trabalho


### Contato


