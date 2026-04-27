import re

# 예제 HTML 파일 경로
file_path = r"C:\Users\beast\PycharmProjects\undetectedChrome\html\20250318_090003.html"
target_date = "20250401"
target_time = "08"  # '06'을 변수로 저장
asc_desc="slow"
book_course="22"  #00 모두 11 서 22 동

# 파일 읽기
with open(file_path, "r", encoding="utf-8") as file:
    html_text = file.read()

# 정규식 패턴
if book_course=="00":
    pattern = re.compile(
        rf"javascript:goResvTime\('{target_date}', '{target_time}(\d{{2}})', '(11|22)', '(\d+)', '(\d+)', '(\d+)'\)"
    )
else:
    pattern = re.compile(
        rf"javascript:goResvTime\('{target_date}', '{target_time}(\d{{2}})', '({book_course})', '(\d+)', '(\d+)', '(\d+)'\)"
    )


# 검색 실행
matches = pattern.findall(html_text)

# matches 값 확인 후 처리
if matches:
    print("✅ [검색된 값 목록]")
    print(matches)

    if asc_desc == 'fast' :
        # 1. 두 번째 요소(그룹 '11', '22')로 정렬 후, 첫 번째 요소(시간 '37', '44'...)로 정렬 (오름차순)
        first_item_group = sorted(matches, key=lambda x: (x[1], int(x[0])))
    else:
        # 2. 두 번째 요소(그룹 '11', '22')로 정렬 후, 첫 번째 요소(시간 '37', '44'...)로 정렬 (내림차순)
          first_item_group = sorted(matches, key=lambda x: (x[1] != '11', -int(x[0])))

    # 첫 번째 값 선택 (오름차순 기준)
    first_item = first_item_group[0]

    # HTML 생성
    html = f"javascript:goResvTime('{target_date}', '{target_time}{first_item[0]}', '{first_item[1]}', '{first_item[2]}', '{first_item[3]}', '{first_item[4]}')"

    # 결과 출력
    print(f"\n✅ [{target_date} {asc_desc} 첫 번째 HTML]")
    print(html)
    print(first_item_group)

#<a href="javascript:goResvTime('20250401', '0801', '11', '1', '00015', '18')" class="reservBtn">08:01</a>
#<a href="javascript:goResvTime('20250401', '0801', '11', '1', '00015', '18')" class="reservBtn">08:01</a>
#<a href="javascript:goResvTime('20250401', '0829', '11', '1', '00019', '18')" class="reservBtn">08:29</a>
#<a href="javascript:goResvTime('20250401', '0829', '11', '1', '00019', '18')" class="reservBtn">08:29</a>
#<a href="javascript:goResvTime('20250401', '0843', '22', '1', '00065', '18')" class="reservBtn">08:43</a>
#<a href="javascript:goResvTime('20250401', '0843', '22', '1', '00065', '18')" class="reservBtn">08:43</a>
else:
    print("❌ 값이 없습니다.")
