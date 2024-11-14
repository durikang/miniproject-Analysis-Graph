# save_analysis_result_as_csv.py

from PyQt5.QtWidgets import QMessageBox

import pandas as pd
from sklearn.linear_model import LinearRegression
import os
from config import config_manager
from data import data_manager
from analysis.plotter import INCOME_STATEMENT_ITEM_CODES, BALANCE_SHEET_ITEM_CODES


def save_analysis_results_as_csv(selected_companies, income_statement_data, balance_sheet_data):
    # CSV 저장 경로 설정
    csv_save_path = config_manager.get_csv_save_path()
    os.makedirs(csv_save_path, exist_ok=True)

    # CSV 파일 경로 설정
    csv_file_path = os.path.join(csv_save_path, "analysis_results.csv")

    # 최종 데이터 저장을 위한 빈 리스트 생성
    analysis_results = []

    # 각 회사에 대해 분석 실행
    for company in selected_companies:
        # 각 항목에 대해 데이터 처리
        for item_code, item_name in {**INCOME_STATEMENT_ITEM_CODES, **BALANCE_SHEET_ITEM_CODES}.items():
            # 데이터 타입에 따라 적절한 데이터프레임 선택
            if item_code in INCOME_STATEMENT_ITEM_CODES:
                data = income_statement_data
            else:
                data = balance_sheet_data

            # 회사와 항목 코드에 해당하는 데이터 필터링
            filtered_data = data[(data['회사명'] == company) & (data['항목코드'] == item_code)][['연도', '당기']]

            # 데이터가 없는 경우 생략
            if filtered_data.empty:
                continue

            # 결측값 채우기 및 연도 정렬
            filtered_data['당기'] = filtered_data['당기'].astype(str).str.replace(',', '').astype(float)
            filtered_data.sort_values(by="연도", inplace=True)
            full_years = pd.DataFrame({'연도': range(2019, 2024)})
            filtered_data = pd.merge(full_years, filtered_data, on="연도", how="left")
            filtered_data['당기'] = filtered_data['당기'].interpolate(method='linear')

            # 2019–2023 데이터와 2024 예측값 설정
            years = filtered_data["연도"].values.reshape(-1, 1)
            values = filtered_data["당기"].values  # 백만원 단위 변환 없이 원래 값 사용
            model = LinearRegression()
            model.fit(years[:-1], values[:-1])  # 2024년 제외하고 학습
            predicted_2024 = model.predict([[2024]])[0]

            # 결과를 분석 리스트에 추가
            result_row = {
                "회사명": company,
                "항목코드": item_code,
                "항목명": item_name,
                "2019": values[0] if len(values) > 0 else None,
                "2020": values[1] if len(values) > 1 else None,
                "2021": values[2] if len(values) > 2 else None,
                "2022": values[3] if len(values) > 3 else None,
                "2023": values[4] if len(values) > 4 else None,
                "2024(예측)": predicted_2024
            }
            analysis_results.append(result_row)

    # 데이터프레임으로 변환 후 CSV 파일로 저장
    results_df = pd.DataFrame(analysis_results)
    results_df.to_csv(csv_file_path, index=False, encoding="utf-8-sig")
    print(f"[Info] Analysis results saved successfully at {csv_file_path}")
