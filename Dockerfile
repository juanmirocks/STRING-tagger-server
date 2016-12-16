# Base container while inheriting work from larsjuhljensen/tagger#
# VERSION       1
# For testing: "worm_dictionary.tar.gz", "tagger_dictionary.tar.gz"

FROM larsjuhljensen/tagger
LABEL authors="Juan Miguel Cejuela (@juanmirocks), Shpend Mahmuti (shpendmahmuti@gmail.com)"

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
RUN pip install pandas

ENV DICS_NAME="tagger_dictionary.tar.gz"
ENV DICS_URL="http://download.jensenlab.org/$DICS_NAME"
ENV DICS_DIR="/app/tagger/dics/"

RUN mkdir -p ${DICS_DIR}
RUN wget ${DICS_URL}
RUN tar xvzf ${DICS_NAME} -C dics/

WORKDIR /app/tagger/

# download all directories for uniprot id mapping
WORKDIR /app/tagger/
COPY links.txt /app/tagger/.
RUN wget -c -i /app/tagger/links.txt
RUN gunzip *.gz

COPY server.py ${WORKDIR}
COPY testServer.py ${WORKDIR}

WORKDIR /app/tagger/

EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["server.py", "-p 5000"]
#CMD ["test_server.py"]
