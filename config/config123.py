#config/config.py
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
    "csv_save_path": "./datasets/CSV",
    "bs_raw_path": "./datasets/BS_raw",
    "is_raw_path": "./datasets/IS_raw"
}

# PyInstaller에서 실행 파일의 임시 디렉토리 경로 설정
def get_base_path():
    """실행 파일의 위치를 기준으로 경로를 설정"""
    if getattr(sys, 'frozen', False):  # PyInstaller로 패키징된 경우
        return sys._MEIPASS
    return os.path.abspath(".")

base_path = get_base_path()
CONFIG_FILE_PATH = os.path.join(base_path, CONFIG_FILE)

def load_config():
    """config.json 파일에서 설정을 불러와 기본 설정값과 병합"""
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
            config.update(json.load(f))

    # 상대 경로를 절대 경로로 변환
    for key, value in config.items():
        if value.startswith("./"):
            config[key] = os.path.abspath(os.path.join(get_base_path(), value))

    return config

# 전역 설정 데이터 로드
config_data = load_config()

def save_config(config_data):
    """config.json 파일에 설정 데이터를 저장"""
    with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)

# 설정 경로 관련 메서드
def get_csv_save_path():
    return config_data.get("csv_save_path", "./datasets/CSV")

def set_csv_save_path(path):
    config_data["csv_save_path"] = path
    save_config(config_data)

def get_png_save_path():
    return config_data.get("png_save_path", "./datasets/PNG")

def set_png_save_path(path):
    config_data["png_save_path"] = path
    save_config(config_data)
