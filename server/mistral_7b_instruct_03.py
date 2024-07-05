import json
import os
from typing import List
from dotenv import load_dotenv, find_dotenv

from hugging_face_model import HuggingFaceModel

class Mistral_7B_Instruct_03(HuggingFaceModel):

    def __init__(self, logger):
        name ="mistralai/Mistral-7B-Instruct-v0.3"
        super().__init__(name, logger)
   
    def build_prompt(self, requirements: List[str]) -> str:
        newline = '\n'
        prompt=f"""[INST]
You are an expert in manual software testing.
You will be provided with one or several requirements, you are in charge to describe the test cases necessary to validate these specific requirements.
You must provide the test cases in JSON as a JSON array whose each element is defined with three text fields defining one test case: "title", "action", and "expected_result".
Be careful, your answer must contain only the JSON and no Markdown code block!

Write test cases for the following requirements:
{newline.join(requirements)}
[/INST]
"""
        return prompt
