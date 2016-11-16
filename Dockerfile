# Base container while inheriting work from larsjuhljensen/tagger#
# VERSION       1
# For testing: "worm_dictionary.tar.gz", "tagger_dictionary.tar.gz"

FROM larsjuhljensen/tagger
MAINTAINER shpendmahmuti@gmail.com

RUN yum -y update && \
	yum -y install wget && \
	yum -y install tar && \
	yum clean all

RUN yum -y install epel-release && yum clean all
RUN yum -y install python-pip && yum clean all

WORKDIR /app/tagger/

# pip install app requirements
COPY requirements.txt /app/tagger/.
RUN pip install -r /app/tagger/requirements.txt

ENV DICS_NAME="tagger_dictionary.tar.gz"
ENV DICS_URL="http://download.jensenlab.org/$DICS_NAME"
ENV DICS_DIR="/app/tagger/dics/"

RUN mkdir -p ${DICS_DIR}
RUN wget ${DICS_URL}
RUN tar xvzf ${DICS_NAME} -C dics/

COPY server.py ${WORKDIR}
COPY testServer.py ${WORKDIR}

EXPOSE 5000
ENTRYPOINT ["python", "/app/tagger/server.py"]
