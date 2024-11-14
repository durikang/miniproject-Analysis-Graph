import json
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
import subprocess
import traceback
import os
import sys

class UpdateWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("업데이트 확인 옵션")
        self.setGeometry(200, 200, 400, 250)

        # 레이아웃 설정
        layout = QVBoxLayout()

        # 현재 버전과 최신 버전 정보를 표시할 라벨
        self.current_version_label = QLabel("현재 버전: 확인 중...")
        self.latest_version_label = QLabel("최신 버전: 확인 중...")

        # 최신 버전 확인 버튼
        self.check_update_button = QPushButton("최신 버전 확인하기")
        self.check_update_button.clicked.connect(self.check_for_updates)

        # 업데이트 버튼
        self.update_button = QPushButton("업데이트")
        self.update_button.setEnabled(False)  # 초기 상태에서는 비활성화
        self.update_button.clicked.connect(self.perform_update)

        # 레이아웃에 위젯 추가
        layout.addWidget(self.current_version_label)
        layout.addWidget(self.latest_version_label)
        layout.addWidget(self.check_update_button)
        layout.addWidget(self.update_button)

        self.setLayout(layout)

        # 설정 파일에서 메타 정보 경로 가져오기
        self.metadata_path = self.get_metadata_path_from_config()

        # 현재 버전 불러오기
        self.local_version = self.load_local_version()

    def get_metadata_path_from_config(self):
        """config.json에서 메타 정보 파일 경로를 절대 경로로 읽어옴"""
        try:
            config_path = r"/config.json"  # 절대 경로 지정
            if not os.path.exists(config_path):
                raise FileNotFoundError("config.json 파일이 없습니다.")

            with open(config_path, "r") as config_file:
                config = json.load(config_file)
                metadata_path = config.get("metadata_path")
                if metadata_path and os.path.isabs(metadata_path):
                    return metadata_path
                else:
                    return os.path.join(os.path.dirname(config_path), metadata_path)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            QMessageBox.critical(self, "오류", f"설정 파일을 불러올 수 없습니다: {e}")
            return "config/metadata.json"  # 기본 경로로 설정

    def load_local_version(self):
        """메타 정보에서 현재 시맨틱 버전을 불러옴"""
        try:
            with open(self.metadata_path, "r", encoding="utf-8") as file:
                metadata = json.load(file)
                version = metadata.get("version", "버전 정보 없음")
                self.current_version_label.setText(f"현재 버전: {version}")
                return version
        except FileNotFoundError:
            self.current_version_label.setText("현재 버전: 메타 정보 파일 없음")
            return None
        except json.JSONDecodeError:
            self.current_version_label.setText("현재 버전: 메타 정보 파일 오류")
            return None

    def get_latest_tag(self):
        """원격 저장소의 최신 태그 가져오기"""
        try:
            project_dir = os.getcwd()

            # Step 1: git fetch --tags
            fetch_result = subprocess.run(["git", "fetch", "--tags"], capture_output=True, text=True, cwd=project_dir,
                                          encoding="utf-8")
            if fetch_result.returncode != 0:
                raise subprocess.CalledProcessError(fetch_result.returncode, fetch_result.args, fetch_result.stdout,
                                                    fetch_result.stderr)

            # Step 2: git rev-list --tags --max-count=1
            rev_list_result = subprocess.run(
                ["git", "rev-list", "--tags", "--max-count=1"],
                capture_output=True, text=True, cwd=project_dir, encoding="utf-8"
            )
            if rev_list_result.returncode != 0:
                raise subprocess.CalledProcessError(rev_list_result.returncode, rev_list_result.args,
                                                    rev_list_result.stdout, rev_list_result.stderr)

            latest_commit_id = rev_list_result.stdout.strip()
            if not latest_commit_id:
                raise ValueError("태그가 없습니다. 저장소에 태그를 추가하세요.")

            # Step 3: git describe --tags <commit_id>
            describe_result = subprocess.run(
                ["git", "describe", "--tags", latest_commit_id],
                capture_output=True, text=True, cwd=project_dir, encoding="utf-8"
            )
            if describe_result.returncode != 0:
                raise subprocess.CalledProcessError(describe_result.returncode, describe_result.args,
                                                    describe_result.stdout, describe_result.stderr)

            latest_tag = describe_result.stdout.strip()
            self.latest_version_label.setText(f"최신 버전: {latest_tag}")
            return latest_tag

        except subprocess.CalledProcessError as e:
            error_message = f"원격 최신 버전 확인 중 오류 발생:\n{traceback.format_exc()}\n\nCommand: {e.cmd}\nReturn code: {e.returncode}\nError output:\n{e.stderr}"
            QMessageBox.critical(self, "오류", error_message)
        except ValueError as e:
            QMessageBox.critical(self, "오류", str(e))
        except Exception as e:
            error_message = f"원격 최신 버전 확인 중 예외 발생:\n{traceback.format_exc()}"
            QMessageBox.critical(self, "오류", error_message)
        return None

    def check_for_updates(self):
        """로컬 시맨틱 버전과 원격 태그 버전을 비교하여 업데이트 필요 여부 확인"""
        latest_version = self.get_latest_tag()

        if self.local_version and latest_version:
            if self.local_version != latest_version:
                self.update_button.setEnabled(True)
                QMessageBox.information(
                    self,
                    "업데이트 필요",
                    f"현재 버전:\n{self.local_version}\n\n최신 버전:\n{latest_version}\n\n새 버전이 있습니다.",
                )
            else:
                QMessageBox.information(self, "최신 상태", "프로그램이 최신 상태입니다.")
        else:
            QMessageBox.critical(self, "오류", "업데이트 상태를 확인할 수 없습니다.")

    def perform_update(self):
        """업데이트를 수행하는 메서드"""
        try:
            exe_path = sys.executable

            # update_helper.py 실행으로 업데이트 실행
            subprocess.Popen([sys.executable, "update_helper.py", exe_path])

            # 현재 프로그램 종료
            sys.exit(0)

        except Exception as e:
            error_message = f"업데이트 중 오류 발생:\n{traceback.format_exc()}"
            QMessageBox.critical(self, "업데이트 오류", error_message)
