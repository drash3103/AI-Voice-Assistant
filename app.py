import os
import requests
import sqlite3
import time
import threading
from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Get API key from environment variables
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

#hardcoded API key for backend's routes
API_KEY = "voicecall"

# Database Setup
def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect('calls.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS call_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            call_id TEXT NOT NULL,
            status TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Call Simulation 
def simulate_call_events(call_id):
    """
    Simulates a call flow in a background thread and updates the database.
    Emits real-time status updates via WebSocket.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Simulate connection and ringing
        statuses = ["Connecting...", "Ringing...", "In Progress...", "Call ended."]
        for status in statuses:
            time.sleep(2)  # Simulate network delay
            cursor.execute("INSERT INTO call_logs (call_id, status) VALUES (?, ?)", (call_id, status))
            conn.commit()
            socketio.emit('call_status', {'call_id': call_id, 'status': status})
            print(f"Simulating call status update: {status}")

    except Exception as e:
        print(f"Error during call simulation: {e}")
    finally:
        if conn:
            conn.close()

# API Endpoints
@app.before_request
def before_request_func():
    """A simple authentication check for API endpoints."""
    # Authenticate only on POST requests to protected endpoints
    if request.method == 'POST' and request.path in ['/generate_audio', '/place_call']:
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401

@app.route("/")
def home():
    """Serves the main HTML page."""
    return send_from_directory('.', 'index.html')

@app.route("/get_voices", methods=["GET"])
def get_voices():
    """
    Fetches a list of available voices from ElevenLabs API.
    """
    if not ELEVENLABS_API_KEY:
        return jsonify({"error": "ElevenLabs API key not configured"}), 500

    url = "https://api.elevenlabs.io/v1/voices"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        voices_data = response.json()
        
        # Extract and return relevant voice information
        voices = [{"voice_id": v["voice_id"], "name": v["name"]} for v in voices_data.get("voices", [])]
        return jsonify(voices)
    except requests.exceptions.RequestException as e:
        print(f"ElevenLabs API Error: {e}")
        return jsonify({"error": "Failed to fetch voices. Check your API key."}), 500


@app.route("/generate_audio", methods=["POST"])
def generate_audio():
    """
    Generates an audio file from text using the ElevenLabs API.
    """
    data = request.json
    text = data.get("text")
    voice_id = data.get("voice_id")

    if not text or not voice_id:
        return jsonify({"error": "Missing text or voice ID"}), 400

    if not ELEVENLABS_API_KEY:
        return jsonify({"error": "ElevenLabs API key not configured"}), 500

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
        },
    }

    try:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        response.raise_for_status()

        # Save the audio stream to a file
        audio_file_path = f"static/{voice_id}.mp3"
        os.makedirs(os.path.dirname(audio_file_path), exist_ok=True)
        with open(audio_file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

        audio_url = f"/static/{voice_id}.mp3"
        return jsonify({"audio_url": audio_url})
    except requests.exceptions.RequestException as e:
        print(f"ElevenLabs API Error: {e}")
        return jsonify({"error": "Failed to generate audio. Check your API key or input."}), 500

@app.route("/place_call", methods=["POST"])
def place_call():
    """
    Simulates a telephony call flow by starting a background thread.
    """
    data = request.json
    audio_url = data.get("audio_url")
    call_id = data.get("call_id")

    if not audio_url or not call_id:
        return jsonify({"error": "Missing audio_url or call_id"}), 400

    # Start the call simulation in a new thread
    call_thread = threading.Thread(target=simulate_call_events, args=(call_id,))
    call_thread.start()
    
    # Return a success message immediately
    return jsonify({
        "message": "Call initiated.",
        "call_id": call_id,
        "audio_url": audio_url
    }), 200

# Endpoint to serve static files
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/call_logs', methods=['GET'])
def get_call_logs():
    """Returns all call logs from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    logs = cursor.execute("SELECT * FROM call_logs ORDER BY timestamp DESC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in logs])

# Initialize the database when the application starts
with app.app_context():
    init_db()

if __name__ == '__main__':
    socketio.run(app, debug=True)