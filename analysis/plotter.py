import json
import plotly.graph_objects as go
import os
from sklearn.linear_model import LinearRegression
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

            # 결측값을 선형 보간으로 채우기
            filtered_data['당기'] = filtered_data['당기'].interpolate(method='linear')

            # 디버깅용 필터링된 데이터 출력
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            pd.set_option('display.expand_frame_repr', False)
            print(f"[Debug] Filtered and interpolated data for company '{self.company_name}' with item '{item_name_kr}':\n{filtered_data}")
            pd.reset_option('display.max_rows')
            pd.reset_option('display.max_columns')
            pd.reset_option('display.expand_frame_repr')

            years = filtered_data["연도"].values.reshape(-1, 1)
            values = filtered_data["당기"].values / 1e8  # 백만원 단위로 변환

            # 선형 회귀 모델을 통해 2024년 예측
            model = LinearRegression()
            model.fit(years, values)
            predicted_value = model.predict([[2024]])[0]

            # 그래프 생성
            fig = go.Figure()

            # 기존 데이터 표시
            fig.add_trace(go.Scatter(
                x=years.flatten(), y=values, mode="lines+markers", name=f"{item_name_kr}",
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
                yaxis_tickformat=",.0f",  # y축 단위 변경 (백만원 단위, 쉼표 추가)
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

    def save_data_as_csv(self, item_code, data_type):
        """선택된 회사와 항목의 데이터를 CSV 형식으로 저장합니다."""
        try:
            # 데이터 타입에 따라 적절한 데이터 선택
            data = self.income_statement_data if data_type == "손익계산서" else self.balance_sheet_data

            # 데이터 필터링
            filtered_data = data[(data['회사명'] == self.company_name) & (data['항목코드'] == item_code)]

            # CSV 파일로 저장할 경로 설정
            config = config_manager.load_config()
            csv_directory = config["income_result_path"] if data_type == "손익계산서" else config["balance_result_path"]
            os.makedirs(csv_directory, exist_ok=True)
            file_name = f"{self.company_name}_{item_code}_{data_type}.csv"
            file_path = os.path.join(csv_directory, file_name)

            # CSV로 파일 저장
            filtered_data.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"[Info] Data saved successfully as CSV at: {file_path}")
            return file_path

        except Exception as e:
            print(f"[Error - CSV Save]: {e}")
            raise

