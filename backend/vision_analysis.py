import os
import json
import cv2
import torch
from ultralytics import YOLO
import pytesseract
from paddleocr import PPStructure, PaddleOCR
from PIL import Image
import logging
import numpy as np
from config import Config

# initialize yolo model
model_path = 'models/yolov8x.pt'
model_url = 'https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8x.pt'

def download_model(url, path):
    from urllib.request import urlretrieve
    logging.info(f"downloading model from {url} to {path}...")
    os.makedirs(os.path.dirname(path), exist_ok=True)  # ensure the directory exists
    urlretrieve(url, path)

def initialize_yolo():
    if not os.path.exists(model_path):
        logging.info("model file not found. downloading...")
        download_model(model_url, model_path)
    model = YOLO(model_path)
    model.to('cuda')
    return model

# initialize yolo model globally
yolo_model = initialize_yolo()

def initialize_ocr(use_gpu=Config.PADDLEOCR_USE_GPU):
    return PaddleOCR(use_angle_cls=Config.PADDLEOCR_USE_ANGLE_CLS, lang=Config.PADDLEOCR_LANG, use_gpu=use_gpu, use_cudnn=Config.PADDLEOCR_USE_CUDNN)

def initialize_layout(use_gpu=Config.PADDLEOCR_USE_GPU):
    return PPStructure(recovery=False, layout=True, table=True, ocr=True, use_gpu=use_gpu, use_cudnn=Config.PADDLEOCR_USE_CUDNN)

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        logging.error(f"failed to read image: {image_path}")
        return None
    if len(img.shape) == 2:  # grayscale
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    elif img.shape[2] == 4:  # rgba
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    return img

def analyze_image(image_path):
    img = preprocess_image(image_path)
    if img is None:
        return {}

    # yolo analysis
    yolo_results = yolo_model(img)

    logging.info(f"yolo results: {yolo_results}")

    # access the names directly from the model
    class_names = yolo_model.names

    # check for detections and log detailed information
    if yolo_results[0].boxes is not None:
        boxes = yolo_results[0].boxes
        classes = boxes.cls.cpu().numpy() if boxes.cls is not None else []
        confidences = boxes.conf.cpu().numpy() if boxes.conf is not None else []

        logging.info(f"classes detected: {classes}")
        logging.info(f"confidences: {confidences}")

        tags = [class_names[int(cls)] for cls in classes]
        objects = [{'name': class_names[int(cls)], 'confidence': float(conf), 'bbox': box.tolist()}
                   for box, cls, conf in zip(boxes.xyxy.cpu().numpy(), classes, confidences)]

        # draw bounding boxes on the image
        for box in boxes.xyxy.cpu().numpy():
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # save the annotated image for verification
        annotated_image_path = f"{os.path.splitext(image_path)[0]}_annotated.png"
        cv2.imwrite(annotated_image_path, img)
        logging.info(f"saved annotated image to {annotated_image_path}")

    else:
        tags = []
        objects = []

    return {
        "object_detection_model_description": f"detected {len(objects)} objects.",
        "object_detection_tags": tags,
        "object_detection_objects": objects,
    }

def extract_text_with_tesseract(image_path):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return text
    except Exception as e:
        logging.error(f"error during tesseract ocr extraction: {e}")
        return ""

def layout_analysis(image_path, use_gpu=Config.PADDLEOCR_USE_GPU):
    layout = initialize_layout(use_gpu=use_gpu)
    img = preprocess_image(image_path)
    if img is None:
        return []
    try:
        result = layout(img)
        logging.debug(f"ppstructure result: {result}")
        layout_results = []
        for item in result:
            if 'type' in item and 'bbox' in item:
                layout_results.append({
                    'type': item['type'],
                    'bbox': item['bbox'],
                    'text': item['res'] if 'res' in item else []
                })
        return layout_results
    except Exception as e:
        logging.error(f"error during layout analysis: {e}")
        return []

def get_image_analysis(image_path, use_gpu=Config.PADDLEOCR_USE_GPU):
    analysis = analyze_image(image_path)
    text_results = extract_text_with_tesseract(image_path)
    layout_results = layout_analysis(image_path, use_gpu=use_gpu)

    analysis["ocr_text"] = text_results
    analysis["layout_analysis_results"] = layout_results

    return analysis
