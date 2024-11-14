import glob
import platform
import subprocess
import os
import sys
import traceback
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from config import config_manager
from utils.logger import log_debug_message  # logger 모듈을 임포트

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
        log_debug_message(f"로드된 로컬 버전: {self.local_version}")

    def load_local_version(self):
        """로컬 메타 데이터에서 버전 정보를 불러옵니다."""
        try:
            metadata = config_manager.load_metadata()
            version = metadata.get("version", "버전 정보 없음")
            self.current_version_label.setText(f"현재 버전: {version}")
            return version
        except Exception as e:
            log_debug_message(f"Error loading local version: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "오류", f"현재 버전을 불러오는 중 오류 발생: {e}")
            return None

    def get_latest_tag(self):
        """원격 저장소에서 최신 태그를 가져옵니다."""
        try:
            project_dir = os.getcwd()
            fetch_result = subprocess.run(
                ["git", "fetch", "--tags"], cwd=project_dir, check=True, capture_output=True, text=True
            )
            log_debug_message(f"git fetch --tags 결과: {fetch_result.stdout}")

            rev_list_result = subprocess.run(
                ["git", "rev-list", "--tags", "--max-count=1"],
                cwd=project_dir, capture_output=True, text=True
            )
            latest_commit_id = rev_list_result.stdout.strip()
            log_debug_message(f"최신 커밋 ID: {latest_commit_id}")

            if not latest_commit_id:
                raise ValueError("태그가 없습니다. 저장소에 태그를 추가하세요.")

            describe_result = subprocess.run(
                ["git", "describe", "--tags", latest_commit_id],
                cwd=project_dir, capture_output=True, text=True
            )
            latest_tag = describe_result.stdout.strip()
            log_debug_message(f"로드된 최신 태그: {latest_tag}")
            self.latest_version_label.setText(f"최신 버전: {latest_tag}")
            return latest_tag

        except subprocess.CalledProcessError as e:
            log_debug_message(f"Error fetching latest tag: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "오류", "원격 최신 버전 확인 실패")
            return None
        except ValueError as e:
            QMessageBox.critical(self, "오류", str(e))
            return None
        except Exception as e:
            log_debug_message(f"Unexpected error in get_latest_tag: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "오류", f"태그를 가져오는 도중 오류 발생: {e}")
            return None

    def check_for_updates(self):
        """로컬 버전과 원격 버전을 비교하여 업데이트 필요 여부를 확인합니다."""
        try:
            latest_version = self.get_latest_tag()
            log_debug_message(f"체크 중인 최신 원격 버전: {latest_version}")
            if self.local_version and latest_version:
                if self.local_version != latest_version:
                    self.update_button.setEnabled(True)
                    QMessageBox.information(self, "업데이트 필요", f"새 버전 {latest_version}이 있습니다.")
                else:
                    QMessageBox.information(self, "최신 상태", "프로그램이 최신 상태입니다.")
            else:
                log_debug_message("Error in check_for_updates: 로컬 또는 원격 버전 정보를 확인할 수 없습니다.")
        except Exception as e:
            log_debug_message(f"Error checking for updates: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "오류", f"업데이트 상태를 확인하는 중 오류 발생: {e}")

    def perform_update(self):
        try:
            latest_version = self.get_latest_tag()
            if latest_version is None:
                log_debug_message("최신 태그를 가져오지 못했습니다.")
                QMessageBox.critical(self, "업데이트 오류", "업데이트를 수행할 수 없습니다.")
                return

            subprocess.run(["git", "fetch", "--tags"], check=True)
            subprocess.run(["git", "checkout", f"tags/{latest_version}"], check=True)

            # 빌드 실행
            if platform.system() == "Windows" and getattr(sys, 'frozen', False):
                # 빌드된 .exe 환경에서 실행 시
                build_result = subprocess.run(["pyinstaller", "--onefile", "main.py"], stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE, text=True)
                log_debug_message(f"빌드 결과: {build_result.stdout}")

                if build_result.returncode != 0:
                    log_debug_message(f"빌드 실패: {build_result.stderr}")
                    QMessageBox.critical(self, "업데이트 오류", "업데이트 중 빌드에 실패했습니다.")
                    return
            else:
                log_debug_message("개발 환경에서 실행 중: 빌드 프로세스를 건너뜁니다.")

            # dist 폴더 내 exe 파일 검색
            dist_path = os.path.join(os.path.abspath("dist"), "main")  # dist/main 폴더 지정
            exe_files = glob.glob(os.path.join(dist_path, "*.exe"))  # main 폴더 내 exe 파일 검색

            if exe_files:
                target_exe = exe_files[0]
                current_exe_path = os.path.abspath(sys.argv[0])
                os.replace(target_exe, current_exe_path)
                log_debug_message(f"{current_exe_path}가 성공적으로 업데이트되었습니다.")
            else:
                raise FileNotFoundError(f"{dist_path} 폴더 내에 exe 파일이 존재하지 않습니다.")

            metadata = config_manager.load_metadata()
            metadata["version"] = latest_version
            config_manager.save_metadata(metadata)

            QMessageBox.information(self, "업데이트 완료", f"{latest_version} 버전으로 업데이트가 완료되었습니다.")
            log_debug_message(f"{latest_version} 버전으로 업데이트 완료.")

            python = sys.executable
            subprocess.Popen([python, *sys.argv])
            sys.exit()

        except subprocess.CalledProcessError as e:
            log_debug_message(f"Error during perform_update (git fetch or checkout failed): {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "업데이트 오류", f"업데이트 중 오류 발생: {e}")
        except FileNotFoundError as e:
            log_debug_message(f"Update failed due to missing file: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "업데이트 오류", f"파일을 찾을 수 없습니다: {e}")
        except Exception as e:
            log_debug_message(f"Unexpected error in perform_update: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "업데이트 오류", f"업데이트 중 예기치 않은 오류 발생: {e}")