# Multi-threaded OpenAI Embedding Vector Generator

This script generates embeddings from text using multiple OpenAI endpoints. It supports multi-threading and can resume from previously processed data. It reads data from Excel, CSV, or JSON files and writes output to TSV, CSV, or JSON files.

## Requirements

- Python 3
- pandas
- requests
- openai
- tqdm

You can install the necessary libraries using pip:

```bash
pip install pandas requests openai tqdm
```

## Usage

You can run the script from the command line with the following arguments:

- `--input`: Path to the input file (Excel, CSV, or JSON format).
- `--output`: Path to the output file (TSV, CSV, or JSON format).
- `--config`: Path to the configuration file (JSON format).
- `--threads`: Number of worker threads (default is 50).
- `--batch-size`: Number of items to process before saving results (default is 100).
- `--retry-limit`: Number of times to retry on error (default is 5).

Here's an example of how to run the script:

```bash
python run.py --input input.xlsx --output output.tsv --config config.json --threads 100 --batch-size 200 --retry-limit 3
```

## Configuration File

The configuration file is a JSON file that contains the OpenAI endpoints and keys. It is useful when you need to setup multiple regions to avoid rate limit for millions of docs to get embed. 

Here's an example of what the configuration file might look like:

```json
{
  "openai_endpoints_and_keys": [
    ["https://xxx.openai.azure.com", "api_key_1", "embed"],
    ["https://xxx.openai.azure.com", "api_key_2", "embed"],
    ["https://xxx.openai.azure.com", "api_key_3", "embed"],
    ["https://xxx.openai.azure.com", "api_key_4", "embed"]
  ]
}
```

## Input File

The input file should be an Excel, CSV, or JSON file containing the text from which to generate embeddings. The script will dynamically handle the columns present in the input file.

## Output File

The output file will be a TSV, CSV, or JSON file containing the generated embeddings along with the original data. The script will create an additional `vectors` column for the embeddings.

## Progress

The script displays a progress bar while processing the documents. It also logs information about the processing status and any errors that occur.

![CleanShot 2023-10-04 at 11 01 12](https://github.com/yigitkonur/bulk-openai-embeddings-creator/assets/9989650/6e0baadd-de70-45b1-af44-928a1a72e261)
