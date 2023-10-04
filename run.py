# TODO: Install necessary libraries with pip
# pip install pandas requests openai tqdm

import os
import argparse
import threading
import queue
import time
import pandas as pd
import requests
import logging
import json
from openai.api_resources.abstract.api_resource import APIResource
from openai.error import OpenAIError
from requests.exceptions import HTTPError
from typing import List
from itertools import cycle
from tqdm import tqdm

# Set up logging
logging.basicConfig(level=logging.INFO)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Generate embeddings from text using multiple OpenAI endpoints.')
parser.add_argument('--input', required=True, help='Path to the input file (Excel, CSV, or JSON format)')
parser.add_argument('--output', required=True, help='Path to the output file (TSV, CSV, or JSON format)')
parser.add_argument('--config', required=True, help='Path to the configuration file (JSON format)')
parser.add_argument('--threads', type=int, default=50, help='Number of worker threads')
parser.add_argument('--batch-size', type=int, default=100, help='Number of items to process before saving results')
parser.add_argument('--retry-limit', type=int, default=5, help='Number of times to retry on error')
args = parser.parse_args()

# Load API endpoints and keys from configuration file
with open(args.config) as f:
    config = json.load(f)
openai_endpoints_and_keys = cycle(config['openai_endpoints_and_keys'])

# Function to generate embeddings
def generate_embedding(text: str, endpoint: str, api_key: str, deployment_name: str) -> List[float]:
    retries = 0
    while retries < args.retry_limit:
        try:
            headers = {'Content-Type': 'application/json', 'api-key': api_key}
            url = f"{endpoint}/openai/deployments/{deployment_name}/embeddings?api-version=2023-05-15"
            payload = {"input": text}
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()['data'][0]['embedding']
        except (OpenAIError, HTTPError) as e:
            logging.error(f"Error: {e}. Retrying after {SLEEP_TIME} seconds.")
            retries += 1
            time.sleep(SLEEP_TIME)
    logging.error(f"Failed to generate embedding for text: {text}")
    return []

# Worker function to be run on multiple threads
def worker():
    while True:
        item = q.get()
        if item is None:
            break
        index, row = item
        logging.info(f"Processing document {index}")
        endpoint, api_key, deployment_name = next(openai_endpoints_and_keys)
        vectors = generate_embedding(row['document'], endpoint, api_key, deployment_name)
        output_df.loc[index] = [row['id'], row['wopeCat'], row['googleCat'], row['openaiCat'], str(vectors)]  # Convert the list into a string
        q.task_done()

# Start the worker threads
threads = []
for i in range(args.threads):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)

# Load data from input file
if args.input.lower().endswith('.xlsx'):
    df = pd.read_excel(args.input)
elif args.input.lower().endswith('.csv'):
    df = pd.read_csv(args.input)
elif args.input.lower().endswith('.json'):
    df = pd.read_json(args.input)
else:
    raise ValueError("Unsupported input file type. Supported file types are .xlsx, .csv, and .json")

# Put the items (documents) into the queue
for i, item in enumerate(tqdm(df.iterrows(), total=df.shape[0])):
    q.put(item)
    if i % args.batch_size == 0 and i > 0:
        # Save the dataframe to the output file
        if args.output.lower().endswith('.tsv'):
            output_df.to_csv(args.output, sep='\t', index=False)
        elif args.output.lower().endswith('.csv'):
            output_df.to_csv(args.output, index=False)
        elif args.output.lower().endswith('.json'):
            output_df.to_json(args.output)
        else:
            raise ValueError("Unsupported output file type. Supported file types are .tsv, .csv, and .json")

# Block until all tasks are done
q.join()

# Stop worker threads
for i in range(args.threads):
    q.put(None)
for t in threads:
    t.join()

# Save the final dataframe to the output file
if args.output.lower().endswith('.tsv'):
    output_df.to_csv(args.output, sep='\t', index=False)
elif args.output.lower().endswith('.csv'):
    output_df.to_csv(args.output, index=False)
elif args.output.lower().endswith('.json'):
    output_df.to_json(args.output)
else:
    raise ValueError("Unsupported output file type. Supported file types are .tsv, .csv, and .json")
