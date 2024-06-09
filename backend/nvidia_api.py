import os
import json
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv
import logging

# Load NVIDIA API key from environment variables
load_dotenv()
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

def initialize_nvidia_api():
    if not NVIDIA_API_KEY or not NVIDIA_API_KEY.startswith("nvapi-"):
        raise ValueError("Invalid or missing NVIDIA API key")

    llm = ChatNVIDIA(model="mistralai/mixtral-8x22b-instruct-v0.1", api_key=NVIDIA_API_KEY)
    return llm

def process_with_nvidia_api(combined_analysis, max_tokens=40536):
    try:
        llm = initialize_nvidia_api()

        instructions = """
        You are an AI presenter. You will be given a JSON formatted input where each entry represents a slide from a PowerPoint presentation.
        Each slide entry will have a slide number, text content extracted via OCR, and additional image analysis data from object detection.
        Your task is to generate an engaging, structured presentation script for each slide, going beyond just reading the text. The text that you generate will be read and presented by an autonomous AI agent entity. Your perspective for the presentation output is first person.
        Make sure to present the content in a way that is informative and engaging, similar to how a human presenter would use slide points to talk about the topic.
        Your output must be relevant to the content of the slides and the points that they're talking about, and you should be trying to "say something" with each slide that provides value to the listener. Verbosity is fine, but what output you do use needs to be relevant and useful to the listener. In other words, fluff for the sake of fluff is to be avoided.
        Please expand upon each slide with detailed explanations, historical context, examples, analogies, and any additional context that can make the presentation richer and more informative.
        Break down each point into smaller segments, discussing each aspect thoroughly.
        Be verbose and detailed in your explanations.
        Your output for presentation_text and slide_number MUST correspond 1:1 with the slide_number from your input. YOU MUST NOT create more slides than there are in the source input.
        Your output should be in JSON format, with each slide's content under a corresponding slide number.
        Example input:

        The input JSON will have data from three models: OCR (optical character recognition), object detection, and layout analysis. The 'bbox' fields represent bounding boxes for detected elements, given as [x1, y1, x2, y2] coordinates, indicating the region of the slide where each element is located.
        Example input:
        [
            {
                "slide_number": 1,
                "ocr_text": "Database Concepts\n\nNinth Edition\n\nChapter 6\n\nDatabase Administration\n\nDavid M. Kroenke\nScott L. Vandenberg\nRobert C. Yoder\n\n@ Pearson Copyright 2020, 2017, 2015 Pearson Education, Inc. All Rights Reserved",
                "image_analysis": {
                    "object_detection_model_description": "Detected 1 objects.",
                    "object_detection_tags": [
                        "person"
                    ],
                    "object_detection_objects": [
                        {
                            "name": "person",
                            "confidence": 0.9626411199569702,
                            "bbox": [
                                215.86947631835938,
                                155.97494506835938,
                                873.6431274414062,
                                705.0689086914062
                            ]
                        }
                    ],
                    "layout_analysis_results": [
                        {
                            "type": "title",
                            "bbox": [50, 50, 700, 100],
                            "text": [
                                {
                                    "text": "Database Concepts",
                                    "confidence": 0.98,
                                    "text_region": [
                                        [50, 50],
                                        [700, 50],
                                        [700, 100],
                                        [50, 100]
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "text",
                            "bbox": [50, 150, 700, 250],
                            "text": [
                                {
                                    "text": "Ninth Edition",
                                    "confidence": 0.95,
                                    "text_region": [
                                        [50, 150],
                                        [700, 150],
                                        [700, 200],
                                        [50, 200]
                                    ]
                                }
                            ]
                        }
                    ]
                }
            },
            {
                "slide_number": 2,
                "ocr_text": "Learning Objectives (1 of 2)\n\nUnderstand the need for and importance of database administration\nKnow basic administrative and managerial DBA functions\nUnderstand the need for concurrency control, security, and backup and recovery\nLearn about typical problems that can occur when multiple users process a database concurrently\nUnderstand the use of locking and the problem of deadlock\nLearn the difference between optimistic and pessimistic locking\nKnow the meaning of ACID transaction\nLearn the four 1992 ANSI standard isolation levels\nLearn different ways of processing a database using cursors.",
                "image_analysis": {
                    "object_detection_model_description": "Detected 0 objects.",
                    "object_detection_tags": [],
                    "object_detection_objects": [],
                    "layout_analysis_results": [
                        {
                            "type": "text",
                            "bbox": [50, 150, 700, 800],
                            "text": [
                                {
                                    "text": "Understand the need for and importance of database administration",
                                    "confidence": 0.98,
                                    "text_region": [
                                        [50, 150],
                                        [700, 150],
                                        [700, 200],
                                        [50, 200]
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        
        Example output:
        [
            {
                "slide_number": 1,
                "presentation_text": "Hello everyone, welcome to my presentation about <topic>. Let's begin by talking about the core concepts of database systems. In this session, we will dive into the world of databases, exploring their fundamental aspects and significance."
            },
            {
                "slide_number": 2,
                "presentation_text": "Let's start with today's learning objectives. We aim to understand the importance of database administration and the basic functions involved. Additionally, we'll discuss the necessity of concurrency control, security, and backup and recovery. We'll also explore common issues that arise with concurrent database access and the strategies to handle them, such as locking mechanisms and the distinction between optimistic and pessimistic locking. Finally, we'll cover ACID transactions, standard isolation levels, and various methods for database processing using cursors."
            }
        ]
        """

        prompt = instructions + "\nInput:\n" + json.dumps(combined_analysis, indent=4)
        print("Mixtral prompt:", prompt[:10000], "<...>")
        logging.debug("Sending the following prompt to NVIDIA API: {}".format(prompt[:500]))
        result = llm.invoke(prompt, temperature=0.7, top_p=0.9, max_tokens=max_tokens)
        return result.content
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        return {"error": "Invalid JSON format provided."}
    except Exception as e:
        logging.error(f"General error in NVIDIA API processing: {e}")
        return {"error": str(e)}
