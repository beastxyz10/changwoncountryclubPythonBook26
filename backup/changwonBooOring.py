# 25년 3월 14일 1차분 완료
# booking.txt 파일에 날짜, 원하는 시간을 입력
# WAIT_TIME = "08:59:59" 에 시작 시간 입력
# 자동 실행 경고창 부분에서 오류가 발생
# 너무 빨리 로드가 되어서 완료가 되기도 전에 종료하고 넘어가 버리는 현상 발생



from playwright.sync_api import sync_playwright
from playwright_stealth.stealth import stealth_sync
import time
from datetime import datetime
import os
import re

# 예약 데이터 불러오기 (텍스트 파일)
BOOKING_FILE = "booking.txt"
TARGET_URL = "https://changwoncountryclub.co.kr/Reservation/Reservation.aspx"
WAIT_TIME = "08:59:59"  # 특정 시간 (이 시간이 되면 버튼을 클릭)
BUTTON_XPATH = "//*[@id='container']/div[2]/a[2]"

def load_booking_data():
    """텍스트 파일에서 예약할 날짜 및 시간을 가져오기"""
    if not os.path.exists(BOOKING_FILE):
        print(f"❌ {BOOKING_FILE} 파일이 존재하지 않습니다!")
        return None, None

    with open(BOOKING_FILE, "r", encoding="utf-8") as f:
        line = f.readline().strip()  # 첫 줄만 읽기

    if not line:
        print(f"❌ {BOOKING_FILE} 파일이 비어 있습니다!")
        return None, None

    data = line.split(",")
    target_date = data[0].strip()
    target_times = [time.strip() for time in data[1:]]

    return target_date, target_times

def wait_for_time(target_time):
    """특정 시간이 될 때까지 대기"""
    while True:
        now = datetime.now().strftime("%H:%M:%S")
        print(f"⏳ 현재 시간: {now} (목표 시간: {target_time})", end="\r")

        if now >= target_time:
            print(f"\n🚀 {target_time} 도달! 버튼 클릭 시작!")
            break

        time.sleep(0.5)  # 0.5초마다 체크 (정확성 향상)

def handle_alert(page):
    """경고창을 무조건 감지하고, 표시 후 닫기"""
    def on_dialog(dialog):
        print(f"⚠️ 경고창 발생: {dialog.message}")  # 경고창 메시지 표시
        dialog.accept()  # 경고창 확인 버튼 클릭
        print("✅ 경고창 확인 완료")
        time.sleep(0.2)  # 버튼 클릭 후 대기

    # 🔥 Playwright의 `on("dialog")` 이벤트를 사용하여 경고창 강제 감지
    page.on("dialog", on_dialog)

def wait_for_page_load(page):
    """페이지가 완전히 로드될 때까지 기다림"""
    try:
        page.wait_for_load_state("domcontentloaded", timeout=10000)  # DOM이 로드될 때까지 최대 10초 대기
        page.wait_for_load_state("networkidle", timeout=5000)  # 네트워크 요청이 끝날 때까지 최대 5초 대기
        print("✅ 페이지 로드 완료!")
    except Exception as e:
        print(f"⚠️ 페이지 로드 대기 중 오류 발생: {e}")

def click_button_until_site_opens(page):
    """특정 버튼을 계속 클릭하다가 목표 사이트(TARGET_URL)가 열리면 종료"""
    handle_alert(page)  # 🔥 경고창 감지 기능 활성화

    while True:

        current_url = ""
        current_url = page.url

        # 🔥 목표 사이트가 열려도 경고창이 떠 있으면 처리 후 진행
        if TARGET_URL in current_url:
            print(f"✅ 목표 사이트({TARGET_URL})가 열렸습니다! 경고창 여부 확인 중...")

            wait_for_page_load(page)

            # 🔥 경고창이 떠 있으면 닫고 다시 확인
            if handle_alert(page):
                print("🔄 경고창이 떠 있어서 닫고 다시 체크...")
                continue  # 다시 반복문 실행하여 경고창이 사라졌는지 확인

            print(f"🚀 경고창 없음, 예약 시작!")
            break  # 목표 사이트에 정상 도달했으면 종료

        try:
            print(f"🔄 버튼 클릭 시도: {BUTTON_XPATH}")
            page.locator(f"xpath={BUTTON_XPATH}").click()
            wait_for_page_load(page)
            time.sleep(0.2)  # 버튼 클릭 후 대기

        except Exception as e:
            print(f"⚠️ 버튼 클릭 실패: {e}")

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
    print(f"📄 클릭 전 페이지 소스 저장 완료: {filename}")

