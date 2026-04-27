# 25년 3월 18일 2차분 완료
# config.ini 파일에 날짜, 원하는 시간을 입력
# 3-21일 부킹 성공 토요일
# 이걸로 사용을 한다

from playwright.sync_api import sync_playwright
from playwright_stealth.stealth import stealth_sync
import time
from datetime import datetime
import os
import re
import configparser
import subprocess
import logging

# 로깅 설정
def setup_logging():
    # 로그 디렉토리 생성
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # 로그 파일명 설정 (날짜 포함)
    log_file = os.path.join(log_dir, f"booking_{datetime.now().strftime('%Y%m%d')}.log")
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()  # 콘솔 출력도 유지
        ]
    )
    return logging.getLogger(__name__)

# 로거 초기화
logger = setup_logging()

# config.ini 수정기 실행
subprocess.Popen(["python", "configUI.py"], shell=True)

# 예약 데이터 불러오기 (텍스트 파일)

TARGET_URL = START_URL = start_url2 = WAIT_TIME = BUTTON_XPATH = REAL_BOOK = ""
target_date = target_time = asc_desc = book_course = ""


def load_data():
    global TARGET_URL, START_URL, start_url2, WAIT_TIME, BUTTON_XPATH, REAL_BOOK
    global target_date, target_time, asc_desc, book_course

    config = configparser.ConfigParser()
    config.read("config.ini")  # 설정 파일 경로 (파일과 같은 폴더에 있어야 함)

    # 변수 값 읽기
    TARGET_URL = config["settings"]["TARGET_URL"]
    START_URL = config["settings"]["START_URL"]
    WAIT_TIME = config["settings"]["WAIT_TIME"]
    BUTTON_XPATH = config["settings"]["BUTTON_XPATH"]
    REAL_BOOK = config["settings"]["REAL_BOOK"]
    target_date = config["settings"]["target_date"]
    target_time = config["settings"]["target_time"]
    asc_desc = config["settings"]["asc_desc"]
    book_course = config["settings"]["book_course"]
    start_url2= config["settings"]["start_url2"]

def wait_for_time(target_time):
    """특정 시간이 될 때까지 대기"""
    while True:
        now = datetime.now().strftime("%H:%M:%S")
        logger.info(f"⏳ 현재 시간: {now} (목표 시간: {target_time})")

        if now >= target_time:
            load_data()  #속도 저하 발생 가능성 , 시간과 날짜를 바꿀시 종료 시키지 않구 갈수 있는방법
            logger.info(f"🚀 {target_time} 도달! 버튼 클릭 시작!")
            break

        #time.sleep(0.2)  # 0.5초마다 체크 (정확성 향상)

def handle_alert(page):
    """경고창을 무조건 감지하고, 표시 후 닫기"""
    wait_for_page_load(page)

    def on_dialog(dialog):
        logger.warning(f"⚠️ 경고창 발생: {dialog.message}")  # 경고창 메시지 표시
        dialog.accept()  # 경고창 확인 버튼 클릭
        logger.info("✅ 경고창 확인 완료")

        #time.sleep(0.2)  # 버튼 클릭 후 대기

    # 🔥 Playwright의 `on("dialog")` 이벤트를 사용하여 경고창 강제 감지
    page.on("dialog", on_dialog)

def wait_for_page_load(page):
    """페이지가 완전히 로드될 때까지 기다림"""
    try:
        page.wait_for_load_state("domcontentloaded", timeout=10000)  # DOM이 로드될 때까지 최대 10초 대기
        page.wait_for_load_state("networkidle", timeout=5000)  # 네트워크 요청이 끝날 때까지 최대 5초 대기
        logger.info("✅ 페이지 로드 완료!")
    except Exception as e:
        logger.error(f"⚠️ 페이지 로드 대기 중 오류 발생: {e}")

def click_button_until_site_opens(page):
    """특정 버튼을 계속 클릭하다가 목표 사이트(TARGET_URL)가 열리면 종료"""
    handle_alert(page)  # 🔥 경고창 감지 기능 활성화

    while True:

        current_url = ""
        current_url = page.url

        # 🔥 목표 사이트가 열려도 경고창이 떠 있으면 처리 후 진행
        if TARGET_URL in current_url:
            logger.info(f"✅ 목표 사이트({TARGET_URL})가 열렸습니다! 경고창 여부 확인 중...")

            wait_for_page_load(page)

            # 🔥 경고창이 떠 있으면 닫고 다시 확인
            if handle_alert(page):
                logger.info("🔄 경고창이 떠 있어서 닫고 다시 체크...")
                continue  # 다시 반복문 실행하여 경고창이 사라졌는지 확인

            logger.info("🚀 경고창 없음, 예약 시작!")
            break  # 목표 사이트에 정상 도달했으면 종료

        try:
            logger.info(f"🔄 버튼 클릭 시도: {BUTTON_XPATH}")
            page.locator(f"xpath={BUTTON_XPATH}").click()
            wait_for_page_load(page)
            #time.sleep(0.2)  # 버튼 클릭 후 대기

        except Exception as e:
            logger.error(f"⚠️ 버튼 클릭 실패: {e}")

        #time.sleep(0.1)  # 클릭 반복 간격 (0.1초)

