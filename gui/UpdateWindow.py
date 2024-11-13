from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
import requests
import subprocess
import traceback  # traceback 모듈 추가
import os

class UpdateWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("업데이트 확인")
        self.setGeometry(200, 200, 400, 200)

        # 레이아웃 설정
        layout = QVBoxLayout()

        # 현재 버전과 최신 버전 정보를 표시할 라벨
        self.current_version_label = QLabel("현재 버전: 확인 중...")
        self.latest_version_label = QLabel("최신 버전: 확인 중...")

        # 업데이트 버튼
        self.update_button = QPushButton("업데이트")
        self.update_button.setEnabled(False)  # 초기 상태에서는 비활성화
        self.update_button.clicked.connect(self.perform_update)

        # 레이아웃에 위젯 추가
        layout.addWidget(self.current_version_label)
        layout.addWidget(self.latest_version_label)
        layout.addWidget(self.update_button)

        self.setLayout(layout)

        # 업데이트 상태 확인
        self.check_for_updates()

    def get_latest_commit(self, repo_url):
        """원격 저장소의 최신 커밋 해시 가져오기"""
        # 기본 브랜치를 main에서 master로 변경
        api_url = f"https://api.github.com/repos/{repo_url}/commits/master"
        try:
            response = requests.get(api_url)
            response.raise_for_status()  # 응답 상태 코드가 200이 아닌 경우 예외 발생
            return response.json()["sha"]
        except requests.exceptions.RequestException as e:
            error_message = f"최신 버전 확인 중 오류 발생:\n{traceback.format_exc()}"
            QMessageBox.critical(self, "오류", f"GitHub API 요청 실패: {error_message}")
        return None

    def get_local_commit(self):
        """로컬 저장소의 현재 커밋 해시 가져오기"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                cwd="C:\\Users\\CAD09\\Desktop\\projectMini"
            )
            if result.returncode != 0:  # Git 명령어 실패 시
                raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            error_message = f"로컬 Git 명령어 실행 중 오류 발생:\n{traceback.format_exc()}\n\nError output:\n{e.stderr}"
            QMessageBox.critical(self, "오류", error_message)
        except Exception as e:
            error_message = f"현재 버전 확인 중 오류 발생:\n{traceback.format_exc()}"
            QMessageBox.critical(self, "오류", error_message)
        return None

    def check_for_updates(self):
        """로컬 및 원격 커밋을 비교하여 업데이트 필요 여부 확인"""
        repo_url = "durikang/miniproject-Analysis-Graph"
        latest_commit = self.get_latest_commit(repo_url)
        local_commit = self.get_local_commit()

        if latest_commit and local_commit:
            self.current_version_label.setText(f"현재 버전: {local_commit}")
            self.latest_version_label.setText(f"최신 버전: {latest_commit}")

            if local_commit != latest_commit:
                self.update_button.setEnabled(True)  # 업데이트가 가능하면 버튼 활성화
                QMessageBox.information(self, "업데이트 가능", "새 버전이 있습니다.")
            else:
                QMessageBox.information(self, "최신 상태", "프로그램이 최신 상태입니다.")
        else:
            QMessageBox.critical(self, "오류", "업데이트 상태를 확인할 수 없습니다.")

    def perform_update(self):
        """업데이트를 수행하는 메서드"""
        try:
            project_dir = os.getcwd()  # 현재 작업 디렉터리
            result = subprocess.run(["git", "pull"], capture_output=True, text=True, cwd=project_dir)
            QMessageBox.information(self, "업데이트 완료", "업데이트가 완료되었습니다.\n프로그램을 다시 시작해 주세요.")
            self.update_button.setEnabled(False)  # 업데이트 완료 후 버튼 비활성화
            print(result.stdout)
        except Exception as e:
            error_message = f"업데이트 중 오류가 발생했습니다:\n{traceback.format_exc()}"
            QMessageBox.critical(self, "업데이트 오류", error_message)