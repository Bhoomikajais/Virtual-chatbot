import tkinter as tk
from tkinter import scrolledtext
import json
import re
import datetime
import pyttsx3
import speech_recognition as sr
import wikipedia
import webbrowser
import threading
import string
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='wikipedia')

# Load response data
with open("responses.json", "r") as file:
    data = json.load(file)

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 160)

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Get chatbot response based on input
def get_response(user_input):
    user_input = user_input.lower().strip()
    user_input_clean = user_input.translate(str.maketrans('', '', string.punctuation))

    # Check greetings
    if any(greet in user_input_clean for greet in data.get("greeting", [])):
        return data["responses"].get("greeting", "Hello! 😊")

    # Check thanks
    if any(thank in user_input_clean for thank in data.get("thanks", [])):
        return data["responses"].get("thanks", "You're welcome! 😊")

    # Check help
    if "help" in user_input_clean:
        return data["responses"].get("help", "You can ask me about the time, date, or who someone is.")

    # **Time/Date check BEFORE Wikipedia**
    if any(keyword in user_input_clean for keyword in ["time", "date", "day", "today"]):
        now = datetime.datetime.now()
        if "time" in user_input_clean:
            return f"The current time is {now.strftime('%H:%M:%S')} ⏰"
        else:
            return f"Today's date is {now.strftime('%A, %B %d, %Y')} 📅"

    # Wikipedia query check (after time/date)
    if user_input_clean.startswith(("who is", "what is", "tell me about")):
        query = user_input_clean.replace("who is", "").replace("what is", "").replace("tell me about", "").strip()
        try:
            summary = wikipedia.summary(query, sentences=2, auto_suggest=False, redirect=True)
            return summary + " 🤓"
        except Exception:
            return "Sorry, I couldn't find any information on that. 🤔"

    # Fallback response
    return data["responses"].get("default", "Sorry, I don't understand that. 🤔")



# Save chat to log file
def save_chat(user, bot):
    with open("chat_log.txt", "a", encoding="utf-8") as log:
        log.write(f"You: {user}\nBot: {bot}\n")

# Recognize voice input in separate thread (so GUI doesn't freeze)
def listen_and_send():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        chat_area.insert(tk.END, "Bot: Listening... 🎤\n")
        chat_area.see(tk.END)
        audio = recognizer.listen(source, phrase_time_limit=5)
    try:
        user_input = recognizer.recognize_google(audio)
        chat_area.insert(tk.END, f"You (voice): {user_input}\n")
        chat_area.see(tk.END)
        bot_reply = get_response(user_input)
        chat_area.insert(tk.END, f"Bot: {bot_reply}\n")
        chat_area.see(tk.END)
        speak(bot_reply)
        save_chat(user_input, bot_reply)
    except sr.UnknownValueError:
        chat_area.insert(tk.END, "Bot: Sorry, I didn't catch that. Please try again. 🤷‍♂️\n")
    except sr.RequestError:
        chat_area.insert(tk.END, "Bot: Sorry, my speech service is down. 😞\n")

# Send message handler
def send_message():
    user_input = user_entry.get()
    if user_input.strip() == "":
        return

    chat_area.insert(tk.END, f"You: {user_input}\n")
    chat_area.see(tk.END)
    user_entry.delete(0, tk.END)

    # Check goodbye first to exit immediately
    if any(word in user_input.lower() for word in data["goodbye"]):
        bot_reply = data["responses"]["goodbye"] + " 👋"
        chat_area.insert(tk.END, f"Bot: {bot_reply}\n")
        speak(bot_reply)
        save_chat(user_input, bot_reply)
        root.after(2000, root.destroy)
        return

    # Other response handling code here ...
    bot_reply = get_response(user_input)
    chat_area.insert(tk.END, f"Bot: {bot_reply}\n")
    chat_area.see(tk.END)
    speak(bot_reply)
    save_chat(user_input, bot_reply)

# GUI Setup
root = tk.Tk()
root.title("Virtual Chatbot with Extras 🎉")
root.geometry("600x550")
root.resizable(False, False)

# Chat area (scrollable)
chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=25, font=("Arial", 11))
chat_area.pack(padx=10, pady=10)

# Initial greeting
hour = datetime.datetime.now().hour
if hour < 12:
    greeting = "Good morning! ☀️ I'm your virtual assistant. Type 'help' for options."
elif hour < 18:
    greeting = "Good afternoon! 🌤️ I'm your virtual assistant. Type 'help' for options."
else:
    greeting = "Good evening! 🌙 I'm your virtual assistant. Type 'help' for options."

chat_area.insert(tk.END, f"Bot: {greeting}\n")
speak(greeting)

# User input entry
user_entry = tk.Entry(root, font=("Arial", 12), width=50)
user_entry.pack(pady=5)
user_entry.bind("<Return>", lambda event=None: send_message())

# Buttons frame
btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

# Send Button
send_btn = tk.Button(btn_frame, text="Send", command=send_message, font=("Arial", 12), bg="#4CAF50", fg="white")
send_btn.grid(row=0, column=0, padx=10)

# Voice Input Button
voice_btn = tk.Button(btn_frame, text="🎤 Speak", command=lambda: threading.Thread(target=listen_and_send).start(), font=("Arial", 12), bg="#2196F3", fg="white")
voice_btn.grid(row=0, column=1, padx=10)

root.mainloop()
