import os
import re
import logging
from transformers import GPT2Tokenizer, GPT2LMHeadModel, T5Tokenizer, T5ForConditionalGeneration, AutoTokenizer, AutoModelForSeq2SeqLM

# Configure logging
logging.basicConfig(
    filename='nlp_processing.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def chunk_text(text, chunk_size=2000):
    text = re.sub(r'\s+', ' ', text).strip()
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    logging.info(f"Chunked text into {len(chunks)} parts.")
    return chunks

def initialize_model_and_tokenizer(model_name):
    if model_name == "GPT-2":
        tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        model = GPT2LMHeadModel.from_pretrained("gpt2")
    elif model_name == "T5":
        tokenizer = T5Tokenizer.from_pretrained('t5-small')
        model = T5ForConditionalGeneration.from_pretrained('t5-small')
    elif model_name == "LLaMA":
        tokenizer = AutoTokenizer.from_pretrained("facebook/llama")
        model = AutoModelForSeq2SeqLM.from_pretrained("facebook/llama")
    else:
        raise ValueError(f"Model {model_name} is not supported.")
    return model, tokenizer

def analyze_text(text, model, tokenizer, prompt):
    try:
        inputs = tokenizer(f"{prompt}: {text}", return_tensors="pt", max_length=512, truncation=True)
        outputs = model.generate(inputs.input_ids, attention_mask=inputs['attention_mask'], max_length=150, num_beams=5, early_stopping=True)
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return decoded
    except Exception as e:
        logging.error(f"Error in analysis: {e}")
        return None

def analyze_document(text, model, tokenizer):
    results = {}
    results['Company'] = analyze_text(text, model, tokenizer, "Extract the company name from the document")
    results['Year'] = analyze_text(text, model, tokenizer, "Extract the year of the document from the text")
    results['Transaction Exposure'] = analyze_text(text, model, tokenizer, "Detail the transaction exposure of the company")
    results['Translation Exposure'] = analyze_text(text, model, tokenizer, "Detail the translation exposure of the company")
    results['Economic Exposure'] = analyze_text(text, model, tokenizer, "Detail the economic exposure of the company")
    results['Hedging Strategies'] = analyze_text(text, model, tokenizer, "List the hedging strategies used by the company")
    results['FX Risk Management Policies'] = analyze_text(text, model, tokenizer, "Describe the company's FX risk management policies")
    return results

def process_text_files(directory, output_directory, model_name):
    model, tokenizer = initialize_model_and_tokenizer(model_name)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        logging.info(f"Created output directory: {output_directory}")

    for company_folder in os.listdir(directory):
        company_path = os.path.join(directory, company_folder)
        if os.path.isdir(company_path):
            logging.debug(f"Processing company folder: {company_folder}")
            for file_name in os.listdir(company_path):
                if file_name.endswith(".txt"):
                    file_path = os.path.join(company_path, file_name)
                    logging.info(f"Processing file: {file_path}")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            text = file.read()
                        
                        chunks = chunk_text(text)
                        all_results = {}
                        for chunk in chunks:
                            results = analyze_document(chunk, model, tokenizer)
                            for key, value in results.items():
                                if key not in all_results:
                                    all_results[key] = value
                                else:
                                    all_results[key] += "\n" + value

                        save_results(output_directory, company_folder, model_name, all_results)
                    except Exception as e:
                        logging.error(f"Error processing file {file_path}: {e}")

def save_results(output_directory, company, model_name, results):
    if not results:
        logging.warning(f"No results for {company} with model {model_name}.")
        return

    result_file_path = os.path.join(output_directory, company, f"{company}_{model_name}_output.txt")
    try:
        with open(result_file_path, 'w', encoding='utf-8') as file:
            for key, value in results.items():
                file.write(f"{key}: {value}\n\n")
        logging.info(f"Saved {model_name} results to {result_file_path}")
    except Exception as e:
        logging.error(f"Error saving results to {result_file_path}: {e}")

# Directories
input_directory = 'extracted_data'
output_directory_base = 'nlp_results'

# List of models to use
models = ["GPT-2", "T5", "LLaMA"]

# Process all extracted text files for each model
for model_name in models:
    output_directory = os.path.join(output_directory_base, model_name)
    process_text_files(input_directory, output_directory, model_name)
