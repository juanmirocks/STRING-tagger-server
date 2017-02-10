import os
import argparse
import flask
from flask import request
import json
import glob
import time

from tagger import Tagger

# -----------------------------------------------------------------------------------

app = flask.Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # uglify json; http://flask.pocoo.org/docs/0.10/config/

TAGGER = None
MAPPING_DICS = None  # dictionary or organism ids (NCBI Taxonomy) to dictionary of string_ids to tuple (uniprot_ac, uniprot_id)

# -----------------------------------------------------------------------------------

def parse_mapping_dics():

    def parse_mapping_file(file_path):
        ret = {}
        with open(file_path) as f:
            next(f)  # skip header
            for line in f:
                _, uniprot, string_id, _, _ = line.split("\t")
                ret[string_id] = tuple(uniprot.split("|"))  # e.g. P31946|1433B_HUMAN
        return ret

    ret = {}

    for file_path in glob.glob("mapping_dics/*.tsv"):
        filename = os.path.basename(file_path)
        organism = filename.split("_")[0]  # note, type string

        ret[organism] = parse_mapping_file(file_path)

    return ret


def init():
    global TAGGER
    global MAPPING_DICS

    TAGGER = Tagger()

    if app.debug:
        # Keep for quick development as the tagger dictionaries take much time to load
        TAGGER.add_name("p53", 9606, "ENSP00000269305")
        TAGGER.add_name("p53", 9606, "ENSP00000269305-non-mappable")
        TAGGER.add_name("human", -3, "9606")
        TAGGER.add_name("membrane", -22, "GO:0019898")
    else:
        TAGGER.load_global("tagger_dics/tagger_global.tsv")
        TAGGER.load_names("tagger_dics/tagger_entities.tsv", "tagger_dics/tagger_names.tsv")

    MAPPING_DICS = parse_mapping_dics()


# -----------------------------------------------------------------------------------


def unicode2ascii(unicode_text):
    return unicode_text.encode('utf-8')


def ascii2unicode_offset_mappings(unicode_text):
    offsets = {}
    ascii_offset = 0  # aka, byte-based offset vs (unicode_offset == character-based offset)

    for unicode_offset, char in enumerate(unicode_text):
        offsets[ascii_offset] = unicode_offset
        ascii_offset += len(char.encode('utf-8'))

    return offsets


def tagger2simple(tagger_output, unicode_text):
    offsets = ascii2unicode_offset_mappings(unicode_text)

    ret = []
    for entity in tagger_output:
        start, end, norms = entity
        start = offsets[start]
        # the tagger defines the end as the last actual (including) character vs the more commoon (e.g. java, python) of writing the next not inclusive character (+1)
        end = offsets[end] + 1

        mapped_norms = []
        for typ, norm_id in norms:

            if typ > 0:
                # it's a protein of species type; https://bitbucket.org/larsjuhljensen/tagger
                organism = str(typ)
                mapped_norms.append({"type": "string_id:" + organism, "id": norm_id})

                organism_mapping = MAPPING_DICS.get(organism)

                if organism_mapping:
                    mapped = organism_mapping.get(norm_id)
                    if mapped:
                        uniprot_ac, uniprot_id = mapped
                        mapped_norms.append({"type": "uniprot_ac:" + organism, "id": uniprot_ac})
                        mapped_norms.append({"type": "uniprot_id:" + organism, "id": uniprot_id})

            else:
                mapped_norms.append({"type": str(typ), "id": norm_id})

        ret.append({"start": start, "end": end, "ids": mapped_norms})

    return ret

# -----------------------------------------------------------------------------------


@app.route('/')
def root():
    return 'Welcome'


@app.route('/annotate', methods=['POST'])
def annotate():

    ids = request.json.get('ids', request.args.get('ids', '9606,-22,-3'))
    ids = {int(x) for x in ids.split(",")}
    auto_detect = request.json.get('autodetect', request.args.get('autodetect', 'true'))
    auto_detect = bool(auto_detect.lower())
    output = request.json.get('output', request.args.get('output', 'simple'))
    document_id_stub = "1"
    unicode_text = request.json.get('text', request.args.get('text', None))
    if not unicode_text:
        raise AssertionError("The text to tag must be provided")
    else:
        ascii_text = unicode2ascii(unicode_text)

    matches = TAGGER.get_matches(ascii_text, document_id_stub, entity_types=ids, auto_detect=auto_detect, allow_overlap=False, protect_tags=False)

    if output == "simple":
        return flask.jsonify(tagger2simple(matches, unicode_text))

    elif output == "tagger-unicode":  # with unicode, character-based offsets
        offsets = ascii2unicode_offset_mappings(unicode_text)
        ret = [(offsets[start], offsets[end], norms) for start, end, norms in matches]
        return flask.jsonify(ret)

    elif output == "tagger-raw":  # with ascii, byte-based offsets
        return flask.jsonify(matches)


# -----------------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Annotate mentions in text of proteins, subcellular localizations, and organisms')
    parser.add_argument('--port', '-p', type=int, required=False, default=5000, help='The port for the REST server to listen to.')
    parser.add_argument('--debug', '-d', required=False, default=False, action="store_true", help='Run in debug mode')
    args = parser.parse_args()

    init()

    app.run(host='0.0.0.0', port=args.port, debug=args.debug, threaded=True)
