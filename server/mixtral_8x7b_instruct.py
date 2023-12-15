import json
import os
from dotenv import load_dotenv, find_dotenv

from base_model import Base_Model

load_dotenv(find_dotenv())

class Mixtral_8x7B_Instruct(Base_Model):

    def __init__(self, logger):
        name ="mistralai/Mixtral-8x7B-Instruct-v0.1"
        description = """This model is <A href='https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1' target='_blank'>mistralai/Mixtral-8x7B-Instruct-v0.1</A>.<BR>
Its parameters are described <A href='https://docs.together.ai/docs/inference-rest' target='_blank'>here</A>.<BR>
It is hosted by Together AI.
"""
        url = "https://api.together.xyz/inference"
        token = os.getenv("TOGETHERAI_API_TOKEN")
        parameters = [ { 'key': 'temperature', 'title': 'Temperature of the sampling operation', 'type': 'float', 'min': 0.0, 'max': 100.0, 'value': 0.7},
                       { 'key': 'repetition_penalty', 'title': 'The more a token is used the more it is penalized to not be picked again', 'type': 'float', 'min': 0.0, 'max': 100.0, 'value': 1},
                       { 'key': 'max_tokens', 'title': 'Max tokens', 'type': 'integer', 'value': 512},
                       { 'key': 'top_k', 'title': 'Top tokens considered within the sample operation', 'type': 'integer', 'value': 50},
                       { 'key': 'top_p', 'title': 'Tokens that are within the sample operation of text generation', 'type': 'float', 'value': 0.7} ]
        super().__init__(name, description, parameters, url, token, logger)

    
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
            "model": self.name(),
            "request_type": "language-model-inference",
            "prompt": prompt
        }
        for f in self.parameters:
            if f['value'] is not None:
                payload[f['key']] = f['value']
        try:
            data = self.query(payload)
        except Exception as e:
            print("Error while querying: " + str(e), flush=True)
        generated_text = data['output']['choices'][0]['text']
        print("generated_text = " + generated_text, flush=True)
        try:
            tests = json.loads(generated_text)
        except json.JSONDecodeError as e:
            self.logger.log("error", f"Error while trying to parse generated text as JSON\n{e}\nThe generated text is\n{generated_text}")
        return tests
