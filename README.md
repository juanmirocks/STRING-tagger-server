# STRING-tagger-server

Here we are trying to develop a way to use tagging through the REST API. The idea is to  use dockers and a server and to allow people to input their documents or maybe to directly type the part they want it tagged. Below is documented the work and potential directions while developing.


# Running

0. Clone this repository
0. Build: `docker build -t tagger:1.0 .`
0. Run: `docker run -p 5000:5000 tagger:1.0`
0. Or run with your own dictionaries: `docker run -p 5000:5000 -v ${your_dics_folder}:/app/tagger/dics tagger`

# Testing for text with/without ids and autodetect

```
curl -H "Content-type: application/json" -X POST http://127.0.0.1:5000/annotate/post -d '{"text":"Brachydanio rerio  or danio rerio have aldh9a1a and ab-cb8"}'

curl -i -H "Content-Type: application/json" -X POST http://localhost:5000/annotate/post -d '{"ids":"-22,9606","text":"p53 mouse tp53","autodetect":"False"}'

curl -i -H "Content-Type: application/json" -X POST http://localhost:5000/annotate/post -d '{"ids":"-22,10090","text":"p53"}'

```
# Running tests

```shell
docker run -p 5000:5000 --entrypoint bash tagger

# python testServer.py 

```

# Development

* Understanding the work:
 0. from larsjuhljensen/tagger we created a new dockerfile
 0. The dockerfile is adapted to our needs and it downloads the correct data (currently using worm_data for testing)
 0. Included requirements.txt in the dockerfile which can be modified when we need to modify it
 0. Copied a new server.py
 0. Do the tests and check the results

* Modifying the work:
 0. Validate the inputs
 0. Validate the outputs and check correctness

* Added unit tests and changed the way the queries are done:
 0. Specify what you want tagged
 0. Validate the inputs in tests
 0. Automated tests can be run in order to stabilize the software against failures when changing methods


# Required to run the software:
 0. You need to install docker in [docker website](https://docs.docker.com/) and choose the apprepriate one for you
 0. Check whether it is working by following their instructions (simple tests needed)
 0. Try to create a admin terminal in order to avoid giving permissions all the time (this simplifies the work)
