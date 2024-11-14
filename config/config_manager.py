import os
import json
import sys

CONFIG_FILE = "config/config.json"

# 기본 설정값
DEFAULT_CONFIG = {
    "income_data_path": "./datasets/IS",
    "income_result_path": "./datasets/IS_graph",
    "balance_data_path": "./datasets/BS",
    "balance_result_path": "./datasets/BS_graph",
    "png_save_path": "./datasets/PNG",
    "csv_save_path": "./datasets/CSV",  # CSV 저장 경로 추가
    "bs_raw_path": "./datasets/BS_raw",
    "is_raw_path": "./datasets/IS_raw"
}

# PyInstaller에서의 임시 디렉토리 경로 설정
def get_base_path():
    """실행 파일의 위치를 기준으로 경로를 설정"""
    if getattr(sys, 'frozen', False):
        # PyInstaller로 패키징된 경우
        return sys._MEIPASS
    return os.path.abspath(".")

base_path = get_base_path()
CONFIG_FILE_PATH = os.path.join(base_path, CONFIG_FILE)
ITEM_CODES_FILE = os.path.join(base_path, "config", "item_codes.json")
METADATA_FILE_PATH = os.path.join(base_path, "config", "metadata.json")

def load_config():
    """config.json 파일에서 설정을 불러와 기본 설정값과 병합"""
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
            config.update(json.load(f))

    # 상대 경로일 경우에만 실행 파일 기준 절대 경로로 변환
    for key in DEFAULT_CONFIG:
        if config[key].startswith("./"):
            config[key] = os.path.abspath(os.path.join(get_base_path(), config[key]))

    return config

# 전역 설정 데이터 로드
config_data = load_config()

def save_config(config_data):
    with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)

def load_item_codes():
    """item_codes.json 파일을 로드하는 함수"""
    if os.path.exists(ITEM_CODES_FILE):
        with open(ITEM_CODES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "INCOME_STATEMENT_ITEM_CODES": {},
        "BALANCE_SHEET_ITEM_CODES": {}
    }

def save_item_codes(data):
    """item_codes.json 파일에 데이터를 저장하는 함수"""
    with open(ITEM_CODES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_metadata():
    """metadata.json 파일을 로드하는 함수"""
    if os.path.exists(METADATA_FILE_PATH):
        with open(METADATA_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "unknown"}

def save_metadata(data):
    """metadata.json 파일에 데이터를 저장하는 함수"""
    with open(METADATA_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# 경로 설정 관련 메서드
def get_income_data_path():
    return config_data["income_data_path"]

def set_income_data_path(path):
    config_data["income_data_path"] = path
    save_config(config_data)

def get_balance_data_path():
    return config_data["balance_data_path"]

def set_balance_data_path(path):
    config_data["balance_data_path"] = path
    save_config(config_data)

def get_income_result_path():
    return config_data["income_result_path"]

def set_income_result_path(path):
    config_data["income_result_path"] = path
    save_config(config_data)

def get_balance_result_path():
    return config_data["balance_result_path"]

def set_balance_result_path(path):
    config_data["balance_result_path"] = path
    save_config(config_data)

# png 경로 가져오기
def get_png_save_path():
    return config_data.get("png_save_path", "datasets/PNG")

def set_png_save_path(path):
    config_data["png_save_path"] = path
    save_config(config_data)

# csv 경로 가져오기
def get_csv_save_path():
    return config_data.get("csv_save_path", "datasets/CSV")

def set_csv_save_path(path):
    config_data["csv_save_path"] = path
    save_config(config_data)

# 항목 코드 설정 관련 메서드
def get_income_statement_item_codes():
    return config_data.get("income_statement_item_codes", {})

def set_income_statement_item_codes(new_codes):
    config_data["income_statement_item_codes"] = new_codes
    save_config(config_data)

def get_balance_sheet_item_codes():
    return config_data.get("balance_sheet_item_codes", {})

def set_balance_sheet_item_codes(new_codes):
    config_data["balance_sheet_item_codes"] = new_codes
    save_config(config_data)
