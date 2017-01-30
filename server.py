"""Tagger Server"""

import argparse
import os
import flask
from flask import Flask
from flask import request, current_app, json
from flask.json import JSONEncoder
import optparse
import time
import sys, getopt, io
import csv
import json
from collections import OrderedDict
import re

from tagger import Tagger

# -----------------------------------------------------------------------------------

app = Flask(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # see http://flask.pocoo.org/docs/0.10/config/

REVIEWED_UNIPROT_2_STRING_DATE = '04_2015'

tagger = Tagger()

# loads the corresponding data
tagger.load_global("dics/tagger_global.tsv")
tagger.load_names("dics/tagger_entities.tsv", "dics/tagger_names.tsv")

# -----------------------------------------------------------------------------------

# returns a dictionary that is further used for conversion to uniprotID
def matches_to_simple_json(matches):
    a_list = list()
    for a in matches:
        for e in a[2]:
            if (e[0] == -3 or e[0] == -22):
                resp = list()
                odict = OrderedDict([('id2', e[1]), ('type2', e[0])])
                resp.insert(0, odict)
            else:
                resp = list()
                odict = OrderedDict([('id', e[1]), ('type', e[0])])
                odict2 = OrderedDict([('id2', 'toreplace' + e[1]), ('type2', 'uniprot:' + str(e[0]))])
                resp.insert(0, odict)
                resp.insert(1, odict2)
            create_matching = OrderedDict([('end', a[1]), ('normalizations', resp), ('start', a[0])])
            a_list.append(create_matching)
    out = {'entities': a_list}
    return out

# -----------------------------------------------------------------------------------

# convert StringID to UniprotID
def string_id_to_uniprot_id(values):
    # find all IDs and types corresponding to them
    def find_values(id, json_repr):
        results = []

        def _decode_dict(a_dict):
            try:
                results.append(a_dict[id])
            except KeyError:
                pass
            return a_dict

        json.loads(json_repr, object_hook=_decode_dict)
        return results

    # format ids and types in a dictionary format
    def json_ids_and_types(json_text):
        # find all occurrences of ids and types
        ids1 = find_values('id', json_text)
        types1 = find_values('type', json_text)

        types = [item for item in types1 if (item != -3 or item != -22)]
        ids = [x for x in ids1 if not (x.isdigit() or x[0] == '-' and x[1:].isdigit())]

        # create a ordered dictionary with ids and types
        new_dict = OrderedDict(zip(ids, types))  # new_dict = OrderedDict(zip(ids, types))
        return (new_dict)

    # dictionary of common organisms
    common_organisms = {'10090': '10090_reviewed_uniprot_2_string.' + REVIEWED_UNIPROT_2_STRING_DATE + '.tsv',
                        '9606': '9606_reviewed_uniprot_2_string.' + REVIEWED_UNIPROT_2_STRING_DATE + '.tsv',
                        '3702': '3702_reviewed_uniprot_2_string.' + REVIEWED_UNIPROT_2_STRING_DATE + '.tsv',
                        '4896': '4896_reviewed_uniprot_2_string.' + REVIEWED_UNIPROT_2_STRING_DATE + '.tsv',
                        '4932': '4932_reviewed_uniprot_2_string.' + REVIEWED_UNIPROT_2_STRING_DATE + '.tsv',
                        '511145': '511145_reviewed_uniprot_2_string.' + REVIEWED_UNIPROT_2_STRING_DATE + '.tsv',
                        '6239': '6239_reviewed_uniprot_2_string.' + REVIEWED_UNIPROT_2_STRING_DATE + '.tsv',
                        '7227': '7227_reviewed_uniprot_2_string.' + REVIEWED_UNIPROT_2_STRING_DATE + '.tsv',
                        '7955': '7955_reviewed_uniprot_2_string.' + REVIEWED_UNIPROT_2_STRING_DATE + '.tsv',
                        'full': 'full_uniprot_2_string.' + REVIEWED_UNIPROT_2_STRING_DATE + '.tsv',
                        '10116': '10116' # there is no file for conversion to uniprotId
                        }

    # find conversion of StringID to UniprotID
    def str_to_uni(str_id, entity):
        if entity != '10116':
            with open(entity) as tsv_file:
                # Skip first line
                next(tsv_file, None)
                data = dict(enumerate(csv.reader(tsv_file, delimiter='\t')))
                for row in data:
                    if data[row][2] == str_id and data[row][1] != None:
                        return data[row][1]
        return ""

    # loop through all occurrences of ids for each type
    for i in range(0, (len(json_ids_and_types(values).keys()))):
        # get the complete filename that contains the type_name
        matching = common_organisms[str(list(json_ids_and_types(values).values())[i])]
        # find replacements of stringID with uniprotId in tsv and change values of json object
        values = values.replace('toreplace' + str(list(json_ids_and_types(values).keys())[i]),
                                str_to_uni(str(list(json_ids_and_types(values).keys())[i]), str(matching)))

    values = re.sub("id2", "id", values)
    values = re.sub("type2", "type", values)
    return (values)

# -----------------------------------------------------------------------------------

# used to test whether server is running (localhost:5000/ should display the 'Wellcome' message
@app.route('/')
def root():
    return 'Wellcome'

# -----------------------------------------------------------------------------------

# used to provide the corresponding json output for the post requests
@app.route('/annotate/post', methods=['POST'])
def annotate_post():
    entity_types = request.json.get('ids')
    if entity_types is None:
        entity_types = "-22,9606"  # default

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
    parser = optparse.OptionParser(usage="python server.py -p ")
    parser.add_option('-p', '--port', action='store', dest='port', help='The port to listen.')
    (args, _) = parser.parse_args()
    if args.port == None:
        print("Missing required argument: -p/--port")
        sys.exit(1)

    app.run(host='0.0.0.0', port=int(args.port), debug=False)
