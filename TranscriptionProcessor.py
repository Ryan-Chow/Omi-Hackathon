import json
import os
from datetime import datetime
from typing import Dict, List, Any

class TranscriptionProcessor:
    def __init__(self, output_file: str = "live_transcript.json"):
        self.output_file = output_file
        self.ensure_json_file_exists()
    
    def ensure_json_file_exists(self):
        """Create the JSON file if it doesn't exist, or ensure it has valid JSON structure"""
        if not os.path.exists(self.output_file):
            with open(self.output_file, 'w') as f:
                json.dump([], f)
        else:
            # Verify the file contains valid JSON
            try:
                with open(self.output_file, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError:
                # If file is corrupted, reset it
                with open(self.output_file, 'w') as f:
                    json.dump([], f)
    
    def transform_segment(self, segment: Dict[str, Any]) -> Dict[str, str]:
        """Transform a single segment to the desired format"""
        return {
            "speaker": segment.get("speaker", ""),
            "text": segment.get("text", ""),
            "timestamp": str(segment.get("start", ""))
        }
    
    def process_incoming_data(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Process incoming livestream data and transform segments"""
        segments = data.get("segments", [])
        transformed_segments = []
        
        for segment in segments:
            transformed_segment = self.transform_segment(segment)
            transformed_segments.append(transformed_segment)
        
        return transformed_segments
    
    def append_to_json_file(self, new_segments: List[Dict[str, str]]):
        """Append new segments to the JSON file"""
        # Read existing data
        with open(self.output_file, 'r') as f:
            existing_data = json.load(f)
        
        # Append new segments
        existing_data.extend(new_segments)
        
        # Write back to file
        with open(self.output_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
    
    def process_livestream_chunk(self, incoming_data: Dict[str, Any]):
        """Main method to process a chunk of livestream data"""
        try:
            # Transform the data
            transformed_segments = self.process_incoming_data(incoming_data)
            
            # Only append if there are segments to add
            if transformed_segments:
                self.append_to_json_file(transformed_segments)
                print(f"Added {len(transformed_segments)} segments to {self.output_file}")
                
                # Optional: print the segments for debugging
                for segment in transformed_segments:
                    print(f"Speaker: {segment['speaker']}, Text: {segment['text']}, Time: {segment['timestamp']}")
            
        except Exception as e:
            print(f"Error processing livestream chunk: {e}")

# Example usage and testing
def simulate_livestream():
    """Simulate incoming livestream data for testing"""
    processor = TranscriptionProcessor("live_transcription.json")
    
    # Sample incoming data (like what you showed)
    sample_data = {
        "session_id": "QhE0XF6nTNXTqfxvn05BBhxpxuJ3",
        "segments": [
            {
                "id": "e4613fdb-b10b-457a-8eda-4138a479835a",
                "text": "And",
                "speaker": "SPEAKER_1",
                "speaker_id": 1,
                "is_user": False,
                "person_id": None,
                "start": 936.5400999999997,
                "end": 937.02,
                "translations": []
            },
            {
                "id": "f5724edc-c21c-568b-9feb-5249b590946b",
                "text": "this is a test",
                "speaker": "SPEAKER_2",
                "speaker_id": 2,
                "is_user": True,
                "person_id": None,
                "start": 940.1,
                "end": 942.5,
                "translations": []
            }
        ]
    }
    
    # Process the sample data
    processor.process_livestream_chunk(sample_data)

# For real livestream integration, you might use something like:
def integrate_with_livestream(processor):
    """
    Example of how to integrate with an actual livestream
    Replace this with your actual livestream source
    """
    # Example with websocket or API polling
    # while True:
    #     try:
    #         # Get data from your livestream source
    #         incoming_data = get_from_livestream_source()  # Your implementation
    #         processor.process_livestream_chunk(incoming_data)
    #         time.sleep(0.1)  # Adjust based on your stream rate
    #     except KeyboardInterrupt:
    #         break
    #     except Exception as e:
    #         print(f"Livestream error: {e}")
    #         time.sleep(1)  # Wait before retrying
    pass

if __name__ == "__main__":
    # Run the simulation
    simulate_livestream()
    
    # Print the contents of the file to verify
    print("\nContents of the JSON file:")
    with open("live_transcription.json", 'r') as f:
        data = json.load(f)
        print(json.dumps(data, indent=2))