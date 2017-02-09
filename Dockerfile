FROM larsjuhljensen/tagger

LABEL version="1.0.0"
LABEL authors="Juan Miguel Cejuela (@juanmirocks)"

#
# Basic
#

# RUN yum -y update -- This line shows problems in some versions of docker
RUN yum -y install wget && \
	yum -y install tar && \
	yum clean all

# Shpend: epel_release is used for gpg keys when installing python (it creates problems sometimes in centOs system based on larstagger). It didn't work without it
RUN yum -y install epel-release && yum clean all
RUN yum -y install python-pip && yum clean all

ENV TAGGER_DIR="/app/tagger"

#
# Download first all dictionaries: this is slow, therefore last images should have them already for speedier developing
#

ENV TAGGER_DICS_NAME="tagger_dictionary.tar.gz"
ENV TAGGER_DICS_URL="http://download.jensenlab.org/$TAGGER_DICS_NAME"
ENV TAGGER_DICS_DIR="${TAGGER_DIR}/tagger_dics/"
RUN mkdir -p ${TAGGER_DICS_DIR}
WORKDIR ${TAGGER_DICS_DIR}
RUN wget ${TAGGER_DICS_URL}
RUN tar xvzf *.tar.gz

# Dictionaries for stringID to uniprotID mapping
ENV MAPPING_DICS_DIR="${TAGGER_DIR}/mapping_dics/"
WORKDIR ${MAPPING_DICS_DIR}
COPY links.txt .
RUN wget -c -i links.txt
RUN gunzip *.gz

#
# Now install the app
#

WORKDIR ${TAGGER_DIR}
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY server.py .
COPY test_server.py .

RUN python test_server.py

EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["server.py", "-p 5000"]
