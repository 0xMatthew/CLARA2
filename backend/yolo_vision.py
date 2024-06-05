# import os
# import json
# import cv2
# import torch
# from ultralytics import YOLO
# import pytesseract
# from PIL import Image
# import logging

# model_path = 'models/yolov8x.pt'
# model_url = 'https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8x.pt'

# def download_model(url, path):
#     from urllib.request import urlretrieve
#     logging.info(f"downloading model from {url} to {path}...")
#     urlretrieve(url, path)

# def initialize_yolo():
#     if not os.path.exists(model_path):
#         logging.info("model file not found. Downloading...")
#         download_model(model_url, model_path)
#     model = YOLO(model_path)
#     model.to('cuda')
#     return model

# def analyze_image(image_path):
#     model = initialize_yolo()
#     results = model(image_path)

#     logging.info(f"YOLO results: {results}")

#     # access the names directly from the model
#     class_names = model.names

#     # check for detections and log detailed information
#     if results[0].boxes is not None:
#         boxes = results[0].boxes
#         classes = boxes.cls.cpu().numpy() if boxes.cls is not None else []
#         confidences = boxes.conf.cpu().numpy() if boxes.conf is not None else []

#         logging.info(f"classes detected: {classes}")
#         logging.info(f"confidences: {confidences}")

#         tags = [class_names[int(cls)] for cls in classes]
#         objects = [{'name': class_names[int(cls)], 'confidence': float(conf), 'bbox': box.tolist()}
#                    for box, cls, conf in zip(boxes.xyxy.cpu().numpy(), classes, confidences)]

#         # draw bounding boxes on the image
#         img = cv2.imread(image_path)
#         for box in boxes.xyxy.cpu().numpy():
#             x1, y1, x2, y2 = map(int, box)
#             cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

#         # save the annotated image for verification
#         annotated_image_path = f"{os.path.splitext(image_path)[0]}_annotated.png"
#         cv2.imwrite(annotated_image_path, img)
#         logging.info(f"saved annotated image to {annotated_image_path}")

#     else:
#         tags = []
#         objects = []

#     return {
#         "description": f"detected {len(objects)} objects.",
#         "tags": tags,
#         "objects": objects,
#     }

# def extract_text(image_path):
#     text = pytesseract.image_to_string(Image.open(image_path))
#     return text

# def get_image_analysis(image_path):
#     analysis = analyze_image(image_path)
#     text_results = extract_text(image_path)

#     analysis["text"] = text_results

#     return analysis
