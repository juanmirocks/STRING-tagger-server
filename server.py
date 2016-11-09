"""Tagger Server"""

import argparse
import os

import flask
import markdown
from flask import Flask
from flask import request, current_app
from flask.json import JSONEncoder
import optparse
import time
import sys, getopt, io
from flask import render_template
from flask import Markup

from tagger import Tagger

#app = Flask(__name__)

class MiniJSONEncoder(JSONEncoder):
    """Minify JSON output."""
    item_separator = ','
    key_separator = ':'

app = Flask(__name__)

#with app.app_context():
    # within this block, current_app points to app.
#    annotate("1", "shpendm")
#    print current_app.name
app.json_encoder = MiniJSONEncoder
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # see http://flask.pocoo.org/docs/0.10/config/

tagger = Tagger()
tagger.add_name("shpendmahmuti", "-111", "123")  # stub when testing
tagger.load_global("dics/worm_global.tsv") #tagger_global
tagger.load_names("dics/worm_entities.tsv", "dics/worm_names.tsv")
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

@app.route('/')
def form():
    return """
        <html>
            <body>

                <h1>Tagging</h1>
                <form action="/" method="post" enctype="multipart/form-data">
		  <fieldset>
		    <legend>Run the docker with parameters below</legend>
                    <p> Tagger Global <input type="file" name="filename2" style="margin-left:80px;" />
                    <p> Tagger Entities <input type="file" name="filename3" style="margin-left:75px;" />
                    <p> Tagger Names <input type="file" name="filename4" style="margin-left:80px;" />
                    <p>
			<label>Add Name, Type and ID</label>
			  <input type = "text" id = "name_input"  value = "" />
			  <input type = "text" id = "type_input"  value = "" />
			  <input type = "text" id = "id_input"  value = "" />
		    </p>
                    <p><button type="submit"> Submit data </button>
		  </fieldset>
                </form>
		
		 <h1>Search for tagging</h1>
		    <form action="/tests" method="post" enctype="multipart/form-data">
		      <fieldset>
			<legend>Input the values</legend>
			<p>
			  <label>Text</label>
			  <input type = "text" id = "id_text" value = "" />
			</p>
			<p>
			  <label>Entity type</label>
			  <input type = "text" id = "id_entity_type" value = "" />
			</p>
			<p>
			  <button type="submit"> Tag values </button>
		      </fieldset>
		    </form>

             <!--   <form action="/results" method="post" enctype="multipart/form-data">
                    <p><b> Show the content of your chosen file</b></p>
                    <p> Pick a file <input type="file" name="filename" />
                    <button type="submit"> Show content </button>
                </form>
	     -->
            </body>
        </html>
    """

"""
	@app.route('/results', methods=["POST"])
	def results_view():
	    f = request.files['filename']
	    if not f:
		return "No file"

	    stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
	    lines =''
	    val = 0
	    while True:
		    val+=1
		    read_data = stream.readline()
		    lines += '<p> Line nr: %d ----- %s</p>' % (val, read_data)
		    if bool(read_data)==False:
			break

	    return lines
"""
@app.route('/tests', methods=["POST"])
def tests_view():
    f = request.files['filename']
    if not f:
        return "No file"

    stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
    lines =''
    val = 0
    while True:
            val+=1
	    read_data = stream.readline()
	    lines += '<p> Line nr: %d ----- %s</p>' % (val, read_data)
	    if bool(read_data)==False:
		break

    return lines

@app.route("/annotate/<entity_types>", methods=['POST','PUT','GET'])#, methods=['PUT', 'POST'])
def annotate(entity_types, text=None): #(): #(entity_types, text=None):
    """
    entity_types: e.g., "9606,-3,-22"
    """

    text = "shpendmahmuti" #text = 13 chars
    entity_types = "2, -10, -111"  #type=-1, id=123  (type: if one number is on the document, then it tags it

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
    except RuntimeError as e:
        if str(e) == 'working outside of application context':
            pass
        else:
            raise

    return json #"It is working!"

# -----------------------------------------------------------------------------------

# Simple text
with app.app_context():
    # within this block, current_app points to app.
    annotate("2, -111","shpendm") #()#("1", "shpendm")
    print current_app.name

if __name__ == '__main__':
    parser = optparse.OptionParser(usage="python server.py -p ")
    parser.add_option('-p', '--port', action='store', dest='port', help='The port to listen.')
    (args, _) = parser.parse_args()
    if args.port == None:
        print "Missing required argument: -p/--port"
        sys.exit(1)
    app.run(host='0.0.0.0', port=int(args.port), debug=False)