def save_page_source(html_content):
    """변수에 저장된 HTML을 현재 날짜/시간으로 된 파일명으로 저장"""
    # 🔥 저장할 디렉토리 경로 설정
    save_dir = "html"
    os.makedirs(save_dir, exist_ok=True)  # 디렉토리 없으면 생성

    # 🔥 현재 날짜 및 시간으로 파일명 설정
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(save_dir, f"{timestamp}.html")

    # 🔥 HTML 파일로 저장
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info(f"📄 페이지 소스 저장 완료: {filename}")

def find_and_click_reservation(page, target_date, target_times):
    """특정 날짜에서 '서', '동' 코스를 포함하여 지정된 시간 리스트 순서대로 클릭"""
    wait_for_page_load(page)

    # target_time을 하나씩 시도
    target_time_list = target_times.split(",")
    for t_time in target_time_list:
        logger.info(f"🚀 날짜: '{target_date}', 예약 가능 시간: {t_time} 찾는 중...")
        if book_course == "00":
            pattern = re.compile(
                rf"javascript:goResvTime\('{target_date}', '{t_time}(\d{{2}})', '(11|22)', '(\d+)', '(\d+)', '(\d+)'\)"
            )
        else:
            pattern = re.compile(
                rf"javascript:goResvTime\('{target_date}', '{t_time}(\d{{2}})', '({book_course})', '(\d+)', '(\d+)', '(\d+)'\)"
            )

        # 검색 실행
        matches = pattern.findall(page.content())

        # matches가 있으면 즉시 반복문 종료
        if matches:
            target_time = t_time  # 성공한 target_time을 변수로 저장
            break

    # matches 값 확인 후 처리
    if matches:
        if asc_desc == 'fast':
            first_item_group = sorted(matches, key=lambda x: (x[1], int(x[0])))
        else:
            first_item_group = sorted(matches, key=lambda x: (x[1] != '11', -int(x[0])))

        # 첫 번째 값 선택 (오름차순 기준)
        first_item = first_item_group[0]

        # HTML 생성
        html = f"javascript:goResvTime('{target_date}', '{target_time}{first_item[0]}', '{first_item[1]}', '{first_item[2]}', '{first_item[3]}', '{first_item[4]}')"
        page_source_text = page.content()

        # 예약 시도 및 경고창 처리
        def handle_booking_alert(dialog):
            if "다른 사람이 예약을 하였읍니다" in dialog.message:
                logger.warning("⚠️ 다른 사람이 이미 예약했습니다. 다른 시간을 시도합니다.")
                dialog.accept()
                return True
            return False

        # 경고창 이벤트 리스너 설정
        page.on("dialog", handle_booking_alert)

        # 예약 시도
        page.evaluate(html)
        logger.info(f"예약 시도: {html}")
        save_page_source(page_source_text)

        # 경고창이 발생했는지 확인
        if handle_booking_alert:
            logger.info("🔄 다른 시간을 시도합니다...")
            # 현재 시간을 제외하고 다시 시도
            remaining_times = [t for t in target_time_list if t != target_time]
            if remaining_times:
                return find_and_click_reservation(page, target_date, ",".join(remaining_times))
            else:
                logger.error("❌ 모든 가능한 시간이 예약되었습니다.")
                return False

        logger.info(f"\n✅ [{target_date} {asc_desc} 첫 번째 HTML]")
        return True

    logger.error(f"❌ '{target_date}'에서 예약 가능한 시간이 없습니다!")
    return False


def main():
    logger.info("예약 프로그램 시작")
    with sync_playwright() as p:
        load_data()

        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        if REAL_BOOK == 'yes':
            page.goto(START_URL)
        else:
            page.goto(start_url2)
        stealth_sync(page)

        while True:
            if REAL_BOOK=='yes':
                wait_for_time(WAIT_TIME)
                click_button_until_site_opens(page)
            else:
                input("🔄 부킹시작 ? (아무키): ")

            logger.info("🚀 목표 사이트 로드 완료! 예약을 시작합니다.")

            # 예약 시도 및 자동 재시도
            max_retries = 3
            retry_count = 0
            success = False

            while retry_count < max_retries and not success:
                success = find_and_click_reservation(page, target_date, target_time)
                if not success:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.info(f"🔄 예약 재시도 중... ({retry_count}/{max_retries})")
                        # 대기시간 제거 - 빠른 재시도를 위해

            if success:
                logger.info(f"🚀 예약 완료! '{target_date}'의 예약 버튼을 클릭했습니다.")
            else:
                logger.error("❌ 최대 재시도 횟수를 초과했습니다.")

            retry = input("🔄 다시 부킹하시겠습니까? (y/n): ").strip().lower()
            if retry != 'y':
                logger.info("🚪 프로그램을 종료합니다.")
                break
            load_data()

if __name__ == "__main__":
    main()
