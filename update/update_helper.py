import os
import shutil
import subprocess
import sys
import time

# 현재 exe 파일 경로
exe_path = sys.argv[1]
backup_path = exe_path + ".bak"  # 백업 파일 경로

# 기존 exe 백업
if os.path.exists(backup_path):
    os.remove(backup_path)
shutil.move(exe_path, backup_path)

# Git 업데이트 수행
project_dir = os.path.dirname(exe_path)
subprocess.run(["git", "fetch", "--tags"], cwd=project_dir)
subprocess.run(["git", "pull"], cwd=project_dir)

# 백업된 exe 파일을 새 exe 파일로 교체
shutil.copyfile(backup_path, exe_path)

# 업데이트가 완료되었으므로 프로그램을 재실행
time.sleep(1)  # 복사가 완료되도록 대기 시간 추가
subprocess.Popen([exe_path])  # 새로 업데이트된 exe 실행
