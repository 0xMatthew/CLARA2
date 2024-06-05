import os

class Config:
    UPLOAD_FOLDER = 'uploads'
    IMAGE_FOLDER = 'images'
    OUTPUT_FOLDER = 'outputs'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB limit
    
    GOOGLE_APPLICATION_CREDENTIALS = '/path/to/your/service-account-file.json'
    GOOGLE_TTS_LANGUAGE_CODE = 'en-US'
    GOOGLE_TTS_VOICE_NAME = 'en-US-Wavenet-F'
    GOOGLE_TTS_SSML_GENDER = 'FEMALE'
    GOOGLE_TTS_AUDIO_ENCODING = 'LINEAR16'
    
    PDF_CONVERSION_DENSITY = '150'
    PDF_CONVERSION_FORMAT = 'png'
    
    OCR_TIMEOUT = 60  # seconds
    OCR_MAX_WORKERS = min(8, os.cpu_count() - 1)
    
    NVIDIA_MODEL_NAME = 'mistralai/mixtral-8x22b-instruct-v0.1'
    PADDLEOCR_USE_GPU = True
    PADDLEOCR_LANG = 'en'
    PADDLEOCR_USE_ANGLE_CLS = True
    PADDLEOCR_USE_CUDNN = True
