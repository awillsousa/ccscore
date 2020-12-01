# Informacoes de instalacao e configuração
# obtidas de https://hub.docker.com/r/dbpedia/dbpedia-spotlight
# Um teste da API pode ser executado online em 
# https://www.dbpedia-spotlight.org/api/pt


# Puxa imagem de hub.docker.com
docker pull dbpedia/dbpedia-spotlight

# Cria volume para persistir modelos
docker volume create spotlight-models

