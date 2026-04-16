import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import urllib3

# SSL 인증서 경고 숨기기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_customs_rate_unipass():
    # 1. 발급받으신 유니패스 인증키 입력
    api_key = "k250k246v024z146n060b070c0"
    
    # 2. 오늘 날짜 (YYYYMMDD 형식)
    today = datetime.now().strftime('%Y%m%d')
    
    # 3. 가이드에 명시된 정확한 URL 및 포트(38010) 
    url = "https://unipass.customs.go.kr:38010/ext/rest/trifFxrtInfoQry/retrieveTrifFxrtInfo"
    
    # 4. 가이드에 명시된 파라미터 규격 [cite: 916, 921]
    params = {
        'crkyCn': api_key,
        'qryYymmDd': today,
        'imexTp': '2'  # 2: 수입, 1: 수출 
    }
    
    try:
        # 포트 38010 통신 및 관세청 사설 인증서 충돌 방지를 위해 verify=False 유지
        response = requests.get(url, params=params, verify=False, timeout=15)
        response.encoding = 'utf-8'
        
        # XML 파싱
        root = ET.fromstring(response.content)
        
        # 5. 응답 결과 확인 (tCnt가 -1 이면 에러) [cite: 1348]
        tcnt = root.find('.//tCnt')
        if tcnt is not None and tcnt.text == '-1':
            error_msg = root.find('.//ntceInfo').text
            print(f"❌ API 호출 에러: {error_msg}")
            return

        # 6. 가이드에 명시된 응답 태그(<trifFxrtInfoQryRsltVo>) 파싱 [cite: 921]
        for item in root.findall('.//trifFxrtInfoQryRsltVo'):
            curr = item.find('currSgn')
            
            # 통화코드가 CNY(위안화)인 경우 값 추출 [cite: 918]
            if curr is not None and curr.text == 'CNY':
                rate = item.find('fxrt').text
                print(f"✅ 테스트 성공! 오늘의 위안화(CNY) 수입 고시환율: {rate}원")
                return
                
        print("❌ 위안화 환율 데이터를 찾을 수 없습니다. (응답은 성공함)")
        
    except Exception as e:
        print(f"❌ 시스템 에러 발생: {e}")

test_customs_rate_unipass()
