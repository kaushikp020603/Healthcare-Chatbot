from flask import Flask, request, render_template, session
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Gemini Pro model and get responses
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    
    # Join the chunks into a single string
    raw_response = ''.join(chunk.text for chunk in response)
    
    # Basic formatting: replace newlines with HTML line breaks and look for patterns for bullet points
    formatted_response = raw_response.replace('\n', '<br>')
    
    # Example: if the response contains a pattern like "- ", wrap it in <ul><li> tags for bullet points
    if '- ' in formatted_response:
        formatted_response = '<ul>' + ''.join(
            f'<li>{line.strip()}</li>' if line.startswith('- ') else line 
            for line in formatted_response.split('<br>')
        ) + '</ul>'
    
    return formatted_response

# Initialize chat history in session
def init_chat_history():
    if 'chat_history' not in session:
        session['chat_history'] = []

@app.route('/', methods=['GET', 'POST'])
def chatbot():
    init_chat_history()  # Ensure chat history is initialized

    user_input = ''
    bot_response = ''

    if request.method == 'POST':
        user_input = request.form['input']
        response = get_gemini_response(user_input)
        
        # Modify bot response for healthcare context (customize as per needs)
        bot_response = f"👨‍⚕️ Dr.Donna : {response}"

        # Store the user input and response in chat history
        session['chat_history'].append(('You', user_input))
        session['chat_history'].append(('Bot', bot_response))

    return render_template('chat.html', chat_history=session['chat_history'], user_input=user_input, bot_response=bot_response)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
