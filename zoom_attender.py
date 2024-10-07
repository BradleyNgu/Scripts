import schedule
import time
import webbrowser
import pyautogui
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from random import randint
import pyaudio
import queue
import openai
from google.cloud import speech

# Load the environment variables from .env file
load_dotenv()

# Set GOOGLE_APPLICATION_CREDENTIALS for Google Cloud authentication
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Set OpenAI and Google Cloud API keys
openai.api_key = os.getenv("OPENAI_API_KEY")

# Get the Zoom URL from the .env file
meeting_url = os.getenv("ZOOM_URL")

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

# Queue to communicate between the audio callback and main thread
audio_queue = queue.Queue()

# Initialize Google Cloud Speech client
client = speech.SpeechClient()

# Function to join the Zoom meeting
def join_zoom_meeting():
    webbrowser.open(meeting_url)  # Open the Zoom meeting link from .env
    time.sleep(10)  # Wait for the Zoom to open (adjust based on your system)
    pyautogui.moveTo(900, 580)  # Adjust coordinates based on your screen
    pyautogui.click()  # Click the "Join" button
    print("Joined the Zoom meeting")
    good_morning_chat()  # Call the chat function after joining
    listen_and_transcribe()  # Start live transcription after joining

# Function to say good morning in the Zoom meeting
def good_morning_chat():
    introduction_dialogue = ["Good morning miss", "Hello!", "Good morning"]  # list of introductions strings
    time.sleep(15)  # Wait for Zoom to fully load the meeting and chat box
    pyautogui.moveTo(800, 700)  # Move to chat box (adjust coordinates)
    pyautogui.click()  # Open the chat window
    time.sleep(2)
    pyautogui.write(introduction_dialogue[randint(0, 2)], interval=0.01)  # Type the message
    pyautogui.press('enter')  # Press Enter to send the message
    print("Sent 'Good morning' message")

# OpenAI API for answering questions based on transcription
def answer_questions(transcript):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant answering questions from a transcript."},
            {"role": "user", "content": f"Answer the following questions based on this transcript:\n{transcript}"}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

# Function to capture audio and transcribe in real-time
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

                # Send transcript to OpenAI and generate answers
                answer = answer_questions(transcript)
                print(f"Answer: {answer}")

                # Use pyautogui to type the answer into the Zoom chat
                pyautogui.moveTo(800, 700)  # Move to chat box (adjust coordinates)
                pyautogui.click()  # Open the chat window
                pyautogui.write(answer, interval=0.01)  # Type the generated answer
                pyautogui.press('enter')  # Press Enter to send the message
                print(f"Sent answer: {answer}")

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

# Generator to get audio chunks for the transcription API
def audio_generator():
    while True:
        data = audio_queue.get()
        if data is None:
            break
        yield speech.StreamingRecognizeRequest(audio_content=data)

# Function to leave the Zoom meeting
def leave_zoom_meeting():
    pyautogui.moveTo(1480, 720)  # Move mouse to the 'Leave' button (adjust coordinates)
    pyautogui.click()  # Click the 'Leave' button
    time.sleep(1)
    pyautogui.moveTo(1480, 650)  # Adjust coordinates for the 'Confirm leave' button
    pyautogui.click()  # Confirm leaving the meeting
    print("Left the Zoom meeting")

# Schedule the Zoom meeting to join and leave at the right times
def schedule_zoom():
    # Schedule joining at 11:35 AM every Thursday
    schedule.every().thursday.at("11:35").do(join_zoom_meeting)

    # Schedule leaving at 2:25 PM (2 hours and 50 minutes after 11:35)
    leave_time = (datetime.strptime("11:35", "%H:%M") + timedelta(hours=2, minutes=50)).strftime("%H:%M")
    schedule.every().thursday.at(leave_time).do(leave_zoom_meeting)
    
    print("Scheduled Zoom meeting every Thursday from 11:35 AM to 2:25 PM")

# Schedule the meeting
schedule_zoom()

# Keep the script running to check for scheduled events
while True:
    schedule.run_pending()
    time.sleep(1)
