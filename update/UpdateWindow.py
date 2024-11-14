import json
import subprocess
import os
import sys
import traceback
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
import config_manager

class UpdateWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("업데이트 확인 옵션")
        self.setGeometry(200, 200, 400, 250)

        layout = QVBoxLayout()

        self.current_version_label = QLabel("현재 버전: 확인 중...")
        self.latest_version_label = QLabel("최신 버전: 확인 중...")

        self.check_update_button = QPushButton("최신 버전 확인하기")
        self.check_update_button.clicked.connect(self.check_for_updates)

        self.update_button = QPushButton("업데이트")
        self.update_button.setEnabled(False)
        self.update_button.clicked.connect(self.perform_update)

        layout.addWidget(self.current_version_label)
        layout.addWidget(self.latest_version_label)
        layout.addWidget(self.check_update_button)
        layout.addWidget(self.update_button)

        self.setLayout(layout)

        # 로컬 버전 로드
        self.local_version = self.load_local_version()
        print(f"[DEBUG] 로드된 로컬 버전: {self.local_version}")  # 로컬 버전 출력

    def load_local_version(self):
        """로컬 메타 데이터에서 버전 정보를 불러옵니다."""
        try:
            metadata = config_manager.load_metadata()
            version = metadata.get("version", "버전 정보 없음")
            self.current_version_label.setText(f"현재 버전: {version}")
            return version
        except Exception as e:
            print("[DEBUG] Error loading local version:")
            traceback.print_exc()
            QMessageBox.critical(self, "오류", f"현재 버전을 불러오는 중 오류 발생: {e}")
            return None

    def get_latest_tag(self):
        """원격 저장소에서 최신 태그를 가져옵니다."""
        try:
            project_dir = os.getcwd()

            # Step 1: 최신 태그 목록을 가져옵니다.
            fetch_result = subprocess.run(
                ["git", "fetch", "--tags"], cwd=project_dir, check=True, capture_output=True, text=True
            )
            print(f"[DEBUG] git fetch --tags 결과: {fetch_result.stdout}")

            # Step 2: 최신 커밋 ID를 가져옵니다.
            rev_list_result = subprocess.run(
                ["git", "rev-list", "--tags", "--max-count=1"],
                cwd=project_dir, capture_output=True, text=True
            )
            latest_commit_id = rev_list_result.stdout.strip()
            print(f"[DEBUG] 최신 커밋 ID: {latest_commit_id}")

            if not latest_commit_id:
                raise ValueError("태그가 없습니다. 저장소에 태그를 추가하세요.")

            # Step 3: 최신 커밋 ID에 대한 태그 설명을 가져옵니다.
            describe_result = subprocess.run(
                ["git", "describe", "--tags", latest_commit_id],
                cwd=project_dir, capture_output=True, text=True
            )
            latest_tag = describe_result.stdout.strip()
            print(f"[DEBUG] 로드된 최신 태그: {latest_tag}")
            self.latest_version_label.setText(f"최신 버전: {latest_tag}")
            return latest_tag

        except subprocess.CalledProcessError as e:
            print("[DEBUG] Error fetching latest tag:")
            traceback.print_exc()
            QMessageBox.critical(self, "오류", "원격 최신 버전 확인 실패")
            return None
        except ValueError as e:
            QMessageBox.critical(self, "오류", str(e))
            return None
        except Exception as e:
            print("[DEBUG] Unexpected error in get_latest_tag:")
            traceback.print_exc()
            QMessageBox.critical(self, "오류", f"태그를 가져오는 도중 오류 발생: {e}")
            return None
    def check_for_updates(self):
        """로컬 버전과 원격 버전을 비교하여 업데이트 필요 여부를 확인합니다."""
        try:
            latest_version = self.get_latest_tag()
            print(f"[DEBUG] 체크 중인 최신 원격 버전: {latest_version}")  # 최신 원격 버전 출력
            if self.local_version and latest_version:
                if self.local_version != latest_version:
                    self.update_button.setEnabled(True)
                    QMessageBox.information(self, "업데이트 필요", f"새 버전 {latest_version}이 있습니다.")
                else:
                    QMessageBox.information(self, "최신 상태", "프로그램이 최신 상태입니다.")
            else:
                print("[DEBUG] Error in check_for_updates: 로컬 또는 원격 버전 정보를 확인할 수 없습니다.")
        except Exception as e:
            print("[DEBUG] Error checking for updates:")
            traceback.print_exc()
            QMessageBox.critical(self, "오류", f"업데이트 상태를 확인하는 중 오류 발생: {e}")

    def perform_update(self):
        """특정 태그의 최신 파일을 로컬로 업데이트합니다."""
        try:
            latest_version = self.get_latest_tag()

            if latest_version is None:
                print("[DEBUG] 최신 태그를 가져오지 못했습니다.")
                QMessageBox.critical(self, "업데이트 오류", "업데이트를 수행할 수 없습니다.")
                return

            # 최신 태그로 체크아웃
            subprocess.run(["git", "fetch", "--tags"], check=True)
            subprocess.run(["git", "checkout", f"tags/{latest_version}"], check=True)

            # 로컬 메타데이터 버전 정보 업데이트
            metadata = config_manager.load_metadata()
            metadata["version"] = latest_version
            config_manager.save_metadata(metadata)

            QMessageBox.information(self, "업데이트 완료", f"{latest_version} 버전으로 업데이트가 완료되었습니다.")
            print(f"[DEBUG] {latest_version} 버전으로 업데이트 완료.")

        except subprocess.CalledProcessError as e:
            print("[DEBUG] Error during perform_update (git fetch or checkout failed):")
            traceback.print_exc()
            QMessageBox.critical(self, "업데이트 오류", f"업데이트 중 오류 발생: {e}")
        except Exception as e:
            print("[DEBUG] Unexpected error in perform_update:")
            traceback.print_exc()
            QMessageBox.critical(self, "업데이트 오류", f"업데이트 중 예기치 않은 오류 발생: {e}")
