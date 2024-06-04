import os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from config import Config

def analyze_image(image_path):
    key = Config.AZURE_AI_SERVICES_KEY
    endpoint = Config.AZURE_AI_SERVICES_ENDPOINT
    client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))
    
    with open(image_path, "rb") as image_stream:
        analysis = client.analyze_image_in_stream(
            image_stream,
            visual_features=[VisualFeatureTypes.categories, VisualFeatureTypes.tags, VisualFeatureTypes.description, VisualFeatureTypes.objects]
        )
    
    return analysis

def extract_text(image_path):
    key = Config.AZURE_AI_SERVICES_KEY
    endpoint = Config.AZURE_AI_SERVICES_ENDPOINT
    client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

    with open(image_path, "rb") as image_stream:
        read_response = client.read_in_stream(image_stream, raw=True)

    # extracting the operation ID from the response headers
    operation_location = read_response.headers["Operation-Location"]
    operation_id = operation_location.split("/")[-1]

    # waiting for the operation to complete
    import time
    while True:
        result = client.get_read_result(operation_id)
        if result.status.lower() not in ['notstarted', 'running']:
            break
        time.sleep(1)

    # extracting text from the read result
    text_results = []
    if result.status == "succeeded":
        for page in result.analyze_result.read_results:
            for line in page.lines:
                text_results.append(line.text)

    return "\n".join(text_results)

def get_image_analysis(image_path):
    analysis = analyze_image(image_path)
    
    description = analysis.description.captions[0].text if analysis.description.captions else ""
    tags = [tag.name for tag in analysis.tags]
    objects = [obj.object_property for obj in analysis.objects]
    layout_text = "\n".join([f"{obj.object_property}: {obj.rectangle}" for obj in analysis.objects if obj.rectangle])

    text_results = extract_text(image_path)

    return {
        "description": description,
        "tags": tags,
        "objects": objects,
        "layout": layout_text,
        "text": text_results
    }
