from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from config import config_manager
from .path_settings import PathSettings
from .table_manager import TableManager
import traceback

class OptionsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            self.setWindowTitle("옵션 설정")
            self.setGeometry(300, 200, 600, 600)

            # 설정 데이터 로드
            self.config_data = config_manager.load_config()
            self.item_codes = config_manager.load_item_codes()

            # 모듈 인스턴스 생성
            self.path_settings = PathSettings(self.config_data)
            self.table_manager = TableManager()

            # 레이아웃 설정
            layout = QVBoxLayout(self)

            # 경로 설정 UI 추가
            self.path_settings.add_path_settings(layout)
            self.path_settings.add_result_path_settings(layout)
            self.path_settings.add_png_path_setting(layout)  # PNG 저장 경로 추가

            # 테이블 설정 UI 추가
            self.table_manager.setup_tables(layout, self.item_codes)

            # 저장 버튼
            save_button = QPushButton("저장")
            save_button.clicked.connect(self.save_settings)
            layout.addWidget(save_button)
            self.setLayout(layout)

        except Exception as e:
            print("[DEBUG] An error occurred during OptionsWindow initialization:")
            print(e)
            traceback.print_exc()
            QMessageBox.critical(self, "오류", f"옵션 창 초기화 중 오류가 발생했습니다: {e}")

    def save_settings(self):
        try:
            # 모든 경로와 테이블 데이터 수집
            self.config_data.update(self.path_settings.get_paths())
            self.item_codes["INCOME_STATEMENT_ITEM_CODES"] = self.table_manager.extract_table_data(self.table_manager.income_table)
            self.item_codes["BALANCE_SHEET_ITEM_CODES"] = self.table_manager.extract_table_data(self.table_manager.balance_table)

            # 설정 파일과 항목 코드 저장
            config_manager.save_config(self.config_data)
            config_manager.save_item_codes(self.item_codes)

            QMessageBox.information(self, "저장 완료", "설정이 성공적으로 저장되었습니다.")
            self.close()
        except Exception as e:
            error_message = f"설정 저장 중 오류가 발생했습니다:\n{str(e)}"
            print("[DEBUG] An error occurred during settings save:")
            print(traceback.format_exc())
            QMessageBox.critical(self, "오류", error_message)
