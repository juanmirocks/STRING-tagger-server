import os
import argparse
import flask
from flask import request
import glob
import time

from tagger import Tagger

# -----------------------------------------------------------------------------------

app = flask.Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # uglify json; http://flask.pocoo.org/docs/0.10/config/

tagger = None
mapping_dics = None  # dictionary or organism ids (NCBI Taxonomy) to dictionary of string_ids to tuple (uniprot_ac, uniprot_id)

# -----------------------------------------------------------------------------------

def parse_mapping_dics():

    def parse_mapping_file(file_path):
        ret = {}
        with open(file_path) as f:
            next(f)  # skip header
            for line in f:
                _, uniprot, string_id, _, _ = line.split("\t")
                ret[string_id] = tuple(uniprot.split("|"))
        return ret

    ret = {}

    for file_path in glob.glob("mapping_dics/*.tsv"):
        filename = os.path.basename(file_path)
        organism = int(filename.split("_")[0])

        ret[organism] = parse_mapping_file(file_path)

    return ret


def init():
    global tagger
    global mapping_dics

    tagger = Tagger()
    tagger.load_global("tagger_dics/tagger_global.tsv")
    tagger.load_names("tagger_dics/tagger_entities.tsv", "tagger_dics/tagger_names.tsv")
    mapping_dics = parse_mapping_dics()


# -----------------------------------------------------------------------------------

def tagger2simple(tagger_output):
    for entity in tagger_output:
        start, end, norms = entity

        start -= 1  # tagger is 1-indexed; we return 0-indexed

    pass


# -----------------------------------------------------------------------------------

@app.route('/')
def root():
    return 'Welcome'


@app.route('/annotate', methods=['POST'])
def annotate():

    ids = request.json.get('ids', request.args.get('ids', '9606,-22,-3'))
    ids = set([int(x) for x in ids.split(",")])
    auto_detect = request.json.get('autodetect', request.args.get('autodetect', 'true'))
    auto_detect = bool(auto_detect.tolower())
    text = request.json.get('text', request.args.get('text', Exception("The text to tag must be provided")))
    output = request.json.get('output', request.args.get('output', 'simple'))
    document_id_stub = 1

    matches = tagger.get_matches(text, document_id_stub, ids, auto_detect, protect_tags=False)

    if output == "simple":
        raise NotImplementedError

    elif output == "tagger":
        return flask.jsonify(matches)


# -----------------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Annotate mentions in text of proteins, subcellular localizations, and organisms')
    parser.add_argument('--port', '-p', type=int, required=False, default=5000, help='The port for the REST server to listen to.')
    args = parser.parse_args()

    init()

    app.run(host='0.0.0.0', port=args.port, debug=False)
