import streamlit as st
from audiorecorder import audiorecorder
import sys
sys.path.append("/home/anish_2204/repos/blabbermouth/")
from backend.transcribe.dg_transcribe import transcribe_audio
import time
import streamlit_shortcuts
# backend/blabbermouth_llm/llm_helper.py
from backend.blabbermouth_llm.llm_helper import get_tasks_from_transcript, update_whiteboard_state_by_tasks
from backend.blabbermouth_llm.base_models import StickyNoteShape, RectangleShape, TextBoxShape, ArrowShape, EllipseShape
import pprint
from time import strftime
import uuid

st.title("Audio Recorder")
audio = audiorecorder("RECORD", "STOP")

current_white_board_state = [
StickyNoteShape(x = 500, y = 500, width = 100, height = 100, text = "Hello World 1"),
StickyNoteShape(x = 500, y = 600, width = 100, height = 100, text = "Hello World 2"),
RectangleShape(x = 500, y = 700, width = 100, height = 100)
]
cursor_position = (400.0,600.0)
st.write(f"Current Whiteboard State: {pprint.pformat(current_white_board_state, indent=4)}")
start = time.time()
if len(audio) > 0:
    print(f"len audio: {len(audio)}")
    # To play audio in frontend:
    audio_file_name = f"audio + {strftime('%Y%m%d-%H%M%S')}.wav"  
    st.audio(audio.export().read())  

    # To save audio to a file, use pydub export method:
    audio.export(audio_file_name, format="wav")

    # To get audio properties, use pydub AudioSegment properties:
    st.write(f"Frame rate: {audio.frame_rate}, Frame width: {audio.frame_width}, Duration: {audio.duration_seconds} seconds")
    
    transcript = transcribe_audio(audio_file_name)  # Call the transcribe function
    st.write(f"transcript: {transcript}")
    tasks = get_tasks_from_transcript(transcript, current_white_board_state, cursor_position)
    st.write(f"tasks: {tasks}")
    current_white_board_state = update_whiteboard_state_by_tasks(tasks, current_white_board_state, cursor_position)
    st.write(f"Current Whiteboard State: {pprint.pformat(current_white_board_state, indent=4)}")
    end = time.time()
    st.write(f"Time taken: {end-start} seconds")