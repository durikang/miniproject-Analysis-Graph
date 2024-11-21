#data/data_loader/py

import os
import csv
import traceback
import pandas as pd
import glob

# 매출액을 나타내는 항목 코드 (사용자가 알려준 대로 수정 가능)
SALES_CODE = "ifrs-full_Revenue"


def load_company_data(balance_data_path, income_data_path):
    try:
        company_sets = {year: set() for year in range(2019, 2024)}

        for year in range(2019, 2024):
            balance_files = glob.glob(os.path.join(balance_data_path, f"{year}_*.csv"))
            for file in balance_files:
                try:
                    data = pd.read_csv(file)
                    if "회사명" in data.columns:
                        company_sets[year].update(data["회사명"].dropna().unique())
                except Exception as e:
                    print(f"[ERROR] Failed to load balance file {file}: {e}")
                    traceback.print_exc()

        income_data = {}
        for year in range(2019, 2024):
            income_files = glob.glob(os.path.join(income_data_path, f"{year}_*.csv"))
            for file in income_files:
                try:
                    data = pd.read_csv(file)
                    if "회사명" in data.columns and "항목코드" in data.columns:
                        sales_data = data[data["항목코드"] == SALES_CODE]
                        income_data[year] = sales_data["회사명"].dropna().unique()
                except Exception as e:
                    print(f"[ERROR] Failed to load income file {file}: {e}")
                    traceback.print_exc()

        valid_companies = set(company_sets[2019])
        for year in range(2020, 2024):
            valid_companies &= company_sets[year]
            valid_companies &= set(income_data.get(year, []))

        return sorted(valid_companies)
    except Exception as e:
        print("[ERROR] Failed to load company data.")
        traceback.print_exc()
        return []


def prepare_balance_sheet_data(balance_data_path, selected_companies):
    try:
        data_frames = []
        for year in range(2019, 2024):
            balance_files = glob.glob(os.path.join(balance_data_path, f"{year}_*.csv"))

            for file in balance_files:
                try:
                    balance_data = pd.read_csv(file)
                    balance_data = balance_data[balance_data["회사명"].isin(selected_companies)]
                    balance_data["연도"] = year
                    balance_data["데이터종류"] = "재무상태표"
                    balance_data.fillna(0, inplace=True)
                    data_frames.append(balance_data)
                except Exception as e:
                    print(f"[ERROR] Failed to process balance file {file}: {e}")
                    traceback.print_exc()

        balance_sheet_data = pd.concat(data_frames, ignore_index=True)
        return balance_sheet_data
    except Exception as e:
        print("[ERROR] Failed to prepare balance sheet data.")
        traceback.print_exc()
        return pd.DataFrame()


def prepare_income_statement_data(income_data_path, selected_companies):
    try:
        data_frames = []
        for year in range(2019, 2024):
            income_files = glob.glob(os.path.join(income_data_path, f"{year}_*.csv"))

            for file in income_files:
                try:
                    income_data = pd.read_csv(file)
                    income_data = income_data[income_data["회사명"].isin(selected_companies)]
                    income_data["연도"] = year
                    income_data["데이터종류"] = "손익계산서"
                    income_data.fillna(0, inplace=True)
                    data_frames.append(income_data)
                except Exception as e:
                    print(f"[ERROR] Failed to process income file {file}: {e}")
                    traceback.print_exc()

        income_statement_data = pd.concat(data_frames, ignore_index=True)
        return income_statement_data
    except Exception as e:
        print("[ERROR] Failed to prepare income statement data.")
        traceback.print_exc()
        return pd.DataFrame()
