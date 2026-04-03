import os
import re
import hashlib
from aqt import mw
from aqt.qt import *
from aqt.browser import Browser
from aqt.utils import showInfo, tooltip
from anki.utils import stripHTML
from .gui import AnkiVNTTSDialog, AnkiVNProgressDialog
from .generator import generate_audio_sync

def on_generate_audio(browser: Browser):
    nids = browser.selectedNotes()
    if not nids:
        showInfo("Vui lòng chọn ít nhất 1 thẻ (note).")
        return
        
    dialog = AnkiVNTTSDialog(browser, nids)
    if not dialog.exec():
        return
        
    config = dialog.get_config()
    
    # Show progress dialog
    progress_dialog = AnkiVNProgressDialog(browser, len(nids), config)
    progress_dialog.show()
    
    mw.taskman.run_in_background(
        lambda: run_batch_generation(nids, config, progress_dialog),
        lambda future: on_generation_done(browser, future, progress_dialog)
    )

def run_batch_generation(nids, config, progress_dialog):
    src_field = config["source_field"]
    dst_field = config["destination_field"]
    voice = config["voice"]
    mode = config["mode"]
    rate = config.get("rate", "+0%")
    pitch = config.get("pitch", "+0Hz")
    volume = config.get("volume", "+0%")
    engine = config.get("engine", "Edge TTS")
    piper_exe = config.get("piper_exe", "")
    piper_model = config.get("piper_model", "")
    
    media_dir = mw.col.media.dir()
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    from .generator import clean_tts_text
    
    for idx, nid in enumerate(nids):
        if config.get("abort"):
            break
            
        def update_ui(c=idx+1, s=success_count, e=error_count, sk=skipped_count):
            mw.taskman.run_on_main(lambda: progress_dialog.update_stats(c, s, e, sk))
            
        note = mw.col.get_note(nid)
        if src_field not in note or dst_field not in note:
            skipped_count += 1
            update_ui(sk=skipped_count)
            continue
            
        # If append mode and sound already exists in dst_field, skip
        if mode == "Append" and "[sound:" in note[dst_field]:
            skipped_count += 1
            update_ui(sk=skipped_count)
            continue
            
        raw_text = note[src_field]
        text = clean_tts_text(raw_text)
        
        if not text:
            skipped_count += 1
            update_ui(sk=skipped_count)
            continue
            
        try:
            # Hash context for filename: includes engine, text, voice, rate, pitch, volume, piper_model
            hash_ctx = f"{engine}_{text}_{voice}_{rate}_{pitch}_{volume}_{os.path.basename(piper_model)}"
            hash_str = hashlib.md5(hash_ctx.encode("utf-8")).hexdigest()[:10]
            
            eng_prefix = engine.split()[0].lower() # "edge", "google", "windows", "piper"
            filename = f"ankivntts_{eng_prefix}_{voice}_{hash_str}.mp3"
            filepath = os.path.join(media_dir, filename)
            
            # Generate if not exists
            if not os.path.exists(filepath):
                generate_audio_sync(text, voice, filepath, rate, pitch, volume, engine, piper_exe, piper_model)
                
            sound_tag = f"[sound:{filename}]"
            
            if mode == "Overwrite":
                note[dst_field] = sound_tag
            else: # Append
                if sound_tag not in note[dst_field]:
                    note[dst_field] = note[dst_field] + " " + sound_tag
            
            mw.col.update_note(note)
            success_count += 1
            
        except Exception as e:
            print(f"Error generating audio for nid {nid}: {e}")
            error_count += 1
            
        update_ui()
            
    return success_count, error_count, skipped_count

def on_generation_done(browser, future, progress_dialog):
    progress_dialog.accept()
    try:
        success_count, error_count, skipped_count = future.result()
    except Exception as e:
        showInfo(f"Đã xảy ra lỗi hệ thống: {e}")
        return
        
    # Reload browser to show updated notes
    browser.model.reset()
    mw.requireReset()
    
    showInfo(f"Hoàn thành!\nĐã tạo thành công: {success_count} thẻ.\nLỗi: {error_count} thẻ.\nBỏ qua: {skipped_count} thẻ.")

from aqt import gui_hooks
from aqt.qt import QMenu

def setup_browser_menu(browser):
    menu = QMenu("AnkiVN TTS", browser.form.menubar)
    
    action = QAction("Add Audio (Edge TTS)...", browser)
    action.triggered.connect(lambda _, b=browser: on_generate_audio(b))
    menu.addAction(action)
    
    browser.form.menubar.addMenu(menu)

gui_hooks.browser_menus_did_init.append(setup_browser_menu)
