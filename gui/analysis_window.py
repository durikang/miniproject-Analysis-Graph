from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QMessageBox,
    QHBoxLayout, QMenuBar, QAction, QDialog, QFileDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from analysis.plotter import Plotter, INCOME_STATEMENT_ITEM_CODES, BALANCE_SHEET_ITEM_CODES
import pandas as pd
from config import config_manager

class AnalysisWindow(QWidget):
    def __init__(self, income_statement_data, balance_sheet_data, company_list):
        super().__init__()
        self.setWindowTitle("Analysis Window")
        self.setGeometry(100, 100, 1200, 900)  # 창 크기를 넓게 조정하여 그래프와 버튼이 잘 보이도록 함
        self.income_statement_data = income_statement_data
        self.balance_sheet_data = balance_sheet_data

        # 창을 최대화 모드로 설정
        self.showMaximized()

        # 메인 레이아웃 설정
        main_layout = QVBoxLayout(self)

        # 회사 선택과 그래프를 표시할 상단 레이아웃
        top_layout = QVBoxLayout()

        # 회사 선택 라벨과 드롭다운 메뉴를 수평으로 배치하는 레이아웃
        company_selection_layout = QHBoxLayout()
        company_selection_layout.addWidget(QLabel("회사 선택"))

        # 회사 선택 드롭다운 메뉴
        self.company_menu = QComboBox()
        self.company_menu.addItems(company_list)
        company_selection_layout.addWidget(self.company_menu)

        # 상단 레이아웃에 회사 선택 레이아웃 추가
        top_layout.addLayout(company_selection_layout)

        # 그래프 표시를 위한 QWebEngineView 추가
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(600)
        self.web_view.setMinimumWidth(1000)
        top_layout.addWidget(self.web_view)

        # 상단 레이아웃을 메인 레이아웃에 추가
        main_layout.addLayout(top_layout)

        # 손익계산서 항목에 대한 버튼 생성
        main_layout.addWidget(QLabel("손익계산서 항목"))
        for code, item_name in INCOME_STATEMENT_ITEM_CODES.items():
            button = QPushButton(item_name)
            button.clicked.connect(lambda _, c=code: self.display_graph(c, "손익계산서"))
            main_layout.addWidget(button)

        # 재무상태표 항목에 대한 버튼 생성
        main_layout.addWidget(QLabel("재무상태표 항목"))
        for code, item_name in BALANCE_SHEET_ITEM_CODES.items():
            button = QPushButton(item_name)
            button.clicked.connect(lambda _, c=code: self.display_graph(c, "재무상태표"))
            main_layout.addWidget(button)

        self.setLayout(main_layout)

    def display_graph(self, item_code, data_type):
        """선택된 항목과 데이터 종류에 따라 그래프를 생성하고 저장합니다."""
        company = self.company_menu.currentText()
        print(f"[Info] Displaying graph for company: {company}, item: {item_code} ({data_type})")

        try:
            # 데이터 타입에 따라 적절한 데이터 선택
            if data_type == "손익계산서":
                data = self.income_statement_data
                item_mapping = INCOME_STATEMENT_ITEM_CODES
            elif data_type == "재무상태표":
                data = self.balance_sheet_data
                item_mapping = BALANCE_SHEET_ITEM_CODES
            else:
                raise ValueError("올바르지 않은 데이터 종류입니다.")

            # 항목명을 한글로 가져오기
            item_name_kr = item_mapping.get(item_code)
            if not item_name_kr:
                raise ValueError("유효하지 않은 항목 코드입니다.")

            # 올바른 데이터셋에서 회사와 항목코드가 일치하는 데이터를 필터링
            filtered_data = data[(data['회사명'] == company) & (data['항목코드'] == item_code)][['연도', '항목코드', '당기']]
            if filtered_data.empty:
                print(f"[Debug] No data found for company '{company}' with item '{item_name_kr}' in {data_type}.")
            else:
                pd.set_option('display.max_rows', None)
                pd.set_option('display.max_columns', None)
                pd.set_option('display.expand_frame_repr', False)
                print(f"[Debug] Filtered data for company '{company}' with item '{item_name_kr}':\n{filtered_data}")
                pd.reset_option('display.max_rows')
                pd.reset_option('display.max_columns')
                pd.reset_option('display.expand_frame_repr')

            # Plotter 인스턴스에 선택된 데이터만 전달
            plotter = Plotter(company, data)
            fig = plotter.create_graph(item_code, item_name_kr)  # item_name_kr 인자를 추가로 전달

            # 그래프를 HTML 파일로 저장 후 QWebEngineView에 표시
            save_path = plotter.save_graph_as_html(fig, item_code, data_type)
            print(f"[Debug] HTML file saved at: {save_path}")

            # PNG로 그래프 저장
            png_save_path = plotter.save_graph_as_png(fig, item_code, data_type)
            print(f"[Debug] PNG file saved at: {png_save_path}")

            # QWebEngineView에 HTML 파일 로드
            self.web_view.setUrl(QUrl.fromLocalFile(save_path))
            print("[Info] Graph displayed in web view.")

        except ValueError as e:
            QMessageBox.critical(self, "오류", str(e))
            print(f"[Error - Graph Creation]: {e}")  # 에러 메시지 출력
        except Exception as e:
            QMessageBox.critical(self, "오류", f"예기치 못한 오류 발생: {e}")
            print(f"[Error - Graph Creation - Unexpected]: {e}")
