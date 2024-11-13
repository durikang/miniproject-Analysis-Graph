# path_settings.py

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog

class PathSettings:
    def __init__(self, config_data):
        self.income_data_path = QLineEdit(config_data.get("income_data_path", ""))
        self.balance_data_path = QLineEdit(config_data.get("balance_data_path", ""))
        self.income_result_path = QLineEdit(config_data.get("income_result_path", ""))
        self.balance_result_path = QLineEdit(config_data.get("balance_result_path", ""))
        self.png_save_path = QLineEdit(config_data.get("png_save_path", ""))  # png 경로 추가

    def add_path_settings(self, layout):
        layout.addWidget(QLabel("손익계산서 데이터 경로"))
        income_path_button = QPushButton("경로 선택")
        income_path_button.clicked.connect(self.select_income_data_path)
        income_layout = QHBoxLayout()
        income_layout.addWidget(self.income_data_path)
        income_layout.addWidget(income_path_button)
        layout.addLayout(income_layout)

        layout.addWidget(QLabel("재무상태표 데이터 경로"))
        balance_path_button = QPushButton("경로 선택")
        balance_path_button.clicked.connect(self.select_balance_data_path)
        balance_layout = QHBoxLayout()
        balance_layout.addWidget(self.balance_data_path)
        balance_layout.addWidget(balance_path_button)
        layout.addLayout(balance_layout)

    def add_png_path_setting(self, layout):
        layout.addWidget(QLabel("그래프 저장 png 경로"))
        png_path_button = QPushButton("경로 선택")
        png_path_button.clicked.connect(self.select_png_save_path)
        png_layout = QHBoxLayout()
        png_layout.addWidget(self.png_save_path)
        png_layout.addWidget(png_path_button)
        layout.addLayout(png_layout)

    def select_png_save_path(self):
        path = QFileDialog.getExistingDirectory(None, "PNG 그래프 저장 경로 선택")
        if path:
            self.png_save_path.setText(path)

    def add_result_path_settings(self, layout):
        layout.addWidget(QLabel("손익계산서 그래프 저장 경로"))
        income_result_button = QPushButton("경로 선택")
        income_result_button.clicked.connect(self.select_income_result_path)
        income_result_layout = QHBoxLayout()
        income_result_layout.addWidget(self.income_result_path)
        income_result_layout.addWidget(income_result_button)
        layout.addLayout(income_result_layout)

        layout.addWidget(QLabel("재무상태표 그래프 저장 경로"))
        balance_result_button = QPushButton("경로 선택")
        balance_result_button.clicked.connect(self.select_balance_result_path)
        balance_result_layout = QHBoxLayout()
        balance_result_layout.addWidget(self.balance_result_path)
        balance_result_layout.addWidget(balance_result_button)
        layout.addLayout(balance_result_layout)

    def select_income_data_path(self):
        path = QFileDialog.getExistingDirectory(None, "손익계산서 데이터 경로 선택")
        if path:
            self.income_data_path.setText(path)

    def select_balance_data_path(self):
        path = QFileDialog.getExistingDirectory(None, "재무상태표 데이터 경로 선택")
        if path:
            self.balance_data_path.setText(path)

    def select_income_result_path(self):
        path = QFileDialog.getExistingDirectory(None, "손익계산서 그래프 저장 경로 선택")
        if path:
            self.income_result_path.setText(path)

    def select_balance_result_path(self):
        path = QFileDialog.getExistingDirectory(None, "재무상태표 그래프 저장 경로 선택")
        if path:
            self.balance_result_path.setText(path)

    def get_paths(self):
        return {
            "income_data_path": self.income_data_path.text(),
            "balance_data_path": self.balance_data_path.text(),
            "income_result_path": self.income_result_path.text(),
            "balance_result_path": self.balance_result_path.text(),
            "png_save_path": self.png_save_path.text()  # png 경로 추가
        }
