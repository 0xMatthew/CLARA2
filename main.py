import os
import logging
import json
import uuid
import time
from backend.ocr import process_presentation
from backend.nvidia_api import process_with_nvidia_api
from backend.google_tts import text_to_speech as google_text_to_speech
# from backend.elevenlabs_tts import text_to_speech as elevenlabs_text_to_speech # uncomment this line if you want to use ElevenLabs for TTS
from backend.vision_analysis import get_image_analysis
from backend.config import Config
from backend.utils import wait_for_file
from backend.audio2face_module import push_audio_to_audio2face

# set up logging
logging.basicConfig(level=logging.INFO)
ocr_logger = logging.getLogger('ppocr')
ocr_logger.setLevel(logging.WARNING)  # Suppress debug logs from paddleocr

# ensure necessary directories exist
os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.IMAGE_FOLDER, exist_ok=True)
os.makedirs(Config.MODELS_FOLDER, exist_ok=True)

def process_batch(slide_data_batch, output_folder, pptx_filename, batch_num, state):
    if not state["should_continue"]:
        logging.info(f"Processing stopped at batch {batch_num}")
        return
    
    try:
        nvidia_response_json = json.loads(process_with_nvidia_api(slide_data_batch))
        if "error" in nvidia_response_json:
            logging.error(f"error processing batch {batch_num}: {nvidia_response_json['error']}")
            return

        generate_tts_per_slide(nvidia_response_json, output_folder, pptx_filename, state)
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error during batch processing: {e}")
    except Exception as e:
        logging.error(f"Failed to process batch {batch_num}: {e}")

def orchestrate_process(file_path, output_folder, state):
    logging.info(f"starting orchestration process for file: {file_path}")
    
    pptx_filename = os.path.basename(file_path)
    
    slide_data, image_folder = process_presentation(file_path)
    
    if slide_data is None:
        return {"error": "failed to process presentation for OCR."}

    logging.info("OCR processing completed.")
    
    for slide in slide_data:
        if not state["should_continue"]:
            logging.info("processing stopped.")
            return {"message": "processing stopped.", "status": "stopped"}

        slide_number = slide["slide_number"]
        image_path = os.path.join(image_folder, f"slide_{slide_number - 1}.png")
        
        if wait_for_file(image_path):
            analysis = get_image_analysis(image_path)
            slide["image_analysis"] = {k: v for k, v in analysis.items() if k != "ocr_text"}
            slide["text"] = analysis.get("ocr_text", slide["text"])
            logging.info(f"processing image {image_path} with vision analysis completed.")
        else:
            logging.error(f"image {image_path} not found or not created.")
            slide["image_analysis"] = {}

    # batch processing
    batch_size = 5
    num_batches = (len(slide_data) + batch_size - 1) // batch_size

    for batch_num in range(num_batches):
        if not state["should_continue"]:
            logging.info("Processing stopped.")
            return {"message": "processing stopped.", "status": "stopped"}
        
        slide_data_batch = slide_data[batch_num * batch_size:(batch_num + 1) * batch_size]
        process_batch(slide_data_batch, output_folder, pptx_filename, batch_num, state)

    logging.info("all batches processing completed.")
    state["current_slide"] = len(slide_data)  # update the state to reflect the completion

    return {
        "message": "presentation audio generation and processing completed.",
        "status": "completed",
    }

def generate_tts_per_slide(nvidia_response_json, output_folder, pptx_filename, state):
    for slide in nvidia_response_json:
        if not state["should_continue"]:
            logging.info("processing stopped.")
            return

        slide_number = slide["slide_number"]
        audio_filename = f"{pptx_filename[:10]}-slide_audio{slide_number}.wav"
        audio_path = os.path.join(output_folder, audio_filename)
        logging.debug(f"generating TTS for slide {slide_number} to {audio_path}")
        google_text_to_speech([slide], audio_path)
        #elevenlabs_text_to_speech([slide], audio_path) # uncomment this line and remove the google_text_to_speech call above in order to use ElevenLabs TTS in place of Google TTS
        logging.info(f"generated audio for slide {slide_number} at {audio_path}")
        # Push audio to Audio2Face
        push_audio_to_audio2face(audio_path, "/World/audio2face/PlayerStreaming")
    logging.info("TTS processing completed for all slides.")

if __name__ == "__main__":
    file_path = os.path.join(Config.UPLOAD_FOLDER, 'your_test_file.pptx')
    output_folder = Config.OUTPUT_FOLDER
    state = {
        "is_processing": False,
        "should_continue": True,
        "current_slide": 0
    }
    orchestrate_process(file_path, output_folder, state)
