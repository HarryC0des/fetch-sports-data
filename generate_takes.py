import json
import os
import requests
from datetime import datetime

def get_most_recent_guid_from_records():
    """Get the guid of the most recent entry in records.json"""
    records_file = 'data/records.json'
    if not os.path.exists(records_file):
        return None
    
    with open(records_file, 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    if records:
        return records[0]['guid']  # Most recent is at index 0
    return None

def get_most_recent_guid_from_results():
    """Get the guid of the most recent entry in results.json"""
    results_file = 'results.json'
    if not os.path.exists(results_file):
        return None
    
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        if results:
            return results[0]['guid']  # Most recent is at index 0
        return None
    except json.JSONDecodeError:
        return None

def generate_take():
    # 1. Setup OpenRouter API configuration
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    api_key = os.getenv("OPEN_ROUTER_KEY")
    print(f"[DEBUG] Using API endpoint: {api_url}")
    
    if not api_key:
        print("ERROR: OPEN_ROUTER_KEY environment variable is not set!")
        return
    print("[DEBUG] OPEN_ROUTER_KEY found in environment")
    
    # 2. Define file paths
    input_file = 'data/records.json'
    output_file = 'results.json'

    # 3. Safety Check: Does the source file exist?
    print(f"[DEBUG] Checking for input file: {input_file}")
    if not os.path.exists(input_file):
        print(f"[ERROR] Could not find {input_file}. Check your folder structure.")
        return
    print(f"[DEBUG] Input file found: {input_file}")

    # 4. Load the sports data
    print(f"[DEBUG] Loading records from {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        records = json.load(f)
    print(f"[DEBUG] Loaded {len(records)} records")

    # 5. Get the most recent guids from both files
    records_guid = get_most_recent_guid_from_records()
    results_guid = get_most_recent_guid_from_results()
    print(f"[DEBUG] Records GUID: {records_guid}")
    print(f"[DEBUG] Results GUID: {results_guid}")

    # 6. Load existing results
    results = []
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            print(f"[DEBUG] Loaded existing results.json with {len(results)} entries")
        except json.JSONDecodeError:
            print("[WARNING] results.json was empty or corrupt. Starting fresh.")
    else:
        print(f"[DEBUG] No existing results.json found, starting fresh")

    # 7. Check if guids match
    if records_guid == results_guid:
        # GUIDs match - create entry with message
        message_entry = {
            "guid": records_guid,
            "link": records[0]['link'] if records else None,
            "take": "No new article to process. The most recent entry in records.json matches the most recent entry in results.json.",
            "original_title": records[0]['title'] if records else None,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
        
        results.insert(0, message_entry)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        
        print("[DEBUG] Most recent entries match. No new article to process.")
        return

    # 8. New entry found - send only content_html to API
    target_entry = records[0]  # Get the most recent entry
    content_html = target_entry.get('content_html', '')
    print(f"[DEBUG] Processing new article: {target_entry.get('title')}")
    print(f"[DEBUG] Content length: {len(content_html)} characters")
    
    prompt = f"""You are a professional sports analyst. Generate a unique, memorable, and distinct sports take.

STRICT RULES:
1. Use ONLY the facts provided below.
2. Do NOT hallucinate stats, teams, or details not in the text.
3. Be bold and sharp, but 100% factually grounded.
4. Return ONLY the take itself.

FACTS TO USE:
{content_html}"""

    # 9. Generate content using the OpenRouter API
    print(f"[DEBUG] Sending request to OpenRouter API")
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/HarryC0des/fetch-sports-data",
            "X-Title": "Sports Takes Generator"
        }
        print(f"[DEBUG] Request headers prepared (Authorization: Bearer [REDACTED])")
        
        payload = {
            "model": "openai/gpt-4-turbo",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        print(f"[DEBUG] Request payload prepared (model: openai/gpt-4-turbo, prompt length: {len(prompt)} chars)")
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        print(f"[DEBUG] API response status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[ERROR] OpenRouter API returned status code {response.status_code}")
            print(f"[DEBUG] Response content: {response.text[:500]}")
            take_text = f"[Failed to generate take: OpenRouter API returned status {response.status_code}]"
        else:
            response_json = response.json()
            print(f"[DEBUG] API response received, parsing...")
            print(f"[DEBUG] Response keys: {list(response_json.keys())}")
            
            # Extract message from OpenRouter response format (choices -> content)
            try:
                if 'choices' in response_json and len(response_json['choices']) > 0:
                    take_text = response_json['choices'][0].get('message', {}).get('content', '').strip()
                else:
                    take_text = ""
            except (KeyError, IndexError, TypeError) as e:
                print(f"[DEBUG] Error extracting content from choices: {e}")
                take_text = ""
            
            if not take_text:
                print(f"[WARNING] API response was empty or missing expected fields")
                print(f"[DEBUG] Full response: {response_json}")
                take_text = "[Failed to generate take: empty response from API]"
            else:
                print(f"[DEBUG] Successfully generated take ({len(take_text)} chars)")
    except requests.exceptions.Timeout:
        print(f"[ERROR] OpenRouter API request timed out (60 second timeout)")
        take_text = "[Failed to generate take: API request timeout]"
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error during OpenRouter API call: {e}")
        print(f"[DEBUG] Exception type: {type(e).__name__}")
        print(f"[DEBUG] Full error: {str(e)}")
        take_text = f"[Failed to generate take: Network error]"
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse OpenRouter API response JSON: {e}")
        try:
            print(f"[DEBUG] Raw response: {response.text[:500]}")
        except:
            print(f"[DEBUG] Could not read response text")
        take_text = "[Failed to generate take: invalid API response format]"
    except Exception as e:
        print(f"[ERROR] Unexpected error during OpenRouter API call: {e}")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        print(f"[DEBUG] Full error details: {str(e)}")
        take_text = f"[Failed to generate take: Unexpected error]"

    # 10. Format the new record with all current fields from results.json structure
    new_take = {
        "guid": target_entry.get('guid'),
        "link": target_entry['link'],
        "take": take_text,
        "original_title": target_entry['title'],
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }

    # 11. Insert at the top and Save
    results.insert(0, new_take)
    print(f"[DEBUG] Created new result entry with GUID: {target_entry.get('guid')}")

    print(f"[DEBUG] Saving {len(results)} total results to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"[SUCCESS] Successfully created a take for: {target_entry['title']}")

if __name__ == "__main__":
    generate_take()
