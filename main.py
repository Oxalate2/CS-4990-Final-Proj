import logging

from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from abilities import llm_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def is_english(text):
    try:
        text.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

@app.route("/")
def root_route():
    return render_template("template.html")

@app.route("/send_message", methods=['POST'])
def send_message():
    user_message = request.json['message']
    if 'history' not in session:
        session['history'] = []
    session['history'].append({"user": user_message})
    if len(session['history']) > 10:
        session['history'] = session['history'][-10:]
    tagalog_response = llm_prompt(prompt=f"Translate '{user_message}' to Tagalog.", model="gpt-3.5-turbo-1106", temperature=0.5)
    english_response = llm_prompt(prompt=f"Translate '{user_message}' to English.", model="gpt-3.5-turbo-1106", temperature=0.5)
    combined_response = f"{tagalog_response} ({english_response})"
    session['history'].append({"bot": combined_response})
    return jsonify({"message": combined_response})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)