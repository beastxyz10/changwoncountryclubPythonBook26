from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem, QLabel,
                             QSpinBox, QMessageBox, QHeaderView, QFrame, QGroupBox,
                             QFormLayout, QLineEdit, QComboBox, QCheckBox,
                             QStatusBar, QScrollArea, QGridLayout, QDoubleSpinBox,
                             QDialog, QTextEdit)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor
from naver_data import NaverRealEstateData

class DetailDialog(QDialog):
    def __init__(self, article_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("매물 상세 정보")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # 상세 정보 표시
        detail_text = QTextEdit()
        detail_text.setReadOnly(True)
        
        # 매물 정보 포맷팅
        info = f"""
        [기본 정보]
        매물번호: {article_data.get('articleNo', '')}
        거래유형: {article_data.get('tradeTypeName', '')}
        가격: {article_data.get('dealOrWarrantPrc', '')}만원
        
        [면적 정보]
        면적: {article_data.get('area1', '')}㎡ ({float(article_data.get('area1', 0)) / 3.3:.1f}평)
        층: {article_data.get('floorInfo', '')}
        
        [등록 정보]
        등록일: {article_data.get('articleConfirmYmd', '')}
        수정일: {article_data.get('articleModifyYmd', '')}
        
        [추가 정보]
        방향: {article_data.get('direction', '')}
        관리비: {article_data.get('maintenanceFee', '')}만원
        주차: {article_data.get('parkingCount', '')}대
        """
        
        detail_text.setText(info)
        layout.addWidget(detail_text)
        
        # 닫기 버튼
        close_button = QPushButton("닫기")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("네이버 부동산 데이터 뷰어")
        self.setMinimumSize(1400, 900)
        
        # 스타일 설정
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 1em;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
                color: #333333;
                font-weight: bold;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 5px;
                gridline-color: #f0f0f0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 5px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
            }
            QStatusBar {
                background-color: #f5f5f5;
                color: #333333;
            }
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 10px;
                background-color: white;
            }
        """)
        
        # 데이터 관리자 초기화
        self.data_manager = NaverRealEstateData()
        
        # 메인 위젯 설정
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 검색 필터 영역
        filter_group = QGroupBox("검색 필터")
        filter_layout = QGridLayout()
        
        # 가격 범위
        price_group = QGroupBox("가격 범위")
        price_layout = QFormLayout()
        self.min_price = QLineEdit()
        self.max_price = QLineEdit()
        price_layout.addRow("최소 가격:", self.min_price)
        price_layout.addRow("최대 가격:", self.max_price)
        price_group.setLayout(price_layout)
        
        # 면적 범위
        area_group = QGroupBox("면적 범위")
        area_layout = QFormLayout()
        self.min_area = QDoubleSpinBox()
        self.max_area = QDoubleSpinBox()
        self.min_area.setRange(0, 1000)
        self.max_area.setRange(0, 1000)
        self.min_area.setSuffix(" ㎡")
        self.max_area.setSuffix(" ㎡")
        area_layout.addRow("최소 면적:", self.min_area)
        area_layout.addRow("최대 면적:", self.max_area)
        area_group.setLayout(area_layout)
        
        # 거래 유형
        trade_group = QGroupBox("거래 유형")
        trade_layout = QVBoxLayout()
        self.trade_types = {
            "매매": QCheckBox("매매"),
            "전세": QCheckBox("전세"),
            "월세": QCheckBox("월세")
        }
        for checkbox in self.trade_types.values():
            trade_layout.addWidget(checkbox)
        trade_group.setLayout(trade_layout)
        
        # 필터 레이아웃에 그룹 추가
        filter_layout.addWidget(price_group, 0, 0)
        filter_layout.addWidget(area_group, 0, 1)
        filter_layout.addWidget(trade_group, 0, 2)
        
        # 검색 버튼
        search_button = QPushButton("검색")
        search_button.clicked.connect(self.apply_filters)
        filter_layout.addWidget(search_button, 0, 3)
        
        filter_group.setLayout(filter_layout)
        
        # 컨트롤 영역
        control_layout = QHBoxLayout()
        
        # 페이지 선택
        page_layout = QHBoxLayout()
        page_label = QLabel("페이지:")
        self.page_spinbox = QSpinBox()
        self.page_spinbox.setMinimum(1)
        self.page_spinbox.setMaximum(100)
        self.page_spinbox.setValue(1)
        page_layout.addWidget(page_label)
        page_layout.addWidget(self.page_spinbox)
        
        # 버튼들
        self.fetch_button = QPushButton("데이터 가져오기")
        self.save_button = QPushButton("JSON 저장")
        self.load_button = QPushButton("JSON 불러오기")
        
        # 버튼 이벤트 연결
        self.fetch_button.clicked.connect(self.fetch_data)
        self.save_button.clicked.connect(self.save_data)
        self.load_button.clicked.connect(self.load_data)
        
        # 컨트롤 레이아웃에 위젯 추가
        control_layout.addLayout(page_layout)
        control_layout.addWidget(self.fetch_button)
        control_layout.addWidget(self.save_button)
        control_layout.addWidget(self.load_button)
        control_layout.addStretch()
        
        # 테이블 설정
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "매물번호", "가격", "면적(㎡)", "면적(평)", "층", "등록일", "거래유형"
        ])
        
        # 테이블 컬럼 너비 설정
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # 매물번호
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 가격
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # 면적(㎡)
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # 면적(평)
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # 층
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # 등록일
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # 거래유형
        
        # 테이블 더블클릭 이벤트 연결
        self.table.itemDoubleClicked.connect(self.show_detail)
        
        # 레이아웃에 위젯 추가
        layout.addWidget(filter_group)
        layout.addLayout(control_layout)
        layout.addWidget(self.table)
        
        # 상태 표시줄 추가
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("준비")
        
        # 초기 데이터 로드
        self.fetch_data()
    
    def show_detail(self, item):
        row = item.row()
        if hasattr(self, 'current_data'):
            articles = self.current_data.get('articleList', [])
            if 0 <= row < len(articles):
                article = articles[row]
                dialog = DetailDialog(article, self)
                dialog.exec()
    
    def apply_filters(self):
        # 필터 값 수집
        filters = {}
        
        # 가격 필터
        try:
            min_price = self.min_price.text().strip()
            if min_price:
                filters['min_price'] = int(min_price.replace(',', ''))
        except ValueError:
            pass
            
        try:
            max_price = self.max_price.text().strip()
            if max_price:
                filters['max_price'] = int(max_price.replace(',', ''))
        except ValueError:
            pass
        
        # 면적 필터
        filters['min_area'] = self.min_area.value()
        filters['max_area'] = self.max_area.value()
        
        # 거래 유형 필터
        selected_types = [trade_type for trade_type, checkbox in self.trade_types.items() 
                         if checkbox.isChecked()]
        if selected_types:
            filters['trade_types'] = selected_types
        
        # 필터 적용하여 데이터 가져오기
        page = self.page_spinbox.value()
        data = self.data_manager.fetch_data(page=page, filters=filters)
        if data:
            self.update_table(data)
            self.statusBar.showMessage(f"필터 적용 완료 - {len(data.get('articleList', []))}개 항목")
        else:
            QMessageBox.warning(self, "오류", "필터 적용 중 오류가 발생했습니다.")
            self.statusBar.showMessage("필터 적용 실패")
    
    def fetch_data(self):
        page = self.page_spinbox.value()
        data = self.data_manager.fetch_data(page=page)
        if data:
            self.update_table(data)
            self.statusBar.showMessage(f"데이터 로드 완료 - {len(data.get('articleList', []))}개 항목")
        else:
            QMessageBox.warning(self, "오류", "데이터를 가져오는데 실패했습니다.")
            self.statusBar.showMessage("데이터 로드 실패")
    
    def save_data(self):
        if hasattr(self, 'current_data'):
            if self.data_manager.save_to_json(self.current_data):
                QMessageBox.information(self, "성공", "데이터가 저장되었습니다.")
                self.statusBar.showMessage("데이터 저장 완료")
            else:
                QMessageBox.warning(self, "오류", "데이터 저장에 실패했습니다.")
                self.statusBar.showMessage("데이터 저장 실패")
        else:
            QMessageBox.warning(self, "오류", "저장할 데이터가 없습니다.")
    
    def load_data(self):
        data = self.data_manager.load_from_json()
        if data:
            self.current_data = data
            self.update_table(data)
            self.statusBar.showMessage(f"데이터 불러오기 완료 - {len(data.get('articleList', []))}개 항목")
        else:
            QMessageBox.warning(self, "오류", "저장된 데이터가 없습니다. 데이터를 먼저 가져와주세요.")
            self.statusBar.showMessage("데이터 불러오기 실패")
    
    def update_table(self, data):
        try:
            articles = data.get('articleList', [])
            self.table.setRowCount(len(articles))
            
            for row, article in enumerate(articles):
                # 매물번호
                self.table.setItem(row, 0, QTableWidgetItem(str(article.get('articleNo', ''))))
                
                # 가격
                price = article.get('dealOrWarrantPrc', '')
                if price:
                    try:
                        # 숫자형 가격 처리
                        price = int(price)
                        price = f"{price:,}만원"
                    except (ValueError, TypeError):
                        # 문자열 가격 처리 (예: "7억")
                        price = str(price)
                self.table.setItem(row, 1, QTableWidgetItem(price))
                
                # 면적(㎡)
                area = article.get('area1', '')
                if area:
                    try:
                        area_value = float(area)
                        area = f"{area_value:.1f}㎡"
                        # 면적(평) 계산 및 표시
                        pyeong = f"{area_value / 3.3:.1f}평"
                        self.table.setItem(row, 3, QTableWidgetItem(pyeong))
                    except (ValueError, TypeError):
                        area = str(area)
                        self.table.setItem(row, 3, QTableWidgetItem(""))
                self.table.setItem(row, 2, QTableWidgetItem(area))
                
                # 층
                floor = article.get('floorInfo', '')
                self.table.setItem(row, 4, QTableWidgetItem(str(floor)))
                
                # 등록일
                date = article.get('articleConfirmYmd', '')
                self.table.setItem(row, 5, QTableWidgetItem(str(date)))
                
                # 거래유형
                trade_type = article.get('tradeTypeName', '')
                self.table.setItem(row, 6, QTableWidgetItem(str(trade_type)))
            
            self.current_data = data
            
        except Exception as e:
            QMessageBox.warning(self, "오류", f"데이터 표시 중 오류가 발생했습니다: {str(e)}")
            self.statusBar.showMessage("데이터 표시 오류") 