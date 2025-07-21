# Omi-Hackathon

> **Made by 3 high schoolers — Blake Almon, Cody Luu, and Ryan Chow — during the "Most Controversial App" Hackathon hosted by Omi at Stanford University. This was a winning project!**



A Python project for processing, analyzing, and interacting with live transcriptions from OMI webhooks, with OpenAI-powered question generation and text-to-speech features.

## Features

- **Live Webhook Listener**: Continuously fetches and processes new transcription data from a webhook endpoint. The webhook receives live data from a custom-built Omi app using Omi's listening necklaces which deliver json formatted to the webhook.
- **Phrase Detection**: Detects the phrase "I like your" in any segment and triggers an OpenAI-powered function.
- **OpenAI Integration**: Generates a unique, well-crafted question about the conversation using GPT-3.5-turbo and reads it aloud using an open source text-to-speech library.
- **Transcription Management**: Deduplicates, archives, and appends new transcription segments.
- **Utilities**: Includes scripts for cleaning up duplicates, testing parsing, and standalone text-to-speech.

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd Omi-Hackathon
```

### 2. Set up a Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install requests openai pyttsx3
```

### 4. Configure API Keys

- Edit `webhook.py` and `openai.py` to set your actual webhook UUID and API keys.
- For security, you may want to use environment variables for your OpenAI API key.

### 5. Run the main program

```bash
python webhook.py
```

This will:
- Scan existing transcriptions for the trigger phrase.
- Archive previous conversations.
- Start listening for new webhook data and process it in real time.

## Project Structure

- **webhook.py**  
  Main entry point. Listens to the webhook, processes new transcription data, detects trigger phrases, and manages conversation files.

- **openai.py**  
  Contains the function called when the trigger phrase is detected. It generates a question using OpenAI and reads it aloud.

- **test_parsing.py**  
  Utility script to test parsing and processing of a single webhook entry from `live_transcript.json`.

- **cleanup_duplicates.py**  
  Removes duplicate segments from `processed_transcription.json`.

- **elevenlabs.py**  
  Simple script to convert user-input text to speech using `pyttsx3`.

- **live_transcript.json**  
  Stores all received webhook payloads.

- **processed_transcription.json**  
  Stores processed and deduplicated transcription segments.

- **previous_conversations/**  
  Archives of past processed conversations.

- **.gitignore**  
  Ignores `.env` (for environment variables).

## Notes

- The main program (`webhook.py`) must be run to start the system.
- Make sure your system audio is enabled for text-to-speech output.
- For best security, do not hardcode API keys; use environment variables or a `.env` file (add `.env` to `.gitignore`).

## Example Usage

When the phrase "I like your" is detected in any transcription segment, the system will:
1. Call OpenAI to generate a thoughtful question about the conversation.
2. Print and speak the question aloud.

---

Let me know if you want to add usage examples, API key setup instructions, or anything else!
