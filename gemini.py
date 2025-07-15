import google.generativeai as genai
from serpapi import GoogleSearch
import os
import json

# --- Configuration ---
# Correct: use the NAME of the env variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

if not GEMINI_API_KEY or not SERPAPI_API_KEY:
    raise ValueError("Please set GEMINI_API_KEY and SERPAPI_API_KEY environment variables.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

HISTORY_FILE = "chat_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def search(query):
    params = {
        "q": query,
        "hl": "en",
        "gl": "us",
        "api_key": SERPAPI_API_KEY
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
    except Exception as e:
        print(f"Search API error: {e}")
        return "No results found due to search error."

    if "organic_results" in results:
        snippets = [res.get("snippet", "") for res in results["organic_results"][:5]]
        return "\n".join(snippets)

    return "No results found."

def chat_with_ai(query):
    chat_history = load_history()

    if any(keyword in query.lower() for keyword in ["weather", "price", "news", "who is", "what is"]):
        search_results = search(query)
        context = f"Real-time Search Results:\n{search_results}\n"
    else:
        context = ""

    chat_history.append(f"User: {query}")

    prompt = context + "\n".join(chat_history) + "\nAI:"

    try:
        response = model.generate_content(prompt)
        answer = response.text.strip()
    except Exception as e:
        answer = f"Error generating response: {e}"

    chat_history.append(f"AI: {answer}")
    save_history(chat_history)
    return answer

if __name__ == "__main__":
    print("Welcome to the AI Chatbot! Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() == "exit":
            break
        reply = chat_with_ai(user_input)
        print("AI:", reply)
