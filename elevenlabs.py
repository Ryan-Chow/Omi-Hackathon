import pyttsx3

# Initialize the TTS engine
engine = pyttsx3.init()

# Get text input from user
text = input("Enter text to speak: ")

# Convert text to speech
engine.say(text)
engine.runAndWait()