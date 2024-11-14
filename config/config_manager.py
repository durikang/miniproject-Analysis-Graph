import os
import json
import sys

CONFIG_FILE = "config/config.json"
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
    """실행 파일의 위치를 기준으로 경로를 설정"""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS  # 패키징된 실행파일의 임시 폴더
    return os.path.abspath(".")

def get_config_path():
    """config.json 파일 경로"""
    return os.path.join(get_base_path(), CONFIG_FILE)

def load_config():
    """config.json 파일에서 설정을 불러와 기본 설정값과 병합"""
    config = DEFAULT_CONFIG.copy()
    config_path = get_config_path()

    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config.update(json.load(f))

    for key in config:
        if config[key].startswith("./"):
            config[key] = os.path.abspath(os.path.join(get_base_path(), config[key]))

    return config

def save_config(config_data):
    """config.json 파일에 설정을 저장"""
    config_path = get_config_path()
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)

config_data = load_config()

def get_path(key):
    """특정 경로 설정 값을 반환"""
    return config_data.get(key, "")

def set_path(key, path):
    """경로 설정을 업데이트하고 저장"""
    config_data[key] = path
    save_config(config_data)

def load_metadata():
    """metadata.json 파일을 로드하는 함수"""
    metadata_path = os.path.join(get_base_path(), METADATA_FILE)
    if os.path.exists(metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "unknown"}

def save_metadata(data):
    """metadata.json 파일에 데이터를 저장하는 함수"""
    metadata_path = os.path.join(get_base_path(), METADATA_FILE)
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
