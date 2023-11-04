from dotenv import load_dotenv, find_dotenv
import os
import requests
import json
from html import escape

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

with open('requirements.json', 'r') as file:
    spec = json.load(file)

def convert_string_to_html(str):
    s = escape(str)
    return s.replace('\n', '<br>')

def convert_to_html(spec):
    html = f"<h1>{convert_string_to_html(spec['title'])}</h1>\n"
    html += "<ul>\n"
    for requirement in spec['requirements']:
        html += f"<li>{convert_string_to_html(requirement)}</li>\n"
    if 'parts' in spec:
        for part in spec['parts']:
            html += f"<li>"
            html += convert_to_html(part)
            html += f"</li>"
    html += "</ul>\n"
    return html

def generate_html(spec):
    html = "<html>\n"
    html += "<head>\n"
    html += "<title>My Page</title>\n"
    html += "</head>\n"
    html += "<body>\n"
    html += convert_to_html(spec)
    html += "</body>\n"
    html += "</html>\n"
    return html

html_content = generate_html(spec)

# Write the HTML content to a file
with open('data.html', 'w') as f:
    f.write(html_content)

os.startfile('data.html')
