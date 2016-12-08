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
import pandas as pd
import json
from collections import OrderedDict
import re

from tagger import Tagger

app = Flask(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # see http://flask.pocoo.org/docs/0.10/config/

tagger = Tagger()
#tagger.add_name("p511", "-12", "1234")  # stub when testing
tagger.load_global("dics/tagger_global.tsv") #tagger_global  #dics/worm_global
tagger.load_names("dics/tagger_entities.tsv", "dics/tagger_names.tsv") #worm_entities, worm_names
# TODO perhaps add groups

# -----------------------------------------------------------------------------------

def matches_to_simple_json(matches):
    aList = list()
    for a in matches:
        for e in a[2]:
            if(e[0]==-3):
                resp = [{'type': e[0], 'id': e[1]}]
            else:
                resp = [{'id': e[1], 'type': e[0]}, {'id2': 'toreplace'+e[1],'type2':'uniprot:' + str(e[0])}]
            createMatching = {'start': a[0], 'end': a[1] + 1, 'normalizations': resp}
        aList.append(createMatching)

    out = {'entities': aList}
    return out

# -----------------------------------------------------------------------------------

# Read names from uniprot files
def tsvFilesList():
    filesList = []
    for filename in os.listdir('/app/tagger'): #/uniprot
        if filename.endswith(".tsv"):
            filesList.append(filename)
            continue
        else:
            continue
    return filesList

# test json samples
json1 = '{"entities":[{"id":"ENSMUSP00000104298","type":10090},{"id":"ENSP00000269305","type":9606},{"id":"ENSMUSP00000029699","type":10090}]}'
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
        ids1 = find_values('id', jsonText)
        types1 = find_values('type', jsonText)

        types = [item for item in types1 if item != -3]
        ids = [x for x in ids1 if not (x.isdigit() or x[0] == '-' and x[1:].isdigit())]

        # create a ordered dictionary with ids and types
        new_dict = OrderedDict(zip(ids, types)) #new_dict = OrderedDict(zip(ids, types))
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
        values = values.replace('toreplace'+str(list(jsonIDsAndTypes(values).keys())[i]),
                             StrToUni(str(list(jsonIDsAndTypes(values).keys())[i]), str(matching).strip('\'[]\'')))

    values = re.sub("id2", "id", values)
    values = re.sub("type2", "type", values)
    return(values)

# test example
#print(stringIDtoUniprotID(json3))

# -----------------------------------------------------------------------------------

@app.route('/annotate/post', methods=['POST'])
def annotatePost():

    text = json.dumps(request.json.get('text'))

    document_id_stub = 1
    entity_types="-22,9606" #-3,-22,9606
    entity_types = set([int(x) for x in entity_types.split(",")])

    matches = tagger.get_matches(text, document_id_stub, entity_types, auto_detect=True, protect_tags=False)
    jsonOut = matches_to_simple_json(matches)
    jsonOut = json.dumps(jsonOut)
    jsonOut = jsonOut.replace("'",'"')
    jsonOut = stringIDtoUniprotID(jsonOut)
    jsonOut = json.loads(jsonOut)

    try:
        jsonOut = flask.jsonify(jsonOut)
	jsonOut.status_code = 200
    except RuntimeError as e:
        if str(e) == 'working outside of application context':
            pass
        else:
            raise

    return jsonOut


'''

@app.route('/annotate', methods=['GET'])
def annotateGet(text=None):
    print(request.args.get('text'))

    # basically anything separated by a space before or after the correct text is tagged and the position is noted
    #test case: http://localhost:5000/annotate?text=p53%20human%20mouse%20human%20tp53
    text = request.args.get('text')
    text = str(text)

    if text is None:
        text = request.args.get('text')
    if text is None:
        text = request.form['text']

    document_id_stub = 1
    entity_types="-22,9606" #-3,-22,9606
    entity_types = set([int(x) for x in entity_types.split(",")])

    matches = tagger.get_matches(text, document_id_stub, entity_types, auto_detect=True, protect_tags=False)
    jsonOut = matches_to_simple_json(matches)
    #jsonOut ='{"entities":[{"id":"ENSMUSP00000104298","type":10090},{"id":"ENSP00000269305","type":9606},{"id":"ENSMUSP00000029699","type":10090}]}'
    jsonOut = json.dumps(jsonOut)
    jsonOut = jsonOut.replace("'",'"')
    jsonOut = stringIDtoUniprotID(jsonOut)
    jsonOut = json.loads(jsonOut)

    try:
        jsonOut = flask.jsonify(jsonOut)
	jsonOut.status_code = 200
    except RuntimeError as e:
        if str(e) == 'working outside of application context':
            pass
        else:
            raise

    return jsonOut

'''

if __name__ == '__main__':
    parser = optparse.OptionParser(usage="python server.py -p ")
    parser.add_option('-p', '--port', action='store', dest='port', help='The port to listen.')
    (args, _) = parser.parse_args()
    if args.port == None:
        print("Missing required argument: -p/--port")
        sys.exit(1)

    app.run(host='0.0.0.0', port=int(args.port), debug=False)

