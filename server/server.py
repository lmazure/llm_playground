from dotenv import load_dotenv, find_dotenv
import os
import requests
import json
from flask import Flask, Response, request, render_template
import webbrowser

from logger import Logger

logger = Logger()
   
# ----- LLM request handling

load_dotenv(find_dotenv())
token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

model ="HuggingFaceH4/zephyr-7b-beta" # see https://huggingface.co/HuggingFaceH4/zephyr-7b-beta

API_URL = "https://api-inference.huggingface.co/models/" + model # see https://huggingface.co/docs/api-inference/detailed_parameters

def query(payload, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(API_URL, headers=headers, json=payload)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        error_message = response.text
        print(f"Request failed with error: {error_message}")
        # Handle the error or raise an exception
        raise Exception("An error occurred")
    return response.json()

def build_prompt(requirement):
    system_message = """You are an expert on manual software testing.
You will be provided with a requirement, you are in charge to describe the test cases necessary to validate this specific requirement.
You must provide the test cases formatted in JSON as a JSON array whose each element is defined with three text fields defining one test case: "title", "action", and "expected_result".
Your answer must not contain anything else that the JSON."""

    prompt_template=f'''<|im_start|>system
{system_message}<|im_end|>
<|im_start|>user
Write test cases for the following requirement:
{requirement}<|im_end|>
<|im_start|>assistant
'''
    
    return prompt_template


def call_llm(token, query, build_prompt, requirement):
    prompt = build_prompt(requirement)

    payload = {
    "inputs": prompt,
    "parameters": {
        "return_full_text": False,
        "max_new_tokens": 1024
        }
    }

    print(f"requirement={requirement}", flush=True)
    print(f"prompt={prompt}", flush=True)
    data = query(payload, token)
    test = data[0]['generated_text']
    logger.log("info", test)
    return json.loads(test)


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
    logger.log("info", "/submit has been called for IDs" + (''.join(map(str, ids))))
    requirements = [requirement_list[id] for id in ids]
    try:
        tests = call_llm(token, query, build_prompt, requirements[0])
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
    logger.log("info", "GET /parameters has been called")
    parameters = { 'fields': [ { 'key': 'return_full_text ', 'title': 'Return full text', 'type': 'boolean', 'value': False },
                               { 'key': 'max_new_tokens ', 'title': 'Max new tokens', 'type': 'number', 'value': '1024'} ] }
    response = Response(json.dumps(parameters), mimetype='application/json')
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
