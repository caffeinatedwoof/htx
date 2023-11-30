FROM continuumio/miniconda3

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents and the environment.yml file into the container at /usr/src/app
COPY . .

# Use Conda to create a Python environment as per the environment.yml file
RUN conda env create -f environment.yml

# Make port 8001 available to the world outside this container
EXPOSE 8001

# Use the environment created by Conda as the default one
SHELL ["conda", "run", "-n", "htx-asr", "/bin/bash", "-c"]

# Define environment variable
ENV NAME asr-api

# The command to run the app using Uvicorn
CMD ["conda", "run", "-n", "htx-asr", "uvicorn", "asr_api:app", "--host", "0.0.0.0", "--port", "8001"]
