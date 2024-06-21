import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from pydub import AudioSegment
import ffmpeg
import speech_recognition as sr
from flask_cors import CORS 

UPLOAD_FOLDER = "/Users/deepakrawat/Desktop/Anusandhan/static"
ALLOWED_EXTENSIONS = set(['webm'])

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to allow webm files
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to convert webm to wav using ffmpeg
def convert_webm_to_wav(input_path, output_path):
    ffmpeg.input(input_path).output(output_path, y='-y').run()
    

# Function to split audio into chunks
def split_audio_file(file_path, chunk_length_in_seconds):
    audio = AudioSegment.from_wav(file_path)
    chunks = []
    
    for i in range(0, len(audio), chunk_length_in_seconds * 1000):
        chunk = audio[i:i + chunk_length_in_seconds * 1000]
        chunks.append(chunk)
        
    return chunks

# Function to save each chunk of the audio as a file in the output folder
def save_chunks_as_wav_files(chunks, output_folder):
    for i, chunk in enumerate(chunks):
        output_file_path = f"{output_folder}/chunk_{i}.wav"
        chunk.export(output_file_path, format="wav")

# Function using Google speech recognition to convert audio to text
def speech_to_text(file_path):
    audio = AudioSegment.from_wav(file_path)
    audio.export("temp.wav", format="wav")
    
    recognizer = sr.Recognizer()
    with sr.AudioFile("temp.wav") as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)

    return text

@app.route('/media/upload', methods=['POST'])
def upload_media():
    if 'file' not in request.files:
        return jsonify({'error': 'media not provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'invalid file'}), 400

    filename = secure_filename(file.filename)
    file_path_webm = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_path_wav = os.path.join(app.config['UPLOAD_FOLDER'], 'output.wav')

    # Save the WebM file
    file.save(file_path_webm)

    # Convert WebM to WAV using ffmpeg
    convert_webm_to_wav(file_path_webm, file_path_wav)

    # Split the WAV file into chunks
    chunk_length_in_seconds = 50
    chunks = split_audio_file(file_path_wav, chunk_length_in_seconds)

    # Save chunks as WAV files
    output_folder = "/Users/deepakrawat/Desktop/Anusandhan/static"
    save_chunks_as_wav_files(chunks, output_folder)

    # Perform speech-to-text on each chunk
    result = ""
    for i, chunk in enumerate(chunks):
        file_path_chunk = f"{output_folder}/chunk_{i}.wav"
        text = speech_to_text(file_path_chunk)
        result += text

    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True, port=9090)
