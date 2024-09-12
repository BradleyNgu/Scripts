import schedule
import time
import webbrowser
import pyautogui
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from random import randint

# Load the environment variables from .env file
load_dotenv()

# Get the Zoom URL from the .env file
meeting_url = os.getenv("ZOOM_URL")

# Function to join the Zoom meeting
def join_zoom_meeting():
    webbrowser.open(meeting_url)  # Open the Zoom meeting link from .env
    time.sleep(10)  # Wait for the Zoom to open (adjust based on your system)
    pyautogui.moveTo(900, 580)  # Adjust coordinates based on your screen
    pyautogui.click()  # Click the "Join" button
    print("Joined the Zoom meeting")
    #good_morning_chat()  # Call the chat function after joining

# Function to say good morning in the Zoom meeting
def good_morning_chat():
    introduction_dialogue =  ["Good morning miss", "Hello!", "Good morning"] #list of introductions strings
    time.sleep(15)  # Wait for Zoom to fully load the meeting and chat box
    pyautogui.moveTo(800, 700)  # Move to chat box (adjust coordinates)
    pyautogui.click()  # Open the chat window
    time.sleep(2)
    pyautogui.write(introduction_dialogue[randint(0,2)] , interval=0.01)  # Type the message
    pyautogui.press('enter')  # Press Enter to send the message
    print("Sent 'Good morning' message")

def break_chat():
    pyautogui.moveTo(800, 700)  # Move to chat box (adjust coordinates)
    pyautogui.click()  # Open the chat window
    time.sleep(2)
    pyautogui.write('Back', interval=0.01)  # Type the message
    pyautogui.press('enter')  # Press Enter to send the message
    print("Sent 'Back' message")

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

    break_time = (datetime.strptime("11:35", "%H:%M") + timedelta(hours=1, minutes=20)).strftime("%H:%M")
    schedule.every().thursday.at(break_time).do(break_chat)
    
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
