import requests
import json
import time
import os
from datetime import datetime
from typing import List, Dict, Any

class TranscriptionProcessor:
    def __init__(self):
        pass
    
    def parse_webhook_data(self, webhook_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Parse webhook data from OMI transcription and convert to simplified format.
        
        Args:
            webhook_data: The raw webhook data containing transcription segments
            
        Returns:
            List of dictionaries with speaker, text, and timestamp fields
        """
        processed_segments = []
        
        # Extract the content from the webhook data
        content = webhook_data.get('content')
        
        if isinstance(content, str):
            try:
                # Parse the JSON string in the content field
                content_data = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Failed to parse content as JSON: {e}")
                return processed_segments
        else:
            # If content is already a dict
            content_data = content or {}
        
        # Get segments from the content
        segments = content_data.get('segments', [])
        
        for segment in segments:
            processed_segment = {
                "speaker": segment.get('speaker', 'UNKNOWN'),
                "text": segment.get('text', '').strip(),
                "timestamp": self._format_timestamp(segment.get('start', 0))
            }
            processed_segments.append(processed_segment)
        
        return processed_segments
    
    def _format_timestamp(self, start_time: float) -> str:
        """
        Convert start time in seconds to a readable timestamp format.
        
        Args:
            start_time: Time in seconds from start of recording
            
        Returns:
            Formatted timestamp string (HH:MM:SS)
        """
        # Convert seconds to hours, minutes, seconds
        total_seconds = int(start_time)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def append_to_processed_file(self, webhook_data: Dict[str, Any], output_file: str = 'processed_transcription.json') -> None:
        """
        Process new webhook data and append to existing processed file.
        
        Args:
            webhook_data: New webhook payload to process
            output_file: Path to the processed transcription file
        """
        try:
            # Try to read existing data
            existing_data = []
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:  # Only try to parse if file is not empty
                        existing_data = json.loads(content)
                    else:
                        existing_data = []
            except FileNotFoundError:
                existing_data = []
            except json.JSONDecodeError as e:
                print(f"Error reading existing file, starting fresh: {e}")
                existing_data = []
            
            # Process new webhook data
            new_segments = self.parse_webhook_data(webhook_data)
            
            # Create a set of existing segment identifiers for deduplication
            existing_segment_ids = set()
            for segment in existing_data:
                # Create a unique identifier for each segment
                segment_id = f"{segment['speaker']}_{segment['text']}_{segment['timestamp']}"
                existing_segment_ids.add(segment_id)
            
            # Filter out duplicates from new segments
            unique_new_segments = []
            for segment in new_segments:
                segment_id = f"{segment['speaker']}_{segment['text']}_{segment['timestamp']}"
                if segment_id not in existing_segment_ids:
                    unique_new_segments.append(segment)
                    existing_segment_ids.add(segment_id)
            
            # Append unique new segments (only if there are any)
            if unique_new_segments:
                existing_data.extend(unique_new_segments)
                
                # Write back to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=2, ensure_ascii=False)
                
                print(f"Added {len(unique_new_segments)} new unique segments to {output_file}")
            else:
                print("No new unique segments to add")
            
        except Exception as e:
            print(f"Error appending to processed file: {e}")

# Initialize the transcription processor
processor = TranscriptionProcessor()

uuid = "e00c4adb-0534-4647-b85f-10d3f936fd38"  # Replace with your actual inbox UUID
api_key = "8a26d082-f54b-4cce-88a2-ddd3e6dd68c7"  # Replace with your actual API key

url = f"https://webhook.site/token/{uuid}/request/latest"

headers = {
    "Api-Key": api_key
}

def initialize_new_conversation():
    """Initialize a new conversation by clearing live_transcript.json and archiving processed_transcription.json"""
    
    # Create previous_conversations directory if it doesn't exist
    os.makedirs('previous_conversations', exist_ok=True)
    
    # Find the next conversation number
    conversation_number = 1
    while os.path.exists(f'previous_conversations/convo_{conversation_number}.json'):
        conversation_number += 1
    
    # Clear live_transcript.json
    if os.path.exists('live_transcript.json'):
        os.remove('live_transcript.json')
        print(f"Cleared live_transcript.json")
    
    # Archive existing processed_transcription.json if it exists
    if os.path.exists('processed_transcription.json'):
        # Check if the file has content (not empty)
        if os.path.getsize('processed_transcription.json') > 0:
            archive_path = f'previous_conversations/convo_{conversation_number}.json'
            os.rename('processed_transcription.json', archive_path)
            print(f"Archived previous conversation to {archive_path}")
        else:
            # If file is empty, just remove it
            os.remove('processed_transcription.json')
            print("Removed empty processed_transcription.json")
    
    # Create new empty processed_transcription.json
    with open('processed_transcription.json', 'w') as f:
        json.dump([], f)
    
    print(f"Created new processed_transcription.json for conversation #{conversation_number}")
    return conversation_number

# Initialize new conversation
conversation_number = initialize_new_conversation()

print("Starting webhook listener... (Press Ctrl+C to stop)")
print("Checking for new requests every second...")

try:
    while True:
        try:
            response = requests.get(url, headers=headers)
            data = response.json()

            if response.status_code == 200:
                # Print to console (optional)
                print(json.dumps(data, indent=4))
                
                # Process the new data first (always process new webhook data)
                processor.append_to_processed_file(data)
                
                # Load existing data or create empty list
                try:
                    with open('live_transcript.json', 'r') as f:
                        existing_data = json.load(f)
                        # Ensure existing_data is a list
                        if not isinstance(existing_data, list):
                            existing_data = [existing_data]
                except FileNotFoundError:
                    existing_data = []
                except json.JSONDecodeError:
                    existing_data = []
                
                # Check if current data already exists
                if data not in existing_data:
                    existing_data.append(data)
                    
                    # Save updated data back to file
                    with open('live_transcript.json', 'w') as f:
                        json.dump(existing_data, f, indent=4)
                    
                    print("\nNew data appended to live_transcript.json")
                else:
                    print("\nData already exists in live_transcript.json - not appending")
            else:
                print("Failed to fetch requests:", response.status_code)
                print("Details:", response.text)
                
        except requests.RequestException as e:
            print(f"Request error: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        
        time.sleep(1)  # Wait 1 second before next request
        
except KeyboardInterrupt:
    print("\nWebhook listener stopped by user")