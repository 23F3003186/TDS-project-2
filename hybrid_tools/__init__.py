"""
Hybrid Agent Toolset
Provides web scraping, Python code execution, multimodal processing, and charting tools.
"""

import os
import io
import sys
import base64
import subprocess
import requests
from typing import Dict, Any, Optional
from langchain_core.tools import tool
from .send_request import post_request, reset_submission_tracking

@tool
def get_rendered_html(url: str) -> str:
    """Fetch and render HTML pages with JavaScript execution using Playwright (or requests fallback)."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=10000)
            content = page.content()
            browser.close()
            return content
    except Exception:
        # Fallback to requests if playwright is not initialized
        resp = requests.get(url, timeout=15)
        return resp.text

@tool
def extract_context(html: str, base_url: str = "") -> Dict[str, Any]:
    """Extract form actions, submit URLs, script tags, and API endpoints from rendered HTML."""
    from bs4 import BeautifulSoup
    import re
    from urllib.parse import urljoin
    
    soup = BeautifulSoup(html, "html.parser")
    forms = []
    for form in soup.find_all("form"):
        forms.append({
            "action": urljoin(base_url, form.get("action", "")),
            "method": form.get("method", "GET").upper(),
            "inputs": [inp.get("name") for inp in form.find_all(["input", "textarea", "select"]) if inp.get("name")]
        })
    
    scripts = [s.get_text() for s in soup.find_all("script") if s.get_text()]
    
    # Simple regex for finding endpoints inside scripts
    api_patterns = re.findall(r'["\'](/api/[^"\']+|https?://[^"\']+)["\']', html)
    
    return {
        "forms": forms,
        "api_endpoints": list(set(api_patterns)),
        "scripts_count": len(scripts),
        "text_content": soup.get_text()[:2000]
    }

@tool
def download_file(url: str, filename: str = "") -> str:
    """Download a file from URL and save it locally in the workspace."""
    if not filename:
        filename = url.split("?")[0].split("/")[-1] or "downloaded_file.dat"
    
    save_dir = os.path.join(os.getcwd(), "hybrid_llm_files")
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, filename)
    
    resp = requests.get(url, stream=True, timeout=30)
    with open(file_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            
    return file_path

@tool
def run_code(code: str) -> str:
    """Execute Python code in a subprocess sandbox with 90s timeout and return stdout / answer."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=90
        )
        if result.returncode == 0:
            return result.stdout.strip() or "Execution succeeded with no output."
        else:
            return f"Error (Exit {result.returncode}):\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "Execution timed out after 90 seconds."
    except Exception as e:
        return f"Execution error: {e}"

@tool
def add_dependencies(packages: str) -> str:
    """Dynamically install Python packages via pip."""
    try:
        pkg_list = packages.replace(",", " ").split()
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install"] + pkg_list,
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Pip install error: {e}"

@tool
def transcribe_audio(audio_url: str) -> str:
    """Transcribe audio from URL using SpeechRecognition / Whisper."""
    try:
        import speech_recognition as sr
        # Download temp file
        local_path = download_file.invoke({"url": audio_url, "filename": "temp_audio.wav"})
        r = sr.Recognizer()
        with sr.AudioFile(local_path) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data)
            return text
    except Exception as e:
        return f"Speech recognition error: {e}"

@tool
def analyze_image(image_url: str, question: str = "") -> str:
    """Analyze images and OCR text using Google Gemini Vision or PIL."""
    try:
        import google.generativeai as genai
        from PIL import Image
        local_path = download_file.invoke({"url": image_url, "filename": "temp_img.png"})
        img = Image.open(local_path)
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = question or "Transcribe all text, numbers, and data tables visible in this image."
            response = model.generate_content([prompt, img])
            return response.text
        return "Image downloaded successfully at " + local_path
    except Exception as e:
        return f"Image analysis error: {e}"

@tool
def create_visualization(data_description: str, chart_type: str = "bar", title: str = "") -> str:
    """Generate charts as Base64-encoded PNG strings using matplotlib/seaborn."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(8, 5))
    plt.title(title or f"{chart_type.capitalize()} Chart")
    # Placeholder chart generation
    plt.plot([1, 2, 3, 4], [10, 20, 15, 30])
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    plt.close()
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:image/png;base64,{img_b64}"

@tool
def create_chart_from_data(data_code: str, chart_config: str = "") -> str:
    """Execute custom Python plotting code and return Base64-encoded PNG string."""
    script = f"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64

{data_code}

buf = io.BytesIO()
plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
buf.seek(0)
print('BASE64:' + base64.b64encode(buf.read()).decode('utf-8'))
"""
    result = run_code.invoke({"code": script})
    if "BASE64:" in result:
        b64 = result.split("BASE64:")[-1].strip()
        return f"data:image/png;base64,{b64}"
    return result

# Re-export tools
__all__ = [
    "get_rendered_html",
    "extract_context",
    "download_file",
    "run_code",
    "add_dependencies",
    "transcribe_audio",
    "analyze_image",
    "create_visualization",
    "create_chart_from_data",
    "post_request",
    "reset_submission_tracking"
]
