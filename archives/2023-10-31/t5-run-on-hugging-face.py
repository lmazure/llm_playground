from langchain import PromptTemplate, HuggingFaceHub, LLMChain
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

template = """Question: {question}

Answer: Let's think step by step."""

prompt = PromptTemplate(template=template, input_variables=["question"])

llm_chain = LLMChain(prompt=prompt, 
                     llm=HuggingFaceHub(repo_id="google/flan-t5-large", 
                                        model_kwargs={"temperature":0, 
                                                      "max_length":64}))

question = "What is the capital of France?"

print(llm_chain.run(question))
