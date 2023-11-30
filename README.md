# HTX Technical Test

## Setup Instructions

#### Clone the Repository:

First, clone the Git repository to your local machine.
```bash
git clone https://github.com/caffeinatedwoof/htx.git
```

After cloning, navigate into the repository's directory:
```bash
cd htx
```

#### Installing and Setting up Conda:

**Install Conda (if not already installed):**
If Conda is not installed on your machine, download and install it from [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/) or [Anaconda](https://www.anaconda.com/download).

**Create and Activate the Conda Environment:**
In the root directory of the cloned repository, where the environment.yml file is located, create a new Conda environment:
```bash
conda env create -f environment.yml
```

This will install all necessary dependencies as specified in environment.yml.

Activate the newly created environment:
```bash
conda activate htx
```

## Task 2

This section outlines the implementation details of an Automatic Speech Recognition (ASR) microservice, as per the provided task instructions.

#### Folder Structure

- `asr/`: This directory contains all the code for the ASR task.
  - `asr_api.py`: The core file for the ASR microservice.
  - `cv-decode.py`: Script to transcribe audio files from the Common Voice dataset.
  - `asr.Dockerfile`: Used to containerize the ASR service.
  - `environment.yml`: Environment configuration for containerised microservice.
  - `data`: Folder for common voice dataset. Only cv-valid-dev.csv and updated_csv-valid-dev.csv are uploaded for ease of assessment by the hiring panel.

#### ASR Microservice (`asr_api.py`)

1. **Model and Processor Initialization**:
   - Utilizes `Wav2Vec2Processor` and `Wav2Vec2ForCTC` from `transformers`.
   - Model and processor are loaded from `facebook/wav2vec2-large-960h`.

2. **Endpoints**:
   - `/ping`: GET request endpoint returning a `{"message": "pong"}` response. Used to verify the service's operational status.
   - `/asr`: POST request endpoint for audio file transcription.

3. **ASR Endpoint Process**:
   - Receives an MP3 file and loads it using `torchaudio`.
   - Resamples the audio to 16kHz if necessary.
   - Processes the audio to input tensor format.
   - Performs model inference to get logits.
   - Decodes the logits to text and calculates the audio duration.
   - Returns the transcription and duration as JSON.

#### Common Voice Dataset Processing (`cv-decode.py`)

- Reads `cv-valid-dev.csv` from the Common Voice dataset.
- Transcribes each audio file using the `/asr` endpoint.
- Adds the transcription as `generated_text` in the dataset.
- Saves the updated dataset with transcriptions.

#### Dockerization (`asr.Dockerfile`)

- Builds from `continuumio/miniconda3`.
- Sets `/usr/src/app` as the working directory.
- Copies the necessary files into the container.
- Installs dependencies, including `torchaudio`.
- Exposes port 8001.
- Sets the default environment and command for running the ASR service using Uvicorn.

#### Instructions for Running asr_api.py and cv-decode.py

1. Start the FastAPI App:

   Navigate to the `asr` directory and start the FastAPI server:
   ```bash
   uvicorn asr_api:app --reload --host 0.0.0.0 --port 8001
This command starts the ASR service on `localhost` at port `8001`.

2. Running `cv-decode.py`
   - Download the Common Voice dataset as specified in the task instructions.
   - Ensure the dataset is located in the `data/common_voice/` directory, or update the `dataset_folder` variable in `cv-decode.py` to match the location of your dataset.
   - Run `cv-decode.py` to process the audio files and generate transcriptions:
   ```bash
   python cv-decode.py
#### Building and Running the Docker Container

1. **Build the Docker Image**:
   Navigate to the directory containing the `Dockerfile` and run:
   ```bash
   docker build -f asr.Dockerfile -t asr-api .
This command builds the Docker image with the tag asr-api.

2. **Run the Docker Container**
   To start the container, run:
   ```bash
   docker run -p 8001:8001 asr-api
This command runs the container and maps port 8001 of the container to port 8001 on the host machine, allowing access to the microservice.

3. **Transcribe an Audio File**
   With the Docker container running, you can now send a MP3 file to the service for transcription:
   - **Prepare your MP3 File**: Ensure that your MP3 file is accessible on your machine and note its file path.
   - **Send the File for Transcription**: Use the following curl command in the terminal, replacing <path-to-your-mp3-file> with the actual file path of your MP3 file:
   ```bash
   curl -F 'file=@<path-to-your-mp3-file>' http://localhost:8001/asr
This command sends the MP3 file to the ASR service, which processes the file, returns the transcription and duration, and then deletes the file.

4. **Receive Transcription and Duration**
   The response from the service will be in JSON format containing the transcription and the duration of the audio file.
   Example of a response:
   ```bash
   {
     "transcription": "Your transcribed text",
     "duration": "10.5"
   }
Notes:
- After spinning up the Docker container, it takes about a minute to download the model and processor before the app is ready for transcription requests.
- The app creates a copy of the uploaded file in a temporary location on your server and then deletes that copy after processing. This ensures that no residual data remains on the server after the file is processed, ensuring data privacy and server resource management.