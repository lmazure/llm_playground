from typing import List
import requests
import json

class Base_Model():

    def __init__(self, model_name, model_description, parameters, url, token, logger):
        self.model_name = model_name
        self.model_html_description = model_description
        self.url = url
        self.token = token
        self.logger = logger
        self.parameters = parameters

    def query(self, payload):
        headers = {"Authorization": f"Bearer {self.token}"}
        
        self.logger.log("info", self.url + "\nhas been called with payload\n" + json.dumps(payload))
        try:
            response = requests.post(self.url, headers=headers, json=payload)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            error_message = response.text
            self.logger.log("error", self.url + "\nreturned error\n" + error_message)
            raise Exception("Model failed") from e
        except Exception as e:
            self.logger.log("error", self.url + "\nfailed with exception\n" + str(e))
            raise Exception("An error occurred") from e
        txt =response.text
        print("API answer = " + txt, flush=True)
        jsonz = {}
        try:
            jsonz = json.loads(txt)
        except BaseException as e:
            self.logger.log("error", f"Error while trying to extract JSON\n{e}\nThe API answer is\n{txt}")
            raise Exception(f"Error while trying to extract JSON from \"{txt}\" shit is " + str(e)) from e
        return jsonz

    def name(self):
        return self.model_name
    
    def get_html_description(self):
        return self.model_html_description
    
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

    def generate_test_cases(self, requirements: List[str]):
        payload = self.prepare_payload(requirements)
        data = self.query(payload)
        tests = self.parse_result(data)
        return tests
    