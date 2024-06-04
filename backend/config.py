import os

class Config:
    UPLOAD_FOLDER = 'uploads'
    IMAGE_FOLDER = 'images'
    OUTPUT_FOLDER = 'outputs'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB limit

    # azure Computer Vision configuration
    AZURE_AI_SERVICES_KEY = os.getenv('AZURE_AI_SERVICES_KEY')
    AZURE_AI_SERVICES_ENDPOINT = os.getenv('AZURE_AI_SERVICES_ENDPOINT')
    AZURE_AI_SERVICES_REGION = os.getenv('AZURE_AI_SERVICES_REGION')
