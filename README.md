Speech-to-Text API using Flask and Google Speech Recognition

Overview

This is a Flask-based API that accepts WebM audio files, converts them to WAV, splits them into chunks, and uses Google Speech Recognition to transcribe the audio into text.

Creating a Virtual Environment

It's highly recommended to create a virtual environment for this project to isolate the dependencies and avoid conflicts with other projects. Here's how to create a virtual environment:

Using venv (Python 3.x)
Open a terminal and navigate to the project directory.
Run python -m venv venv to create a new virtual environment named venv.
Activate the virtual environment by running source venv/bin/activate (on Linux/Mac) or venv\Scripts\activate (on Windows).
Install the required packages by running pip install -r requirements.txt.
Deactivate the virtual environment by running deactivate when you're done.
Using conda (optional)
Open a terminal and navigate to the project directory.
Run conda create --name myenv python to create a new virtual environment named myenv.
Activate the virtual environment by running conda activate myenv.
Install the required packages by running pip install -r requirements.txt.
Deactivate the virtual environment by running conda deactivate when you're done.

Installation

Install the required packages by running pip install -r requirements.txt
Make sure you have ffmpeg installed on your system.

Usage

Start the API by running python app.py
The API will be available at http://localhost:9090
Send a POST request to /media/upload with a WebM audio file attached as a form file named file.
The API will respond with a JSON object containing the transcribed text.

Configuration

The following configuration options are available:

UPLOAD_FOLDER: The folder where uploaded files will be stored. Defaults to /Users/deepakrawat/Desktop/Anusandhan/static.
NOTE: Change the path to your specific directory.
ALLOWED_EXTENSIONS: The allowed file extensions for uploads. Defaults to set(['webm']).
chunk_length_in_seconds: The length of each chunk in seconds. Defaults to 50.
Functions

The API uses the following functions:

allowed_file(filename): Checks if a file has an allowed extension.
convert_webm_to_wav(input_path, output_path): Converts a WebM file to WAV using ffmpeg.
split_audio_file(file_path, chunk_length_in_seconds): Splits a WAV file into chunks of a specified length.
save_chunks_as_wav_files(chunks, output_folder): Saves each chunk as a WAV file in the specified output folder.
speech_to_text(file_path): Uses Google Speech Recognition to transcribe a WAV file into text.
