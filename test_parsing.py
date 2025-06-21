import json
from webhook import TranscriptionProcessor

# Load existing webhook data
with open('live_transcript.json', 'r') as f:
    webhook_data_list = json.load(f)

# Initialize processor
processor = TranscriptionProcessor()

# Test parsing with the first webhook entry
if webhook_data_list:
    first_webhook = webhook_data_list[0]
    print("Testing with first webhook entry:")
    print(f"Webhook keys: {list(first_webhook.keys())}")
    
    # Parse the webhook data
    segments = processor.parse_webhook_data(first_webhook)
    print(f"Parsed {len(segments)} segments:")
    for segment in segments:
        print(f"  {segment['timestamp']} - {segment['speaker']}: {segment['text']}")
    
    # Test appending to processed file
    processor.append_to_processed_file(first_webhook)
    print("Successfully processed first webhook entry")
else:
    print("No webhook data found") 