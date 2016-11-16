"""Tagger Server"""

import argparse
import os
import flask
from flask import Flask
from flask import request, current_app
from flask.json import JSONEncoder
import optparse
import time
import sys, getopt, io

from tagger import Tagger

app = Flask(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # see http://flask.pocoo.org/docs/0.10/config/

tagger = Tagger()
tagger.add_name("shpendm", "-111", "123")  # stub when testing
tagger.add_name("p511", "-12", "1234")  # stub when testing
tagger.load_global("dics/tagger_global.tsv") #tagger_global  #dics/worm_global
tagger.load_names("dics/tagger_entities.tsv", "dics/tagger_names.tsv") #worm_entities, worm_names
# TODO perhaps add groups

# -----------------------------------------------------------------------------------

def matches_to_simple_json(matches):
    """
    Example

    in: [(0, 5, ((1, '1'),))]
    out: {"entities": [{"end": 7, "entities": [{"id": "shpendmahmuti", "type": 1}], "start": 0}]}
    """

    return {'entities': [{'start': x[0], 'end': x[1]+1, 'entities': [{'type': e[0], 'id': e[1]} for e in x[2]]} for x in matches]}

# -----------------------------------------------------------------------------------

@app.route('/annotate', methods=['GET', 'POST'])
def annotate(entity_types=None, text=None):
    print request.args.get('entity_types') #example "-111" or "-111,2,15" etc (numbers)
    print request.args.get('text') #example "shpendm", "shpen-dm", "SHpend-m", "-shpend-m", ".SH-pendm" etc.  ("sh.pendm", "shpendm-" shpendmm" return empty result)

    # basically anything separated by a space before or after the correct text is tagged and the position is noted
    # example: sadasd.-SHp-endm%20eshte is tagged. the result is: {"entities":[{"end":16,"entities":[{"id":"123","type":-111}],"start":8}]}
    #test case: http://localhost:5000/annotate?entity_types=10090,9606,1856129&text=p53%20dhe%20.p53%20dhe%20P53.1%20dhe%20P5-3%20dhe%20-p53%20and%20nucleus%20and%20human
    text = request.args.get('text')
    entity_types = request.args.get('entity_types')
    text = str(text)
    entity_types = str(entity_types)

    if text is None:
        text = request.args.get('text')
    if text is None:
        text = request.form['text']

    document_id_stub = 1
    entity_types = set([int(x) for x in entity_types.split(",")])

    matches = tagger.get_matches(text, document_id_stub, entity_types, auto_detect=True, protect_tags=False)
    json = matches_to_simple_json(matches)

    try:
        json = flask.jsonify(json)
	json.status_code = 200
    except RuntimeError as e:
        if str(e) == 'working outside of application context':
            pass
        else:
            raise

    return json

if __name__ == '__main__':
    parser = optparse.OptionParser(usage="python server.py -p ")
    parser.add_option('-p', '--port', action='store', dest='port', help='The port to listen.')
    (args, _) = parser.parse_args()
    if args.port == None:
        print "Missing required argument: -p/--port"
        sys.exit(1)

    app.run(host='0.0.0.0', port=int(args.port), debug=False)
