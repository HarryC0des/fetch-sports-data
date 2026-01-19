import json
import os
from google import genai

def generate_take():
    # 1. Setup Gemini Client
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
    # 2. Path to your records.json
    input_file = 'data/records.json'
    output_file = 'results.json'

    if not os.path.exists(input_file):
        print(f"Error: Could not find {input_file}")
        return

    # 3. Load the sports data
    with open(input_file, 'r') as f:
        records = json.load(f)

    # 4. Find the latest entry not already in results.json
    processed_links = set()
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            existing_data = json.load(f)
            processed_links = {item['link'] for item in existing_data}

    # Get the most recent entry (assuming list)
    target_entry = None
    for entry in reversed(records):
        if entry['link'] not in processed_links:
            target_entry = entry
            break

    if not target_entry:
        print("No new news to process.")
        return

    # 5. Generate the Grounded "Sports Take"
    prompt = f"""
    Using ONLY the facts below, create a unique, memorable, and distinct sports take.
    Do not hallucinate or add outside info. Use a sharp, professional tone.
    
    FACTS:
    Title: {target_entry['title']}
    Details: {target_entry['description']}
    Full Context: {target_entry.get('content_html', '')}
    """

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    
    take_text = response.text.strip()

    # 6. Save to results.json
    new_take = {
        "link": target_entry['link'],
        "take": take_text,
        "original_title": target_entry['title'],
        "generated_at": target_entry.get('ingested_at', '2026-01-19')
    }

    results = []
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            results = json.load(f)
    
    results.append(new_take)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"Success! Take generated for: {target_entry['title']}")

if __name__ == "__main__":
    generate_take()