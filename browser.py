import os
import re
import hashlib
import concurrent.futures
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
        
    tasks = dialog.get_tasks()
    if not tasks:
        return
        
    progress_dialog = AnkiVNProgressDialog(browser, len(nids) * len(tasks))
    progress_dialog.show()
    
    mw.taskman.run_in_background(
        lambda: run_batch_generation(nids, tasks, progress_dialog),
        lambda future: on_generation_done(browser, future, progress_dialog)
    )

def run_batch_generation(nids, tasks, progress_dialog):
    from .generator import clean_tts_text
    
    media_dir = mw.col.media.dir()
    success_count = 0
    error_count = 0
    skipped_count = 0
    current_count = 0
    
    work_items = []
    note_updates = {nid: {} for nid in nids}
    
    for nid in nids:
        note = mw.col.get_note(nid)
        for t in tasks:
            src = t["source_field"]
            dst = t["destination_field"]
            mode = t["mode"]
            
            if src not in note or dst not in note:
                skipped_count += 1
                current_count += 1
                continue
                
            if mode == "Append" and "[sound:" in note[dst]:
                skipped_count += 1
                current_count += 1
                continue
                
            raw_text = note[src]
            text = clean_tts_text(raw_text)
            
            if not text:
                skipped_count += 1
                current_count += 1
                continue
                
            engine = t.get("engine", "Edge TTS")
            voice = t.get("voice", "")
            rate = t.get("rate", "+0%")
            pitch = t.get("pitch", "+0Hz")
            volume = t.get("volume", "+0%")
            piper_exe = t.get("piper_exe", "")
            piper_model = t.get("piper_model", "")
            
            hash_ctx = f"{engine}_{text}_{voice}_{rate}_{pitch}_{volume}_{os.path.basename(piper_model)}"
            hash_str = hashlib.md5(hash_ctx.encode("utf-8")).hexdigest()[:10]
            
            eng_prefix = engine.split()[0].lower() # edge, google, windows, piper
            filename = f"ankivntts_{eng_prefix}_{voice}_{hash_str}.mp3"
            filepath = os.path.join(media_dir, filename)
            sound_tag = f"[sound:{filename}]"
            
            if dst not in note_updates[nid]:
                note_updates[nid][dst] = {"mode": mode, "tags": []}
            note_updates[nid][dst]["tags"].append(sound_tag)
            
            if not os.path.exists(filepath):
                work_items.append({
                    "text": text, "voice": voice, "filepath": filepath,
                    "rate": rate, "pitch": pitch, "volume": volume,
                    "engine": engine, "piper_exe": piper_exe, "piper_model": piper_model
                })
            else:
                success_count += 1
                current_count += 1

    # Update UI with initial skipped/cached stats
    def update_ui(c, s, e, sk):
        mw.taskman.run_on_main(lambda: progress_dialog.update_stats(c, s, e, sk))
        
    update_ui(current_count, success_count, error_count, skipped_count)

    # ĐA LUỒNG - MULTI THREADING GENERATION
    if work_items:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_work = {}
            for w in work_items:
                f = executor.submit(generate_audio_sync, 
                                    w["text"], w["voice"], w["filepath"], 
                                    w["rate"], w["pitch"], w["volume"], 
                                    w["engine"], w["piper_exe"], w["piper_model"])
                future_to_work[f] = w
                
            for future in concurrent.futures.as_completed(future_to_work):
                if progress_dialog.abort_flag:
                    for pf in future_to_work: pf.cancel()
                    break
                    
                current_count += 1
                try:
                    future.result()
                    success_count += 1
                except Exception as exc:
                    print(f"Lỗi đa luồng: {exc}")
                    error_count += 1
                    
                update_ui(current_count, success_count, error_count, skipped_count)

    # APPLY TAGS TO NOTES
    for nid, fields_to_update in note_updates.items():
        if not fields_to_update:
            continue
        try:
            note = mw.col.get_note(nid)
            changed = False
            for dst, data in fields_to_update.items():
                mode = data["mode"]
                if mode == "Overwrite":
                    note[dst] = " ".join(data["tags"])
                    changed = True
                else:
                    for tag in data["tags"]:
                        if tag not in note[dst]:
                            note[dst] = note[dst] + (" " if note[dst] else "") + tag
                            changed = True
                            
            if changed:
                mw.col.update_note(note)
        except Exception as e:
            print(f"Lỗi cập nhật Note {nid}: {e}")

    return success_count, error_count, skipped_count

def on_generation_done(browser, future, progress_dialog):
    progress_dialog.accept()
    try:
        success_count, error_count, skipped_count = future.result()
    except Exception as e:
        showInfo(f"Đã xảy ra lỗi hệ thống: {e}")
        return
        
    # LOẠI BỎ LAG - THAY VÌ Reset Toàn Hệ Thống, Chỉ Vẽ Lại Danh Sách:
    browser.model.beginReset()
    browser.model.endReset()
    
    showInfo(f"Hoàn thành!\nĐã tạo thành công: {success_count} tác vụ.\nLỗi: {error_count} tác vụ.\nBỏ qua (có sẵn): {skipped_count} tác vụ.")

from aqt import gui_hooks
from aqt.qt import QMenu

def setup_browser_menu(browser):
    menu = QMenu("AnkiVN TTS", browser.form.menubar)
    
    action = QAction("Add Audio (Edge TTS/Google/Local)...", browser)
    action.triggered.connect(lambda _, b=browser: on_generate_audio(b))
    menu.addAction(action)
    
    browser.form.menubar.addMenu(menu)

gui_hooks.browser_menus_did_init.append(setup_browser_menu)
