# MySQL Database Manager

MySQL 데이터베이스를 관리하기 위한 GUI 프로그램입니다.

## 기능

- MySQL 서버 연결
- 데이터베이스 및 테이블 목록 표시
- 테이블 데이터 조회
- 열별 검색 기능
- 날짜 범위 필터링
- SQL 쿼리 직접 실행

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 프로그램 실행:
```bash
python main.py
```

## 사용 방법

1. 서버 연결
   - Host, Username, Password를 입력하고 "Connect" 버튼을 클릭합니다.
   - 연결이 성공하면 사용 가능한 데이터베이스 목록이 표시됩니다.

2. 데이터베이스 탐색
   - Database 드롭다운에서 데이터베이스를 선택합니다.
   - Table 드롭다운에서 테이블을 선택합니다.
   - 선택한 테이블의 데이터가 표시됩니다.

3. 데이터 필터링
   - Column 드롭다운에서 검색할 열을 선택합니다.
   - Search 입력창에 검색어를 입력합니다.
   - From과 To 날짜 선택기를 사용하여 날짜 범위를 지정할 수 있습니다.

4. SQL 쿼리 실행
   - "SQL Query" 탭으로 이동합니다.
   - 쿼리 입력창에 SQL 문을 입력합니다.
   - "Execute Query" 버튼을 클릭하여 쿼리를 실행합니다.
   - 결과가 테이블 형태로 표시됩니다.

## 요구사항

- Python 3.8 이상
- PyQt6
- mysql-connector-python
- pandas 