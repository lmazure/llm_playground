from dotenv import load_dotenv, find_dotenv
import os
import requests
import json
from html import escape
from flask import Flask, request

load_dotenv(find_dotenv())
token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

model ="HuggingFaceH4/zephyr-7b-beta" # see https://huggingface.co/HuggingFaceH4/zephyr-7b-beta

API_URL = "https://api-inference.huggingface.co/models/" + model # see https://huggingface.co/docs/api-inference/detailed_parameters

def query(payload, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

system_message = """You are an expert on manual software testing.
You will be provided with a requirement, you are in charge to describe the test cases necessary to validate this specific requirement.
You must provide the test cases formatted in JSON as a JSON array whose each element is defined with three text fields defining one test case: "title", "action", and "expected_result".
Your answer must not contain anything else that the JSON."""

prompt = """
On the "Login" page, if the user clicks on submit and the value of the "login" field and the "password" field correspond to an existing usernname / password or to an exiting email / password, the "Welcome" page should be displayed. Otherwise, the "Login" page should be still display, but with an "Invalid credentials." message.
"""

prompt_template=f'''<|im_start|>system
{system_message}<|im_end|>
<|im_start|>user
{prompt}<|im_end|>
<|im_start|>assistant
'''

payload = {
    "inputs": prompt_template,
    "parameters": {
        "return_full_text": False,
        "max_new_tokens": 1024
    }
}

#data = query(payload, token)
#print(data[0]['generated_text'])



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

def convert_string_to_html(str):
    s = escape(str)
    return s.replace('\n', '<br>')

def convert_to_html(spec):
    incr = 1
    html = f"<h1>{convert_string_to_html(spec['title'])}</h1>\n"
    html += "<ul>\n"
    for requirement in spec['requirements']:
        html += f"<li><input type='checkbox' id='{incr}'>{convert_string_to_html(requirement['id'])} - {convert_string_to_html(requirement['text'])}</li>\n"
        incr += 1
    if 'parts' in spec:
        for part in spec['parts']:
            html += f"<li>{convert_to_html(part)}</li>"
    html += "</ul>\n"
    return html

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
            {convert_to_html(spec)}
            <button type="button" onclick="submitForm()">Submit</button>
          </form> 
        </body>
      </html>"""

html_content = generate_html(spec)

# Write the HTML content to a file
with open('data.html', 'w') as f:
    f.write(html_content)

os.startfile('data.html')

app = Flask(__name__)

@app.route('/submit', methods=['POST'])
def submit():
    print("Request received", flush=True)
    selected_items = request.form.getlist('selectedItems')
    selected_items = [int(item) for item in json.loads(selected_items[0])]
    print(selected_items)
    return 'Request successful'

if __name__ == '__main__':
    app.run()
