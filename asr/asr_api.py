# standard library imports
from pathlib import Path
import shutil

# third party imports
from fastapi import FastAPI, File, UploadFile
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import librosa
import torch
import torchaudio

app = FastAPI()

# create temporary directory
try:
    Path("temp_files").mkdir(parents=True, exist_ok=True)
except Exception as e:
    print("Error in creating temporary directory")

# load model and processor
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")


@app.get("/ping")
async def ping():
    return {"message": "pong"}


@app.post("/asr")
async def asr_endpoint(file: UploadFile = File(...)):
    # Save temporary file locally
    temp_file_path = Path("temp_files") / file.filename
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Load and process the audio file
    audio_input, rate = torchaudio.load(temp_file_path)

    # Resample if necessary
    if rate != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=rate, new_freq=16000)
        audio_input = resampler(audio_input)

    # Prepare the input tensor
    input_values = processor(
        audio_input.squeeze(0).numpy(), sampling_rate=16000, return_tensors="pt"
    ).input_values

    # Perform inference
    with torch.no_grad():
        logits = model(input_values).logits

    # Decode the model output
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)

    # Calculate duration
    duration = librosa.get_duration(y=audio_input.numpy(), sr=16000)

    # Delete the file after processing
    try:
        temp_file_path.unlink()  # Delete the saved file
    except Exception as e:
        print(f"Error occurred while deleting the file: {e}")

    return {"transcription": transcription[0], "duration": f"{duration:.2f}"}
