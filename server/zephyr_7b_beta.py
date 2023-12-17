import json
import os
from typing import List
from dotenv import load_dotenv, find_dotenv

from base_model import Base_Model

load_dotenv(find_dotenv())

class Zephyr_7b_Beta(Base_Model):

    def __init__(self, logger):
        name ="HuggingFaceH4/zephyr-7b-beta"
        description = """This model is <A href='https://huggingface.co/HuggingFaceH4/zephyr-7b-beta' target='_blank'>HuggingFaceH4/zephyr-7b-beta</A>.<BR>
Its parameters are described <A href='https://huggingface.co/docs/api-inference/detailed_parameters#text-generation-task' target='_blank'>here</A>.<BR>
It is hosted by 🤗 Hugging Face.
"""
        url = "https://api-inference.huggingface.co/models/" + name
        token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        parameters = [ { 'key': 'return_full_text', 'title': 'Return full text', 'type': 'boolean', 'value': False },
                       { 'key': 'temperature', 'title': 'Temperature of the sampling operation', 'type': 'float', 'min': 0.0, 'max': 100.0, 'value': 1.0},
                       { 'key': 'repetition_penalty', 'title': 'The more a token is used the more it is penalized to not be picked again', 'type': 'float', 'min': 0.0, 'max': 100.0, 'value': None},
                       { 'key': 'max_new_tokens', 'title': 'Max new tokens', 'type': 'integer', 'value': 1024},
                       { 'key': 'top_k', 'title': 'Top tokens considered within the sample operation', 'type': 'integer', 'value': None},
                       { 'key': 'top_p', 'title': 'Tokens that are within the sample operation of text generation', 'type': 'float', 'value': None} ]
        super().__init__(name, description, parameters, url, token, logger)
   
    def build_prompt(self, requirements: List[str]) -> str:
        newline = '\n'
        system_message = """You are an expert in manual software testing.
You will be provided with one or several requirements, you are in charge to describe the test cases necessary to validate these specific requirements.
You must provide the test cases formatted in JSON as a JSON array whose each element is defined with three text fields defining one test case: "title", "action", and "expected_result".
Your answer must contain only the JSON."""
    
        prompt=f"""<|im_start|>system
{system_message}<|im_end|>
<|im_start|>user
Write test cases for the following requirements:
{newline.join(requirements)}<|im_end|>
<|im_start|>assistant
"""
        return prompt
        
    def prepare_payload(self, requirements: List[str]):
        prompt = self.build_prompt(requirements)
        params = { f['key']:f['value'] for f in self.parameters if f['value'] is not None }
        payload = {
          "inputs": prompt,
          "parameters": params
        }
        return payload

    def parse_result(self, data):
        generated_text = data[0]['generated_text']
        #print("generated_text = " + generated_text, flush=True)
        #tests = []
        try:
            tests = json.loads(generated_text)
        except json.JSONDecodeError as e:
            self.logger.log("error", f"Error while trying to parse generated text as JSON\n{e}\nThe generated text is\n{generated_text}")
        return tests
