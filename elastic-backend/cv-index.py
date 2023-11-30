# standard library imports
from io import StringIO
from typing import Any, Dict, Iterator, NoReturn
import logging
import os
import socket

# third party imports
from elasticsearch import Elasticsearch, helpers
import boto3
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Load environment variables and configurations
# Fallback to .env file for local deployment
if not os.getenv("ELASTIC_PASSWORD") or not os.getenv("HOST"):
    from dotenv import load_dotenv

    # Load environment variables from .env file
    load_dotenv()

password = os.getenv("ELASTIC_PASSWORD")
host = os.getenv("HOST")

# For local deployment, FILEPATH will be used
# For cloud deployment, BUCKET_NAME and FILE_KEY will be used
filepath = os.getenv("FILEPATH")
bucket_name = os.getenv("BUCKET_NAME")
file_key = os.getenv("FILE_KEY")

# Check if required configurations are available
if not all([password, host, filepath or (bucket_name and file_key)]):
    logger.error("Required configurations are missing")
    exit(1)  # Exit if configurations are incomplete


def log_dns_resolution(host: str) -> NoReturn:
    """
    Attempts to resolve the DNS for the given host and logs the result.

    This function tries to resolve the DNS for a specified hostname. If the resolution is successful,
    it logs the IP addresses associated with the host. If the resolution fails, it logs an error message.

    Args:
        host (str): The hostname for which DNS resolution is to be attempted.

    Raises:
        socket.gaierror: If there is an error in resolving the DNS for the host.
    """
    try:
        logger.info(f"Attempting DNS resolution for {host}")
        ip_addresses = socket.gethostbyname_ex(host)
        logger.info(f"DNS resolution successful: {ip_addresses}")
    except socket.gaierror as e:
        logger.error(f"DNS resolution failed for {host}: {e}")


# Function to read data from S3
def read_csv_from_s3(bucket: str, key: str) -> pd.DataFrame:
    """
    Reads a CSV file from an AWS S3 bucket and returns it as a pandas DataFrame.

    This function takes the name of an S3 bucket and a key (the path to the file within the bucket),
    uses the boto3 library to fetch the CSV file, and then converts it into a pandas DataFrame.

    Args:
        bucket (str): The name of the S3 bucket.
        key (str): The key (path) of the CSV file within the bucket.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the data from the CSV file.

    Raises:
        botocore.exceptions.NoCredentialsError: If credentials are not available or incorrect.
        botocore.exceptions.ClientError: If there is an error in fetching the object from S3.
        ValueError: If the CSV file cannot be decoded or parsed.
    """
    s3_client = boto3.client("s3")
    csv_obj = s3_client.get_object(Bucket=bucket, Key=key)
    body = csv_obj["Body"]
    csv_string = body.read().decode("utf-8")
    return pd.read_csv(StringIO(csv_string))


def generate_data(df: pd.DataFrame) -> Iterator[Dict[str, Any]]:
    """
    Generates a dictionary for each row in the provided DataFrame suitable for Elasticsearch indexing.

    This generator function iterates over each row in the DataFrame, processing it to create a dictionary
    that matches the schema required for Elasticsearch indexing. It yields a dictionary for each row. If any
    row raises an exception, it logs the error and re-raises the exception.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to be processed.

    Yields:
        Iterator[Dict[str, Any]]: A generator yielding dictionaries in the format required for Elasticsearch.

    Raises:
        Exception: If there is an error processing a row of the DataFrame.
    """
    for index, row in df.iterrows():
        try:
            yield {
                "_index": "cv-transcriptions",
                "_source": {
                    "generated_text": ""
                    if pd.isna(row["generated_text"])
                    else row["generated_text"],
                    "duration": None if pd.isna(row["duration"]) else row["duration"],
                    "age": None if pd.isna(row["age"]) else row["age"],
                    "gender": None if pd.isna(row["gender"]) else row["gender"],
                    "accent": None if pd.isna(row["accent"]) else row["accent"],
                },
            }
        except Exception as e:
            logger.info(f"Error processing row {index}: {e}")
            raise e  # Re-raise the exception to stop the script


def main():
    # Read CSV data from the appropriate source
    if filepath:  # If FILEPATH is provided, use it as the local path to the CSV.
        df = pd.read_csv(filepath)
    elif (
        bucket_name and file_key
    ):  # If BUCKET_NAME and FILE_KEY are provided, fetch the CSV from S3.
        df = read_csv_from_s3(bucket_name, file_key)
    else:
        raise ValueError("No valid source for CSV data provided.")

    # Establish ElasticSearch Connection
    es = Elasticsearch([host], basic_auth=("elastic", password), verify_certs=False)

    # Create an index if it doesn't exist
    if not es.indices.exists(index="cv-transcriptions"):
        es.indices.create(index="cv-transcriptions")

    try:
        # Bulk index data
        successes, failures = helpers.bulk(es, generate_data(df), stats_only=True)
        logger.info(f"Indexed {successes} documents with {failures} failures.")

    except helpers.BulkIndexError as e:
        logger.error(f"Bulk indexing failed with {len(e.errors)} errors")
        for error in e.errors:
            logger.error(error)


if __name__ == "__main__":
    main()
