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
    "png_save_path": "./datasets/PNG"
}

def get_base_path():
    """실행 파일의 위치를 기준으로 경로를 설정"""
    if getattr(sys, 'frozen', False):
        # PyInstaller로 패키징된 경우
        return sys._MEIPASS
    return os.path.abspath(".")

def load_config():
    config = DEFAULT_CONFIG.copy()
    config_path = os.path.join(get_base_path(), CONFIG_FILE)  # 실행 경로 기준 설정 파일 경로 지정

    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config.update(json.load(f))

    # 실행 파일 위치를 기준으로 동적 경로 설정
    for key in DEFAULT_CONFIG:
        config[key] = os.path.join(get_base_path(), config[key])

    return config

def save_config(config_data):
    config_path = os.path.join(get_base_path(), CONFIG_FILE)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)

def parse_item_codes(item_codes_str):
    item_codes = {}
    for item in item_codes_str.split(";"):
        code, name = item.split("=")
        item_codes[code] = name
    return item_codes

def format_item_codes(item_codes):
    if isinstance(item_codes, dict):
        return ";".join(f"{code}={name}" for code, name in item_codes.items())
    return item_codes
