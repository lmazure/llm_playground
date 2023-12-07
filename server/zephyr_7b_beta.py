import json
import os
from dotenv import load_dotenv, find_dotenv
import requests

# see https://huggingface.co/docs/api-inference/detailed_parameters#text-generation-task

load_dotenv(find_dotenv())

class Zephyr_7b_Beta():

    def __init__(self, logger):
        self._model ="HuggingFaceH4/zephyr-7b-beta" # see https://huggingface.co/HuggingFaceH4/zephyr-7b-beta
        self.logger = logger
        self.parameters = [ { 'key': 'return_full_text', 'title': 'Return full text', 'type': 'boolean', 'value': False },
                            #{ 'key': 'temperature', 'title': 'Temperature of the sampling operation', 'type': 'number', 'min': 0.0, 'max': 100.0, 'value': 1.0},
                            { 'key': 'max_new_tokens', 'title': 'Max new tokens', 'type': 'number', 'value': 1024} ]
        self.token = os.getenv("HUGGINGFACEHUB_API_TOKEN")


    def query(self, payload):
        headers = {"Authorization": f"Bearer {self.token}"}
        url = "https://api-inference.huggingface.co/models/" + self.name()
        self.logger.log("info", "URL = " + url + " called with payload " + json.dumps(payload))
        response = requests.post(url, headers=headers, json=payload)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            error_message = response.text
            self.logger.log("error", "URL = " + url + " failed with error " + error_message)
            raise Exception("An error occurred")
        print("API answer = " + response.text)
        return response.json()
    
    def build_prompt(self, requirements):
        newline = '\n'
        system_message = """You are an expert on manual software testing.
You will be provided with one or several requirements, you are in charge to describe the test cases necessary to validate these specific requirements.
You must provide the test cases formatted in JSON as a JSON array whose each element is defined with three text fields defining one test case: "title", "action", and "expected_result".
Your answer must not contain anything else that the JSON."""
    
        prompt=f"""<|im_start|>system
{system_message}<|im_end|>
<|im_start|>user
Write test cases for the following requirements:
{newline.join(requirements)}<|im_end|>
<|im_start|>assistant
"""
        return prompt
        
    def generate_test_cases(self, requirements):
        prompt = self.build_prompt(requirements)
        params = { f['key']:f['value'] for f in self.parameters }
        payload = {
          "inputs": prompt,
          "parameters": params
        }
        data = self.query(payload)
        generated_text = data[0]['generated_text']
        print("generated_text = " + generated_text, flush=True)
        tests = []
        try:
            tests = json.loads(generated_text)
        except json.JSONDecodeError as e:
            self.logger.log("error", f"Error parsing generated text: {e}\nThe generated text is:\n{generated_text}")
        return tests
    
    def name(self):
        return self._model
    
    def get_parameters(self):
        return self.parameters  
    
    def set_parameters(self, parameters):
        for parameter,value in parameters.items():
            found = False
            for f in self.parameters:
                if parameter == f['key']:
                    f['value'] = value
                    found = True
            if not found:
                raise Exception(f"Unknown key: {parameter}")
