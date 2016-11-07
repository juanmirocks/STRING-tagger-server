from flask import Flask, make_response, request, jsonify, url_for
import io, csv
import sys, getopt
import cgi, os
import cgitb; cgitb.enable()
import subprocess
import re
import click


app = Flask(__name__)

def results(text_file_contents):
    return text_file_contents.replace("=", ",")


@app.route('/')
def form():
    return """
        <html>
            <body>
                <h1>Tagging of files</h1>

                <form action="/" method="post" enctype="multipart/form-data">
                    <p><b> Run the docker with parameters below. Files should be in a folder inside the current working directory</b></p>
                     <!-- <p> Directory <input type="file" name="filename1" style="margin-left:50px;" /> -->
                    <p> Types <input type="file" name="filename2" style="margin-left:80px;" />
                    <p> Entities <input type="file" name="filename3" style="margin-left:65px;" />
                    <p> Names <input type="file" name="filename4" style="margin-left:70px;" />
                    <p> Documents <input type="file" name="filename5" style="margin-left:35px;" />
                    <p><button type="submit"> Submit data </button>
                </form>

                <form action="/results" method="post" enctype="multipart/form-data">
                    <p><b> Show the content of your chosen file</b></p>
                    <p> Pick a file <input type="file" name="filename" />
                    <button type="submit"> Show content </button>
                </form>
            </body>
        </html>
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

@app.before_first_request
def run_after_start():
    # f2 = request.files['filename2']
    # fileName2 = f2.filename
    # f3 = request.files['filename3']
    # fileName3 = f3.filename
    # f4 = request.files['filename4']
    # fileName4 = f4.filename
    # f5 = request.files['filename5']
    # fileName5 = f5.filename

    os.setuid(os.geteuid())
    return os.popen("sudo docker run --volume %s:/data larsjuhljensen/tagger --types=%s"
             " --entities=%s --names=%s --documents=%s >output_file" % (os.getcwd(), "test_types.tsv", "test_entities.tsv", "test_names.tsv", "test_documents.tsv"), 'w')

if __name__ == "__main__":
    run_after_start()
    app.run(host='0.0.0.0', port=5001, debug=True)
