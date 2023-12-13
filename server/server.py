import json
from flask import Flask, Response, request, render_template, jsonify
import webbrowser
import logging
from zephyr_7b_beta import Zephyr_7b_Beta

from logger import Logger

requirement_list = None

logger = Logger()
model = Zephyr_7b_Beta(logger)

# ----- Spec file loading

def build_requirement_list(spec):
    """
    Build a list of requirements from a given specification.
    
    Parameters:
        spec (dict): The specification from which to build the requirements list.
    
    Returns:
        tuple: A tuple containing the list of requirements and the updated increment value.
    """
    list = []
    for requirement in spec['requirements']:
        list.append(requirement['text'])
    if 'parts' in spec:
        for part in spec['parts']:
            list.extend(build_requirement_list(part))
    return list

# configure Flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Open the HTML client in the default web browser
webbrowser.open("http://127.0.0.1:5000/")

# ----- Start the server

app = Flask(__name__)

@app.route('/submit', methods=['POST'])
def submit() -> Response:
    payload = request.form.getlist('selectedItems')
    ids = [int(item) for item in json.loads(payload[0])]
    logger.log("info", "POST /submit\nhas been called with IDs " + (', '.join(map(str, ids))))
    requirements = [requirement_list[id] for id in ids]
    try:
        tests = model.generate_test_cases(requirements)
    except Exception as e:
        return Response(f"Internal error {e} ", status=500)
    response = Response(json.dumps(tests), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/parameters', methods=['GET'])
def get_parameters() -> Response:
    data = { 'html_description': model.get_html_description(),
             'fields': model.get_parameters() }
    logger.log("info", "GET /parameters\nhas been called and answered\n" + json.dumps(data))
    response = Response(json.dumps(data), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/parameters', methods=['POST'])
def set_parameters() -> Response:
    payload = request.form.getlist('parameters')
    logger.log("info", "POST /parameters\nhas been called with payload\n" + json.dumps(payload))
    payload_dict = json.loads(payload[0])
    model.set_parameters(payload_dict)
    response = Response({}, mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/logs', methods=['GET'])
def get_logs() -> Response:
    first_index = int(request.args.get('firstIndex'))
    last_index = int(request.args.get('lastIndex'))
    logs = logger.logs(first_index, last_index)
    response = Response(json.dumps(logs), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/lastLogIndex', methods=['GET'])
def get_last_log_index() -> Response:
    response = Response(json.dumps(logger.lastLogIndex()), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/upload', methods=['POST'])
def upload() -> Response:
    logger.log("info", "POST /upload\nhas been called")
    spec = get_json_from_request(request)
    global requirement_list
    requirement_list = build_requirement_list(spec)
    if spec:
        response = Response(json.dumps(spec), mimetype='application/json')
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    return jsonify({'success': False, 'message': 'Unable to process the JSON file.'})

def get_json_from_request(request) -> Response:
    try:
        file = request.files['file']
        if file and allowed_file(file.filename):
            content = file.read().decode('utf-8')
            return json.loads(content)
        return None
    except json.JSONDecodeError:
        return None

def allowed_file(filename) -> Response:
    return 'json' in filename.lower()  # Only allow JSON files

@app.route('/')
def index() -> Response:
    return render_template('index.html')

if __name__ == '__main__':
    logger.log("info", "Starting server")
    app.run()
