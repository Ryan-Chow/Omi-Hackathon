import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Set
import re
from bs4 import BeautifulSoup

class WebhookTranscriptScraper:
    def __init__(self, webhook_url: str, raw_file: str = "raw_transcript.json", 
                 processed_file: str = "processed_transcript.json"):
        self.webhook_url = webhook_url
        self.raw_file = raw_file
        self.processed_file = processed_file
        self.seen_requests = set()  # Track processed requests to avoid duplicates
        self.session = requests.Session()
        
        # Initialize the transcription processor
        self.processor = TranscriptionProcessor(processed_file)
        
        # Initialize raw file
        self.ensure_raw_file_exists()
    
    def ensure_raw_file_exists(self):
        """Create the raw transcript file if it doesn't exist"""
        try:
            with open(self.raw_file, 'r') as f:
                json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.raw_file, 'w') as f:
                json.dump([], f)
    
    def fetch_webhook_data(self) -> List[Dict]:
        """Fetch data from webhook.site page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = self.session.get(self.webhook_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse the HTML to extract request data
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for script tags that might contain the data
            script_tags = soup.find_all('script')
            webhook_data = []
            
            for script in script_tags:
                if script.string and 'requests' in script.string:
                    # Try to extract JSON data from the script
                    try:
                        script_content = script.string
                        # Look for patterns that might contain request data
                        json_match = re.search(r'requests\s*[:=]\s*(\[.*?\])', script_content, re.DOTALL)
                        if json_match:
                            requests_data = json.loads(json_match.group(1))
                            webhook_data.extend(requests_data)
                    except:
                        continue
            
            return webhook_data
            
        except Exception as e:
            print(f"Error fetching webhook data: {e}")
            return []
    
    def extract_transcript_from_request(self, request_data: Dict) -> Dict:
        """Extract transcript data from a webhook request"""
        try:
            # Get the request content
            content = request_data.get('content', '')
            
            # Try to parse as JSON if it looks like JSON
            if content.strip().startswith('{'):
                try:
                    json_content = json.loads(content)
                    return {
                        'timestamp': request_data.get('created_at', ''),
                        'request_id': request_data.get('uuid', ''),
                        'raw_content': content,
                        'parsed_content': json_content
                    }
                except json.JSONDecodeError:
                    pass
            
            # If not JSON, store as raw text
            return {
                'timestamp': request_data.get('created_at', ''),
                'request_id': request_data.get('uuid', ''),
                'raw_content': content,
                'parsed_content': None
            }
            
        except Exception as e:
            print(f"Error extracting transcript: {e}")
            return None
    
    def save_raw_transcript(self, new_data: List[Dict]):
        """Save raw transcript data to file"""
        if not new_data:
            return
        
        try:
            # Read existing data
            with open(self.raw_file, 'r') as f:
                existing_data = json.load(f)
            
            # Append new data
            existing_data.extend(new_data)
            
            # Write back
            with open(self.raw_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            print(f"Saved {len(new_data)} raw transcript entries")
            
        except Exception as e:
            print(f"Error saving raw transcript: {e}")
    
    def process_transcript_data(self, transcript_data: Dict):
        """Process transcript data through the TranscriptionProcessor"""
        try:
            parsed_content = transcript_data.get('parsed_content')
            if parsed_content:
                # Check if it matches your expected format
                if 'segments' in parsed_content:
                    self.processor.process_livestream_chunk(parsed_content)
                elif isinstance(parsed_content, list):
                    # Handle if it's a list of segments
                    fake_data = {'segments': parsed_content}
                    self.processor.process_livestream_chunk(fake_data)
                else:
                    print(f"Unknown format in transcript data: {type(parsed_content)}")
        except Exception as e:
            print(f"Error processing transcript data: {e}")
    
    def monitor_webhooks(self, poll_interval: int = 5):
        """Main loop to monitor webhook.site for new transcript data"""
        print(f"Starting to monitor webhook.site: {self.webhook_url}")
        print(f"Polling every {poll_interval} seconds...")
        print("Press Ctrl+C to stop")
        
        while True:
            try:
                # Fetch latest webhook data
                webhook_data = self.fetch_webhook_data()
                
                if webhook_data:
                    new_transcripts = []
                    
                    for request in webhook_data:
                        request_id = request.get('uuid', '')
                        
                        # Skip if we've already processed this request
                        if request_id in self.seen_requests:
                            continue
                        
                        # Extract transcript data
                        transcript_data = self.extract_transcript_from_request(request)
                        
                        if transcript_data:
                            new_transcripts.append(transcript_data)
                            self.seen_requests.add(request_id)
                            
                            # Process through transcription processor
                            self.process_transcript_data(transcript_data)
                    
                    # Save raw data
                    if new_transcripts:
                        self.save_raw_transcript(new_transcripts)
                
                time.sleep(poll_interval)
                
            except KeyboardInterrupt:
                print("\nStopping webhook monitor...")
                break
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(poll_interval)

# Alternative API-based approach (if webhook.site supports API access)
class WebhookAPITranscriptScraper:
    def __init__(self, webhook_token: str, raw_file: str = "raw_transcript.json"):
        self.webhook_token = webhook_token
        self.raw_file = raw_file
        self.seen_requests = set()
        self.processor = TranscriptionProcessor("processed_transcript.json")
    
    def fetch_webhook_requests(self) -> List[Dict]:
        """Fetch webhook requests via API (if available)"""
        try:
            # webhook.site API endpoint (you may need to check their documentation)
            api_url = f"https://webhook.site/token/{self.webhook_token}/requests"
            
            response = requests.get(api_url)
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                print(f"API request failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error fetching via API: {e}")
            return []
    
    def monitor_via_api(self, poll_interval: int = 3):
        """Monitor using API calls"""
        print(f"Monitoring webhook via API...")
        
        while True:
            try:
                requests_data = self.fetch_webhook_requests()
                
                for request in requests_data:
                    request_id = request.get('uuid', '')
                    
                    if request_id not in self.seen_requests:
                        # Process the request
                        content = request.get('content', '')
                        
                        try:
                            if content.strip().startswith('{'):
                                json_content = json.loads(content)
                                if 'segments' in json_content:
                                    self.processor.process_livestream_chunk(json_content)
                                    self.seen_requests.add(request_id)
                                    print(f"Processed request {request_id}")
                        except:
                            pass
                
                time.sleep(poll_interval)
                
            except KeyboardInterrupt:
                print("\nStopping API monitor...")
                break
            except Exception as e:
                print(f"Error in API monitoring: {e}")
                time.sleep(poll_interval)

# Include the TranscriptionProcessor from the previous code
class TranscriptionProcessor:
    def __init__(self, output_file: str = "transcription_log.json"):
        self.output_file = output_file
        self.ensure_json_file_exists()
    
    def ensure_json_file_exists(self):
        try:
            with open(self.output_file, 'r') as f:
                json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.output_file, 'w') as f:
                json.dump([], f)
    
    def transform_segment(self, segment: Dict[str, Any]) -> Dict[str, str]:
        return {
            "speaker": segment.get("speaker", ""),
            "text": segment.get("text", ""),
            "timestamp": str(segment.get("start", ""))
        }
    
    def process_incoming_data(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        segments = data.get("segments", [])
        transformed_segments = []
        
        for segment in segments:
            transformed_segment = self.transform_segment(segment)
            transformed_segments.append(transformed_segment)
        
        return transformed_segments
    
    def append_to_json_file(self, new_segments: List[Dict[str, str]]):
        with open(self.output_file, 'r') as f:
            existing_data = json.load(f)
        
        existing_data.extend(new_segments)
        
        with open(self.output_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
    
    def process_livestream_chunk(self, incoming_data: Dict[str, Any]):
        try:
            transformed_segments = self.process_incoming_data(incoming_data)
            
            if transformed_segments:
                self.append_to_json_file(transformed_segments)
                print(f"Added {len(transformed_segments)} segments to {self.output_file}")
                
        except Exception as e:
            print(f"Error processing livestream chunk: {e}")

# Usage
if __name__ == "__main__":
    # Your webhook.site URL
    webhook_url = "https://webhook.site/#!/share/e00c4adb-0534-4647-b85f-10d3f936fd38/0693c194-c98f-4656-9833-ac05f47f5e20/885ffc2d-693a-4753-9f05-b6fb66c5330c/1"
    
    # Initialize scraper
    scraper = WebhookTranscriptScraper(webhook_url)
    
    # Start monitoring (polls every 5 seconds)
    scraper.monitor_webhooks(poll_interval=5)
    
    # Alternative: If you have the webhook token, you can try API approach
    # webhook_token = "e00c4adb-0534-4647-b85f-10d3f936fd38"
    # api_scraper = WebhookAPITranscriptScraper(webhook_token)
    # api_scraper.monitor_via_api()