# STRING-tagger-server

[STRING tagger](https://bitbucket.org/larsjuhljensen/tagger) **dockerized** as a **REST API**.

* Features:

  * Docker image directly depends on original [Docker image (larsjuhljensen/tagger)](https://hub.docker.com/r/larsjuhljensen/tagger/)
  * This new image **contains the STRING dictionaries**
  * REST API
  * **Fast annotation** of individual or small document-texts:
    * original image expects big batches and thus ignores the initial time-consuming loading of the heavy dictionaries),
    * this new image loads the dictionaries only once and keeps them in memory through the REST API web server
  * **Mapping of STRING ids to UniProt ids**


# Installation & Running

0. Clone this repository
0. Build: `docker build -t tagger .`
0. Run: `docker run -p 5000:5000 tagger` (uses STRING dictionaries)
0. (optionally) run with your dictionaries: `docker run -p 5000:5000 -v ${your_dics_folder}:/app/tagger/dics tagger`


# Development

## Run general tests

```shell
docker run -p 5000:5000 tagger test_server.py
```

## Other texts

```
# Have ids=default (not given) and have autodetect=default (not given)
curl -H "Content-type: application/json" -X POST http://127.0.0.1:5000/annotate/post -d '{"text":"Brachydanio rerio  or danio rerio have aldh9a1a and ab-cb8"}'

# Specify ids and autodetect=False
curl -i -H "Content-Type: application/json" -X POST http://localhost:5000/annotate/post -d '{"ids":"-22,9606","text":"p53 mouse tp53","autodetect":"False"}'

# Specify ids and have autodetect=default (not given)
curl -i -H "Content-Type: application/json" -X POST http://localhost:5000/annotate/post -d '{"ids":"-22,10090","text":"p53"}'

```

# Required software

0. Install docker from [docker website](https://docs.docker.com/)
0. Check whether it is working by following their instructions (simple tests needed)
0. (optionally) on Linux, create an admin terminal in order to avoid giving permissions all the time (simplifies the work)
