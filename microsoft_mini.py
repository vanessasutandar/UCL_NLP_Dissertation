import os
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import HfApi, HfFolder, whoami

# Ensure the token is set correctly
hf_token = os.getenv('HUGGINGFACE_TOKEN')
if not hf_token:
    raise ValueError("HUGGINGFACE_TOKEN environment variable not set.")

# Print token and model details for debugging purposes
print(f"Using token: {hf_token[:8]}...")  # Print the first few characters for identification

# Model details (change as needed)
model_name = "microsoft/Phi-3-mini-128k-instruct"

# Initialize the Hugging Face API
api = HfApi()
HfFolder.save_token(hf_token)
user_info = whoami(token=hf_token)
print(f"Authenticated as: {user_info['name']}")

# Check if the model exists and list repositories the token has access to
try:
    model_info = api.model_info(model_name, token=hf_token)
    print(f"Model {model_name} exists.")
    print(f"Model details: {model_info}")

    # List models the user has access to
    models = api.list_models(author=user_info['name'], token=hf_token)
    gated_models = [m.modelId for m in models if m.private or m.gated]
    print(f"Models with gated access: {gated_models}")

except Exception as e:
    print(f"Error accessing model or API: {e}")

# Try to load the model and tokenizer to check permissions
model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=hf_token)
tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=hf_token)
print("Model and tokenizer loaded successfully.")

tokenizer.save_pretrained("./Users/vanessasutandar/Downloads/financial_reports/llama-models")
model.save_pretrained("./Users/vanessasutandar/Downloads/financial_reports/llama-models")
