import json
import os
from google import genai

def generate_take():
    # 1. Setup Gemini Client with forced v1 API version for stability
    client = genai.Client(
        api_key=os.getenv("GOOGLE_API_KEY"),
        http_options={'api_version': 'v1'}
    )
    
    # 2. Define file paths
    # Note: Using the path you specified: data/records.json
    input_file = 'data/records.json'
    output_file = 'results.json'

    # 3. Safety Check: Does the source file exist?
    if not os.path.exists(input_file):
        print(f"Error: Could not find {input_file}. Check your folder structure.")
        return

    # 4. Load the sports data
    with open(input_file, 'r', encoding='utf-8') as f:
        records = json.load(f)

    # 5. Deduplication: Load existing results to avoid double-processing
    processed_links = set()
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                processed_links = {item['link'] for item in existing_data}
        except json.JSONDecodeError:
            print("Warning: results.json was empty or corrupt. Starting fresh.")

    # 6. Find the latest entry not already in results.json
    target_entry = None
    # We reverse the list to find the most recent update first
    for entry in reversed(records):
        if entry['link'] not in processed_links:
            target_entry = entry
            break

    if not target_entry:
        print("No new news to process. Everything is up to date!")
        return

    # 7. Construct the Fact-Based Prompt
    # We include 'content_html' if available for deeper context
    context = target_entry.get('content_html', target_entry.get('description', ''))
    
    prompt = f"""
    You are a professional sports analyst. Generate a unique, memorable, and distinct sports take.
    
    STRICT RULES:
    1. Use ONLY the facts provided below.
    2. Do NOT hallucinate stats, teams, or details not in the text.
    3. Be bold and sharp, but 100% factually grounded.
    4. Return ONLY the take itself.

    FACTS TO USE:
    Title: {target_entry['title']}
    Link: {target_entry['link']}
    Content: {context}
    """

    # 8. Generate content using the corrected model ID
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash', 
            contents=prompt
        )
        take_text = response.text.strip()
    except Exception as e:
        print(f"AI Generation failed: {e}")
        return

    # 9. Format the new record
    new_take = {
        "guid": target_entry.get('guid'),
        "link": target_entry['link'],
        "take": take_text,
        "original_title": target_entry['title'],
        "generated_at": target_entry.get('ingested_at')
    }

    # 10. Append and Save
    results = []
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            try:
                results = json.load(f)
            except:
                pass
    
    results.append(new_take)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
    
    print(f"Successfully created a take for: {target_entry['title']}")

if __name__ == "__main__":
    generate_take()