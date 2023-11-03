from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

model_name_or_path = "TheBloke/dolphin-2.1-mistral-7B-GPTQ"
# To use a different branch, change revision
# For example: revision="gptq-4bit-32g-actorder_True"
model = AutoModelForCausalLM.from_pretrained(model_name_or_path,
                                             device_map="auto",
                                             trust_remote_code=False,
                                             revision="main")

tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=True)

system_message = """You are an expert on manual software testing.
You will be provided with a description of a feature. This description is a list of requirements detailing how the feature should behave.
Then you are provided with a requirement, you are in charge to describe the test cases necessary to validate this specific requirement. You must not test the other requirements of the feature, these ones are only provided for your information.
You should provide the test cases formatted in JSON as a JSON array whose each element is defined with the fields defining one test case: "title", "action", and "expected_result"."""
prompt = """Here is the description of the "login" page:
The "login" page should contain:
- a "login" field
- a "password" field
- a "submit" button
- a "Create account" button
On the "Login" page, the "submit" button should be enabled if and only if both the "login" field and the "password" field are filled.
On the "Login" page, if the user clicks on submit and the value of the "login" field and the "password" field correspond to an existing usernname / password or to an exiting email / password, the "Welcome" page should be displayed. Otherwise, the "Login" page should be still display, but with an "Invalid credentials." message.
On the "Login" page, if the user clicks on the "Create account" link, then the "Account creation" page should be displayed.

Can you write test cases to validate this requirement:
On the "Login" page, if the user clicks on submit and the value of the "login" field and the "password" field correspond to an existing usernname / password or to an exiting email / password, the "Welcome" page should be displayed. Otherwise, the "Login" page should be still display, but with an "Invalid credentials." message.

You need to indicate what is a correct login."""
prompt_template=f'''<|im_start|>system
{system_message}<|im_end|>
<|im_start|>user
{prompt}<|im_end|>
<|im_start|>assistant
'''


## print("\n\n*** Generate:")
## 
## input_ids = tokenizer(prompt_template, return_tensors='pt').input_ids.cuda()
## output = model.generate(inputs=input_ids, temperature=0.7, do_sample=True, top_p=0.95, top_k=40, max_new_tokens=2048)
## print(tokenizer.decode(output[0]))



# Inference can also be done using transformers' pipeline

print("*** Pipeline:")
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=1024,
    do_sample=True,
    temperature=0.7,
    top_p=0.95,
    top_k=40,
    repetition_penalty=1.1
)

print(pipe(prompt_template)[0]['generated_text'])
