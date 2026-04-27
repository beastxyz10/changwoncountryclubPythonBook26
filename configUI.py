import sys
import configparser
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox

# 설정 파일 로드 함수
def load_config():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config

# 설정 파일 저장 함수
def save_config(config):
    with open("config.ini", "w") as configfile:
        config.write(configfile)

# UI 클래스
class ConfigEditor(QWidget):
    def __init__(self):
        super().__init__()

        # 설정 파일 로드
        self.config = load_config()

        # UI 요소 생성
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # UI에 표시할 설정 항목들
        self.fields = {}

        # UI에 표시할 설정 항목들 (설명 추가)
        settings = {
            "REAL_BOOK": "REAL_BOOK (실제 예약 여부, yes/no)",
            "target_date": "target_date (예약 날짜 YYYYMMDD)",
            "target_time": "target_time (예약 시간, 두개 가능: 08,12)",
            "asc_desc": "asc_desc (전반시간 fast / 후반시간 slow)",
            "book_course": "book_course (예약 코스: 00=서후동, 11=서, 22=동)",
            "WAIT_TIME": "WAIT_TIME (자동부킹 돌아갈 시간, HHMMSS)",

            "START_URL": "START_URL (시작 페이지)",
            "start_url2": "start_url2 (테스트 부킹 하기 위한 로칼페이지)",
            "TARGET_URL": "TARGET_URL (부킹될 페이지)",
            "BUTTON_XPATH": "BUTTON_XPATH (클릭할 버튼의 XPath)"
        }

        for key, description in settings.items():
            label = QLabel(description)  # 주석 포함된 설명 표시
            edit = QLineEdit(self.config["settings"].get(key, ""))
            self.fields[key] = edit  # 입력 필드를 저장
            layout.addWidget(label)
            layout.addWidget(edit)

        # 저장 버튼
        save_button = QPushButton("저장")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        # UI 설정
        self.setLayout(layout)
        self.setWindowTitle("창원cc config.ini 수정기")
        self.setGeometry(300, 300, 400, 400)

    # 설정 저장 함수 (다이얼로그 추가)
    def save_settings(self):
        for key, edit in self.fields.items():
            self.config["settings"][key] = edit.text()

        save_config(self.config)  # 설정 저장

        # 다이얼로그 창 표시
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)  # 정보 아이콘
        msg.setWindowTitle("저장 완료")  # 창 제목
        msg.setText("✅ 설정이 성공적으로 저장되었습니다.")  # 메시지 내용
        msg.setStandardButtons(QMessageBox.Ok)  # 확인 버튼 추가
        msg.exec_()  # 다이얼로그 실행

# 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = ConfigEditor()
    editor.show()
    sys.exit(app.exec_())
