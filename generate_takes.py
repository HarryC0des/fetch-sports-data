import json
import os
import google.generativeai as genai

# 1. Setup Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_take():
    # 2. Load the source data
    with open('data.json', 'r') as f:
        source_data = json.load(f)
    
    # 3. Load existing results to prevent duplicates
    results = []
    processed_links = set()
    if os.path.exists('results.json'):
        with open('results.json', 'r') as f:
            results = json.load(f)
            processed_links = {item['link'] for item in results}

    # 4. Find the latest entry not yet processed
    # Assuming data.json is a list of entries
    target_entry = None
    for entry in reversed(source_data):
        if entry['link'] not in processed_links:
            target_entry = entry
            break
    
    if not target_entry:
        print("No new articles to process.")
        return

    # 5. The Grounded Prompt
    prompt = f"""
    You are a sharp-witted, professional sports analyst known for "hot takes" that are deeply rooted in facts.
    
    INPUT DATA:
    Title: {target_entry['title']}
    Description: {target_entry['description']}
    Article Content: {target_entry['content_html']}

    TASK:
    Generate a unique, memorable, and distinct sports take based on the provided input.

    STRICT CONSTRAINTS:
    1. NO HALLUCINATION: Do not invent stats, dates, or player movements not mentioned in the text.
    2. FACTUAL GROUNDING: Use ONLY facts from the provided input to build the argument.
    3. TONE: Be bold and opinionated, but remain accurate to the source.
    4. FORMAT: Return only the text of the take. No intro or outro.
    """

    response = model.generate_content(prompt)
    take_text = response.text.strip()

    # 6. Save back to results
    new_result = {
        "guid": target_entry['guid'],
        "link": target_entry['link'],
        "take": take_text,
        "generated_at": target_entry['ingested_at']
    }
    
    results.append(new_result)
    with open('results.json', 'w') as f:
        json.dump(results, f, indent=4)
    print(f"Successfully generated take for: {target_entry['title']}")

if __name__ == "__main__":
    generate_take()