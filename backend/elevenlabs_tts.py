import os
from elevenlabs.client import ElevenLabs
from langchain_community.tools.eleven_labs.text2speech import ElevenLabsText2SpeechTool

def text_to_speech(nvidia_response_json, output_path):
    # ensure the environment variable for Eleven Labs API key is set
    if "ELEVEN_API_KEY" not in os.environ:
        os.environ["ELEVEN_API_KEY"] = "your_elevenlabs_api_key"

    # extract text content from the JSON response
    text = "\n".join([slide["presentation_text"] for slide in nvidia_response_json if "presentation_text" in slide])

    # Initialize Eleven Labs client
    client = ElevenLabs(api_key=os.environ["ELEVEN_API_KEY"])

    # generate speech
    try:
        audio_stream = client.generate(text=text, voice="voice_id_you_want_to_use", model="eleven_multilingual_v2", stream=True)
        
        # save the generated audio to the specified path
        with open(output_path, "wb") as out:
            for chunk in audio_stream:
                out.write(chunk)
        print(f'audio content written to file {output_path}')
    except AttributeError as e:
        print(f"error: {e}")
        print("the 'generate' method is not available in the current version of ElevenLabs.")
        print("please ensure you are using a compatible version of the ElevenLabs package.")
    except Exception as e:
        print(f"an error occurred: {e}")
