# Base container while inheriting work from larsjuhljensen/tagger
#
# VERSION       1

FROM larsjuhljensen/tagger
MAINTAINER shpendmahmuti@gmail.com

RUN yum -y update && \
	yum -y install wget && \
#	yum -y install tar.x86_64 && \
	yum -y install tar && \
	yum clean all

RUN yum -y install epel-release && yum clean all
RUN yum -y install python-pip && yum clean all
RUN yum -y install make g++ swig libboost-regex-dev mercurial openssh openssh-client python35 markdown

WORKDIR /app/tagger/

# pip install app requirements
COPY requirements.txt /app/tagger/.
RUN pip install -r /app/tagger/requirements.txt
#RUN pip install markdown

ENV APP="/tagger"
ENV DICS_NAME="worm_dictionary.tar.gz"
ENV DICS_URL="http://download.jensenlab.org/$DICS_NAME"
ENV DICS_DIR="/tagger/dics/"


RUN mkdir -p /app/tagger/dics/
RUN wget ${DICS_URL}
RUN tar xvzf ${DICS_NAME} -C dics/
RUN ls
RUN pwd


COPY server.py /app/tagger/server.py
RUN ls

COPY Makefile /app/tagger/Makefile

WORKDIR /app/tagger
RUN make

EXPOSE 5000
ENTRYPOINT ["python", "/app/tagger/server.py", "-p 5000"]
