import os
import requests

# Retrieve the token from environment variables
api_token = os.getenv('HF_TOKEN')
if not api_token:
    raise ValueError("Please set the Hugging Face API token in your environment variables")

API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3.1-8B-Instruct"
headers = {"Authorization": f"Bearer {api_token}"}

data = {
    "inputs": [
        {"role": "system", "content": "You are an assistant who helps with computational problems."},
        {"role": "user", "content": "How can I optimize my machine learning model?"}
    ]
}

response = requests.post(API_URL, headers=headers, json=data)
print(response.json())

