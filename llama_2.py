import transformers
import torch
import os

# Use a smaller model if possible
model_id = "meta-llama/Llama-2-7b-chat-hf"  # Consider a smaller model if available

pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.float16},
    device="cuda" if torch.cuda.is_available() else "cpu",  # Ensure GPU usage if available
    use_auth_token=os.getenv('HF_TOKEN')
)

messages = [
    {"role": "system", "content": "You are an FX risk management chatbot who provides detailed information about FX risks, hedging strategies, and their effectiveness."},
    {"role": "user", "content": "What are the main FX risks faced by companies?"},
    {"role": "user", "content": "How can these FX risks be hedged?"},
    {"role": "user", "content": "Are there any situations where FX risks cannot be effectively hedged?"},
]

# Format the messages manually into a single string prompt
prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

# Terminators should be valid EOS tokens
eos_token_id = pipeline.tokenizer.eos_token_id

# Reduce max_new_tokens and adjust temperature/top_p for efficiency
outputs = pipeline(
    prompt,
    max_new_tokens=150,  # Increased to give more detailed responses
    eos_token_id=eos_token_id,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
)

# Print the generated text excluding the prompt
print(outputs[0]["generated_text"][len(prompt):])
