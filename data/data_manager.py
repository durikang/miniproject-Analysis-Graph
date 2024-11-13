# data_manager.py
from data import data_loader


def load_companies(balance_data_path, income_data_path):
    # `data_loader` 모듈을 통해 데이터를 로드하고 가공하는 함수
    try:
        return data_loader.load_company_data(balance_data_path, income_data_path)
    except (FileNotFoundError, KeyError) as e:
        raise e


def sort_items(items):
    # 리스트 아이템을 정렬하는 유틸리티 함수
    return sorted(items)


def prepare_data_for_analysis(balance_data_path, income_data_path, selected_companies):
    """
    선택된 회사들에 대한 손익계산서와 재무상태표 데이터를 개별적으로 로드하여 반환합니다.
    """
    # 손익계산서 데이터와 재무상태표 데이터를 각각 로드
    income_statement_data = data_loader.prepare_income_statement_data(income_data_path, selected_companies)
    balance_sheet_data = data_loader.prepare_balance_sheet_data(balance_data_path, selected_companies)

    # 각각의 데이터프레임을 반환
    return income_statement_data, balance_sheet_data


def get_filtered_data(prepared_data, company, category, data_item):
    # 선택한 회사, 카테고리, 데이터 항목으로 필터링된 데이터를 반환
    filtered_data = prepared_data[(prepared_data["회사명"] == company) &
                                  (prepared_data["데이터종류"] == category) &
                                  (prepared_data["항목명"] == data_item)]
    return filtered_data
