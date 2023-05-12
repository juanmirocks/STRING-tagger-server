This project contains useful logic but is no longer maintained. In particular, as of 2023-05-12, [the docker image `larsjuhljensen/tagger`](https://hub.docker.com/r/larsjuhljensen/tagger/) does not exist and the [referenced dictionary URLs](mapping_files_urls.txt) do not exist either.

[For the latest developments, 👉 check the official STRING tagger repository](https://github.com/larsjuhljensen/tagger)


# STRING-tagger-server

[STRING tagger](https://bitbucket.org/larsjuhljensen/tagger) **dockerized** as a **REST API**.

* Features:

  * Docker image directly depends on original [Docker image (larsjuhljensen/tagger)](https://hub.docker.com/r/larsjuhljensen/tagger/)
  * This new image **contains the STRING dictionaries**
  * **REST API**
  * **Fast annotation** of individual or small document-texts:
    * original image expects big batches and thus ignores the initial time-consuming operation such as loading of the heavy dictionaries,
    * this new image loads the dictionaries through the REST API web server only once and keeps them in memory
  * **Mapping of STRING ids to UniProt ids**
  * Supports **Unicode**
  * Response in **JSON format**


# Prerequisites

1. [Install docker](https://docs.docker.com/engine/installation/) (for help, refer to this [docker cheat sheet](https://github.com/wsargent/docker-cheat-sheet))
1. Check with `docker info` the amount of runtime memory. Our version requires 4GB to run but, for example, Docker for Mac is set to use 2 GB runtime memory by default. This can be changed following these [instructions](https://docs.docker.com/docker-for-mac/).


# Installation & Running

1. Clone this repository: `git clone https://github.com/juanmirocks/STRING-tagger-server.git`
1. `cd` to the created folder
1. Build the image from the Dockerfile: `docker build -t tagger .`
1. Run the docker container: `docker run -p 5000:5000 tagger` (uses STRING dictionaries)
  * (optionally) run with your dictionaries: `docker run -p 5000:5000 -v ${your_dics_folder}:/app/tagger/dics tagger`
1. Check whether the server is running: `localhost:5000/ should display a 'Welcome' message`


# Supported organisms and their [taxonomy ids](http://www.uniprot.org/taxonomy/)

Proteins are tagged for these organisms:

1. Homo sapiens (Human), with NCBI Taxonomy ID: **9606**
1. Arabidopsis thaliana (Mouse-ear cress): **3702**
1. Saccharomyces cerevisiae (Baker's yeast): **4932**
1. Mus musculus (Mouse): **10090**
1. Schizosaccharomyces pombe (Fission yeast): **4896**
1. Escherichia coli str. K-12 substr. MG1655: **511145**
1. Caenorhabditis elegans: **6239**
1. Drosophila melanogaster (Fruit fly): **7227**
1. Danio rerio (Zebrafish) (Brachydanio rerio): **7955**
1. Rattus norvegicus (Rat): **10116** (*currently there is no file for conversion to uniprot Id for this organism*)


# Parameters

Parameters used when sending a post request:

* **ids**:
  * -22: used to tag subcellular localization, normalized (linked) to *GO ID*.
  * -3: used to tag organism names, normalized to *TAXONOMY ID*.
  * taxonomy id (example `9606`): used to tag proteins for the specified taxonomy id, normalized to *STRING ID* and *UNIPROT ID*.

* **autodetect**:
  * *True*:
    * When text is `tp53 mouse`, then it returns the STRING ID and UNIPROT ID for mouse, even if taxonomy id for mouse is not included in the *ids* parameter.
    * When text is `tp53`, then it only returns the STRING ID and UNIPROT ID for the specified taxonomy ids in the *ids* parameter.
  * *False*:
    * When text is `tp53 mouse`, then it returns the STRING ID and UNIPROT ID only for the specified taxonomy id in the *ids* parameter even though `mouse` is included in the *text*.
    * When text is given as `tp53`, then it returns the *STRING ID* and *UNIPROT ID* only for the specified taxonomy id in the *ids* parameter, so it gives the same response as in the previous case.

* **text**:
  * text to tag (example: `tp53 mouse`)

* **output**:
  * choose between (not documented): `simple` (default), `full`, `tagger-unicode`, `tagger-raw`

The default parameters annotate subcellular localization and all organisms' proteins found in the text, always tagging humans' proteins:

* `ids=-22, 9606`
* `autodetect=True`


### Sample Runs:

```shell

curl -H "Content-type: application/json" -X POST http://127.0.0.1:5000/annotate -d '{"text":"Brachydanio rerio or danio rerio have aldh9a1a and ab-cb8"}'

curl -i -H "Content-Type: application/json" -X POST http://localhost:5000/annotate -d '{"ids":"-22,10090","text":"p53"}'

curl -i -H "Content-Type: application/json" -X POST http://localhost:5000/annotate -d '{"ids":"-22,9606","autodetect":"False","text":"p53 mouse tp53"}'
```


# Development

## Run general tests

```shell
docker run -p 5000:5000 tagger test_server.py
```
