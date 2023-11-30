import os
import requests
import pandas as pd

# Set the base URL for ASR API
asr_api_url = "http://localhost:8001/asr"

# Path to the dataset folder
dataset_folder = "data/common_voice/"

# Filenames
input_csv_filename = "cv-valid-dev.csv"
output_csv_filename = "updated_cv-valid-dev.csv"

# Read the CSV file
df = pd.read_csv(os.path.join(dataset_folder, input_csv_filename))


# Function to transcribe the audio file
def transcribe_audio(file_path):
    try:
        with open(file_path, "rb") as file:
            response = requests.post(asr_api_url, files={"file": file})
            response.raise_for_status()  # Raises an HTTPError for bad responses

            # Handle non-JSON responses (optional)
            try:
                response_data = response.json()
                if "transcription" in response_data:
                    return response_data["transcription"]
                else:
                    print(f"Transcription not found in response for file {file_path}")
                    return None
            except ValueError:
                print(f"Invalid JSON response for file {file_path}")
                return None

    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
        return None
    except IOError as io_err:
        print(f"Error occurred while reading the file {file_path}: {io_err}")
        return None

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - {response.text}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except Exception as err:
        print(f"An unexpected error occurred: {err}")

    return None


# Transcribe each audio file and add the transcription to the DataFrame
transcriptions = []
for index, row in df.iterrows():
    audio_file = os.path.join(dataset_folder + "cv-valid-dev", row["filename"])
    transcription = transcribe_audio(audio_file)
    transcriptions.append(transcription)

# Add the transcriptions as a new column
df["generated_text"] = transcriptions

# Save the updated DataFrame to a new CSV file
df.to_csv(os.path.join(dataset_folder, output_csv_filename), index=False)
