from dotenv import load_dotenv, find_dotenv
import os
import requests

load_dotenv(find_dotenv())
token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

model ="HuggingFaceH4/zephyr-7b-beta" # https://huggingface.co/HuggingFaceH4/zephyr-7b-beta

API_URL = "https://api-inference.huggingface.co/models/" + model

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

data = query(payload, token)

print(data[0]['generated_text'])