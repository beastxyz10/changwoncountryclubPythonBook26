from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def connect_to_existing_chrome():
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    # 이미 실행 중인 Chrome에 연결
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def main():
    try:
        # 이미 실행 중인 Chrome에 연결
        driver = connect_to_existing_chrome()
        
        # 현재 페이지 제목 출력
        print(f"현재 페이지 제목: {driver.title}")
        
        # 예시: 현재 페이지에서 특정 요소 찾기
        # wait = WebDriverWait(driver, 10)
        # element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # 5초 대기
        time.sleep(5)
        
    except Exception as e:
        print(f"에러 발생: {str(e)}")
    finally:
        # 브라우저는 닫지 않음 (이미 실행 중인 브라우저이므로)
        pass

if __name__ == "__main__":
    main() 