from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog,QMessageBox
from config import config_manager  # config_manager 임포트가 필요한 경우 추가

class PngPathSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PNG 저장 경로 설정")
        self.setGeometry(300, 200, 400, 200)

        # 레이아웃 설정
        layout = QVBoxLayout(self)

        # 설명 라벨
        layout.addWidget(QLabel("PNG 파일 저장 경로를 선택하세요."))

        # JSON 설정에서 기본 경로 로드
        config = config_manager.load_config()
        default_png_path = config.get("png_save_path", "")  # 기본 경로가 없을 경우 빈 문자열 사용

        # 경로 입력 필드와 찾아보기 버튼
        self.png_path_edit = QLineEdit(self)
        self.png_path_edit.setText(default_png_path)  # 기본 경로 설정
        layout.addWidget(self.png_path_edit)

        browse_button = QPushButton("찾아보기")
        browse_button.clicked.connect(self.select_png_path)
        layout.addWidget(browse_button)

        # 저장 버튼
        save_button = QPushButton("저장")
        save_button.clicked.connect(self.save_png_path)
        layout.addWidget(save_button)

    def select_png_path(self):
        """경로 선택 창을 띄우고 선택한 경로를 입력 필드에 반영합니다."""
        path = QFileDialog.getExistingDirectory(self, "PNG 저장 경로 선택")
        if path:
            self.png_path_edit.setText(path)

    def save_png_path(self):
        """설정된 경로를 JSON에 저장하고 성공 메시지를 표시한 후 다이얼로그를 닫습니다."""
        try:
            # 경로 저장
            config_manager.set_png_save_path(self.png_path_edit.text())

            # 성공 메시지 표시
            QMessageBox.information(self, "저장 완료", "PNG 저장 경로가 성공적으로 저장되었습니다.")

            # 다이얼로그 닫기
            self.accept()

        except Exception as e:
            # 오류 발생 시 에러 메시지 표시
            QMessageBox.critical(self, "저장 실패", f"경로 저장 중 오류가 발생했습니다: {e}")
