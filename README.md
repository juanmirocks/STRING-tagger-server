# STRING-tagger-server


#### Here we are trying to develop a way to use tagging through the web. The idea is to  use dockers and a server and to allow people to input their documents or maybe to directly type the part they want it tagged. Below is documented the work and potential directions while developing.

### Understanding the work:
#### 1. from larsjuhljensen/tagger we created a new dockerfile
#### 2. The dockerfile is adapted to our needs and it downloads the correct data (currently using worm_data for testing)
#### 3. Included requirements.txt in the dockerfile which can be modified when we need to modify it
#### 3. Copied a new server.py and Makefile in the right directory
#### 4. Do the tests and check the results

### Modifying the work so that all the parameters can be given directly through the web (still working):
#### 1. Create correct forms and re-directing
#### 2. Validate the inputs
#### 3. Validate the outputs and maybe put the output in a separate file


### Required to run the software:
#### 1. You need to install docker in https://docs.docker.com/ and choose the apprepriate one for you
#### 2. Check whether it is working by following their instructions (simple tests needed)
#### 3. Try to create a admin terminal in order to avoid giving permissions all the time (this simplifies the work)

### Running the software:
#### 1. Build: $ docker build -t tagger .
#### 2. Run: $ docker run -p 5000:5000 tagger
#### 3. Go to a browser and try:
##### 3.1 http://localhost:5000/   (in development)
##### 3.2 http://localhost:5000/annotate/1  (check a simple result)
#### 4. Optional:  docker run -ti --entrypoint bash tagger
##### 4.1 Check the files/folders of the image inside: ls
##### 4.2 Check the content inside the files/folders of the image: vim [filename]

## IN Development
