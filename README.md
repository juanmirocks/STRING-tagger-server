# STRING-tagger-server

[STRING tagger](https://bitbucket.org/larsjuhljensen/tagger) **dockerized** as a **REST API**.

* Features:

  * Docker image directly depends on original [Docker image (larsjuhljensen/tagger)](https://hub.docker.com/r/larsjuhljensen/tagger/)
  * This new image **contains the STRING dictionaries**
  * REST API
  * **Fast annotation** of individual or small document-texts:
    * original image expects big batches and thus ignores the initial time-consuming operation such as loading of the heavy dictionaries,
    * this new image loads the dictionaries through the REST API web server only once and keeps them in memory 
  * **Mapping of STRING ids to UniProt ids**
  * **Provides response in JSON format for the given post requests**


# Required software

0. Install docker from [docker website](https://docs.docker.com/engine/installation/)
0. Check whether it is working by following their instructions (simple tests needed)
0. (optionally) on Linux, create an admin terminal in order to avoid giving permissions all the time (simplifies the work)
0. For docker related commands, you can refer to the following [docker cheat sheet](https://github.com/wsargent/docker-cheat-sheet)


# Installation & Running

0. Clone this repository: git clone https://github.com/juanmirocks/STRING-tagger-server.git
0. Go to the corresponding dictionary where the Dockerfile is present
0. Build the image from the Dockerfile: `docker build -t tagger .`
0. Run the docker container: `docker run -p 5000:5000 tagger` (uses STRING dictionaries)
0. (optionally) run with your dictionaries: `docker run -p 5000:5000 -v ${your_dics_folder}:/app/tagger/dics tagger`
0. Check whether the server is running: `localhost:5000/ should display a 'Wellcome' message`


# Supported organisms and their [taxonomy ids](http://www.uniprot.org/taxonomy/):

0. Mus musculus(Mouse) with taxonomy id: **10090**
0. Homo sapiens(Human) with taxonomy id: **9606**
0. Arabidopsis thaliana(Mouse-ear cress) with taxonomy id: **3702**
0. Schizosaccharomyces pombe (Fission yeast) with taxonomy id: **4896**
0. Saccharomyces cerevisiae (Baker's yeast) with taxonomy id: **4932**
0. Escherichia coli str. K-12 substr. MG1655 with taxonomy id: **511145**
0. Caenorhabditis elegans with taxonomy id: **6239**
0. Drosophila melanogaster (Fruit fly) with taxonomy id: **7227**
0. Danio rerio (Zebrafish) (Brachydanio rerio) with taxonomy id: **7955**
0. Rattus norvegicus (Rat) with taxonomy id: **10116** (*currently there is no file for conversion to uniprot Id for this organism*)


## Sample Runs

```shell
# Have ids=default (not given) and have autodetect=default (not given)
curl -H "Content-type: application/json" -X POST http://127.0.0.1:5000/annotate/post -d '{"text":"Brachydanio rerio  or danio rerio have aldh9a1a and ab-cb8"}'

# Specify ids and autodetect=False
curl -i -H "Content-Type: application/json" -X POST http://localhost:5000/annotate/post -d '{"ids":"-22,9606","text":"p53 mouse tp53","autodetect":"False"}'

# Specify ids and have autodetect=default (not given)
curl -i -H "Content-Type: application/json" -X POST http://localhost:5000/annotate/post -d '{"ids":"-22,10090","text":"p53"}'
```


# Development

## Run general tests

```shell
docker run -p 5000:5000 tagger test_server.py
```
