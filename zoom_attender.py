import os
import pyaudio
import queue
import time
import google.cloud.speech as speech
import pyautogui
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI and Google Cloud API keys
openai.api_key = os.getenv("OPENAI_API_KEY")

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

# Queue to communicate between the audio callback and main thread
audio_queue = queue.Queue()

# OpenAI API for answering questions
def answer_questions(transcript):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=f"Answer the following questions based on this transcript:\n{transcript}",
        temperature=0.7,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].text.strip()

# Google Cloud speech client
client = speech.SpeechClient()

# Audio stream setup using PyAudio
def record_audio():
    audio_interface = pyaudio.PyAudio()

    # Function to capture audio in chunks and put into queue
    def callback(in_data, frame_count, time_info, status):
        audio_queue.put(in_data)
        return (None, pyaudio.paContinue)

    # Open audio stream
    stream = audio_interface.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        stream_callback=callback
    )
    return stream

# Function to transcribe audio stream to text
def listen_and_transcribe():
    stream = record_audio()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="en-US",
    )
    streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=False)

    with client.streaming_recognize(streaming_config, audio_generator()) as responses:
        for response in responses:
            for result in response.results:
                transcript = result.alternatives[0].transcript
                print(f"Transcript: {transcript}")

                # Process the transcript and generate answers
                answer = answer_questions(transcript)
                print(f"Answer: {answer}")

                # Use pyautogui to type the answer in Zoom chat
                pyautogui.moveTo(800, 700)  # Move to chat box (adjust coordinates)
                pyautogui.click()  # Open the chat window
                pyautogui.write(answer, interval=0.01)  # Type the generated answer
                pyautogui.press('enter')  # Send the message
                print(f"Sent answer: {answer}")

# Generator to get audio chunks for the transcription API
def audio_generator():
    while True:
        data = audio_queue.get()
        if data is None:
            break
        yield speech.StreamingRecognizeRequest(audio_content=data)

if __name__ == "__main__":
    # Start listening and transcribing in real-time
    print("Starting live transcription and answering...")
    listen_and_transcribe()
