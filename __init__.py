import os
import sys
import traceback

vendor_dir = os.path.join(os.path.dirname(__file__), "vendor")
if vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)

try:
    from . import browser
    from aqt import mw
    from aqt.qt import *
    from aqt.utils import showInfo

    def setup_main_menu():
        # Setup AnkiVN TTS inside the Tools menu
        action = QAction("About AnkiVN TTS...", mw)
        action.triggered.connect(lambda _: showInfo("AnkiVN TTS - Free Text-to-Speech\nSử dụng Edge TTS hoàn toàn miễn phí.\n\nTrong cửa sổ Browse, chọn thẻ bài và mở mục AnkiVN TTS để tạo audio bulk."))
        
        # Add to the Tools menu
        tools_menu = getattr(mw.form, "menuTools", getattr(mw.form, "menu_Tools", None))
        if tools_menu is not None:
            tools_menu.addSeparator()
            tools_menu.addAction(action)
        else:
            mw.form.menubar.addAction(action)

    setup_main_menu()
except Exception as e:
    with open(os.path.join(os.path.dirname(__file__), "error.txt"), "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())

