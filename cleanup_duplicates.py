import json

def cleanup_duplicates():
    """Remove duplicate segments from processed_transcription.json"""
    try:
        # Read the current file
        with open('processed_transcription.json', 'r', encoding='utf-8') as f:
            segments = json.load(f)
        
        print(f"Original segments: {len(segments)}")
        
        # Create a set to track unique segments
        seen_segments = set()
        unique_segments = []
        
        for segment in segments:
            # Create a unique identifier for each segment
            segment_id = f"{segment['speaker']}_{segment['text']}_{segment['timestamp']}"
            
            if segment_id not in seen_segments:
                seen_segments.add(segment_id)
                unique_segments.append(segment)
        
        print(f"Unique segments: {len(unique_segments)}")
        print(f"Removed {len(segments) - len(unique_segments)} duplicates")
        
        # Write back the cleaned data
        with open('processed_transcription.json', 'w', encoding='utf-8') as f:
            json.dump(unique_segments, f, indent=2, ensure_ascii=False)
        
        print("Successfully cleaned up duplicates!")
        
    except Exception as e:
        print(f"Error cleaning up duplicates: {e}")

if __name__ == "__main__":
    cleanup_duplicates() 