"""
JARVIS Flask Backend Server
- Reads API key from .env file
- Serves it securely to the frontend on localhost
- Run: python jarvis_server.py
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import uuid
import requests

load_dotenv()  # Load .env file

app = Flask(__name__, static_folder='.')
CORS(app, origins=["null", "http://localhost", "http://127.0.0.1"])

TOKEN_FILE = os.path.join(os.path.dirname(__file__), '.jarvis_engine_token')
ENGINE_TOKEN = os.getenv('JARVIS_ENGINE_TOKEN', '')
if not ENGINE_TOKEN and os.path.exists(TOKEN_FILE):
    try:
        ENGINE_TOKEN = open(TOKEN_FILE, 'r', encoding='utf-8').read().strip()
    except OSError:
        ENGINE_TOKEN = ''
if not ENGINE_TOKEN:
    ENGINE_TOKEN = uuid.uuid4().hex
    try:
        with open(TOKEN_FILE, 'w', encoding='utf-8') as tf:
            tf.write(ENGINE_TOKEN)
    except OSError:
        pass
os.environ['JARVIS_ENGINE_TOKEN'] = ENGINE_TOKEN

GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'

@app.route('/')
def index():
    """Serve jarvis-v2.html as the main page."""
    return send_from_directory('.', 'jarvis-v2.html')

@app.route('/api/config')
def get_config():
    """Return non-secret runtime configuration to the frontend."""
    key = os.getenv('GROQ_API_KEY', '')
    if not key or key == 'gsk_paste_your_key_here':
        return jsonify({'error': 'API key not configured in .env file'}), 500
    return jsonify({
        'ready': True,
        'engineBase': 'http://127.0.0.1:5050',
        'engineToken': ENGINE_TOKEN
    })


@app.route('/api/chat', methods=['POST'])
def proxy_chat():
    key = os.getenv('GROQ_API_KEY', '')
    if not key or key == 'gsk_paste_your_key_here':
        return jsonify({'error': 'API key not configured in .env file'}), 500

    payload = request.get_json(silent=True) or {}
    model = payload.get('model', 'llama-3.1-8b-instant')
    messages = payload.get('messages', [])
    tools = payload.get('tools', [])
    tool_choice = payload.get('tool_choice', 'auto')

    try:
        r = requests.post(
            GROQ_URL,
            headers={
                'Authorization': f'Bearer {key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': model,
                'messages': messages,
                'tools': tools,
                'tool_choice': tool_choice
            },
            timeout=45
        )
        return jsonify(r.json()), r.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Groq proxy failed: {str(e)}'}), 500


@app.route('/api/vision-analyze', methods=['POST'])
def proxy_vision_analyze():
    key = os.getenv('GROQ_API_KEY', '')
    if not key or key == 'gsk_paste_your_key_here':
        return jsonify({'error': 'API key not configured in .env file'}), 500

    payload = request.get_json(silent=True) or {}
    image_base64 = payload.get('image_base64', '')
    query = payload.get('query', 'Analyze this screenshot')
    if not image_base64:
        return jsonify({'error': 'Missing image payload'}), 400

    body = {
        'model': 'llama-3.2-90b-vision-preview',
        'messages': [{
            'role': 'user',
            'content': [
                {'type': 'text', 'text': f'Analyze this screenshot. Context: {query}. Describe what you see in detail so the main AI can answer the user.'},
                {'type': 'image_url', 'image_url': {'url': image_base64}}
            ]
        }],
        'temperature': 0.2,
        'max_tokens': 1024
    }

    try:
        r = requests.post(
            GROQ_URL,
            headers={
                'Authorization': f'Bearer {key}',
                'Content-Type': 'application/json'
            },
            json=body,
            timeout=60
        )
        return jsonify(r.json()), r.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Vision proxy failed: {str(e)}'}), 500

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve any other file in the jarvis directory."""
    blocked = {'.env', 'jarvis_server.py', 'jarvis_engine.py'}
    if filename in blocked:
        return jsonify({'error': 'Access denied'}), 403
    return send_from_directory('.', filename)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  JARVIS SERVER STARTING...")
    key = os.getenv('GROQ_API_KEY', '')
    if not key or key == 'gsk_paste_your_key_here':
        print("  ⚠  WARNING: Set your GROQ_API_KEY in .env file!")
    else:
        print(f"  ✓  API Key loaded: {key[:8]}...{key[-4:]}")
    print(f"  ✓  Engine token: {ENGINE_TOKEN[:8]}...")
    print("  ✓  Open: http://localhost:5000")
    print("="*50 + "\n")
    app.run(host='127.0.0.1', port=5000, debug=False)
