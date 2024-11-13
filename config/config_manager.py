# config_manager.py

import json
import os
import sys
from . import config

CONFIG_FILE = "config/config.json"

# 기본 설정값
DEFAULT_CONFIG = {
    "income_data_path": "./datasets/IS",
    "income_result_path": "./datasets/IS_graph",
    "balance_data_path": "./datasets/BS",
    "balance_result_path": "./datasets/BS_graph",
    "png_save_path": "./datasets/PNG",
    "bs_raw_path": "./datasets/BS_raw",
    "is_raw_path": "./datasets/IS_raw"
}
config_data = config.load_config()

# PyInstaller에서의 임시 디렉토리 경로 설정
base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
ITEM_CODES_FILE = os.path.join(base_path, "config", "item_codes.json")

def load_item_codes():
    """item_codes.json 파일을 로드하는 함수"""
    if os.path.exists(ITEM_CODES_FILE):
        with open(ITEM_CODES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # 파일이 없는 경우 기본 구조 반환
        return {
            "INCOME_STATEMENT_ITEM_CODES": {},
            "BALANCE_SHEET_ITEM_CODES": {}
        }

def save_item_codes(data):
    """item_codes.json 파일에 데이터를 저장하는 함수"""
    with open(ITEM_CODES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# 실행 파일의 위치를 기준으로 기본 경로를 설정하는 함수
def get_base_path():
    """실행 파일의 위치를 기준으로 경로를 설정"""
    return getattr(sys, '_MEIPASS', os.path.abspath("."))

# config.json 파일의 경로를 동적으로 불러오기
CONFIG_FILE_PATH = os.path.join(get_base_path(), "config", "config.json")

# 경로 설정을 불러오는 함수
def load_config():
    config = DEFAULT_CONFIG.copy()
    config_path = os.path.join(get_base_path(), CONFIG_FILE)  # 실행 경로 기준 설정 파일 경로 지정

    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config.update(json.load(f))

    # 실행 파일 위치를 기준으로 동적 경로 설정
    for key in DEFAULT_CONFIG:
        # 상대 경로일 경우에만 실행 파일 기준 절대 경로로 변환
        if config[key].startswith("./"):
            config[key] = os.path.abspath(os.path.join(get_base_path(), config[key]))

    return config

def save_config(config_data):
    config_path = os.path.join(get_base_path(), CONFIG_FILE)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)

# 경로 설정 관련 메서드
def get_income_data_path():
    return config_data["income_data_path"]

def set_income_data_path(path):
    config_data["income_data_path"] = path
    save_config()

def get_balance_data_path():
    return config_data["balance_data_path"]

def set_balance_data_path(path):
    config_data["balance_data_path"] = path
    save_config()

def get_income_result_path():
    return config_data["income_result_path"]

def set_income_result_path(path):
    config_data["income_result_path"] = path
    save_config()

def get_balance_result_path():
    return config_data["balance_result_path"]

# png 경로 가져오기
def get_png_save_path():
    return config_data.get("png_save_path", "datasets/PNG")

def set_png_save_path(path):
    """PNG 저장 경로를 설정하고 JSON 파일에 저장합니다."""
    config = load_config()
    config["png_save_path"] = path
    save_config(config)


def set_balance_result_path(path):
    config_data["balance_result_path"] = path
    save_config()

# 항목 코드 설정 관련 메서드
def get_income_statement_item_codes():
    return config_data["income_statement_item_codes"]

def set_income_statement_item_codes(new_codes):
    config_data["income_statement_item_codes"] = new_codes
    save_config()

def get_balance_sheet_item_codes():
    return config_data["balance_sheet_item_codes"]

def set_balance_sheet_item_codes(new_codes):
    config_data["balance_sheet_item_codes"] = new_codes
    save_config()
