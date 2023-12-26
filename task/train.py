

import openai
# from openai import OpenAI

# client = OpenAI(api_key='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')

def get_data():
    print("Getting data")
    response = openai.files.create(
    file=open("task/reformatted_task_management_dataset_v2.jsonl", "rb"),
    purpose="fine-tune"
    )
    print(response)
