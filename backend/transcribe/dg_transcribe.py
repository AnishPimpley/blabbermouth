import os

from deepgram import (
    DeepgramClient,
    FileSource,
    PrerecordedOptions,
)
from pydub import AudioSegment

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("DG_API_KEY")
# "d7d7fe5989ff12ceb60d97b0fab699b69c497e16"


def transcribe_audio(audio_file_path, api_key=API_KEY):
    try:
        # STEP 1 Create a Deepgram client using the API key
        deepgram_inst = DeepgramClient(API_KEY)

        with open(audio_file_path, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        # STEP 2: Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
        )

        # STEP 3: Call the transcribe_file method with the text payload and options
        response = deepgram_inst.listen.prerecorded.v("1").transcribe_file(payload, options)

        # STEP 4: Print the response
        # print(response.to_json(indent=4))

    except Exception as e:
        print(f"Exception: {e}")

    return response.results.channels[0].alternatives[0].transcript

def get_last_x_seconds_of_audio(x, # in seconds
                                audio_file_path,
                                output_audio_file_name="clipped_audio.wav"):
    new_audio = AudioSegment.from_wav(audio_file_path)
    new_audio = new_audio[-x * 1000:]
    new_audio.export(output_audio_file_name, format="wav")
    return output_audio_file_name