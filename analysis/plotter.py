import json
import plotly.graph_objects as go
import os
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd
from config import config_manager  # config_manager 추가

# JSON 파일에서 항목 코드와 명칭을 불러오는 함수
def load_item_codes():
    with open("config/item_codes.json", "r", encoding="utf-8") as f:
        item_codes = json.load(f)
    return item_codes["INCOME_STATEMENT_ITEM_CODES"], item_codes["BALANCE_SHEET_ITEM_CODES"]

# 항목 코드와 명칭 불러오기
INCOME_STATEMENT_ITEM_CODES, BALANCE_SHEET_ITEM_CODES = load_item_codes()

class Plotter:
    def __init__(self, company_name, data):
        self.company_name = company_name
        self.data = data

    def create_graph(self, item_code, item_name_kr):
        try:
            # 필요한 데이터 필터링
            filtered_data = self.data[(self.data['회사명'] == self.company_name) &
                                      (self.data['항목코드'] == item_code)][['연도', '당기']]

            # 필터링된 데이터가 없는 경우 예외 처리
            if filtered_data.empty:
                print(f"[Debug] No data found for company '{self.company_name}' with item '{item_name_kr}'.")
                raise ValueError(f"{self.company_name}에 대한 {item_name_kr} 데이터가 존재하지 않습니다.")

            # 데이터 형식 변환 및 결측값 처리
            filtered_data['당기'] = filtered_data['당기'].astype(str).str.replace(',', '').astype(float)
            filtered_data.sort_values(by="연도", inplace=True)

            # 2019년부터 2023년까지의 연도를 모두 포함하도록 설정
            full_years = pd.DataFrame({'연도': range(2019, 2024)})
            filtered_data = pd.merge(full_years, filtered_data, on="연도", how="left")
            filtered_data['당기'] = filtered_data['당기'].interpolate(method='linear')

            print(f"[Debug] Filtered and interpolated data for company '{self.company_name}' with item '{item_name_kr}':\n{filtered_data}")

            years = filtered_data["연도"].values
            values = filtered_data["당기"].values / 1e8  # 백만원 단위로 변환

            # 분리된 예측 함수 호출
            predicted_value = self.predict_with_linear_regression(years, values, [[2024]])

            # 그래프 생성
            fig = go.Figure()

            # 기존 데이터 표시
            fig.add_trace(go.Scatter(
                x=years, y=values, mode="lines+markers", name=f"{item_name_kr}",
                line=dict(color="blue")
            ))

            # 2024년 예측 추가
            fig.add_trace(go.Scatter(
                x=[2023, 2024], y=[values[-1], predicted_value], mode="lines+markers",
                name="2024 예측", line=dict(color="orange", dash="dash"), marker=dict(color="orange")
            ))

            fig.update_layout(
                title=dict(
                    text=f"{self.company_name} - {item_name_kr} (2019~2024 예측)",
                    x=0.5,
                    xanchor='center'
                ),
                xaxis_title="연도",
                yaxis_title="값 (백만원 단위)",
                yaxis_tickformat=",.0f",
                width=800,
                height=600,
                margin=dict(l=50, r=50, t=50, b=50)
            )

            return fig

        except ValueError as ve:
            print(f"[ValueError - Graph Creation]: {ve}")
            raise

        except Exception as e:
            print(f"[Unexpected Error - Graph Creation]: {e}")
            raise

    def save_graph_as_png(self, fig, item_code, data_type):
        """생성된 그래프를 PNG 형식으로 저장합니다."""
        try:
            # JSON 설정에서 PNG 저장 경로 가져오기
            png_path = config_manager.get_png_save_path()
            os.makedirs(png_path, exist_ok=True)  # 경로가 없을 경우 생성

            # 파일 이름 설정
            file_name = f"{self.company_name}_{item_code}_{data_type}.png"
            file_path = os.path.join(png_path, file_name)

            # PNG로 파일 저장
            fig.write_image(file_path, format="png")
            print(f"[Info] Graph PNG saved successfully at: {file_path}")
            return file_path
        except Exception as e:
            print(f"[Error - PNG Save]: {e}")
            raise

    def save_graph_as_html(self, fig, item_code, data_type):
        try:
            # config에서 저장 경로를 동적으로 가져오기
            config = config_manager.load_config()
            directory = config["income_result_path"] if data_type == "손익계산서" else config["balance_result_path"]
            os.makedirs(directory, exist_ok=True)
            file_name = f"{self.company_name}_{item_code}.html"
            file_path = os.path.join(directory, file_name)

            # 임시 HTML 파일로 저장
            fig.write_html(file_path)

            # HTML 파일을 열어 중앙 정렬 스타일을 추가
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 그래프 중앙 정렬 CSS 스타일 추가
            centered_content = """
            <style>
                body {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
            </style>
            """ + content

            # 수정된 HTML 파일 덮어쓰기
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(centered_content)

            print(f"[Info] Graph saved successfully at {file_path}")
            return file_path

        except OSError as oe:
            print(f"[OSError - File Save]: {oe}")
            raise

        except Exception as e:
            print(f"[Unexpected Error - File Save]: {e}")
            raise

    @staticmethod
    def predict_with_linear_regression(years, values, target_year):
        """
        주어진 데이터로 선형 회귀 모델을 학습하고 target_year에 대한 값을 예측합니다.
        :param years: 연도 데이터 (1차원 또는 2차원 배열)
        :param values: 값 데이터 (1차원 배열, 문자열로 되어 있을 경우에도 처리 가능)
        :param target_year: 예측할 연도 (정수 또는 2D 배열)
        :return: target_year에 대한 예측 값
        """
        try:
            # 데이터를 2차원 배열로 변환
            years = np.array(years).reshape(-1, 1)

            # values가 문자열일 경우 전처리 (쉼표 제거 및 float 변환)
            if values.dtype == 'object':  # numpy 배열에서 문자열 타입 확인
                values = np.char.replace(values.astype(str), ',', '').astype(float)

            # target_year이 정수로 들어왔을 경우 2D 배열로 변환
            if isinstance(target_year, int):
                target_year = np.array([[target_year]])

            # 선형 회귀 모델 학습
            model = LinearRegression()
            model.fit(years, values)

            # target_year 예측
            predicted_value = model.predict(target_year)[0]  # target_year는 2D 배열이어야 함
            return predicted_value

        except Exception as e:
            print(f"[Error - Prediction]: {e}")
            raise
