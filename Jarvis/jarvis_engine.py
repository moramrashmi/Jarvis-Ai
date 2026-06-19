import os
import subprocess
import base64
import tempfile
import json
import socket
import ipaddress
import uuid
import shlex
from urllib.parse import urlparse
from io import BytesIO
from flask import Flask, request, jsonify
from flask_cors import CORS

try:
    from PIL import ImageGrab
except ImportError:
    print("Installing Pillow for screen capture...")
    subprocess.check_call(["pip", "install", "Pillow"])
    from PIL import ImageGrab

try:
    import requests as http_requests
except ImportError:
    print("Installing requests for web scraping...")
    subprocess.check_call(["pip", "install", "requests"])
    import requests as http_requests

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing BeautifulSoup4 for web scraping...")
    subprocess.check_call(["pip", "install", "beautifulsoup4"])
    from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://127.0.0.1:5000", "http://localhost:5000"]}})

TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".jarvis_engine_token")
ENGINE_TOKEN = os.getenv("JARVIS_ENGINE_TOKEN", "")
if not ENGINE_TOKEN and os.path.exists(TOKEN_FILE):
    try:
        ENGINE_TOKEN = open(TOKEN_FILE, "r", encoding="utf-8").read().strip()
    except OSError:
        ENGINE_TOKEN = ""
if not ENGINE_TOKEN:
    ENGINE_TOKEN = uuid.uuid4().hex
    try:
        with open(TOKEN_FILE, "w", encoding="utf-8") as tf:
            tf.write(ENGINE_TOKEN)
    except OSError:
        pass
    print("[JARVIS ENGINE] JARVIS_ENGINE_TOKEN was not set. Generated local persistent token.")

PYTHON_CMD = os.getenv("JARVIS_PYTHON_CMD", "python")
NODE_CMD = os.getenv("JARVIS_NODE_CMD", "node")


def _is_authorized(req):
    return req.headers.get("X-Jarvis-Token", "") == ENGINE_TOKEN


def _auth_error():
    return jsonify({"error": "Unauthorized request"}), 401


def _is_private_host(hostname):
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return True
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast:
            return True
    return False


def _validate_external_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False, "Only http/https URLs are allowed"
    if not parsed.hostname:
        return False, "Invalid URL hostname"
    if _is_private_host(parsed.hostname):
        return False, "Access to private or local network targets is blocked"
    return True, ""


def _run_safe_command(command):
    lowered = command.strip().lower()
    # Keep a narrow but useful command surface.
    allowed_prefixes = (
        "start ",
        "explorer ",
        "code ",
        "notepad",
        "calc",
        "tasklist",
        "whoami",
        "ipconfig",
        "ping ",
        "dir",
    )
    blocked_keywords = (
        "powershell -enc",
        "curl ",
        "invoke-webrequest",
        "reg add",
        "net user",
        "format ",
        "shutdown",
        "del /f",
        "rd /s",
    )
    if any(k in lowered for k in blocked_keywords):
        return False, "Command blocked by policy"
    if not lowered.startswith(allowed_prefixes):
        return False, "Command not allowed by policy"

    if lowered.startswith("start "):
        target = command.strip()[6:].strip()
        if not target:
            return False, "Missing start target"
        subprocess.Popen(["cmd", "/c", "start", "", target], shell=False)
        return True, "Command started in background"

    if lowered.startswith("explorer "):
        target = command.strip()[9:].strip()
        if not target:
            return False, "Missing explorer target"
        subprocess.Popen(["explorer", target], shell=False)
        return True, "Explorer launched"

    args = shlex.split(command, posix=False)
    if not args:
        return False, "Empty command"
    result = subprocess.run(args, shell=False, capture_output=True, text=True, timeout=15)
    output = result.stdout if result.returncode == 0 else result.stderr
    return result.returncode == 0, (output[:2000] if output else "Command completed")

# ── SYSTEM CONTROL ──
@app.route('/api/system', methods=['POST'])
def system_control():
    """Executes a terminal command on the Windows PC."""
    if not _is_authorized(request):
        return _auth_error()

    data = request.json
    command = data.get('command')
    
    if not command:
        return jsonify({'error': 'No command provided'}), 400
        
    print(f"\n[JARVIS ENGINE] Executing: {command}")
    
    try:
        ok, output = _run_safe_command(command)
        return jsonify({'status': 'Success' if ok else 'Error', 'output': output})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── VISION CAPTURE ──
