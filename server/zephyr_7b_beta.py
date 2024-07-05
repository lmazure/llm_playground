import json
import os
from typing import List
from dotenv import load_dotenv, find_dotenv

from hugging_face_model import HuggingFaceModel

class Zephyr_7b_Beta(HuggingFaceModel):

    def __init__(self, logger):
        name ="HuggingFaceH4/zephyr-7b-beta"
        super().__init__(name, logger)
   
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
