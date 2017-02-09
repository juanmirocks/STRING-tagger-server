import os
import argparse
import flask
from flask import Flask
from flask import request, current_app, json
from flask.json import JSONEncoder
import glob
import json
import time

from tagger import Tagger

# -----------------------------------------------------------------------------------

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # see http://flask.pocoo.org/docs/0.10/config/

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
    tagger = Tagger()
    tagger.load_global("tagger_dics/tagger_global.tsv")
    tagger.load_names("tagger_dics/tagger_entities.tsv", "tagger_dics/tagger_names.tsv")
    mapping_dics = parse_mapping_dics()


init()


# -----------------------------------------------------------------------------------

@app.route('/')
def root():
    return 'Welcome'


# used to provide the corresponding json output for the post requests
@app.route('/annotate', methods=['POST'])
def annotate():


    entity_types = request.json.get('ids')
    if entity_types is None:
        entity_types = "-22,9606"  # default (used to recognize localization_id and uniprot_id)
        # to include organism_id in defaults add "-3" in entity_types

    text = json.dumps(request.json.get('text'))

    auto_detect = request.json.get('autodetect')
    if auto_detect is None or auto_detect != "False":
        auto_detect = True
    else:
        auto_detect = False

    document_id_stub = 1
    entity_types = set([int(x) for x in entity_types.split(",")])

    # uses the tagger wrapper from lars' tagger to get the matches' information
    matches = tagger.get_matches(text, document_id_stub, entity_types, auto_detect, protect_tags=False)
    json_out = matches_to_simple_json(matches)
    json_out = json.dumps(json_out)
    json_out = json_out.replace("'", '"')
    json_out = string_id_to_uniprot_id(json_out)
    json_out = json.loads(json_out)

    try:
        json_out = flask.jsonify(json_out)
        json_out.status_code = 200
    except RuntimeError as e:
        if str(e) == 'working outside of application context':
            pass
        else:
            raise

    return json_out

# -----------------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Annotate mentions in text of proteins, subcellular localizations, and organisms')
    parser.add_argument('--port', '-p', type=int, required=True, default=5000, help='The port for the REST server to listen to.')
    (args, _) = parser.parse_args()

    app.run(host='0.0.0.0', port=args.port, debug=False)
