from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
from config import config_manager


class CsvPngPathSettingsDialog(QDialog):
    """CSV 및 PNG 저장 경로 설정을 위한 다이얼로그"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CSV 및 PNG 저장 경로 설정")
        self.setGeometry(300, 200, 400, 300)

        # 레이아웃 설정
        layout = QVBoxLayout(self)

        # 설명 라벨
        layout.addWidget(QLabel("CSV 및 PNG 파일 저장 경로를 설정하세요."))

        # JSON 설정에서 기본 경로 로드
        config = config_manager.load_config()
        default_png_path = config.get("png_save_path", "")
        default_csv_path = config.get("csv_save_path", "")

        # PNG 경로 입력 필드와 찾아보기 버튼
        self.png_path_edit = QLineEdit(self)
        self.png_path_edit.setText(default_png_path)  # 기본 경로 설정
        layout.addWidget(QLabel("PNG 저장 경로"))
        layout.addWidget(self.png_path_edit)

        png_browse_button = QPushButton("PNG 경로 찾아보기")
        png_browse_button.clicked.connect(lambda: self.select_path(self.png_path_edit))
        layout.addWidget(png_browse_button)

        # CSV 경로 입력 필드와 찾아보기 버튼
        self.csv_path_edit = QLineEdit(self)
        self.csv_path_edit.setText(default_csv_path)  # 기본 경로 설정
        layout.addWidget(QLabel("CSV 저장 경로"))
        layout.addWidget(self.csv_path_edit)

        csv_browse_button = QPushButton("CSV 경로 찾아보기")
        csv_browse_button.clicked.connect(lambda: self.select_path(self.csv_path_edit))
        layout.addWidget(csv_browse_button)

        # 저장 버튼
        save_button = QPushButton("저장")
        save_button.clicked.connect(self.save_paths)
        layout.addWidget(save_button)

    def select_path(self, line_edit):
        """경로 선택 창을 띄우고 선택한 경로를 입력 필드에 반영합니다."""
        path = QFileDialog.getExistingDirectory(self, "저장 경로 선택")
        if path:
            line_edit.setText(path)

    def save_paths(self):
        """설정된 경로를 JSON에 저장하고 성공 메시지를 표시한 후 다이얼로그를 닫습니다."""
        try:
            # 설정된 경로를 JSON 설정 파일에 저장
            config_manager.set_png_save_path(self.png_path_edit.text())
            config_manager.set_csv_save_path(self.csv_path_edit.text())

            QMessageBox.information(self, "저장 완료", "CSV 및 PNG 저장 경로가 성공적으로 저장되었습니다.")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "저장 실패", f"경로 저장 중 오류가 발생했습니다: {e}")
