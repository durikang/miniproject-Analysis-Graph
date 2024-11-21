import traceback
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox, QLineEdit, QHBoxLayout, QFileDialog, QProgressBar
)
from PyQt5.QtCore import Qt
from config import config_manager
from .TxtToCsvConverter import TxtToCsvConverter


class CsvConvertWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("[TRACE] Initializing CsvConvertWindow")
        self.setWindowTitle("CSV 변환")
        self.setGeometry(300, 200, 500, 350)

        # JSON 설정 로드
        print("[TRACE] Loading configuration from JSON")
        self.config = config_manager.load_config()

        # UI 레이아웃 설정
        layout = QVBoxLayout(self)

        # 메인 타이틀 라벨 생성 및 가운데 정렬
        title_label = QLabel("텍스트 파일을 CSV로 변환합니다.")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 각 경로 설정을 위한 UI 구성
        self.bs_raw_path_edit = self.create_path_setting("BS 원본 경로", self.config.get("bs_raw_path", ""))
        layout.addLayout(self.bs_raw_path_edit)

        self.is_raw_path_edit = self.create_path_setting("IS 원본 경로", self.config.get("is_raw_path", ""))
        layout.addLayout(self.is_raw_path_edit)

        self.bs_output_path_edit = self.create_path_setting("BS 저장 경로", self.config.get("balance_data_path", ""))
        layout.addLayout(self.bs_output_path_edit)

        self.is_output_path_edit = self.create_path_setting("IS 저장 경로", self.config.get("income_data_path", ""))
        layout.addLayout(self.is_output_path_edit)

        # 경로 저장 버튼 추가
        save_paths_button = QPushButton("경로 저장")
        save_paths_button.clicked.connect(self.save_paths)
        layout.addWidget(save_paths_button)

        # 변환 버튼 추가
        convert_button = QPushButton("변환하기")
        convert_button.clicked.connect(self.start_conversion)
        layout.addWidget(convert_button)

        # 진행 바 추가
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def create_path_setting(self, label_text, default_path):
        """경로 설정을 위한 레이아웃 생성 메서드."""
        print(f"[TRACE] Creating path setting for: {label_text}")
        layout = QHBoxLayout()
        label = QLabel(label_text)
        path_edit = QLineEdit(default_path)
        browse_button = QPushButton("찾아보기")
        browse_button.clicked.connect(lambda: self.select_directory(path_edit))

        layout.addWidget(label)
        layout.addWidget(path_edit)
        layout.addWidget(browse_button)
        return layout

    def select_directory(self, path_edit):
        """사용자가 디렉토리를 선택할 수 있는 파일 탐색기 창을 엽니다."""
        print("[TRACE] Opening directory selection dialog")
        selected_dir = QFileDialog.getExistingDirectory(self, "폴더 선택")
        if selected_dir:
            print(f"[TRACE] Selected directory: {selected_dir}")
            path_edit.setText(selected_dir)
        else:
            print("[TRACE] No directory selected")

    def save_paths(self):
        """경로 설정을 JSON 파일에 저장합니다."""
        print("[TRACE] Saving paths to configuration")
        self.config["bs_raw_path"] = self.bs_raw_path_edit.itemAt(1).widget().text()
        self.config["is_raw_path"] = self.is_raw_path_edit.itemAt(1).widget().text()
        self.config["balance_data_path"] = self.bs_output_path_edit.itemAt(1).widget().text()
        self.config["income_data_path"] = self.is_output_path_edit.itemAt(1).widget().text()

        try:
            config_manager.save_config(self.config)
            print("[TRACE] Paths saved successfully to configuration")
            QMessageBox.information(self, "저장 완료", "경로 설정이 저장되었습니다.")
        except Exception as e:
            print(f"[TRACE][ERROR] Failed to save paths: {str(e)}")
            traceback.print_exc()
            QMessageBox.critical(self, "오류", f"경로 저장 중 오류 발생: {str(e)}")

    def start_conversion(self):
        """CSV 변환을 시작합니다."""
        print("[TRACE] Starting CSV conversion process")
        bs_raw_path = self.bs_raw_path_edit.itemAt(1).widget().text()
        is_raw_path = self.is_raw_path_edit.itemAt(1).widget().text()
        bs_output_path = self.bs_output_path_edit.itemAt(1).widget().text()
        is_output_path = self.is_output_path_edit.itemAt(1).widget().text()

        if not (bs_raw_path and is_raw_path and bs_output_path and is_output_path):
            print("[TRACE][WARNING] One or more paths are empty")
            QMessageBox.warning(self, "경고", "모든 경로를 설정하세요.")
            return

        try:
            # TxtToCsvConverter 생성 및 실행
            converter = TxtToCsvConverter(bs_raw_path, is_raw_path, bs_output_path, is_output_path)
            total_files = (
                len(converter._get_txt_files(bs_raw_path)) +
                len(converter._get_txt_files(is_raw_path))
            )
            self.progress_bar.setMaximum(total_files)

            def progress_callback(current, total):
                self.progress_bar.setValue(current)

            converter.convert_all(progress_callback=progress_callback)
            print("[TRACE] CSV conversion completed successfully")
            QMessageBox.information(self, "완료", "모든 파일이 CSV로 변환되었습니다.")
            self.accept()

        except Exception as e:
            print(f"[TRACE][ERROR] CSV conversion failed: {str(e)}")
            traceback.print_exc()
            QMessageBox.critical(self, "오류", f"변환 중 오류 발생: {str(e)}")
