import asyncio
import os
import sys
import re
import urllib.parse
import urllib.request
import edge_tts
from anki.utils import stripHTML

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def clean_tts_text(raw_text):
    text = stripHTML(raw_text).strip()
    text = text.replace("&nbsp;", " ")
    # Replace cloze deletions {{c1::text::hint}} -> text
    text = re.sub(r'\{\{c\d+::(.*?)(::.*?)?\}\}', r'\1', text)
    # Remove existing sound tags
    text = re.sub(r'\[sound:.*?\]', '', text)
    # Remove text inside parentheses, brackets
    text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    text = re.sub(r'\{[^}]*\}', '', text)
    # Clean up double spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def sync_get_voices():
    """Retrieve voices sequentially for the GUI dropdown."""
    return asyncio.run(edge_tts.list_voices())

def sync_get_sapi_voices():
    import subprocess
    cmd = ["powershell", "-Command", "Add-Type -AssemblyName System.speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; foreach ($voice in $speak.GetInstalledVoices()) { Write-Host $voice.VoiceInfo.Name }"]
    try:
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=flags)
        if result.returncode == 0:
            return [v.strip() for v in result.stdout.split('\n') if v.strip()]
    except Exception:
        pass
    return []

async def _edge_tts_async(text, voice, output_path, rate="+0%", pitch="+0Hz", volume="+0%"):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=volume)
    await communicate.save(output_path)

def _google_tts_sync(text, lang, output_path):
    lang_code = lang.split('-')[0].lower() if '-' in lang else 'en'
    text = text[:200]
    encoded_text = urllib.parse.quote(text)
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_text}&tl={lang_code}&client=tw-ob"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open(output_path, 'wb') as out_file:
        out_file.write(response.read())

def _sapi_tts_sync(text, voice_name, output_path, rate="+0%"):
    import subprocess
    rate_val = 0
    if rate.endswith("%"):
        try:
            val = int(rate[:-1])
            rate_val = min(max(val // 10, -10), 10)
        except: pass
        
    text_clean = text.replace('"', "'")
    script = f'''
Add-Type -AssemblyName System.speech
$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {{ $speak.SelectVoice("{voice_name}") }} catch {{}}
$speak.Rate = {rate_val}
$speak.SetOutputToWaveFile("{output_path}")
$speak.Speak("{text_clean}")
'''
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    subprocess.run(["powershell", "-Command", script], creationflags=flags)

def _piper_tts_sync(text, output_path, piper_exe, model_path):
    import subprocess
    if not os.path.exists(piper_exe) or not os.path.exists(model_path):
        raise ValueError(f"Thiết lập Piper TTS bị thiếu hoặc sai đường dẫn file!")
        
    cmd = [piper_exe, "--model", model_path, "--output_file", output_path]
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, creationflags=flags)
    process.communicate(input=text.encode("utf-8"))

def generate_audio_sync(text, voice, output_path, rate="+0%", pitch="+0Hz", volume="+0%", engine="Edge TTS", piper_exe="", piper_model=""):
    """Synchronous wrapper to generate audio using selected engine."""
    if engine == "Google TTS":
        _google_tts_sync(text, voice, output_path)
    elif engine == "Windows SAPI":
        _sapi_tts_sync(text, voice, output_path, rate)
    elif engine == "Piper Offline":
        _piper_tts_sync(text, output_path, piper_exe, piper_model)
    else:
        asyncio.run(_edge_tts_async(text, voice, output_path, rate, pitch, volume))
