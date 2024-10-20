import os
import pandas as pd
import whisper
import re
#-----------------------------------------------------------------------------

from flask import Flask, render_template, redirect, url_for
import pyaudio
import wave
import threading
import time

app = Flask(__name__)

# Audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 10
OUTPUT_FILENAME = "recorded_audio.wav"

# def record_audio():
#     audio = pyaudio.PyAudio()
    
#     # Start recording
#     stream = audio.open(format=FORMAT, channels=CHANNELS,
#                         rate=RATE, input=True,
#                         frames_per_buffer=CHUNK)
    
#     print("Recording started...")
#     frames = []

#     for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#         data = stream.read(CHUNK)
#         frames.append(data)

#     # Stop recording
#     stream.stop_stream()
#     stream.close()
#     audio.terminate()

#     # Save the recording
#     with wave.open(OUTPUT_FILENAME, 'wb') as wf:
#         wf.setnchannels(CHANNELS)
#         wf.setsampwidth(audio.get_sample_size(FORMAT))
#         wf.setframerate(RATE)
#         wf.writeframes(b''.join(frames))

#     print(f"Recording saved as {OUTPUT_FILENAME}")

#-----------------------------------------------------------------------------
# Load data
df_c = pd.read_excel(r"C:\Users\tanma\Downloads\data (1).xlsx")

# Function to print n choose k
# for permutation
def print_n_choose_k(n, k):
    superscript_digits = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    subscript_digits = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    n_str = str(n).translate(superscript_digits)
    k_str = str(k).translate(subscript_digits)
    return f"{n_str}P{k_str}"

# Combinations
def print_combi(n, k):
    superscript_digits = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    subscript_digits = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    n_str = str(n).translate(superscript_digits)
    k_str = str(k).translate(subscript_digits)
    return f"{n_str}C{k_str}"

# Integration
def print_integral(n, k):
    superscript_digits = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    subscript_digits = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    n_str = str(n).translate(subscript_digits)
    k_str = str(k).translate(superscript_digits)
    return f"{n_str}{chr(0x222B)}{k_str}"

# Function to escape special characters
def escape_special_characters(text):
    escaped_text = re.escape(text)
    return escaped_text

# Function to convert audio to equation using Whisper
def from_audio_equation(audio_file):
    # Load Whisper model
    model = whisper.load_model("base")  # Use 'base', 'small', 'medium', or 'large' based on your system's capacity
    
    # Save the uploaded file temporarily
    audio_file_path = r"C:\Users\tanma\OneDrive\Documents\Sound Recordings\Recording.wav"
    with open(audio_file_path, "wb") as f:
        f.write(audio_file.getbuffer())

    # Transcribe audio using Whisper
    result = model.transcribe(audio_file_path)
    text = result['text']

    print("Recognized Text:", text)
    process_text_to_equation(text)

    os.remove(audio_file_path)

# Function to convert speech from the microphone using Whisper
def from_microphone():
    audio = pyaudio.PyAudio()
    
    # Start recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    
    print("Recording started...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    # Stop recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recording
    with wave.open(OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"Recording saved as {OUTPUT_FILENAME}")
    
    # Load Whisper model
    model = whisper.load_model("base")  # Use 'base', 'small', 'medium', or 'large'

    # Record audio from the microphone
    print("Say something... (this will record for 10 seconds)")
      
    
    # Transcribe audio using Whisper
    result = model.transcribe("OUTPUT_FILENAME")
    text = result['text']

    print("Recognized Text:", text)
    process_text_to_equation(text)

    os.remove("OUTPUT_FILENAME")

# Function to process the recognized text and convert it into a mathematical equation
def process_text_to_equation(text):
    text_lower = text.lower().split()  # Split the recognized text into words
    equation = ''
    skip_next_words = False

    i = 0
    while i < len(text_lower):
        word = text_lower[i]
        escaped_word = escape_special_characters(word)
        if df_c['Name'].str.contains(escaped_word, case=False).any():
            remaining_text = ' '.join(text_lower[i:])
            
            # Check if the remaining text matches any name in the DataFrame
            for j in range(len(remaining_text.split()), 0, -1):
                str_to_check = ' '.join(remaining_text.split()[:j])
                if str_to_check in df_c['Name'].str.lower().values:
                    if str_to_check == "to the power":
                        i += 3
                        if text_lower[i] == "2":
                            equation += chr(0x00B0 + int(text_lower[i]))
                        elif text_lower[i] == "3":
                            equation += chr(0x00B0 + int(text_lower[i]))
                        else:
                            equation += chr(0x2070 + int(text_lower[i]))
                        i += 1
                    elif str_to_check == "raised to":
                        i += 2
                        if text_lower[i] == "2":
                            equation += chr(0x00B0 + int(text_lower[i]))
                        elif text_lower[i] == "3":
                            equation += chr(0x00B0 + int(text_lower[i]))
                        else:
                            equation += chr(0x2070 + int(text_lower[i]))
                        i += 1
                    elif str_to_check == "square":
                        equation += chr(0x00B0 + int(2))
                        i += 1
                    elif str_to_check == "cube":
                        equation += chr(0x00B0 + int(3))
                        i += 1
                    elif str_to_check == "permutation":
                        var = print_n_choose_k(equation[-2], text_lower[i + 1])
                        equation = equation.replace(equation[-2], var, 1)
                        i += 2
                    elif str_to_check == "combination":
                        var = print_combi(equation[-2], text_lower[i + 1])
                        equation = equation.replace(equation[-2], var, 1)
                        i += 2
                    elif str_to_check == "integral":
                        var = print_integral(equation[-2], text_lower[i + 1])
                        equation = equation.replace(equation[-2], var, 1)
                        i += 2
                    else:
                        equation += df_c.loc[df_c['Name'].str.lower() == str_to_check, 'Symbol'].values[0] + ' '
                        i += len(str_to_check.split())
                    skip_next_words = True
                    break
        if not skip_next_words:
            equation += word + ' '
            i += 1
        else:
            skip_next_words = False

    print("Equation:", equation.strip())

# # Main function
# def main():
#     while True:
#         print("1. Convert from audio file")
#         print("2. Use microphone")
#         print("3. Exit")
#         choice = input("Choose an option: ")

#         if choice == '1':
#             audio_file_path = input("Enter the path to your audio file: ")
#             if os.path.exists(audio_file_path):
#                 with open(audio_file_path, 'rb') as audio_file:
#                     from_audio_equation(audio_file)
#             else:
#                 print("File not found. Please try again.")
#         elif choice == '2':
#             from_microphone()
#         elif choice == '3':
#             print("Exiting...")
#             break
#         else:
#             print("Invalid choice. Please select again.")

@app.route('/')
def index(equation=None):
    return render_template('index.html', equation=equation)

@app.route('/record')
def record():
    # Record audio in a separate thread
    equation = from_microphone()
    return render_template('index.html', equation=equation)

if __name__ == '__main__':
    app.run(debug=True)

