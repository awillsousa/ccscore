 # CCScore requirements
 # Execute the container for DBpedia Spotlight
  
 
 docker run -tid \
 --restart unless-stopped \
 --name dbpedia-spotlight.pt \
 --mount source=spotlight-models,target=/opt/spotlight/models \
 -p 2222:80 \
 dbpedia/dbpedia-spotlight \
 spotlight.sh pt  
