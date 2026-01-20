import json
import os
import google.generativeai as genai
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
    # 1. Setup Gemini API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY environment variable is not set!")
        return
    
    genai.configure(api_key=api_key)
    
    # 2. Define file paths
    input_file = 'data/records.json'
    output_file = 'results.json'

    # 3. Safety Check: Does the source file exist?
    if not os.path.exists(input_file):
        print(f"Error: Could not find {input_file}. Check your folder structure.")
        return

    # 4. Load the sports data
    with open(input_file, 'r', encoding='utf-8') as f:
        records = json.load(f)

    # 5. Get the most recent guids from both files
    records_guid = get_most_recent_guid_from_records()
    results_guid = get_most_recent_guid_from_results()

    # 6. Load existing results
    results = []
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
        except json.JSONDecodeError:
            print("Warning: results.json was empty or corrupt. Starting fresh.")

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
        
        print("Most recent entries match. No new article to process.")
        return

    # 8. New entry found - send only content_html to API
    target_entry = records[0]  # Get the most recent entry
    content_html = target_entry.get('content_html', '')
    
    prompt = f"""
    You are a professional sports analyst. Generate a unique, memorable, and distinct sports take.
    
    STRICT RULES:
    1. Use ONLY the facts provided below.
    2. Do NOT hallucinate stats, teams, or details not in the text.
    3. Be bold and sharp, but 100% factually grounded.
    4. Return ONLY the take itself.

    FACTS TO USE:
    {content_html}
    """

    # 9. Generate content using the corrected model ID
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        take_text = response.text.strip()
    except Exception as e:
        print(f"AI Generation failed: {e}")
        print(f"Error details: {type(e).__name__}")
        # Don't return - continue to at least create the file structure
        take_text = f"[Failed to generate take: {str(e)}]"

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

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully created a take for: {target_entry['title']}")

if __name__ == "__main__":
    generate_take()