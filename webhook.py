import requests
import json
import time
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
        if isinstance(webhook_data.get('content'), str):
            # Parse the JSON string in the content field
            content_data = json.loads(webhook_data['content'])
        else:
            # If content is already a dict
            content_data = webhook_data.get('content', {})
        
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
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except FileNotFoundError:
                existing_data = []
            
            # Process new webhook data
            new_segments = self.parse_webhook_data(webhook_data)
            
            # Append new segments (only if there are any)
            if new_segments:
                existing_data.extend(new_segments)
                
                # Write back to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=2, ensure_ascii=False)
                
                print(f"Added {len(new_segments)} new segments to {output_file}")
            
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

print("Starting webhook listener with live transcription processing...")
print("Raw data saved to: live_transcript.json")
print("Processed data saved to: processed_transcription.json")
print("Press Ctrl+C to stop")

try:
    while True:
        try:
            response = requests.get(url, headers=headers)
            data = response.json()

            if response.status_code == 200:
                # Print to console (optional)
                print(json.dumps(data, indent=4))
                
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
                    
                    # Process the new data
                    processor.append_to_processed_file(data)
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