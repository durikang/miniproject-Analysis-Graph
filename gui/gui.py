from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QListWidget, QListWidgetItem, QMessageBox, QMenuBar, QAction
)
from PyQt5.QtCore import Qt  # Qt 모듈을 import
from config import config_manager
from data import data_manager
# 최상위 모듈에서 시작하도록 구조를 수정한 후:
from gui.analysis_window import AnalysisWindow
from gui.options_window import OptionsWindow
from.CsvConvertWindow import CsvConvertWindow
from update.UpdateWindow import UpdateWindow
from analysis.ExcelFormatter import ExcelFormatter
from analysis.plotter import Plotter  # Plotter를 추가로 가져옵니다.
from utils.utils import open_folder  # utils 모듈에서 open_folder 함수를 가져옵니다.
import traceback  # traceback 모듈 추가

class FinancialApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Financial Data Visualizer")
        self.setGeometry(100, 100, 900, 700)

        # 메뉴바 추가
        menu_bar = QMenuBar(self)
        options_menu = menu_bar.addMenu("옵션")
        update_menu = menu_bar.addMenu("업데이트")

        # 옵션 메뉴 액션 추가
        options_action = QAction("설정", self)
        options_action.triggered.connect(self.open_options_window)
        options_menu.addAction(options_action)

        # CSV 변환 메뉴 추가
        csv_convert_action = QAction("CSV 변환", self)
        csv_convert_action.triggered.connect(self.open_csv_convert_window)
        options_menu.addAction(csv_convert_action)

        # 업데이트 확인 메뉴 추가
        update_action = QAction("업데이트 확인", self)
        update_action.triggered.connect(self.open_update_window)
        update_menu.addAction(update_action)

        # 레이아웃에 메뉴바 추가
        main_layout = QVBoxLayout(self)
        main_layout.setMenuBar(menu_bar)

        # 프로그램 제목 및 설명 추가
        title_label = QLabel("재무 분석 차트 (Financial Analysis Chart)")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")  # 제목 스타일 설정
        title_label.setAlignment(Qt.AlignCenter)  # 제목 가운데 정렬

        description_label = QLabel("재무상태표와 손익계산서를 시각화하여 기업의 재무 상태와 성과를 분석할 수 있는 프로그램입니다.")
        description_label.setAlignment(Qt.AlignCenter)  # 설명 가운데 정렬

        main_layout.addWidget(title_label)
        main_layout.addWidget(description_label)

        # 인스턴스 속성 초기화
        self.company_list = QListWidget()
        self.selected_list = QListWidget()
        self.search_bar = QLineEdit(self)

        # 분석 창 속성 초기화 (None으로 초기 설정)
        self.analysis_window = None

        # Config 로드 및 UI 초기화
        self.config = config_manager.load_config()
        self.init_ui()

        # 기존 레이아웃을 메인 레이아웃에 추가
        main_layout.addLayout(self.init_ui())
        self.setLayout(main_layout)

    def init_ui(self):
        layout = QVBoxLayout()

        # 회사 목록 불러오기 및 분석 실행 버튼
        company_header_layout = QHBoxLayout()

        load_companies_button = QPushButton("회사 목록 불러오기")
        load_companies_button.clicked.connect(self.load_company_list)
        company_header_layout.addWidget(load_companies_button)

        run_analysis_button = QPushButton("분석 실행")
        run_analysis_button.clicked.connect(self.run_analysis)
        company_header_layout.addWidget(run_analysis_button)

        layout.addLayout(company_header_layout)

        # 회사명 검색바 및 검색/초기화 버튼
        search_layout = QHBoxLayout()
        self.search_bar.setPlaceholderText("회사명 검색")

        search_button = QPushButton("검색")
        search_button.clicked.connect(self.search_companies)

        reset_button = QPushButton("초기화")
        reset_button.clicked.connect(self.reset_search)

        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(search_button)
        search_layout.addWidget(reset_button)
        layout.addLayout(search_layout)

        # 회사 목록
        company_frame = QHBoxLayout()
        company_frame.addWidget(self.company_list)

        # 회사 목록과 선택된 목록 간 이동 버튼
        button_layout = QVBoxLayout()
        button_layout.setSpacing(0)
        add_button = QPushButton(">")
        add_button.clicked.connect(self.add_company)
        add_button.setFixedWidth(30)
        remove_button = QPushButton("<")
        remove_button.clicked.connect(self.remove_company)
        remove_button.setFixedWidth(30)
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        company_frame.addLayout(button_layout)

        # 선택된 회사 목록
        company_frame.addWidget(self.selected_list)
        layout.addLayout(company_frame)

        return layout

    def load_company_list(self):
        try:
            balance_path = self.config.get("balance_data_path", "")
            income_path = self.config.get("income_data_path", "")
            companies = data_manager.load_companies(balance_path, income_path)
            self.company_list.clear()
            for company in companies:
                item = QListWidgetItem(company)
                self.company_list.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, "오류", str(e))

    def search_companies(self):
        query = self.search_bar.text().lower()
        for i in range(self.company_list.count()):
            item = self.company_list.item(i)
            item.setHidden(query not in item.text().lower())

    def reset_search(self):
        """검색 필드를 초기화하고 모든 회사를 표시합니다."""
        self.search_bar.clear()
        for i in range(self.company_list.count()):
            self.company_list.item(i).setHidden(False)

    def add_company(self):
        for item in self.company_list.selectedItems():
            self.company_list.takeItem(self.company_list.row(item))
            self.selected_list.addItem(item)

    def remove_company(self):
        for item in self.selected_list.selectedItems():
            self.selected_list.takeItem(self.selected_list.row(item))
            self.company_list.addItem(item)

    def run_analysis(self):
        """선택된 회사들에 대한 분석을 실행하고 결과를 저장하며, 결과 폴더를 엽니다."""
        try:
            # 선택된 회사 리스트 가져오기
            selected_companies = [self.selected_list.item(i).text() for i in range(self.selected_list.count())]
            if not selected_companies:
                QMessageBox.warning(self, "경고", "분석을 실행할 회사를 선택하세요.")
                return

            # 데이터 경로 로드
            balance_path = self.config.get("balance_data_path", "")
            income_path = self.config.get("income_data_path", "")

            # 데이터 로드
            income_statement_data, balance_sheet_data = data_manager.prepare_data_for_analysis(
                balance_path, income_path, selected_companies
            )

            # JSON 파일에서 항목 코드와 명칭을 불러오기
            item_codes = config_manager.load_item_codes()
            INCOME_STATEMENT_ITEM_CODES = item_codes["INCOME_STATEMENT_ITEM_CODES"]
            BALANCE_SHEET_ITEM_CODES = item_codes["BALANCE_SHEET_ITEM_CODES"]

            # Excel 저장 기능 추가
            excel_formatter = ExcelFormatter()  # 엑셀 포맷터 초기화

            for idx, company in enumerate(selected_companies):
                start_row = idx * 17 + 1  # 각 회사의 데이터를 시작할 행 계산
                filtered_income_data = income_statement_data[income_statement_data["회사명"] == company]
                filtered_balance_data = balance_sheet_data[balance_sheet_data["회사명"] == company]

                # 필터링된 데이터를 사용해 엑셀 섹션 생성
                excel_formatter.create_section(start_row, company, filtered_income_data, filtered_balance_data)

            # Excel 파일 저장
            excel_formatter.save_file()
            print(f"[INFO] Excel file saved successfully at '{excel_formatter.output_file}'.")

            # 각 회사와 항목에 대해 PNG 저장 기능 실행
            for company in selected_companies:
                for item_code, item_name in {**INCOME_STATEMENT_ITEM_CODES, **BALANCE_SHEET_ITEM_CODES}.items():
                    try:
                        # 데이터 타입에 따라 적절한 데이터프레임 선택
                        data = income_statement_data if item_code in INCOME_STATEMENT_ITEM_CODES else balance_sheet_data

                        # Plotter 인스턴스를 생성하여 그래프 생성 및 PNG 저장
                        plotter = Plotter(company, data)
                        fig = plotter.create_graph(item_code, item_name)

                        # PNG 파일로 저장
                        plotter.save_graph_as_png(
                            fig, item_code,
                            "손익계산서" if item_code in INCOME_STATEMENT_ITEM_CODES else "재무상태표"
                        )

                    except ValueError as ve:
                        print(
                            f"[Warning] Skipping item '{item_name}' for company '{company}' due to missing data: {ve}")
                        continue  # 데이터가 없는 경우 해당 항목을 생략하고 다음 항목으로 넘어갑니다

            # 분석 창 열기
            self.open_analysis_window(income_statement_data, balance_sheet_data)

            # 저장 폴더 열기
            # png_save_path = config_manager.get_png_save_path()
            # open_folder(png_save_path)

        except Exception as e:
            # 예외 발생 시 디버깅 정보 출력
            print(f"분석 실행 중 오류 발생: {e}")
            traceback.print_exc()  # 스택 추적 정보 출력
            QMessageBox.critical(self, "오류", f"분석 실행 중 오류 발생: {e}")

    def open_analysis_window(self, income_statement_data, balance_sheet_data):
        """손익계산서와 재무상태표 데이터를 받아서 새 창을 엽니다."""
        company_list = income_statement_data["회사명"].unique()
        self.analysis_window = AnalysisWindow(income_statement_data, balance_sheet_data, company_list)
        self.analysis_window.show()

    def open_options_window(self):
        """옵션 창 열기"""
        try:
            options_window = OptionsWindow(self)
            options_window.exec_()
        except Exception as e:
            print("[DEBUG] An error occurred while opening the options window:")
            print(e)
            QMessageBox.critical(self, "오류", f"옵션 창을 여는 도중 오류가 발생했습니다: {e}")

    def open_csv_convert_window(self):
        """CSV 변환 창 열기"""
        csv_convert_window = CsvConvertWindow(self)
        csv_convert_window.exec_()

    def open_update_window(self):
        """업데이트 확인 창 열기"""
        try:
            # 클래스 속성으로 저장하여 참조 유지
            self.update_window = UpdateWindow(self)
            self.update_window.exec_()
        except Exception as e:
            print(f"[DEBUG] An error occurred while opening the update window: {e}")
            QMessageBox.critical(self, "오류", f"업데이트 창을 여는 도중 오류가 발생했습니다: {e}")
