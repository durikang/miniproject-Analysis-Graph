import os
import json
import sys

CONFIG_FILE = "config/config.json"
ITEM_CODES_FILE = "config/item_codes.json"
METADATA_FILE = "config/metadata.json"

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

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.abspath(".")

base_path = get_base_path()
CONFIG_FILE_PATH = os.path.join(base_path, CONFIG_FILE)

def load_config():
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
            config.update(json.load(f))
    for key, value in config.items():
        if value.startswith("./"):
            config[key] = os.path.abspath(os.path.join(base_path, value))
    return config

def save_config(config):
    with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

# 경로 관련 함수
def get_path(key, default=None):
    return config_data.get(key, default)

def set_path(key, path):
    config_data[key] = path
    save_config(config_data)

# 항목 코드 관련
def load_item_codes():
    if os.path.exists(ITEM_CODES_FILE):
        with open(ITEM_CODES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"INCOME_STATEMENT_ITEM_CODES": {}, "BALANCE_SHEET_ITEM_CODES": {}}

def save_item_codes(data):
    with open(ITEM_CODES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# 메타데이터 관련
def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "unknown"}

def save_metadata(data):
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_png_save_path():
    return config_data.get("png_save_path", "./datasets/PNG")

def set_png_save_path(path):
    config_data["png_save_path"] = path
    save_config(config_data)

# 전역 설정 데이터
config_data = load_config()
