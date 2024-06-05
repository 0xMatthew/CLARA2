import os
from google.cloud import texttospeech
from config import Config

def text_to_speech(nvidia_response_json, output_path):
    # ensure the environment variable for google credentials is set
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = Config.GOOGLE_APPLICATION_CREDENTIALS

    client = texttospeech.TextToSpeechClient()

    # extract text content from the json response
    text = "\n".join([slide["presentation_text"] for slide in nvidia_response_json if "presentation_text" in slide])

    synthesis_input = texttospeech.SynthesisInput(text=text)

    # use wavenet female voice for higher quality
    voice = texttospeech.VoiceSelectionParams(
        language_code=Config.GOOGLE_TTS_LANGUAGE_CODE,
        name=Config.GOOGLE_TTS_VOICE_NAME,
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    # set the audio encoding to linear16 for .wav format
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open(output_path, "wb") as out:
        out.write(response.audio_content)
        print(f'audio content written to file {output_path}')
