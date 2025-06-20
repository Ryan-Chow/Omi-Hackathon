import json
from typing import List, Dict, Any
from datetime import datetime, timedelta

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
    
    def process_file(self, input_file: str, output_file: str) -> None:
        """
        Process a JSON file containing webhook data and save processed results.
        
        Args:
            input_file: Path to input JSON file with webhook data
            output_file: Path to output JSON file for processed data
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                webhook_data = json.load(f)
            
            processed_data = self.parse_webhook_data(webhook_data)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2, ensure_ascii=False)
            
            print(f"Successfully processed {len(processed_data)} segments")
            print(f"Output saved to: {output_file}")
            
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found")
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in input file - {e}")
        except Exception as e:
            print(f"Error processing file: {e}")
    
    def process_webhook_payload(self, webhook_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Direct processing of webhook payload for real-time use.
        
        Args:
            webhook_data: The webhook payload dictionary
            
        Returns:
            List of processed transcription segments
        """
        return self.parse_webhook_data(webhook_data)

# Example usage
if __name__ == "__main__":
    processor = TranscriptionProcessor()
    
    # Example with your provided data
    sample_webhook_data = {
        "uuid": "1f87712c-6f01-477f-8fac-a3221956643e",
        "type": "web",
        "content": "{\"session_id\": \"QhE0XF6nTNXTqfxvn05BBhxpxuJ3\", \"segments\": [{\"id\": \"6e1ec2a6-1cfa-4506-b1c5-bf8ab5509072\", \"text\": \"Oh.\", \"speaker\": \"SPEAKER_0\", \"speaker_id\": 0, \"is_user\": false, \"person_id\": null, \"start\": 47.78989999999999, \"end\": 48.190000000000055, \"translations\": []}]}",
        "created_at": "2025-06-20 22:42:37"
    }
    
    # Process the sample data
    result = processor.process_webhook_payload(sample_webhook_data)
    print("Processed result:")
    print(json.dumps(result, indent=2))
    
    # Example of processing from file
    processor.process_file('live_transcript.json', 'processed_transcription.json')