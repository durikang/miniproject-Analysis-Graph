from PyQt5.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton, QVBoxLayout, QHeaderView
import traceback

class TableManager:
    def __init__(self):
        self.income_table = QTableWidget()
        self.balance_table = QTableWidget()

    def setup_tables(self, layout, item_codes):
        self.setup_table(self.income_table, "손익계산서 항목 코드 설정", item_codes.get("INCOME_STATEMENT_ITEM_CODES", {}))
        self.setup_table(self.balance_table, "재무상태표 항목 코드 설정", item_codes.get("BALANCE_SHEET_ITEM_CODES", {}))

        # 테이블 자동 크기 조정
        self.income_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.balance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(QLabel("손익계산서 항목 코드 설정"))
        layout.addWidget(self.income_table)
        layout.addLayout(self.create_button_layout(self.income_table))

        layout.addWidget(QLabel("재무상태표 항목 코드 설정"))
        layout.addWidget(self.balance_table)
        layout.addLayout(self.create_button_layout(self.balance_table))

    def setup_table(self, table_widget, label_text, item_dict):
        table_widget.setColumnCount(2)
        table_widget.setHorizontalHeaderLabels(["코드", "항목 이름"])
        table_widget.setRowCount(0)
        for code, name in item_dict.items():
            row_position = table_widget.rowCount()
            table_widget.insertRow(row_position)
            table_widget.setItem(row_position, 0, QTableWidgetItem(code))
            table_widget.setItem(row_position, 1, QTableWidgetItem(name))

    def create_button_layout(self, table_widget):
        button_layout = QHBoxLayout()
        add_button = QPushButton("항목 추가")
        add_button.clicked.connect(lambda: self.add_table_row(table_widget))
        delete_button = QPushButton("선택 항목 삭제")
        delete_button.clicked.connect(lambda: self.delete_selected_row(table_widget))
        button_layout.addWidget(add_button)
        button_layout.addWidget(delete_button)
        return button_layout

    def add_table_row(self, table_widget):
        row_position = table_widget.rowCount()
        table_widget.insertRow(row_position)

    def delete_selected_row(self, table_widget):
        selected_rows = table_widget.selectionModel().selectedRows()
        for row in selected_rows:
            table_widget.removeRow(row.row())

    def extract_table_data(self, table_widget):
        data = {}
        for row in range(table_widget.rowCount()):
            try:
                code_item = table_widget.item(row, 0)
                name_item = table_widget.item(row, 1)
                if code_item and name_item:
                    code = code_item.text().strip()
                    name = name_item.text().strip()
                    if code:
                        data[code] = name
            except Exception as e:
                print(f"[DEBUG] Error extracting data from row {row}: {e}")
                print(traceback.format_exc())
        return data
