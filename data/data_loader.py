# data_loader.py

import pandas as pd
import glob
import os

# 매출액을 나타내는 항목 코드 (사용자가 알려준 대로 수정 가능)
SALES_CODE = "ifrs-full_Revenue"


def load_company_data(balance_data_path, income_data_path):
    company_sets = {year: set() for year in range(2019, 2024)}

    for year in range(2019, 2024):
        balance_files = glob.glob(os.path.join(balance_data_path, f"{year}_*.csv"))
        for file in balance_files:
            data = pd.read_csv(file)
            if "회사명" in data.columns:
                company_sets[year].update(data["회사명"].dropna().unique())

        print(f"[Debug] Companies in balance sheet for year {year}: {company_sets[year]}")

    income_data = {}
    for year in range(2019, 2024):
        income_files = glob.glob(os.path.join(income_data_path, f"{year}_*.csv"))
        for file in income_files:
            data = pd.read_csv(file)
            if "회사명" in data.columns and "항목코드" in data.columns:
                sales_data = data[data["항목코드"] == SALES_CODE]
                income_data[year] = sales_data["회사명"].dropna().unique()

        print(f"[Debug] Companies with sales data in income statement for year {year}: {income_data.get(year, [])}")

    valid_companies = set(company_sets[2019])
    for year in range(2020, 2024):
        valid_companies &= company_sets[year]
        valid_companies &= set(income_data.get(year, []))

    print(f"[Debug] Valid companies for all years: {sorted(valid_companies)}")
    return sorted(valid_companies)


def prepare_balance_sheet_data(balance_data_path, selected_companies):
    data_frames = []
    for year in range(2019, 2024):
        balance_files = glob.glob(os.path.join(balance_data_path, f"{year}_*.csv"))

        print(f"[Debug] Loading balance sheet files for year {year}: {balance_files}")

        for file in balance_files:
            balance_data = pd.read_csv(file)
            balance_data = balance_data[balance_data["회사명"].isin(selected_companies)]

            # 특정 항목코드 (ifrs_CurrentAssets)가 있는지 필터링하여 디버깅
            if '항목코드' in balance_data.columns:
                filtered_code_data = balance_data[balance_data['항목코드'] == 'ifrs_CurrentAssets']
                print(f"[Debug] Checking for ifrs_CurrentAssets in balance sheet data for {file}:\n{filtered_code_data[['회사명', '항목코드', '당기']]}")

                # 항목코드의 고유 값 확인
                unique_codes = balance_data['항목코드'].unique()
                print(f"[Debug] Unique 항목코드 in the balance sheet data for {file}: {unique_codes}")

            balance_data["연도"] = year
            balance_data["데이터종류"] = "재무상태표"
            balance_data.fillna(0, inplace=True)
            data_frames.append(balance_data)

    balance_sheet_data = pd.concat(data_frames, ignore_index=True)
    print(f"[Debug] Concatenated balance sheet data:\n{balance_sheet_data.head()}")
    return balance_sheet_data



def prepare_income_statement_data(income_data_path, selected_companies):
    data_frames = []
    for year in range(2019, 2024):
        income_files = glob.glob(os.path.join(income_data_path, f"{year}_*.csv"))

        # 각 연도 및 파일별로 디버그 메시지 추가
        print(f"[Debug] Loading income statement files for year {year}: {income_files}")

        for file in income_files:
            income_data = pd.read_csv(file)
            # 회사명 필터링 후 디버그 메시지 추가
            income_data = income_data[income_data["회사명"].isin(selected_companies)]
            print(f"[Debug] Filtered income data for {file}:\n{income_data[['회사명', '항목코드', '당기']]}")

            income_data["연도"] = year
            income_data["데이터종류"] = "손익계산서"
            income_data.fillna(0, inplace=True)
            data_frames.append(income_data)

    income_statement_data = pd.concat(data_frames, ignore_index=True)
    print(f"[Debug] Concatenated income statement data:\n{income_statement_data.head()}")
    return income_statement_data

