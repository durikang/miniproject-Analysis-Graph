import os
from datetime import datetime

LOG_DIR = "logs"
MAX_LOG_FILES = 5

def setup_logger():
    """로그 폴더를 설정하고 파일 개수를 제한합니다."""
    os.makedirs(LOG_DIR, exist_ok=True)
    manage_log_files()

def get_log_file_path():
    """날짜별 로그 파일 경로를 생성합니다 (일별로 하나의 파일에 기록)."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = f"update_log_{date_str}.txt"
    return os.path.join(LOG_DIR, log_file)

def log_debug_message(message):
    """디버그 메시지를 현재 날짜의 로그 파일에 기록합니다."""
    setup_logger()
    log_file_path = get_log_file_path()
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")

def manage_log_files():
    """로그 파일 개수를 관리하여 MAX_LOG_FILES를 초과하면 가장 오래된 파일을 삭제합니다."""
    log_files = sorted(
        [os.path.join(LOG_DIR, f) for f in os.listdir(LOG_DIR) if os.path.isfile(os.path.join(LOG_DIR, f))],
        key=os.path.getmtime
    )

    # 로그 파일이 MAX_LOG_FILES를 초과하면 오래된 파일을 삭제
    while len(log_files) > MAX_LOG_FILES:
        oldest_file = log_files.pop(0)
        os.remove(oldest_file)
        print(f"[DEBUG] 오래된 로그 파일 삭제: {oldest_file}")

def clear_logs():
    """모든 로그 파일을 삭제합니다."""
    setup_logger()
    for filename in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
