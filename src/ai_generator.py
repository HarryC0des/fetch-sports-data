"""
AI-Powered Sports Takes Generator

Generates unique sports takes using OpenRouter API based on news article descriptions.
"""
import os
import requests
from datetime import datetime
from src.utils import load_records, load_results, save_results


API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "tngtech/tng-r1t-chimera:free"


def get_most_recent_guid(records):
    """Get the GUID of the most recent entry in records."""
    return records[0]['guid'] if records else None


def generate_take_from_content(content_html, api_key=None):
    """
    Generate a sports take from article content using OpenRouter API.
    
    Args:
        content_html: Article content as HTML/text
        api_key: OpenRouter API key (uses env var if not provided)
        
    Returns:
        Generated take text or error message
    """
    api_key = api_key or os.getenv("OPEN_ROUTER_KEY")
    
    if not api_key:
        print("[ERROR] OPEN_ROUTER_KEY environment variable is not set!")
        return None
    
    print("[DEBUG] OPEN_ROUTER_KEY found in environment")
    
    prompt = f"""You are a professional sports analyst. Generate a unique, memorable, and distinct sports take.

STRICT RULES:
1. Use ONLY the facts provided below.
2. Do NOT hallucinate stats, teams, or details not in the text.
3. Be bold and sharp, but 100% factually grounded.
4. Return ONLY the take itself.

FACTS TO USE:
{content_html}"""
    
    print(f"[DEBUG] Sending request to OpenRouter API")
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/HarryC0des/fetch-sports-data",
            "X-Title": "Sports Takes Generator"
        }
        print(f"[DEBUG] Request headers prepared (Authorization: Bearer [REDACTED])")
        
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        print(f"[DEBUG] Request payload prepared (model: {MODEL}, prompt length: {len(prompt)} chars)")
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        print(f"[DEBUG] API response status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[ERROR] OpenRouter API returned status code {response.status_code}")
            print(f"[DEBUG] Response content: {response.text[:500]}")
            return f"[Failed to generate take: OpenRouter API returned status {response.status_code}]"
        
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
            return "[Failed to generate take: empty response from API]"
        
        print(f"[DEBUG] Successfully generated take ({len(take_text)} chars)")
        return take_text
        
    except requests.exceptions.Timeout:
        print(f"[ERROR] OpenRouter API request timed out (60 second timeout)")
        return "[Failed to generate take: API request timeout]"
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error during OpenRouter API call: {e}")
        print(f"[DEBUG] Exception type: {type(e).__name__}")
        print(f"[DEBUG] Full error: {str(e)}")
        return f"[Failed to generate take: Network error]"
    except Exception as e:
        print(f"[ERROR] Unexpected error during OpenRouter API call: {e}")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        print(f"[DEBUG] Full error details: {str(e)}")
        return f"[Failed to generate take: Unexpected error]"


def generate_take():
    """
    Main function to generate a take for the most recent article.
    """
    print(f"[DEBUG] Using API endpoint: {API_URL}")
    
    # Load data
    print(f"[DEBUG] Loading records from data/records.json")
    records = load_records()
    print(f"[DEBUG] Loaded {len(records)} records")
    
    if not records:
        print(f"[ERROR] No records found")
        return
    
    results = load_results()
    print(f"[DEBUG] Loaded existing results with {len(results)} entries")
    
    # Get GUIDs
    records_guid = get_most_recent_guid(records)
    results_guid = get_most_recent_guid(results)
    print(f"[DEBUG] Records GUID: {records_guid}")
    print(f"[DEBUG] Results GUID: {results_guid}")
    
    # Check if guids match
    if records_guid == results_guid:
        message_entry = {
            "guid": records_guid,
            "link": records[0]['link'] if records else None,
            "take": "No new article to process. The most recent entry in records.json matches the most recent entry in results.json.",
            "original_title": records[0]['title'] if records else None,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
        
        results.insert(0, message_entry)
        save_results(results)
        
        print("[DEBUG] Most recent entries match. No new article to process.")
        return
    
    # Process new entry
    target_entry = records[0]
    content_html = target_entry.get('content_html', '')
    print(f"[DEBUG] Processing new article: {target_entry.get('title')}")
    print(f"[DEBUG] Content length: {len(content_html)} characters")
    
    take_text = generate_take_from_content(content_html)
    
    if not take_text:
        return
    
    # Create and save result
    new_take = {
        "guid": target_entry.get('guid'),
        "link": target_entry['link'],
        "take": take_text,
        "original_title": target_entry['title'],
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }
    
    results.insert(0, new_take)
    print(f"[DEBUG] Created new result entry with GUID: {target_entry.get('guid')}")
    
    print(f"[DEBUG] Saving {len(results)} total results")
    save_results(results)
    
    print(f"[SUCCESS] Successfully created a take for: {target_entry['title']}")


if __name__ == "__main__":
    generate_take()
