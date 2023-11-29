# HTX Technical Test

## Setup

## Task 2

This section outlines the implementation details of an Automatic Speech Recognition (ASR) microservice, as per the provided task instructions.

#### Folder Structure

- `asr/`: This directory contains all the code for the ASR task.
  - `asr_api.py`: The core file for the ASR microservice.
  - `asr.Dockerfile`: Used to containerize the ASR service.
  - `cv-decode.py`: Script to transcribe audio files from the Common Voice dataset.
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

#### Dockerization (`asr.Dockerfile`)

- Builds from `continuumio/miniconda3`.
- Sets `/usr/src/app` as the working directory.
- Copies the necessary files into the container.
- Installs dependencies, including `torchaudio`.
- Exposes port 8001.
- Sets the default environment and command for running the ASR service using Uvicorn.

#### Common Voice Dataset Processing (`cv-decode.py`)

- Reads `cv-valid-dev.csv` from the Common Voice dataset.
- Transcribes each audio file using the `/asr` endpoint.
- Adds the transcription as `generated_text` in the dataset.
- Saves the updated dataset with transcriptions.

#### Container Usage

- Build and run the container, ensuring it listens on port 8001.
- Utilize the `cv-decode.py` script to process the Common Voice dataset.