import sys
import mysql.connector
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QTableWidget, QTableWidgetItem, QComboBox, 
                           QMessageBox, QTextEdit, QDateEdit, QTabWidget)
from PyQt6.QtCore import Qt, QDate
import pandas as pd

class MySQLManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.connection = None
        self.current_database = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('MySQL Database Manager')
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Connection settings
        conn_group = QWidget()
        conn_layout = QHBoxLayout(conn_group)
        
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText('Host')
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText('Username')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        conn_btn = QPushButton('Connect')
        conn_btn.clicked.connect(self.connect_to_database)
        
        conn_layout.addWidget(QLabel('Host:'))
        conn_layout.addWidget(self.host_input)
        conn_layout.addWidget(QLabel('Username:'))
        conn_layout.addWidget(self.user_input)
        conn_layout.addWidget(QLabel('Password:'))
        conn_layout.addWidget(self.password_input)
        conn_layout.addWidget(conn_btn)
        
        layout.addWidget(conn_group)

        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Database browser tab
        self.db_browser_tab = QWidget()
        self.setup_database_browser()
        self.tab_widget.addTab(self.db_browser_tab, "Database Browser")

        # SQL Query tab
        self.sql_query_tab = QWidget()
        self.setup_sql_query()
        self.tab_widget.addTab(self.sql_query_tab, "SQL Query")

    def setup_database_browser(self):
        layout = QVBoxLayout(self.db_browser_tab)
        
        # Database and table selection
        selection_layout = QHBoxLayout()
        
        self.db_combo = QComboBox()
        self.db_combo.currentTextChanged.connect(self.load_tables)
        selection_layout.addWidget(QLabel('Database:'))
        selection_layout.addWidget(self.db_combo)
        
        self.table_combo = QComboBox()
        self.table_combo.currentTextChanged.connect(self.load_table_data)
        selection_layout.addWidget(QLabel('Table:'))
        selection_layout.addWidget(self.table_combo)
        
        layout.addLayout(selection_layout)

        # Search filters
        filter_layout = QHBoxLayout()
        self.column_combo = QComboBox()
        self.column_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel('Column:'))
        filter_layout.addWidget(self.column_combo)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Search...')
        self.search_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_input)
        
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.dateChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel('From:'))
        filter_layout.addWidget(self.date_from)
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.dateChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel('To:'))
        filter_layout.addWidget(self.date_to)
        
        layout.addLayout(filter_layout)

        # Data table
        self.data_table = QTableWidget()
        layout.addWidget(self.data_table)

    def setup_sql_query(self):
        layout = QVBoxLayout(self.sql_query_tab)
        
        # SQL query input
        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText('Enter SQL query...')
        layout.addWidget(self.query_input)
        
        # Execute button
        execute_btn = QPushButton('Execute Query')
        execute_btn.clicked.connect(self.execute_sql_query)
        layout.addWidget(execute_btn)
        
        # Results table
        self.query_result_table = QTableWidget()
        layout.addWidget(self.query_result_table)

    def connect_to_database(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host_input.text(),
                user=self.user_input.text(),
                password=self.password_input.text()
            )
            self.load_databases()
            QMessageBox.information(self, 'Success', 'Connected to MySQL server successfully!')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to connect: {str(e)}')

    def load_databases(self):
        if not self.connection:
            return
        
        cursor = self.connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        
        self.db_combo.clear()
        self.db_combo.addItems(databases)

    def load_tables(self, database):
        if not self.connection or not database:
            return
        
        self.current_database = database
        cursor = self.connection.cursor()
        cursor.execute(f"USE {database}")
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        self.table_combo.clear()
        self.table_combo.addItems(tables)

    def load_table_data(self, table):
        if not self.connection or not table:
            return
        
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        
        # Update column combo
        self.column_combo.clear()
        self.column_combo.addItems(columns)
        
        # Update data table
        self.data_table.setRowCount(len(data))
        self.data_table.setColumnCount(len(columns))
        self.data_table.setHorizontalHeaderLabels(columns)
        
        for i, row in enumerate(data):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.data_table.setItem(i, j, item)
        
        self.data_table.resizeColumnsToContents()

    def apply_filters(self):
        if not self.connection or not self.table_combo.currentText():
            return
        
        table = self.table_combo.currentText()
        column = self.column_combo.currentText()
        search_text = self.search_input.text()
        date_from = self.date_from.date().toString('yyyy-MM-dd')
        date_to = self.date_to.date().toString('yyyy-MM-dd')
        
        query = f"SELECT * FROM {table} WHERE 1=1"
        params = []
        
        if search_text:
            query += f" AND {column} LIKE %s"
            params.append(f"%{search_text}%")
        
        if date_from and date_to:
            query += f" AND {column} BETWEEN %s AND %s"
            params.extend([date_from, date_to])
        
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        data = cursor.fetchall()
        
        self.update_data_table(data)

    def execute_sql_query(self):
        if not self.connection:
            return
        
        query = self.query_input.toPlainText()
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            
            if data:
                columns = [desc[0] for desc in cursor.description]
                self.query_result_table.setRowCount(len(data))
                self.query_result_table.setColumnCount(len(columns))
                self.query_result_table.setHorizontalHeaderLabels(columns)
                
                for i, row in enumerate(data):
                    for j, value in enumerate(row):
                        item = QTableWidgetItem(str(value))
                        self.query_result_table.setItem(i, j, item)
                
                self.query_result_table.resizeColumnsToContents()
            else:
                QMessageBox.information(self, 'Success', 'Query executed successfully, no results to display.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Query execution failed: {str(e)}')

    def update_data_table(self, data):
        if not data:
            return
        
        self.data_table.setRowCount(len(data))
        self.data_table.setColumnCount(len(data[0]))
        
        for i, row in enumerate(data):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.data_table.setItem(i, j, item)
        
        self.data_table.resizeColumnsToContents()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MySQLManager()
    ex.show()
    sys.exit(app.exec()) 