# STRING-tagger-server


#### Here we are trying to develop a way to use tagging through the web. The idea is to  use dockers and a server and to allow people to input their documents or maybe to directly type the part they want it tagged. Below is documented the work and potential directions while developing.

### First part [Get the dockerfile and build the docker image]:
#### 1. docker pull larsjuhljensen/tagger
#### 2. docker build -t larsjuhljensen/tagger .  [We put the Dockerfile in a folder and build that folder that contains the Dockerfile]
#### 3. Run the docker [this is done via a python software]

### Second part [Run the docker image with arguments]:
#### 1. Execure python runDocker.py arg1 arg2 arg3 arg4 arg5
##### 1.1 Example: python runDocker.py /home/shpend/Desktop/test/larsjuhljensen/tagger/data test_types.tsv test_entities.tsv test_names.tsv test_documents.tsv
##### 1.2 This simulates this command:
	docker run --volume /home/shpend/Desktop/test/larsjuhljensen/tagger/data:/data larsjuhljensen/tagger --types=test_types.tsv --entities=test_entities.tsv --	names=test_names.tsv --documents=test_documents.tsv >output_file.csv

### Third part [Get the CSV file content and post it on the web (here localhost)]:
#### 1. After installing flask and flask-restful, to run the flask app, you need this:
	python runAndShowResults.py
#### 2. You can find the results on localhost:5001
#### 3. There, you can find a button to get the CSV file and one to show the results or appearance on web

### Fourth part [Parameters for running runDocker to be given in web]:
#### 1. The user choses 5 parameters
#### 2. Those parameters are passed and runDocker.py is run in commandline
#### 3. The file output_file.csv is created
#### 4. The content is put on web

### Fifth part [put the code in one part and simplify it] (not complete)
#### 1. Remove runDocker.py and put its content to runAndShowResults.py
#### 2. Allow user to add text to test files and modify them from web
#### 3. Dockerize the python part


Available for testing:

http://localhost:5001/

http://localhost:5000/results
