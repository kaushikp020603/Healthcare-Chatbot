from flask import Flask, request, render_template, session
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")  # Store securely in .env

# Configure Google Generative AI
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Google API key is missing. Set it in the .env file.")

genai.configure(api_key=api_key)

# Initialize Gemini model (using the correct model name)
try:
    model = genai.GenerativeModel("gemini-1.5-pro")  # Updated model name
    chat = model.start_chat(history=[])
except Exception as e:
    print(f"Error initializing Gemini model: {e}")
    chat = None

def get_gemini_response(question):
    """Generates a response using the Gemini model."""
    if not chat:
        return "❌ AI model is unavailable. Please check the API key or model name."

    try:
        response = chat.send_message(question, stream=True)

        # Join the chunks into a single string
        raw_response = ''.join(chunk.text for chunk in response if chunk.text)

        # Basic formatting: replace newlines with HTML line breaks
        formatted_response = raw_response.replace('\n', '<br>')

        # Convert bullet points into HTML <ul><li> list format
        if '- ' in formatted_response:
            formatted_response = '<ul>' + ''.join(
                f'<li>{line.strip()}</li>' if line.startswith('- ') else line
                for line in formatted_response.split('<br>')
            ) + '</ul>'

        return formatted_response if formatted_response else "⚠️ No response from AI."

    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "❌ An error occurred while generating a response."

# Initialize chat history in session
def init_chat_history():
    if 'chat_history' not in session:
        session['chat_history'] = []

@app.route('/', methods=['GET', 'POST'])
def chatbot():
    """Handles user input and AI response generation."""
    init_chat_history()  # Ensure chat history is initialized

    user_input = ''
    bot_response = ''

    if request.method == 'POST':
        user_input = request.form['input'].strip()
        if user_input:
            response = get_gemini_response(user_input)
            bot_response = f"👨‍⚕️ Dr.Donna : {response}"

            # Store the conversation in chat history
            session['chat_history'].append(('You', user_input))
            session['chat_history'].append(('Bot', bot_response))

    return render_template('chat.html', chat_history=session['chat_history'], user_input=user_input, bot_response=bot_response)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
