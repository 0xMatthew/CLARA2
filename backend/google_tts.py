import os
from google.cloud import texttospeech

def text_to_speech(nvidia_response_json, output_path):
    # ensure the environment variable for Google credentials is set
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/your/service-account-file.json"

    client = texttospeech.TextToSpeechClient()

    # extract text content from the JSON response
    text = "\n".join([slide["presentation_text"] for slide in nvidia_response_json if "presentation_text" in slide])

    synthesis_input = texttospeech.SynthesisInput(text=text)

    # use Wavenet female voice for higher quality
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Wavenet-F",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    # set the audio encoding to LINEAR16 for .wav format
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open(output_path, "wb") as out:
        out.write(response.audio_content)
        print(f'audio content written to file {output_path}')
