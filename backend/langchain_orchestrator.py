import os
import json
import uuid
import logging
from ocr import process_presentation
from nvidia_api import process_with_nvidia_api
from google_tts import text_to_speech # uncomment this and comment out elevenlabs import if you prefer google_tts over elevenlabs
# from elevenlabs_tts import text_to_speech # uncomment this and comment out google_tts import if you prefer elevenlabs over google_tts
from azure_vision import get_image_analysis
from config import Config
from utils import wait_for_file

def orchestrate_process(file_path, output_folder):
    logging.info("Starting orchestration process for file: %s", file_path)
    
    # process the presentation to extract OCR results
    ocr_results_path, image_folder = process_presentation(file_path)
    
    if ocr_results_path is None:
        return {"error": "failed to process presentation for OCR."}

    logging.info("OCR processing completed. results saved to: %s", ocr_results_path)
    
    with open(ocr_results_path, 'r') as f:
        ocr_results = json.load(f)
    
    # process images with Azure Vision
    for slide in ocr_results:
        slide_number = slide["slide_number"]
        image_path = os.path.join(image_folder, f"slide_{slide_number - 1}.png")  # subtract 1 to match the zero-based index of the slide images
        
        # ensure the image file exists
        if wait_for_file(image_path):
            analysis = get_image_analysis(image_path)
            slide["image_analysis"] = analysis
            logging.info(f"processing image {image_path} with Azure Vision completed.")
        else:
            logging.error(f"Image {image_path} not found or not created.")
            slide["image_analysis"] = {}
    
    # save the combined results
    combined_results_path = os.path.join(output_folder, f'{uuid.uuid4().hex}_combined_results.json')
    with open(combined_results_path, 'w') as f:
        json.dump(ocr_results, f, indent=4)
    logging.info("combined OCR and image analysis results saved to: %s", combined_results_path)
    
    # process the OCR results with NVIDIA API
    nvidia_response = process_with_nvidia_api(ocr_results)
    
    # log the NVIDIA API response for debugging purposes
    logging.debug("NVIDIA API response: %s", nvidia_response)
    
    try:
        nvidia_response_json = json.loads(nvidia_response, strict=False)
    except json.JSONDecodeError as e:
        logging.error("failed to decode NVIDIA API response: %s", e)
        return {"error": "NVIDIA API processing failed"}
    
    # Save the NVIDIA response
    nvidia_output_path = os.path.join(output_folder, f'{uuid.uuid4().hex}_nvidia_response.json')
    with open(nvidia_output_path, 'w') as f:
        json.dump(nvidia_response_json, f, indent=4)
    logging.info("NVIDIA API processing completed. results saved to: %s", nvidia_output_path)
    
    # Generate TTS from the NVIDIA response
    audio_path = os.path.join(output_folder, f'{uuid.uuid4().hex}.wav')
    text_to_speech(nvidia_response_json, audio_path)
    
    logging.info("TTS processing completed. audio file saved to: %s", audio_path)
    
    # Return the results
    return {
        "message": "file uploaded successfully, OCR and NVIDIA processing finished.",
        "ocr_results": ocr_results_path,
        "combined_results": combined_results_path,
        "nvidia_response": nvidia_output_path,
        "audio_path": audio_path
    }
