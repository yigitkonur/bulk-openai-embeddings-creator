import pandas as pd
import pinecone
import ast
from concurrent.futures import ThreadPoolExecutor
from rich.progress import Progress

# Pinecone setup
pinecone.init(api_key="xxx", environment="us-east1-gcp")
index = pinecone.Index(index_name="category-vectors")

# Function to convert 'vectors' column from string to list
def convert_vectors(row):
    row['vectors'] = ast.literal_eval(row['vectors'])
    row.fillna('unknown', inplace=True)  # replacing NaN values with 'unknown'
    return row

# Load data from TSV file in chunks and convert 'vectors' column
print("Loading and converting data from the TSV file...")
chunks = pd.read_csv("embeddings.tsv", sep="\t", chunksize=1000)
data_to_upsert = []

with Progress() as progress:
    task = progress.add_task("[cyan]Processing...", total=sum(1 for row in open("embeddings.tsv", 'r')))

    for chunk in chunks:
        chunk = chunk.apply(convert_vectors, axis=1)
        for _, row in chunk.iterrows():
            data_to_upsert.append((str(row['id']), row['vectors'], {
                'wopeCat': row['wopeCat'],
                'googleCat': row['googleCat'],
                'openaiCat': row['openaiCat']}))
            progress.update(task, advance=1)

# Function to upsert data to Pinecone
def upsert_data(data):
    index.upsert(vectors=[data])

# Multi-threading for upsert
print("Upserting data to Pinecone...")
with ThreadPoolExecutor(max_workers=100) as executor:
    list(executor.map(upsert_data, data_to_upsert))

# Deinitialize Pinecone when done
print("Deinitializing Pinecone...")
pinecone.deinit()
