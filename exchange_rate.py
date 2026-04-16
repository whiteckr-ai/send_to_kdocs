import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import urllib3
import json

# SSL 인증서 경고 숨기기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_customs_rate():
    # 💡 발급받으신 인증키를 여기에 다시 입력해 주세요
    api_key = "k250k246v024z146n060b070c0"
    today = datetime.now().strftime('%Y%m%d')
    url = "https://unipass.customs.go.kr:38010/ext/rest/trifFxrtInfoQry/retrieveTrifFxrtInfo"
    
    params = {
        'crkyCn': api_key,
        'qryYymmDd': today,
        'imexTp': '2' # 수입
    }
    
    try:
        response = requests.get(url, params=params, verify=False, timeout=15)
        response.encoding = 'utf-8'
        root = ET.fromstring(response.content)
        
        # XML에서 위안화(CNY) 환율만 추출
        for item in root.findall('.//trifFxrtInfoQryRsltVo'):
            curr = item.find('currSgn')
            if curr is not None and curr.text == 'CNY':
                return item.find('fxrt').text
                
        print("❌ 위안화 환율 데이터를 찾을 수 없습니다.")
        return None
        
    except Exception as e:
        print(f"❌ 관세청 API 호출 에러: {e}")
        return None

def send_to_kdocs(rate):
    if not rate:
        return
        
    # 대표님이 제공해주신 KDocs 웹훅 URL
    webhook_url = "https://www.kdocs.cn/api/v3/ide/file/cicR4yEidFqj/script/V2-pgD1PCjAOrmRh8WkVvZx8/sync_task"
    
    # KDocs로 보낼 데이터 구조 (JSON)
    payload = {
        "Context": {
            "argv": {
                "cny_rate": rate
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "AirScript-Token": "1Vg353OyhzW3n27xfSZKUh" # 💡 이 줄이 반드시 추가되어야 합니다.
        
    }
    
    try:
        response = requests.post(webhook_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ KDocs 웹훅 전송 성공! 반영된 환율: {rate}원")
        else:
            print(f"❌ KDocs 전송 실패: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ KDocs 연동 에러 발생: {e}")

if __name__ == "__main__":
    print("🔄 관세청 고시환율 조회를 시작합니다...")
    cny_rate = get_customs_rate()
    
    if cny_rate:
        print(f"수신된 환율: {cny_rate} -> KDocs로 전송합니다.")
        send_to_kdocs(cny_rate)