def find_and_click_reservation(page, target_date, target_times):
    """특정 날짜에서 '서', '동' 코스를 포함하여 지정된 시간 리스트 순서대로 클릭"""
    print(f"🚀 날짜: '{target_date}', 예약 가능 시간: {target_times} 찾는 중...")

    wait_for_page_load(page)

    # 🔥 날짜(td) 요소 찾기
    date_td_locator = page.locator(f"//td[contains(text(), '{target_date}')]")

    if date_td_locator.count() == 0:
        print(f"❌ '{target_date}' 날짜를 찾을 수 없습니다!")
        return False

    print(f"✅ '{target_date}' 날짜 찾음!")

    for date_td in date_td_locator.all():
        # 🔥 날짜(tr)와 그 다음(tr)을 포함하여 검색 (서, 동 코스 포함)
        tr_elements = [date_td.locator("xpath=./parent::tr"),
                       date_td.locator("xpath=./parent::tr/following-sibling::tr[1]")]

        for target_time in target_times:
            for tr in tr_elements:
                try:
                    time_locator = tr.locator(f"xpath=.//a[contains(text(), '{target_time}')]")

                    if time_locator.count() > 0:
                        href_value = time_locator.first.get_attribute("href")
                        if href_value and "예약중" in href_value:
                            print(f"⚠️ '{target_time}' 예약중! 다음 시간 확인 중...")
                            continue  # 다음 시간 탐색

                        print(f"🎯 '{target_time}' 시간 찾음! 버튼 클릭 시도...")
                        page_source_text = page.content()  # 🔥 클릭 전 HTML 저장
                        time_locator.first.click()
                        print(f"🟢 '{target_time}' 예약 버튼 클릭 완료!")
                        save_page_source(page_source_text)
                        return True  # ✅ 예약 성공하면 즉시 종료

                except Exception as e:
                    print(f"⚠️ 오류 발생: {e}")
                    continue

            print(f"❌ '{target_time}' 없음, 다음 시간 확인 중...")

    print(f"❌ '{target_date}'에서 예약 가능한 시간이 없습니다!")
    return False


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://changwoncountryclub.co.kr/main/Default.aspx")
        #page.goto(r"file:///C:/Users/beast/PycharmProjects/undetectedChrome/html/20250313_203450.html")
        stealth_sync(page)  # 탐지 방지 적용

        while True:  # 🔥 예약을 다시 시도할 수 있도록 루프
            target_date, target_times = load_booking_data()

            if not target_date or not target_times:
                print("❌ 예약 정보를 불러오지 못했습니다. 프로그램을 종료합니다.")
                break

            # 특정 시간이 될 때까지 대기
            wait_for_time(WAIT_TIME)

            #input("🔄 부킹시작 ? (아무키): ")
            # 특정 버튼을 계속 클릭하다가 목표 사이트가 열리면 종료
            click_button_until_site_opens(page)

            print(f"🚀 목표 사이트 로드 완료! 예약을 시작합니다.")

            # 기존 예약 로직 실행
            success = find_and_click_reservation(page, target_date, target_times)

            if success:
                print(f"🚀 예약 완료! '{target_date}'의 예약 버튼을 클릭했습니다.")

            retry = input("🔄 다시 부킹하시겠습니까? (y/n): ").strip().lower()
            if retry != 'y':
                print("🚪 프로그램을 종료합니다.")
                break  # 🔥 루프 종료

if __name__ == "__main__":
    main()
