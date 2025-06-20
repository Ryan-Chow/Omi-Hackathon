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
    
    def parse_segments_directly(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Parse data that already contains segments directly (not wrapped in webhook format).
        
        Args:
            data: Dictionary containing segments directly
            
        Returns:
            List of processed segments
        """
        processed_segments = []
        segments = data.get('segments', [])
        
        for segment in segments:
            processed_segment = {
                "speaker": segment.get('speaker', 'UNKNOWN'),
                "text": segment.get('text', '').strip(),
                "timestamp": self._format_timestamp(segment.get('start', 0))
            }
            processed_segments.append(processed_segment)
        
        return processed_segments
    
    def process_file(self, input_file: str, output_file: str) -> None:
        """
        Process a JSON file containing webhook data and save processed results.
        
        Args:
            input_file: Path to input JSON file with webhook data
            output_file: Path to output JSON file for processed data
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"Debug: Input data structure: {type(data)}")
            print(f"Debug: Keys in data: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            # Handle different input formats
            if isinstance(data, list):
                # If it's a list of webhook payloads
                all_processed = []
                for item in data:
                    if isinstance(item, dict):
                        processed = self.parse_webhook_data(item)
                        all_processed.extend(processed)
                processed_data = all_processed
            elif isinstance(data, dict):
                # If it's a single webhook payload or direct segments format
                if 'segments' in data:
                    # Direct segments format
                    processed_data = self.parse_segments_directly(data)
                else:
                    # Webhook format
                    processed_data = self.parse_webhook_data(data)
            else:
                raise ValueError(f"Unsupported data format: {type(data)}")
            
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
            import traceback
            traceback.print_exc()
    
    def process_webhook_payload(self, webhook_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Direct processing of webhook payload for real-time use.
        
        Args:
            webhook_data: The webhook payload dictionary
            
        Returns:
            List of processed transcription segments
        """
        return self.parse_webhook_data(webhook_data)
    
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
            
            # Append new segments
            existing_data.extend(new_segments)
            
            # Write back to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            print(f"Added {len(new_segments)} new segments to {output_file}")
            
        except Exception as e:
            print(f"Error appending to processed file: {e}")

# Example usage
if __name__ == "__main__":
    processor = TranscriptionProcessor()
    
    # Process existing file
    processor.process_file('live_transcript.json', 'processed_transcription.json')