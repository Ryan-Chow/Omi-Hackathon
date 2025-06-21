import requests
import json
import os
import pyttsx3

# Set the API key - better to use environment variable
openai_api_key = ""
engine = pyttsx3.init()


def hello_world():
    """Function that gets called when 'I like your' phrase is detected"""
    print("Hello, world!")
    print("🎉 OpenAI function triggered by 'I like your' phrase!")
    
    try:
        # Simple one-shot prompt - no conversation context
        
       # Load the processed transcription from the JSON file
        with open("processed_transcription.json", "r") as f:
            conversation_data = json.load(f)

        # Extract only the 'text' fields and join them into a single string
        conversation_text = " ".join([entry["text"] for entry in conversation_data if "text" in entry])

        # Original prompt
        prompt = (
            "You are the best conversation talker. I am mid way through this conversation with this person. "
            "Analyze it and determine the best singular broad question about something directly said in the convo. that is medium size, "
            "concise, nice, and well-crafted. Finish this fast and ALSO ONLY return the question by itself. "
            "DO THIS WITH HIGH ACCURACY. and make sure it's a unique question that makes one appear in a good light\n\n"
        )

        # Append the extracted conversation text to the prompt
        prompt += conversation_text

        # Print the final prompt
        print(prompt)
        # Make the API call
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            question = result['choices'][0]['message']['content']
            print(f"🤖 AI Response: {question}")
            engine.say(question)
            engine.runAndWait()
            return question
        else:
            print(f"Error calling OpenAI API: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None

