# CCScore requirements
# Executa um gateway Java-Python
# que permite utilizar a implementação do CoGrOO
# feita em Java, por meio de chamadas do Python


COGROO_DIR=${1:-"/home/willian/desenv/master/ccscore/cogroo"}

#nohup java -cp ../cogroo/CogrooAPI.jar br.ufpr.cogroo.CogrooPythonInterface &
nohup java -cp $COGROO_DIR/CogrooAPI.jar br.ufpr.cogroo.CogrooPythonInterface &

