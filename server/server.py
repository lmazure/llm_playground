import json
from flask import Flask, Response, request, render_template
import webbrowser

from zephyr_7b_beta import Zephyr_7b_beta

from logger import Logger

logger = Logger()
model = Zephyr_7b_beta(logger)

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

def read_spec_file(spec_file):
    try:
        with open(spec_file) as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"The file {spec_file} does not exist.")
        exit(1)
    except json.JSONDecodeError:
        print(f"The file {spec_file} contains invalid JSON.")
        exit(1)
    except Exception as e:
        print(f"An error occurred while reading {spec_file}: ", str(e))
        exit(1)

spec_file = 'specs.json'
spec = read_spec_file(spec_file)
requirement_list = build_requirement_list(spec)

# Open the HTML client in the default web browser
webbrowser.open("http://127.0.0.1:5000/")

# ----- Start the server

app = Flask(__name__)

@app.route('/submit', methods=['POST'])
def submit():
    logger.log("info", "POST /submit has been called")
    payload = request.form.getlist('selectedItems')
    ids = [int(item) for item in json.loads(payload[0])]
    logger.log("info", "/submit has been called for IDs, request = " + (''.join(map(str, ids))))
    requirements = [requirement_list[id] for id in ids]
    try:
        tests = model.generate_test_cases(requirements[0])
    except Exception as e:
        return Response(f"Internal error {e} ", status=500)
    response = Response(json.dumps(tests), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/specification', methods=['GET'])
def specification():
    logger.log("info", "GET /specification has been called")
    response = Response(json.dumps(spec), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/parameters', methods=['GET'])
def get_parameters():
    data = { 'fields': model.getParameters()}
    logger.log("info", "GET /parameters has been called, answer = " + json.dumps(data))
    response = Response(json.dumps(data), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/parameters', methods=['POST'])
def set_parameters():
    payload = request.form.getlist('parameters')
    logger.log("info", "POST /parameters has been called with payload " + json.dumps(payload))
    response = Response({}, mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/logs', methods=['GET'])
def get_logs():
    first_index = int(request.args.get('firstIndex'))
    last_index = int(request.args.get('lastIndex'))
    logs = logger.logs(first_index, last_index)
    response = Response(json.dumps(logs), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/lastLogIndex', methods=['GET'])
def get_last_log_index():
    response = Response(json.dumps(logger.lastLogIndex()), mimetype='application/json')
    print(response, flush=True)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    logger.log("info", "Starting server")
    app.run()
