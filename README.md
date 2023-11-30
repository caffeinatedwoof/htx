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

## Task 4

This section outlines the implementation details of an Elasticsearch cluster, as per the provided task instructions.

#### Folder Structure

- `elastic-backend/`: This directory contains all the code for the task.
  - `docker-compose.yml`: Configuration for setting up a 2-node Elasticsearch cluster using Docker, specifying environment variables, network settings, and resource limits.
  - `cv-index.py`: Script to index `cs-valid-dev.csv` into the elasticsearch service

#### Docker-compose Configuration

- Elasticsearch Cluster Setup: Configured a 2-node Elasticsearch cluster using Docker.
- Container Names: Defined as elasticsearch1 and elasticsearch2.
- Volume Management: Specified esdata01 and esdata02 for persistent data storage.
- Port Configuration: Exposed Elasticsearch on the specified port ${ES_PORT}. (9200 for this assignment)
- Environment Variables: Set up necessary environment variables for node configuration, cluster setup, and CORS settings.
- Network Setup: Utilized a bridge network esnet for inter-container communication.
- Resource Limits: Applied memory limits and ulimit settings to manage resource usage.
- Health Checks: Included health checks to ensure the Elasticsearch service is running properly.

Notes:
- CORS (Cross-Origin Resource Sharing) Settings

   These CORS settings facilitate the communication between the Elasticsearch backend and the SearchUI frontend, ensuring that the browser's same-origin policy doesn't block the requests from the frontend to the Elasticsearch service.

- Using HTTP Instead of HTTPS

   Since this is for technical assessment, and not a production set-up, we focus on the functionality of the application rather than the security aspects. The configuration uses HTTP (with security.enabled=false) instead of HTTPS for simplicity and ease of set-up. It avoids the complexity of generating, managing, and configuring SSL/TLS certificates. However, we would definitely need to use HTTPS with proper security configurations for a production setup.


#### Elasticsearch Service Setup
Follow these instructions to spin up the Elasticsearch service using Docker Compose.

1. **Prerequisites**

- Docker and Docker Compose installed on your system.
- `.env` file with necessary environment variables (`ES_PORT`, `ELASTIC_PASSWORD`, `MEM_LIMIT`).

Note: For the purpose of this technical test, a sample `.env` file is included in the `elastic-backend` directory. This file is provided solely to demonstrate the setup process and facilitate ease of evaluation by the hiring panel.

2. **Navigate to the Directory**

   Change to the `elastic-backend` directory.
   ```bash
   cd elastic-backend
   ```

3. **Launch Elasticsearch Service**

   Run the following command to start the Elasticsearch cluster.
   ```bash
   docker-compose up -d
   ```
   This command will start the Elasticsearch nodes as defined in docker-compose.yml.

4. **Verify the Service**

   Check if the Elasticsearch nodes are running correctly.
   ```bash
   docker-compose ps
   ```

5. **Access Elasticsearch**

   Access the Elasticsearch service by visiting http://localhost:<ES_PORT>, where <ES_PORT> is the port number specified in your .env file.

6. **Stopping the Service**

   To stop the Elasticsearch service, use:
   ```bash
   docker-compose down
   ```

#### Running the 'cv-index.py' Script

1. **Prerequisites**

   Ensure Elasticsearch service is up and running as per the previous setup instructions.

2. **Environment Configuration**

   Make sure the `.env` file is correctly set up in the `elastic-backend` directory with all required environment variables (`ELASTIC_PASSWORD`, `HOST`, `FILEPATH`)

3. **Navigate to the Script Directory**
   Change to the directory containing `cv-index.py`.
   ```bash
   cd elastic-backend
4. **Run the script**
   ```bash
   python cv-index.py
   ```
   This command will start the process of reading the cs-valid-dev.csv file and indexing its content into the Elasticsearch service.

## Task 5

This section describes how to set up the Search UI for the Elasticsearch service to enable searching through indexed documents using various fields like `generated_text`, `duration`, `age`, `gender`, and `accent`.

#### Folder Structure

- `search-ui/`: This directory contains all the code and configurations for the Search UI application.
  - `public/`: Holds static files such as index.html and the assets used by the web application.
  - `src/`: Source directory containing React components, styles, and tests, including:
    - `App.css`: Stylesheet for the main App component.
    - `App.js`: The main React component that wraps the entire application.
    - `index.css`: Global stylesheet for the web application.
    - `index.js`: JavaScript entry point for React, where the App component is rendered.
    - `SearchPage.js`: React component for the search page functionality.
    - `searchStyles.css`: Stylesheet for the search page.
  - `docker-compose.yml:` Docker Compose configuration file to define and run multi-container Docker applications.
  - `package-lock.json:` Automatically generated file to lock down the versions of a package's dependencies.
  - `package.json:` Defines the project dependencies and metadata.

**Node.js Environment Setup**

To set up the Node.js environment, follow these steps:

1. **Install Node.js and npm**:
   - Download and install Node.js from the [official website](https://nodejs.org/).
   - npm is included with Node.js, so you'll have it once Node.js is installed.

2. **Verify Installation**:
   Verify that Node.js and npm are installed by running the following commands in your terminal:
   ```bash
   node --version
   npm --version
   ```

3. **Install Project Dependencies**
   Navigate to the search-ui directory and run the following command to install all the necessary dependencies:
   ```bash
   npm install
   ```
   This will read the package.json file and install all the required packages listed under dependencies and devDependencies.

#### Search-UI Service Setup

1. **Prerequisites**

- Docker and Docker Compose are installed on your system
- The Elasticsearch service is running and accessible at `http://localhost:9200/`
- Data has been indexed using the 'cv-index.py' script
- Node.js environment for running the build process of the Search UI


2. **Environment Variables**

- Create a `.env` file inside the `search-ui` directory with the following environment variables:
     - `REACT_APP_ELASTICSEARCH_USERNAME`: The username for Elasticsearch.
     - `REACT_APP_ELASTICSEARCH_PASSWORD`: The password for Elasticsearch.
     - `REACT_APP_ELASTICSEARCH_HOST`: The Elasticsearch host URL.

   A sample `.env.example` file has been provided for reference.

3. **Build and Run the Container**:
   From the root of the `search-ui` directory, run the following command to build and start the Search UI application:
   ```bash
   docker-compose up --build -d
   ```
   This will build the React application using the Dockerfile and serve it on `http://localhost:3000/`.

4. **Accessing the Search UI**

   After the build process completes and the container is running, open a web browser and navigate to `http://localhost:3000/` to access the Search UI. Use the SearchBox to perform searches, and filter results by age, gender, and accent.

