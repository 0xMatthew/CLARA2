# CLARA 2 (Comprehensive Learning And Review Agent)

## Architecture Overview

CLARA 2 converts PowerPoint presentations into an AI-driven presentation by using OCR/object recognition, LangChain-orchestrated NVIDIA NIM Mixtral 8x22B API calls, text-to-speech, and animation systems. This document provides a detailed technical breakdown of the architecture and the workflow of CLARA 2.

### Components

1. **Frontend**:
    - The frontend files (`frontend/index.html` and `frontend/upload.js`) provide a simple HTML and JavaScript-based UI served by a Flask server. Users interact with this UI to upload their PowerPoint presentations.
    - Files are selected and uploaded through the web page, and user actions (like uploading a PowerPoint file) are handled by `upload.js`.

2. **Backend**:
    - The backend is separated into separate Python modules in the `backend` directory.

3. **Processing Pipeline**:
    - **Presentation Upload and Conversion**:
        - users upload a PowerPoint file, which is saved to a designated upload folder
        - the file is converted to a PDF using LibreOffice, and then each page of the PDF is converted to an image using ImageMagick
    - **OCR and Object Recognition**:
        - each slide image undergoes OCR processing using Tesseract and PaddleOCR to extract layout data so Mixtral has contextual information about the slides
        - object recognition is performed using the YOLO model to identify and label objects within the slide images
        - the results from OCR and object recognition are combined into a JSON object for each slide
    - **NVIDIA Mixtral API**:
        - a 5-slide-at-a-time combined analysis JSON batch is sent to the NVIDIA NIM Mixtral API for generating a structured presentation script
            - batches of 5 slides are used to prevent hitting the ~65k token Mixtral 8x22B context limit
        - the API returns a detailed script for each slide, which is then used for text-to-speech conversion
    - **Text-to-Speech (TTS)**:
        - the generated script is converted to audio using either Google TTS or ElevenLabs TTS (you can use ElevenLabs in place of Google TTS by modifying `main.py` by uncommenting the ElevenLabs lines and commenting out Google TTS lines).
        - the resulting audio files are stored and ready to be read by Audio2Face
    - **Audio2Face and Unreal Engine**:
        - the audio files are sent to NVIDIA Audio2Face, which can send realtime animation data to Unreal Engine
        - the animation data is streamed to Unreal Engine using LiveLink, which renders the final animated CLARA 2 presenter

### Backend Architecture

The backend of CLARA 2 consists of several Python modules, each handling different aspects of the processing pipeline. Here's an overview:

#### `app.py`

- The main Flask application file that handles the web server operations. The startup script `CLARA2.sh` launches the Flask application by running `backend/app.py`.
- **Functions**:
  - serves the frontend files (HTML, JS)
  - manages file uploads and stores the uploaded PowerPoint files
  - tracks and manages the state of the processing
  - provides endpoints to start processing and to stop/restart the Audio2Face service
  
#### `utils.py`

- Contains a single utility function
- **Functions**:
  - `wait_for_file`: waits for a specified file to exist within a given timeout period

#### `audio2face_module.py`

- Manages interactions with NVIDIA Audio2Face
- **Functions**:
  - `push_audio_to_audio2face`: sends audio data to the Audio2Face service for processing and animation
  - handles gRPC communication with the Audio2Face service

#### `ocr.py`

- Handles the OCR processing of PowerPoint slides
- **Functions**:
  - `process_presentation`: orchestrates the conversion of PowerPoint slides to images and processes each image with OCR
  - `convert_pdf_to_images`: converts a PDF file to a series of images
  - `process_images`: processes the images with OCR to extract text
  - `perform_ocr`: performs OCR on a single image using Tesseract

#### `config.py`

- Configuration settings for the backend
- **Functions**:
  - defines paths for various directories (uploads, images, outputs, models).
  - contains settings for OCR, TTS, and other services used in the processing pipeline

#### `audio2face_pb2.py` and `audio2face_pb2_grpc.py`

- Generated files from the gRPC protobuf definitions for interfacing with Audio2Face. These are already configured to work with this Audio2Face setup.
- **Functions**:
  - define the gRPC client and server classes
  - used to serialize and deserialize messages for gRPC communication

#### `vision_analysis.py`

- Performs vision analysis on slide images using YOLO and PaddleOCR
- **Functions**:
  - `initialize_yolo`: initializes the YOLO model for object detection
  - `initialize_ocr` and `initialize_layout`: initializes the OCR and layout analysis models
  - `analyze_image`: performs object detection on an image using YOLO
  - `extract_text_with_tesseract`: extracts text from an image using Tesseract
  - `layout_analysis`: analyzes the layout of text and elements within an image
  - `get_image_analysis`: combines the results of object detection, OCR, and layout analysis for a comprehensive image analysis

#### `google_tts.py`

- Manages text-to-speech conversion using Google Cloud TTS
- **Functions**:
  - `text_to_speech`: converts text to audio using Google Cloud TTS and saves the audio file to the specified path

#### `elevenlabs_tts.py`

- Manages text-to-speech conversion using ElevenLabs TTS
- **Functions**:
  - `text_to_speech`: converts text to audio using ElevenLabs API and saves the audio file to the specified path

#### `convert.py`

- Converts PowerPoint files to PDF
- **Functions**:
  - `convert_to_pdf`: uses LibreOffice to convert PowerPoint files to PDF format

#### `nvidia_api.py`

- Interfaces with the NVIDIA Mixtral API for generating presentation scripts
- **Functions**:
  - `initialize_nvidia_api`: initializes the LangChain-orchestrated NVIDIA Mixtral API client
  - `process_with_nvidia_api`: sends combined analysis data to the Mixtral API and receives a presentation script in response

#### `main.py`

- Orchestrates the end-to-end process from file upload to generating the final animated presentation
- **Functions**:
  - manages the state and progress of the entire processing pipeline
  - `process_batch`: processes a batch of slides, generating TTS audio and sending it to Audio2Face
  - `orchestrate_process`: coordinates the entire process, including OCR, object recognition, NVIDIA Mixtral API calls, TTS generation, and sending data to Audio2Face
  - `generate_tts_per_slide`: generates TTS audio for each slide using the Google Cloud TTS API and sends it to Audio2Face
