from dotenv import load_dotenv, find_dotenv
import os
import requests
import json
from html import escape
from flask import Flask, request

# ----- LLM request handling

load_dotenv(find_dotenv())
token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

model ="HuggingFaceH4/zephyr-7b-beta" # see https://huggingface.co/HuggingFaceH4/zephyr-7b-beta

API_URL = "https://api-inference.huggingface.co/models/" + model # see https://huggingface.co/docs/api-inference/detailed_parameters

def query(payload, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def build_prompt(requirement):
    system_message = """You are an expert on manual software testing.
You will be provided with a requirement, you are in charge to describe the test cases necessary to validate this specific requirement.
You must provide the test cases formatted in JSON as a JSON array whose each element is defined with three text fields defining one test case: "title", "action", and "expected_result".
Your answer must not contain anything else that the JSON."""

    prompt_template=f'''<|im_start|>system
{system_message}<|im_end|>
<|im_start|>user
Write a test case for the following requirement:
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
    print(">>>", flush=True)
    print(test, flush=True)
    print("<<<", flush=True)


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

# ----- Generation of the HTML form

def convert_string_to_html(str):
    s = escape(str)
    return s.replace('\n', '<br>')

def convert_to_html(spec, incr):
    html = f"<h1>{convert_string_to_html(spec['title'])}</h1>\n"
    html += "<ul>\n"
    for requirement in spec['requirements']:
        html += f"<li><input type='checkbox' id='{incr}'>{convert_string_to_html(requirement['id'])} - {convert_string_to_html(requirement['text'])}</li>\n"
        incr += 1
    if 'parts' in spec:
        for part in spec['parts']:
            h, i = convert_to_html(part, incr)
            html += f"<li>{h}</li>\n"
            incr = i
    html += "</ul>\n"
    return html, incr

def generate_html(spec):
    """
    Generates an HTML form with checkboxes based on the given specification.

    Parameters:
    - spec (dict): The specification for generating the HTML form.

    Returns:
    - str: The generated HTML form as a string.
    """
    return f"""
      <html>
        <head>
          <title>Test case generation</title>
            <script>
              function submitForm() {{
                var selectedItems = [];
                var checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
                for (var i = 0; i < checkboxes.length; i++) {{
                    selectedItems.push(checkboxes[i].id);
                }}
                var request = new XMLHttpRequest();
                request.open('POST', 'http://127.0.0.1:5000/submit');
                request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                request.onreadystatechange = function() {{
                    if (request.readyState === 4 && request.status === 200) {{
                        alert('Request successful');
                    }}
                }};
                request.send('selectedItems=' + encodeURIComponent(JSON.stringify(selectedItems)));
              }}
            </script>
          </head>
          <body>
            <form>
            {convert_to_html(spec, 0)[0]}
            <button type="button" onclick="submitForm()">Submit</button>
          </form> 
        </body>
      </html>"""

html_content = generate_html(spec)

# Write the HTML content to a file
with open('data.html', 'w') as f:
    f.write(html_content)

# Open the HTML file in the default web browser
os.startfile('data.html')


# ----- Start the server

app = Flask(__name__)

@app.route('/submit', methods=['POST'])
def submit():
    print("Request received", flush=True)
    payload = request.form.getlist('selectedItems')
    ids = [int(item) for item in json.loads(payload[0])]
    print(ids)
    requirements = [requirement_list[id] for id in ids]
    call_llm(token, query, build_prompt, requirements[0])
    return 'Request successful'

if __name__ == '__main__':
    app.run()
