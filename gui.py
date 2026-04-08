import re
from aqt import mw
from aqt.qt import *
from .generator import sync_get_voices

class AnkiVNTTSDialog(QDialog):
    def __init__(self, browser, nids):
        super().__init__(browser)
        self.browser = browser
        self.nids = nids
        self.fields = self._get_unique_fields(nids)
        self.voices = []
        self.tasks = [] # holds list of config dictionaries
        
        # Load presets from Anki
        self.presets = mw.col.get_config("ankivntts_presets", {})
        
        self.init_ui()
        
    def _get_unique_fields(self, nids):
        fields = set()
        for nid in nids:
            note = mw.col.get_note(nid)
            for key in note.keys():
                fields.add(key)
        return sorted(list(fields))
    
    def init_ui(self):
        self.setWindowTitle("AnkiVN TTS - Batch Generator Workflow")
        self.resize(500, 600)
        main_layout = QVBoxLayout()
        
        # --- PRESET HEADER ---
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Preset:"))
        self.preset_combo = QComboBox()
        self.update_preset_combo()
        
        self.btn_save_preset = QPushButton("Lưu")
        self.btn_del_preset = QPushButton("Xóa")
        self.btn_save_preset.clicked.connect(self.on_save_preset)
        self.btn_del_preset.clicked.connect(self.on_delete_preset)
        self.preset_combo.currentIndexChanged.connect(self.on_preset_selected)
        
        preset_layout.addWidget(self.preset_combo)
        preset_layout.addWidget(self.btn_save_preset)
        preset_layout.addWidget(self.btn_del_preset)
        main_layout.addLayout(preset_layout)
        
        # --- CONFIG FRAME ---
        config_frame = QGroupBox("Cấu hình Tác vụ (Config)")
        layout = QVBoxLayout()
        
        src_layout = QHBoxLayout()
        src_layout.addWidget(QLabel("Source Field:"))
        self.src_combo = QComboBox()
        self.src_combo.addItems(self.fields)
        src_layout.addWidget(self.src_combo)
        layout.addLayout(src_layout)
        
        dst_layout = QHBoxLayout()
        dst_layout.addWidget(QLabel("Destination Field:"))
        self.dst_combo = QComboBox()
        self.dst_combo.addItems(self.fields)
        dst_layout.addWidget(self.dst_combo)
        layout.addLayout(dst_layout)
        
        eng_layout = QHBoxLayout()
        eng_layout.addWidget(QLabel("Engine:"))
        self.engine_combo = QComboBox()
        self.engine_combo.addItems(["Edge TTS", "Google TTS", "Windows SAPI", "Piper Offline"])
        eng_layout.addWidget(self.engine_combo)
        layout.addLayout(eng_layout)
        
        # Piper Config
        self.piper_widget = QWidget()
        piper_layout = QVBoxLayout()
        piper_layout.setContentsMargins(0, 0, 0, 0)
        
        piper_exe_layout = QHBoxLayout()
        piper_exe_layout.addWidget(QLabel("Piper .exe:"))
        self.piper_exe_edit = QLineEdit()
        self.piper_exe_edit.setPlaceholderText("Vd: C:\\piper\\piper.exe")
        piper_exe_layout.addWidget(self.piper_exe_edit)
        piper_layout.addLayout(piper_exe_layout)
        
        piper_mdl_layout = QHBoxLayout()
        piper_mdl_layout.addWidget(QLabel("Model .onnx:"))
        self.piper_model_edit = QLineEdit()
        self.piper_model_edit.setPlaceholderText("Vd: C:\\piper\\vi_VN.onnx")
        piper_mdl_layout.addWidget(self.piper_model_edit)
        piper_layout.addLayout(piper_mdl_layout)
        
        self.piper_widget.setLayout(piper_layout)
        self.piper_widget.setVisible(False)
        layout.addWidget(self.piper_widget)
        self.engine_combo.currentIndexChanged.connect(self.on_engine_changed)
        
        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("Language:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("Loading...")
        self.lang_combo.setEnabled(False)
        voice_layout.addWidget(self.lang_combo)
        
        voice_layout.addWidget(QLabel("Voice:"))
        self.voice_combo = QComboBox()
        self.voice_combo.setEnabled(False)
        voice_layout.addWidget(self.voice_combo)
        
        self.preview_btn = QPushButton("Preview")
        self.preview_btn.setEnabled(False)
        self.preview_btn.clicked.connect(self.on_preview_clicked)
        voice_layout.addWidget(self.preview_btn)
        layout.addLayout(voice_layout)
        
        param_layout = QHBoxLayout()
        param_layout.addWidget(QLabel("Speed:"))
        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setRange(0.5, 3.0)
        self.speed_spin.setValue(1.0)
        self.speed_spin.setSingleStep(0.1)
        self.speed_spin.setSuffix("x")
        param_layout.addWidget(self.speed_spin)
        
        param_layout.addWidget(QLabel("Pitch:"))
        self.pitch_spin = QSpinBox()
        self.pitch_spin.setRange(-100, 100)
        self.pitch_spin.setValue(0)
        self.pitch_spin.setSuffix("Hz")
        param_layout.addWidget(self.pitch_spin)
        
        param_layout.addWidget(QLabel("Volume:"))
        self.volume_spin = QSpinBox()
        self.volume_spin.setRange(-100, 100)
        self.volume_spin.setValue(0)
        self.volume_spin.setSuffix("%")
        param_layout.addWidget(self.volume_spin)
        layout.addLayout(param_layout)
        
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Update Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Append", "Overwrite"])
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)
        
        config_frame.setLayout(layout)
        main_layout.addWidget(config_frame)
        
        # --- QUEUE BUTTON ---
        self.btn_add_queue = QPushButton("🔽 Thêm Tác Vụ Ghi Âm 🔽")
        self.btn_add_queue.setStyleSheet("font-weight: bold; padding: 5px;")
        self.btn_add_queue.clicked.connect(self.on_add_to_queue)
        main_layout.addWidget(self.btn_add_queue)
        
        # --- WORKFLOW QUEUE ---
        queue_frame = QGroupBox("Danh sách Nhiệm vụ đa luồng (Workflow)")
        queue_layout = QVBoxLayout()
        self.queue_list = QListWidget()
        queue_layout.addWidget(self.queue_list)
        self.btn_del_queue = QPushButton("Xóa Nhiệm vụ dã chọn")
        self.btn_del_queue.clicked.connect(self.on_del_queue_item)
        queue_layout.addWidget(self.btn_del_queue)
        queue_frame.setLayout(queue_layout)
        main_layout.addWidget(queue_frame)
        
        # --- BOTTOM BUTTONS ---
        btn_layout = QHBoxLayout()
        self.generate_btn = QPushButton("Chạy tất cả Tác vụ")
        self.generate_btn.setEnabled(False) # Wait for voices to load
        self.generate_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("Đóng")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)
        
        self.setLayout(main_layout)
        
        # Tải nền các voice
        mw.taskman.run_in_background(
            self._fetch_voices_bg,
            self.on_voices_loaded
        )
        
    # --- UI Logic Methods ---
    def _fetch_voices_bg(self):
        from .generator import sync_get_voices, sync_get_sapi_voices
        edge_v = []
        try:
            edge_v = sync_get_voices()
        except: pass
        sapi_v = sync_get_sapi_voices()
        return (edge_v, sapi_v)
        
    def on_engine_changed(self):
        engine = self.engine_combo.currentText()
        is_piper = engine == "Piper Offline"
        self.piper_widget.setVisible(is_piper)
        
        if engine == "Windows SAPI":
            self.lang_combo.setEnabled(False)
            self.voice_combo.clear()
            for v in getattr(self, "sapi_voices", []):
                self.voice_combo.addItem(v, v)
            if not getattr(self, "sapi_voices", []):
                self.voice_combo.addItem("No System Voices Found", "")
                
        elif engine == "Google TTS":
            self.lang_combo.setEnabled(False)
            self.voice_combo.clear()
            self.voice_combo.addItem("Google Standard (vi-VN)", "vi-VN")
            self.voice_combo.addItem("Google Standard (en-US)", "en-US")
            
        elif engine == "Piper Offline":
            self.lang_combo.setEnabled(False)
            self.voice_combo.clear()
            self.voice_combo.addItem("Local File Model", "local")
            
        else: # Edge TTS
            self.lang_combo.setEnabled(True)
            self.update_voice_combo()
            
    def update_voice_combo(self):
        self.voice_combo.clear()
        loc = self.lang_combo.currentText()
        if not loc: return
        voices = self.locales.get(loc, [])
        for v in voices:
            display_name = f"{v.get('ShortName')} ({v.get('Gender')})"
            self.voice_combo.addItem(display_name, v.get("ShortName"))

    def on_voices_loaded(self, future):
        try:
            edge_voices, sapi_voices = future.result()
            self.voices = edge_voices
            self.sapi_voices = sapi_voices
        except Exception:
            return
            
        self.locales = {}
        for v in self.voices:
            loc = v.get("Locale", "Unknown")
            if loc not in self.locales:
                self.locales[loc] = []
            self.locales[loc].append(v)
            
        def locale_sort_key(loc):
            lower_loc = loc.lower()
            if "vi-" in lower_loc: return (0, loc)
            elif "en-" in lower_loc: return (1, loc)
            else: return (2, loc)
                
        self.unique_locales = sorted(self.locales.keys(), key=locale_sort_key)
        self.lang_combo.addItems(self.unique_locales)
        self.lang_combo.currentIndexChanged.connect(self.update_voice_combo)
        
        self.on_engine_changed()
        self.preview_btn.setEnabled(True)
        self.generate_btn.setEnabled(True)
        
    def on_preview_clicked(self):
        # Preview code
        text = "Xin chào, đây là bản nghe thử của Anki VN TTS."
        if self.nids:
            try:
                note = mw.col.get_note(self.nids[0])
                src = self.src_combo.currentText()
                if src in note and note[src].strip():
                    from anki.utils import stripHTML
                    t = stripHTML(note[src]).strip()
                    t = re.sub(r'\[sound:.*?\]', '', t).strip()
                    if t: text = t
            except: pass
            
        percent = int((self.speed_spin.value() - 1.0) * 100)
        rate = f"{percent:+d}%"
        pitch = f"{self.pitch_spin.value():+d}Hz"
        volume = f"{self.volume_spin.value():+d}%"
        engine = self.engine_combo.currentText()
        piper_exe = self.piper_exe_edit.text()
        piper_model = self.piper_model_edit.text()
        voice = self.voice_combo.currentData() or "vi-VN"
        
        self.preview_btn.setEnabled(False)
        mw.taskman.run_in_background(
            lambda: self._generate_preview_sync(text, voice, rate, pitch, volume, engine, piper_exe, piper_model),
            self._on_preview_done
        )
        
    def _generate_preview_sync(self, text, voice, rate, pitch, volume, engine, piper_exe, piper_model):
        import tempfile, os
        from .generator import generate_audio_sync
        fd, temp_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        generate_audio_sync(text, voice, temp_path, rate, pitch, volume, engine, piper_exe, piper_model)
        return temp_path
        
    def _on_preview_done(self, future):
        self.preview_btn.setEnabled(True)
        try:
            temp_path = future.result()
            from aqt.sound import play
            play(temp_path)
        except Exception as e:
            from aqt.utils import showInfo
            showInfo(f"Lỗi: {e}")

    # --- Preset Management ---
    def update_preset_combo(self):
        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()
        self.preset_combo.addItem("-- Mặc định --", "")
        for k in sorted(self.presets.keys()):
            self.preset_combo.addItem(k, k)
        self.preset_combo.blockSignals(False)

    def on_save_preset(self):
        name, ok = QInputDialog.getText(self, "Lưu Preset", "Nhập tên Preset mới:")
        if ok and name.strip():
            name = name.strip()
            # Save the currently queued tasks as the preset instead of just the form!
            # If nothing is queued, save the form as a single task workflow.
            if not self.tasks:
                tasks_to_save = [self.get_current_form_config()]
            else:
                tasks_to_save = self.tasks[:]
                
            self.presets[name] = tasks_to_save
            mw.col.set_config("ankivntts_presets", self.presets)
            self.update_preset_combo()
            self.preset_combo.setCurrentText(name)

    def on_delete_preset(self):
        name = self.preset_combo.currentData()
        if name and name in self.presets:
            del self.presets[name]
            mw.col.set_config("ankivntts_presets", self.presets)
            self.update_preset_combo()
            self.clear_queue()

    def on_preset_selected(self):
        name = self.preset_combo.currentData()
        self.clear_queue()
        if name and name in self.presets:
            saved_tasks = self.presets[name]
            for t in saved_tasks:
                self.tasks.append(t)
                disp = f"{t['source_field']} -> {t['destination_field']} ({t['engine']} | {t['voice']})"
                self.queue_list.addItem(disp)

    # --- Workflow Queue logic ---
    def get_current_form_config(self):
        return {
            "source_field": self.src_combo.currentText(),
            "destination_field": self.dst_combo.currentText(),
            "voice": self.voice_combo.currentData() if self.voice_combo.currentData() else "vi-VN",
            "mode": self.mode_combo.currentText(),
            "rate": f"{int((self.speed_spin.value() - 1.0) * 100):+d}%",
            "pitch": f"{self.pitch_spin.value():+d}Hz",
            "volume": f"{self.volume_spin.value():+d}%",
            "engine": self.engine_combo.currentText(),
            "piper_exe": self.piper_exe_edit.text(),
            "piper_model": self.piper_model_edit.text(),
            "abort": False
        }

    def on_add_to_queue(self):
        conf = self.get_current_form_config()
        self.tasks.append(conf)
        disp = f"{conf['source_field']} -> {conf['destination_field']} ({conf['engine']} | {conf['voice']})"
        self.queue_list.addItem(disp)
        
    def on_del_queue_item(self):
        row = self.queue_list.currentRow()
        if row >= 0:
            self.queue_list.takeItem(row)
            self.tasks.pop(row)

    def clear_queue(self):
        self.queue_list.clear()
        self.tasks = []
        
    def get_tasks(self):
        # If the queue is empty when they hit Generate, just use the form inputs directly.
        if not self.tasks:
            return [self.get_current_form_config()]
        return self.tasks

class AnkiVNProgressDialog(QDialog):
    def __init__(self, parent, total_items, config=None):
        super().__init__(parent)
        self.total_items = total_items
        self.abort_flag = False
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("AnkiVN TTS - Đang xử lý Đa Luồng")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        self.status_label = QLabel(f"Trạng thái: Đang chuẩn bị (0/{self.total_items})...")
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.total_items)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.stats_label = QLabel("Thành công: 0 | Lỗi: 0 | Bỏ qua: 0")
        layout.addWidget(self.stats_label)
        
        self.cancel_btn = QPushButton("Abort / Hủy")
        self.cancel_btn.clicked.connect(self.on_cancel)
        layout.addWidget(self.cancel_btn)
        
        self.setLayout(layout)
        
    def on_cancel(self):
        self.abort_flag = True
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setText("Đang hủy ngang...")
        
    def update_stats(self, current, success, error, skipped):
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Trạng thái: Đang xử lý ({current}/{self.total_items})...")
        self.stats_label.setText(f"Thành công: {success} | Lỗi: {error} | Bỏ qua: {skipped}")
