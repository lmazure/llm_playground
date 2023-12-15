import json
import os
from dotenv import load_dotenv, find_dotenv
import requests

load_dotenv(find_dotenv())

class Mixtral_8x7B_Instruct():

    def __init__(self, logger):
        self._model ="mistralai/Mixtral-8x7B-Instruct-v0.1"
        self.logger = logger
        self.parameters = [ { 'key': 'temperature', 'title': 'Temperature of the sampling operation', 'type': 'float', 'min': 0.0, 'max': 100.0, 'value': 0.7},
                            { 'key': 'repetition_penalty', 'title': 'The more a token is used the more it is penalized to not be picked again', 'type': 'float', 'min': 0.0, 'max': 100.0, 'value': None},
                            { 'key': 'max_tokens', 'title': 'Max tokens', 'type': 'integer', 'value': 512},
                            { 'key': 'top_k', 'title': 'Top tokens considered within the sample operation', 'type': 'integer', 'value': 50},
                            { 'key': 'top_p', 'title': 'Tokens that are within the sample operation of text generation', 'type': 'float', 'value': 0.7} ]
        self.token = os.getenv("TOGETHERAI_API_TOKEN")


    def query(self, payload):
        headers = {"Authorization": f"Bearer {self.token}"}
        url = "https://api.together.xyz/inference"
        self.logger.log("info", url + "\nhas been called with payload\n" + json.dumps(payload))
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            error_message = response.text
            self.logger.log("error", url + "\nreturned error\n" + error_message)
            raise Exception("Model failed") from e
        except Exception as e:
            self.logger.log("error", url + "\nfailed with exception\n" + str(e))
            raise Exception("An error occurred") from e
        txt =response.text
        print("API answer = " + txt, flush=True)
        # print("$$$ before ", flush=True)
        # print("JSON = " + response.json(), flush=True)
        # print("$$$ after ", flush=True)
        jsonz = {}
        try:
            jsonz = json.loads(txt)
            print("1 jsonz = " + str(jsonz), flush=True)
        except BaseException as e:
            self.logger.log("error", f"Error while trying to extract JSON\n{e}\nThe API answer is\n{txt}")
            raise Exception(f"Error while trying to extract JSON from \"{txt}\" shit is " + str(e)) from e
        print("2 jsonz = " + str(jsonz), flush=True)
        return jsonz
    
    def build_prompt(self, requirements):
        newline = '\n'
        prompt=f"""<s> [INST] You are an expert on manual software testing.
You will be provided with one or several requirements, you are in charge to describe the test cases necessary to validate these specific requirements.
You must provide the test cases formatted in JSON as a JSON array whose each element is defined with three text fields defining one test case: "title", "action", and "expected_result".
Your answer must contain only the JSON.
Write test cases for the following requirements:
{newline.join(requirements)}
 [/INST]
"""
        return prompt
        
    def generate_test_cases(self, requirements):
        prompt = self.build_prompt(requirements)
        #params = { f['key']:f['value'] for f in self.parameters if f['value'] is not None }
        payload = {
            "model": self._model,
            "max_tokens": 512,
            "prompt": prompt,
            "request_type": "language-model-inference",
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1
        }
        try:
            data = self.query(payload)
        except Exception as e:
            print("Error while querying: " + str(e), flush=True)
        #print("data = " + str(data), flush=True)
        #print("data['output'] = " + str(data['output']), flush=True)
        #print("data['output']['choices'] = " + str(data['output']['choices']), flush=True)
        #print("data['output']['choices'][0] = " + str(data['output']['choices'][0]), flush=True)
        #print("data['output']['choices'][0]['text'] = " + str(data['output']['choices'][0]['text']), flush=True)
        generated_text = data['output']['choices'][0]['text']
        print("generated_text = " + generated_text, flush=True)
        #tests = []
        try:
            tests = json.loads(generated_text)
        except json.JSONDecodeError as e:
            self.logger.log("error", f"Error while trying to parse generated text as JSON\n{e}\nThe generated text is\n{generated_text}")
        return tests
    
    def name(self):
        return self._model
    
    def get_parameters(self):
        return self.parameters  
    
    def set_parameters(self, parameters):
        pass
        #for parameter,value in parameters.items():
        #    found = False
        #    for f in self.parameters:
        #        if parameter == f['key']:
        #            f['value'] = value
        #            found = True
        #    if not found:
        #        raise Exception(f"Unknown key: {parameter}")

    def get_html_description(self):
        return """This model is <A href='https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1' target='_blank'>mistralai/Mixtral-8x7B-Instruct-v0.1</A>.<BR>
Its parameters are described <A href='https://docs.together.ai/docs/inference-rest' target='_blank'>here</A>.<BR>
It is hosted by Together AI.
"""

