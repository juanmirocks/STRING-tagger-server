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
import pandas as pd
from collections import OrderedDict

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

# Read names from uniprot files
def tsvFilesList():
    filesList = []
    for filename in os.listdir('/app/tagger/uniprot'):
        if filename.endswith(".tsv"):
            filesList.append(filename)
            continue
        else:
            continue
    return filesList

# test json samples
json1 = '{"entities":[{"id":"ENSMUSP00000104298","type":10090},{"id":"ENSP00000269305","type":9606},{"id":"ENSMUSP00000029699","type":10090}]}'
json2 = '{"entities":[{"end":3,"entities":[{"id":"ENSMUSP00000104298","type":10090},{"id":"ENSP00000269305","type":9606}],"start":0},{"end":7,"entities":[{"id":"ENSMUSP00000029699","type":10090}],"start":4},{"end":12,"entities":[{"id":"ENSMUSP00000104298","type":10090},{"id":"ENSP00000269305","type":9606}],"start":9},{"end":16,"entities":[{"id":"ENSMUSP00000029699","type":10090}],"start":13},{"end":20,"entities":[{"id":"ENSMUSP00000104298","type":10090},{"id":"ENSP00000269305","type":9606}],"start":17},{"end":26,"entities":[{"id":"ENSMUSP00000029699","type":10090}],"start":23},{"end":31,"entities":[{"id":"ENSMUSP00000104298","type":10090},{"id":"ENSP00000269305","type":9606}],"start":27},{"end":35,"entities":[{"id":"ENSMUSP00000029699","type":10090}],"start":32},{"end":40,"entities":[{"id":"ENSMUSP00000104298","type":10090},{"id":"ENSP00000269305","type":9606}],"start":37}]}'
json3 = '{"entities":[{"end":183,"entities":[{"id":"ENSP00000358525","type":9606}],"start":180},{"end":188,"entities":[{"id":"ENSP00000431418","type":9606}],"start":184},{"end":252,"entities":[{"id":"ENSMUSP00000110115","type":10090},{"id":"ENSP00000264122","type":9606},{"id":"ENSP00000445920","type":9606}],"start":247},{"end":350,"entities":[{"id":"ENSP00000358525","type":9606}],"start":331},{"end":355,"entities":[{"id":"ENSP00000358525","type":9606}],"start":352},{"end":412,"entities":[{"id":"ENSP00000431418","type":9606}],"start":384},{"end":418,"entities":[{"id":"ENSP00000431418","type":9606}],"start":414},{"end":549,"entities":[{"id":"ENSP00000358525","type":9606}],"start":546},{"end":554,"entities":[{"id":"ENSP00000431418","type":9606}],"start":550},{"end":780,"entities":[{"id":"ENSP00000358525","type":9606}],"start":777},{"end":796,"entities":[{"id":"ENSP00000431418","type":9606}],"start":792},{"end":821,"entities":[{"id":"ENSP00000358525","type":9606}],"start":818},{"end":839,"entities":[{"id":"ENSP00000431418","type":9606}],"start":835},{"end":878,"entities":[{"id":"ENSMUSP00000110115","type":10090},{"id":"ENSP00000264122","type":9606},{"id":"ENSP00000445920","type":9606}],"start":873},{"end":999,"entities":[{"id":"ENSMUSP00000110115","type":10090},{"id":"ENSP00000264122","type":9606},{"id":"ENSP00000445920","type":9606}],"start":994},{"end":1013,"entities":[{"id":"ENSP00000431418","type":9606}],"start":1009},{"end":1106,"entities":[{"id":"ENSMUSP00000101471","type":10090},{"id":"ENSP00000363763","type":9606},{"id":"ENSMUSP00000023462","type":10090},{"id":"ENSP00000215832","type":9606}],"start":1103},{"end":1149,"entities":[{"id":"ENSMUSP00000110115","type":10090},{"id":"ENSP00000264122","type":9606},{"id":"ENSP00000445920","type":9606}],"start":1144},{"end":1228,"entities":[{"id":"ENSMUSP00000110115","type":10090},{"id":"ENSP00000264122","type":9606},{"id":"ENSP00000445920","type":9606}],"start":1223},{"end":1239,"entities":[{"id":"ENSP00000358525","type":9606}],"start":1236},{"end":1244,"entities":[{"id":"ENSP00000431418","type":9606}],"start":1240}]}\n'

# -----------------------------------------------------------------------------------

# convert StringID to UniprotID
def stringIDtoUniprotID(values):
    # find all IDs and types corresponding to them
    def find_values(id, json_repr):
        results = []
        def _decode_dict(a_dict):
            try: results.append(a_dict[id])
            except KeyError: pass
            return a_dict

        json.loads(json_repr, object_hook=_decode_dict)
        return results


    # format ids and types in a dictionary format
    def jsonIDsAndTypes(jsonText):
        #find all occurrences of ids and types
        ids = find_values('id', jsonText)
        types = find_values('type', jsonText)

        # create a ordered dictionary with ids and types
        new_dict = OrderedDict(zip(ids, types))
        return(new_dict)


    # dictionary of common organisms
    #dict = {'10090': 'mouse', '7955': 'else0', '9060': 'human', '3702':'else1', '4896':'else2', '4932':'else3', '511145':'else4', '6239':'else5', '7227':'else6'}


    # find conversion of StringID to UniprotID
    def StrToUni(strId, entity):
        lookup = strId
        indx = None
        with open(entity) as tsvFile:
            for num, line in enumerate(tsvFile, -1):
                if lookup in line:
                    indx = num
        df = pd.read_csv(entity, sep='\t')
        df = df.rename(columns={'#species   uniprot_ac|uniprot_id   string_id   identity   bit_score': 'col'})
        return(str(df.iloc[[indx]]).split()[1 + 1])

    # loop through all occurrences of ids for each type
    for i in range(0,(len(jsonIDsAndTypes(values).keys()))):
        # get the complete filename that contains the type_name
        matching = [s for s in tsvFilesList() if str(list(jsonIDsAndTypes(values).values())[i]) in s]
        # find replacements of stringID with uniprotId in tsv
        StrToUni(str(list(jsonIDsAndTypes(values).keys())[i]), str(matching).strip('\'[]\''))
        # change values of json object
        values = values.replace(str(list(jsonIDsAndTypes(values).keys())[i]),
                             StrToUni(str(list(jsonIDsAndTypes(values).keys())[i]), str(matching).strip('\'[]\'')))

    return(values)

# test example
#print(stringIDtoUniprotID(json3))

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

    return stringIDtoUniprotID(json)

if __name__ == '__main__':
    parser = optparse.OptionParser(usage="python server.py -p ")
    parser.add_option('-p', '--port', action='store', dest='port', help='The port to listen.')
    (args, _) = parser.parse_args()
    if args.port == None:
        print "Missing required argument: -p/--port"
        sys.exit(1)

    app.run(host='0.0.0.0', port=int(args.port), debug=False)
