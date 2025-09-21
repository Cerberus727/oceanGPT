# test_gemini.py

import os
from dotenv import load_dotenv
import google.generativeai as genai

def run_gemini_test():
    """
    A simple function to test the Gemini API connection.
    """
    try:
        # Load the .env file to get the API key
        load_dotenv()
        google_api_key = os.getenv("GOOGLE_API_KEY")

        if not google_api_key:
            print("🔴 ERROR: GOOGLE_API_KEY not found in your .env file.")
            return

        # Configure the generative AI client with the API key
        genai.configure(api_key=google_api_key)

        # Initialize the model (using Flash for a quick response)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Define a simple prompt
        prompt = "In one sentence, what is the main purpose of the ARGO program in oceanography?"

        print(f"🤖 Sending prompt: '{prompt}'")
        print("--------------------------------------------------")

        # Generate the content
        response = model.generate_content(prompt)

        # Print the response text
        print("✅ Gemini Response:")
        print(response.text)

    except Exception as e:
        print(f"🔴 An error occurred: {e}")
        print("   Please check your API key, billing status, and that the Generative AI API is enabled.")

# Run the test function
if __name__ == "__main__":
    run_gemini_test()