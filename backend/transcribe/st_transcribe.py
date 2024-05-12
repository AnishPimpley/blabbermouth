import streamlit as st
from audiorecorder import audiorecorder
import sys
sys.path.append("/home/anish_2204/repos/blabbermouth/")
from backend.transcribe.dg_transcribe import transcribe_audio
import time

st.title("Audio Recorder")
audio = audiorecorder("Click to record", "Click to stop recording")

start = time.time()
if len(audio) > 0:
    # To play audio in frontend:
    st.audio(audio.export().read())  

    # To save audio to a file, use pydub export method:
    audio.export("audio.wav", format="wav")

    # To get audio properties, use pydub AudioSegment properties:
    st.write(f"Frame rate: {audio.frame_rate}, Frame width: {audio.frame_width}, Duration: {audio.duration_seconds} seconds")
    
    transcript = transcribe_audio("audio.wav")  # Call the transcribe function
    st.write(f"transcript: {transcript}")