import sys
import grpc
import numpy as np
import soundfile
from pathlib import Path
import logging
import os
import threading

import audio2face_pb2
import audio2face_pb2_grpc

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

host_ip = os.getenv('HOST_IP_ADDRESS')
def push_audio_to_audio2face(audio_path, instance_name, url=f"{host_ip}:50051"):
    def run():
        try:
            data, samplerate = soundfile.read(audio_path, dtype='float32')
            if data.ndim > 1:
                data = np.mean(data, axis=1)

            # Increased maximum message sizes for send and receive
            options = [
                ('grpc.max_send_message_length', 500 * 1024 * 1024),  # 500 MB
                ('grpc.max_receive_message_length', 500 * 1024 * 1024)  # 500 MB
            ]
            with grpc.insecure_channel(url, options=options) as channel:
                stub = audio2face_pb2_grpc.Audio2FaceStub(channel)
                request = audio2face_pb2.PushAudioRequest(
                    audio_data=data.tobytes(),
                    samplerate=samplerate,
                    instance_name=instance_name,
                    block_until_playback_is_finished=True
                )
                logging.info("Attempting to send audio data to Audio2Face...")
                response = stub.PushAudio(request)
                if response.success:
                    logging.info("Audio successfully sent to Audio2Face.")
                else:
                    logging.error(f"Failed to send audio: {response.message}")
        except grpc.RpcError as e:
            logging.error(f"gRPC error: {e.details()} (code: {e.code()})")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

    threading.Thread(target=run).start()

def main(audio_path, instance_name):
    push_audio_to_audio2face(audio_path, instance_name)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        logging.error("Usage: python audio2face_module.py <path_to_wav_file> <instance_name>")
    else:
        main(sys.argv[1], sys.argv[2])
