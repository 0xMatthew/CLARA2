import os
import json
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv

# load NVIDIA API key from environment variables
load_dotenv()
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

def initialize_nvidia_api():
    if not NVIDIA_API_KEY or not NVIDIA_API_KEY.startswith("nvapi-"):
        raise ValueError("Invalid or missing NVIDIA API key")

    llm = ChatNVIDIA(model="mistralai/mixtral-8x22b-instruct-v0.1")
    return llm

def process_with_nvidia_api(ocr_results):
    llm = initialize_nvidia_api()

    # preface prompt instructions with a request for more detailed output
    instructions = """
    You are an AI presenter. You will be given a JSON formatted input where each entry represents a slide from a PowerPoint presentation.
    Each slide entry will have a slide number and text content extracted via OCR.
    Your task is to generate an engaging, structured presentation script for each slide, going beyond just reading the text. The text that you generate will be read and presented by an autonomous AI agent entity. Your perspective for the presentation output is first person.
    Make sure to present the content in a way that is informative and engaging, similar to how a human presenter would use slide points to talk about the topic.
    Your output must be relevant to the content of the slides and the points that they're talking about, and you should be trying to "say something" with each slide that provides value to the listener. Verbosity is fine, but what output you do use needs to be relevant and useful to the listener. In other words, fluff for the sake of fluff is to be avoided.
    Please expand upon each slide with detailed explanations, historical context, examples, analogies, and any additional context that can make the presentation richer and more informative.
    Break down each point into smaller segments, discussing each aspect thoroughly.
    Be verbose and detailed in your explanations.
    Your output for presentation_text and slide_number MUST correspond 1:1 with the slide_number from your input. YOU MUST NOT create more slides than there are in the source input.
    Your output should be in JSON format, with each slide's content under a corresponding slide number.
    Example input:
    [
        {"slide_number": 1, "text": "Welcome to the presentation."},
        {"slide_number": 2, "text": "Today's agenda includes..."}
    ]
    Example output:
    [
        {"slide_number": 1, "presentation_text": "Hello everyone, welcome to our presentation. We're excited to have you here. Let's begin by talking about..."},
        {"slide_number": 2, "presentation_text": "Let's start with today's agenda. We will be covering the following topics... In detail, we will explore..."}
    ]
    """
    
    prompt = instructions + "\nInput:\n" + json.dumps(ocr_results, indent=4)
    result = llm.invoke(prompt, temperature=0.7, top_p=0.9, max_tokens=4096)
    return result.content
