import os
import logging
import json
import uuid
import time
from backend.ocr import process_presentation
from backend.nvidia_api import process_with_nvidia_api
from backend.google_tts import text_to_speech as google_text_to_speech
from backend.vision_analysis import get_image_analysis
from backend.config import Config
from backend.utils import wait_for_file
from backend.audio2face_module import push_audio_to_audio2face  # import the function

# set up logging
logging.basicConfig(level=logging.INFO)
ocr_logger = logging.getLogger('ppocr')
ocr_logger.setLevel(logging.WARNING)  # suppress debug logs from paddleocr

# ensure necessary directories exist
os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.IMAGE_FOLDER, exist_ok=True)
os.makedirs(Config.MODELS_FOLDER, exist_ok=True)

def generate_mixtral_text(slide_data, output_folder):
    combined_analysis = slide_data
    nvidia_response = process_with_nvidia_api(combined_analysis)
    
    logging.debug(f"nvidia api response: {nvidia_response}")
    
    try:
        nvidia_response_json = json.loads(nvidia_response, strict=False)
    except json.JSONDecodeError as e:
        logging.error(f"failed to decode nvidia api response: {e}")
        return {"error": "nvidia api processing failed"}
    
    nvidia_output_path = os.path.join(output_folder, f'{uuid.uuid4().hex}_nvidia_response.json')
    with open(nvidia_output_path, 'w') as f:
        json.dump(nvidia_response_json, f, indent=4)
    logging.info(f"nvidia api processing completed. results saved to: {nvidia_output_path}")
    
    return nvidia_response_json

def generate_tts_per_slide(nvidia_response_json, output_folder, pptx_filename):
    for slide in nvidia_response_json:
        slide_number = slide["slide_number"]
        audio_filename = f"{pptx_filename[:10]}-slide_audio{slide_number}.wav"
        audio_path = os.path.join(output_folder, audio_filename)
        logging.debug(f"generating tts for slide {slide_number} to {audio_path}")
        google_text_to_speech([slide], audio_path)
    logging.info("tts processing completed for all slides.")

def orchestrate_process(file_path, output_folder):
    logging.info(f"starting orchestration process for file: {file_path}")
    
    pptx_filename = os.path.basename(file_path)
    
    slide_data, image_folder = process_presentation(file_path)
    
    if slide_data is None:
        return {"error": "failed to process presentation for ocr."}

    logging.info("ocr processing completed.")
    
    logging.debug(f"initial slide data with ocr results: {json.dumps(slide_data, indent=4)}")
    
    for slide in slide_data:
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
    
    logging.debug(f"combined slide data with ocr and image analysis results: {json.dumps(slide_data, indent=4)}")
    
    combined_analysis_path = os.path.join(output_folder, f'{uuid.uuid4().hex}_combined_analysis.json')
    with open(combined_analysis_path, 'w') as f:
        json.dump(slide_data, f, indent=4)
    logging.info(f"combined ocr and image analysis results saved to: {combined_analysis_path}")
    
    nvidia_response_json = generate_mixtral_text(slide_data, output_folder)
    
    generate_tts_per_slide(nvidia_response_json, output_folder, pptx_filename)
    
    for slide in nvidia_response_json:
        slide_number = slide["slide_number"]
        audio_filename = f"{pptx_filename[:10]}-slide_audio{slide_number}.wav"
        audio_path = os.path.join(output_folder, audio_filename)
        
        logging.info(f"pushing audio for slide {slide_number} to audio2face.")
        
        instance_name = "/World/audio2face/PlayerStreaming"
        host_ip_address = os.getenv('HOST_IP_ADDRESS', 'localhost')
        push_audio_to_audio2face(audio_path, instance_name, url=f"{host_ip_address}:50051")
        
        logging.info(f"audio for slide {slide_number} pushed to audio2face.")
        
        delay = 3
        logging.info(f"sleeping for {delay} seconds.")
        
        time.sleep(delay)
    
    logging.info("all slides processed and audio pushed to audio2face.")
    
    return {
        "message": "presentation audio successfully generated and processed.",
        "combined_analysis": combined_analysis_path,
        "nvidia_response": nvidia_response_json
    }

if __name__ == "__main__":
    file_path = 'backend/uploads/KROENKE_3_SLIDES.pptx'
    output_folder = 'backend/outputs'
    orchestrate_process(file_path, output_folder)
