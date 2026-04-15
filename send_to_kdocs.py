import csv
import requests
import sys
import os

# 1. GitHub Actions 환경 변수에서 값 가져오기
TOKEN = os.environ.get("KDOCS_TOKEN")
FILE_ID = os.environ.get("KDOCS_FILE_ID")
CSV_FILE = "result.csv"  # BigQuery에서 추출된 CSV 파일명
SCRIPT_NAME = "ReceiveData"  # KDocs에 작성한 함수 이름

if not TOKEN or not FILE_ID:
    print("❌ 에러: 토큰이나 문서 ID가 설정되지 않았습니다.")
    sys.exit(1)

# 2. CSV 파일 읽기
data = []
try:
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
except Exception as e:
    print(f"❌ CSV 읽기 실패: {e}")
    sys.exit(1)

# 3. KDocs API 주소 조합 및 데이터 포장
API_URL = f"https://www.kdocs.cn/api/v3/ide/file/{FILE_ID}/script/{SCRIPT_NAME}/sync_task"

headers = {
    "Content-Type": "application/json",
    "AirScript-Token": TOKEN
}

# KDocs가 인식하는 Context.argv 형태로 포장
payload = {
    "Context": {
        "argv": {
            "rows": data
        }
    }
}

# 4. 전송
print(f"🚀 KDocs로 데이터 전송 시작... (총 {len(data)}행)")
try:
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    print(f"📡 상태 코드: {response.status_code}")
    print(f"📩 응답 내용: {response.text}")
    
    if response.status_code == 200:
        print("✅ KDocs 업데이트 성공!")
    else:
        print("⛔ KDocs 업데이트 실패!")
        sys.exit(1)
except Exception as e:
    print(f"❌ 통신 에러: {e}")
    sys.exit(1)