@app.route('/api/vision', methods=['GET'])
def capture_screen():
    """Takes a screenshot and returns it as a base64 string."""
    if not _is_authorized(request):
        return _auth_error()

    print("\n[JARVIS ENGINE] Capturing Screen...")
    try:
        screenshot = ImageGrab.grab()
        screenshot.thumbnail((1280, 720))
        
        buffered = BytesIO()
        screenshot.save(buffered, format="JPEG", quality=70)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({'image_base64': f"data:image/jpeg;base64,{img_str}"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── SCRIPT EXECUTION (Engineer Mode) ──
@app.route('/api/run_script', methods=['POST'])
def run_script():
    """Writes a script to a temp file and executes it."""
    if not _is_authorized(request):
        return _auth_error()

    data = request.json
    language = data.get('language', 'python')
    script = data.get('script', '')
    
    if not script:
        return jsonify({'error': 'No script provided'}), 400
    
    print(f"\n[JARVIS ENGINE] Running {language} script...")
    print(f"Script preview: {script[:200]}...")
    
    try:
        if language not in ('python', 'node'):
            return jsonify({'error': 'Unsupported script language'}), 400

        ext = '.py' if language == 'python' else '.js'
        cmd = PYTHON_CMD if language == 'python' else NODE_CMD
        
        # Write script to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix=ext, prefix='jarvis_script_', delete=False, encoding='utf-8') as f:
            script_path = f.name
            f.write(script)
        
        # Execute
        result = subprocess.run(
            [cmd, script_path],
            capture_output=True, text=True, timeout=30,
            cwd=os.path.expanduser('~\\Desktop')
        )
        
        output = result.stdout + result.stderr
        status = 'Success' if result.returncode == 0 else 'Error'
        
        print(f"[JARVIS ENGINE] Script {status}: {output[:200]}")
        
        return jsonify({
            'status': status,
            'output': output[:3000] if output else f"Script executed successfully ({status}).",
            'return_code': result.returncode
        })
    except FileNotFoundError:
        return jsonify({'error': f'Runtime not found: {cmd}'}), 500
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Script timed out after 30 seconds'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        try:
            if 'script_path' in locals() and os.path.exists(script_path):
                os.remove(script_path)
        except OSError:
            pass

# ── WEB SCRAPING (Auto-Pilot Agent) ──
@app.route('/api/scrape', methods=['POST'])
def web_scrape():
    """Fetches a URL and extracts text content."""
    if not _is_authorized(request):
        return _auth_error()

    data = request.json
    url = data.get('url', '')
    target = data.get('target', 'main content')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    print(f"\n[JARVIS ENGINE] Scraping: {url}")
    print(f"Target: {target}")

    valid, reason = _validate_external_url(url)
    if not valid:
        return jsonify({'error': reason}), 400
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        resp = http_requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Remove script and style elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'iframe']):
            tag.decompose()
        
        # Extract based on target keywords
        content = ""
        target_lower = target.lower()
        
        # Try to find specific elements based on target
        if 'price' in target_lower or 'cost' in target_lower:
            # Look for price-related elements
            price_elements = soup.find_all(class_=lambda x: x and ('price' in str(x).lower()))
            if price_elements:
                content = "\n".join([el.get_text(strip=True) for el in price_elements[:20]])
        
        if 'table' in target_lower:
            tables = soup.find_all('table')
            for table in tables[:3]:
                rows = table.find_all('tr')
                for row in rows[:30]:
                    cells = row.find_all(['td', 'th'])
                    content += " | ".join([cell.get_text(strip=True) for cell in cells]) + "\n"
        
        if 'title' in target_lower or 'heading' in target_lower:
            headings = soup.find_all(['h1', 'h2', 'h3'])
            content = "\n".join([h.get_text(strip=True) for h in headings[:20]])
        
        # Fallback: get main text content
        if not content:
            # Try article or main tags first
            main = soup.find('article') or soup.find('main') or soup.find(class_='content') or soup.body
            if main:
                paragraphs = main.find_all(['p', 'h1', 'h2', 'h3', 'li'])
                content = "\n".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 10])
        
        # Trim
        content = content[:5000]
        
        if not content:
            content = soup.get_text(separator='\n', strip=True)[:3000]
        
        print(f"[JARVIS ENGINE] Scraped {len(content)} chars")
        
        return jsonify({
            'content': f"Scraped from {url}:\n\n{content}",
            'url': url,
            'length': len(content)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── HEALTH CHECK ──
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'JARVIS Engine Online', 'tools': ['system_control', 'vision', 'run_script', 'web_scrape']})

if __name__ == '__main__':
    print("\n" + "="*55)
    print("  JARVIS IRON MAN ENGINE v3.0")
    print("  " + "-"*40)
    print("  [OK] Local System Control    ONLINE")
    print("  [OK] Vision Capture          ONLINE")
    print("  [OK] Script Execution        ONLINE")
    print("  [OK] Web Scraping Agent      ONLINE")
    print("  " + "-"*40)
    print("  Listening on 127.0.0.1:5050")
    print(f"  Engine token prefix: {ENGINE_TOKEN[:8]}...")
    print("="*55 + "\n")
    app.run(host='127.0.0.1', port=5050, debug=False)
