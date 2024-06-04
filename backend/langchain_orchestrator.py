import os
import json
import uuid
import logging
from ocr import process_presentation
from nvidia_api import process_with_nvidia_api
from google_tts import text_to_speech

def orchestrate_process(file_path, output_folder):
    logging.info("starting orchestration process for file: %s", file_path)
    
    # process the presentation to extract OCR results
    ocr_results_path = process_presentation(file_path)
    logging.info("OCR processing completed. Results saved to: %s", ocr_results_path)
    
    with open(ocr_results_path, 'r') as f:
        ocr_results = json.load(f)
    
    # process the OCR results with NVIDIA API
    nvidia_response = process_with_nvidia_api(ocr_results)
    nvidia_response_json = json.loads(nvidia_response)
    if "error" in nvidia_response_json:
        logging.error("NVIDIA API processing failed: %s", nvidia_response_json["error"])
        return {"error": "NVIDIA API processing failed"}
    
    # save the NVIDIA response
    nvidia_output_path = os.path.join(output_folder, f'{uuid.uuid4().hex}_nvidia_response.json')
    with open(nvidia_output_path, 'w') as f:
        json.dump(nvidia_response_json, f, indent=4)
    logging.info("NVIDIA API processing completed. Results saved to: %s", nvidia_output_path)
    
    # generate TTS from the NVIDIA response
    audio_path = os.path.join(output_folder, f'{uuid.uuid4().hex}.mp3')
    text_to_speech(nvidia_response_json, audio_path)
    
    logging.info("TTS processing completed. Audio file saved to: %s", audio_path)
    
    # return the results
    return {
        "message": "file uploaded successfully, OCR and NVIDIA processing finished.",
        "ocr_results": ocr_results_path,
        "nvidia_response": nvidia_output_path,
        "audio_path": audio_path
    }
