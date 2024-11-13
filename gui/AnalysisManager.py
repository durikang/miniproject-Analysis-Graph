import glob
import os
import pandas as pd
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import re  # 정규 표현식을 사용하기 위해 추가

class AnalysisManager:
    def __init__(self, config, parent=None):
        self.config = config
        self.parent = parent
        # 항목 코드 설정
        self.income_statement_item_codes = config.get("INCOME_STATEMENT_ITEM_CODES", {})
        self.balance_sheet_item_codes = config.get("BALANCE_SHEET_ITEM_CODES", {})

    def prepare_and_run_analysis(self, selected_companies):
        """선택된 회사들의 손익계산서와 재무상태표 데이터를 준비하고 분석을 실행합니다."""
        try:
            balance_path_pattern = os.path.join(self.config.get("balance_data_path", ""), "*.csv")
            income_path_pattern = os.path.join(self.config.get("income_data_path", ""), "*.csv")

            # 데이터를 준비
            income_statement_data, balance_sheet_data = self.prepare_data_for_analysis(
                balance_path_pattern, income_path_pattern, selected_companies
            )

            return income_statement_data, balance_sheet_data

        except Exception as e:
            print(f"데이터 준비 중 오류 발생: {e}")
            QMessageBox.critical(self.parent, "오류", f"데이터 준비 중 오류 발생: {e}")
            return None, None

    def prepare_data_for_analysis(self, balance_path_pattern, income_path_pattern, selected_companies):
        """데이터 준비 및 필터링"""
        try:
            # 파일 패턴에 매칭되는 모든 파일 읽기
            income_files = glob.glob(income_path_pattern)
            balance_files = glob.glob(balance_path_pattern)

            if not income_files or not balance_files:
                raise Exception("손익계산서 또는 재무상태표 파일을 찾을 수 없습니다.")

            # 여러 CSV 파일을 하나의 데이터프레임으로 로드하면서 연도 추가
            income_statement_data = pd.concat(
                [self._load_csv_with_year(file) for file in income_files],
                ignore_index=True
            )
            balance_sheet_data = pd.concat(
                [self._load_csv_with_year(file) for file in balance_files],
                ignore_index=True
            )

            # 회사명으로 필터링
            income_statement_data = income_statement_data[income_statement_data['회사명'].isin(selected_companies)]
            balance_sheet_data = balance_sheet_data[balance_sheet_data['회사명'].isin(selected_companies)]

            # 항목 코드 필터링 - 지정된 항목 코드만 추출
            income_statement_data = income_statement_data[income_statement_data['항목코드'].isin(self.income_statement_item_codes.keys())]
            balance_sheet_data = balance_sheet_data[balance_sheet_data['항목코드'].isin(self.balance_sheet_item_codes.keys())]

            return income_statement_data, balance_sheet_data

        except Exception as e:
            raise Exception(f"데이터 로드 또는 필터링 중 오류 발생: {e}")

    def _load_csv_with_year(self, file_path):
        """파일에서 연도를 추출하고 데이터를 로드하여 연도 정보를 추가합니다."""
        try:
            # 파일명에서 연도를 추출 (파일명은 'YYYY_...' 형태라고 가정)
            file_name = os.path.basename(file_path)
            match = re.match(r"(\d{4})_", file_name)
            if not match:
                raise ValueError(f"파일명에서 연도를 추출할 수 없습니다: {file_name}")

            year = match.group(1)

            # CSV 파일을 읽고 '연도' 열 추가
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            df['연도'] = int(year)

            return df

        except Exception as e:
            raise Exception(f"CSV 파일 로드 중 오류 발생: {file_path}, 오류: {e}")

    def save_combined_csv(self, income_statement_data, balance_sheet_data, selected_companies):
        """선택된 회사들의 손익계산서와 재무상태표 데이터를 하나의 CSV 파일로 저장합니다."""
        try:
            # 항목명 매핑을 통해 항목명을 추가
            income_statement_data['항목명'] = income_statement_data['항목코드'].map(self.income_statement_item_codes)
            balance_sheet_data['항목명'] = balance_sheet_data['항목코드'].map(self.balance_sheet_item_codes)

            # 필요한 열만 선택하고 데이터 피벗
            income_pivot = income_statement_data.pivot_table(
                index=['회사명', '항목코드', '항목명'],
                columns='연도',
                values='당기',
                aggfunc='first'
            ).reset_index()

            balance_pivot = balance_sheet_data.pivot_table(
                index=['회사명', '항목코드', '항목명'],
                columns='연도',
                values='당기',
                aggfunc='first'
            ).reset_index()

            # 두 데이터를 하나의 DataFrame으로 병합
            combined_data = pd.concat([income_pivot, balance_pivot], ignore_index=True)

            # 열 이름 수정
            combined_data.columns.name = None
            combined_data = combined_data.rename(columns=lambda x: str(x) if isinstance(x, int) else x)

            # CSV 저장 경로 설정
            csv_save_path = self.config.get("csv_save_path", "")
            if not csv_save_path:
                csv_save_path = "combined_financial_data.csv"

            file_path, _ = QFileDialog.getSaveFileName(self.parent, "CSV 파일로 저장", csv_save_path, "CSV Files (*.csv)")
            if file_path:
                combined_data.to_csv(file_path, index=False, encoding='utf-8-sig')
                QMessageBox.information(self.parent, "저장 완료", f"CSV 파일이 저장되었습니다: {file_path}")

        except Exception as e:
            QMessageBox.critical(self.parent, "오류", f"CSV 파일 저장 중 오류가 발생했습니다: {e}")
            print(f"[Error - CSV Save]: {e}")

