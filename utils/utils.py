# utils.py
import os
import platform
from PyQt5.QtWidgets import QMessageBox

def open_folder(path):
    """주어진 경로의 폴더를 엽니다."""
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            os.system(f"open '{path}'")
        else:  # Linux
            os.system(f"xdg-open '{path}'")
    except Exception as e:
        print(f"폴더 열기 오류: {e}")
        QMessageBox.warning(None, "오류", f"폴더를 열 수 없습니다: {e}")
