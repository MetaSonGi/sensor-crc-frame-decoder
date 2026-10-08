# CRC 검증·분할 수신 대응 센서 패킷 해석기

바이트 스트림에서 센서 프레임을 찾고 CRC 및 순서를 검증합니다.

- 분야: 하드웨어
- 요구 사항: Python 3.10 이상, 외부 패키지와 API 키 불필요
- 샘플: `frames.hex` (합성 데이터 또는 공개 논문 메타데이터)

## 실행

저장소 루트에서 실행합니다.

```bash
python main.py --chunk-size 3
```

## 동작과 입출력

AA55 + 길이 1바이트 + payload 9바이트 + CRC 2바이트. payload는 big-endian B I h h(장비 ID·순서·섭씨×100·암페어×1000)입니다. CRC는 길이와 payload에 적용합니다.

## 설계 판단

AI 출력을 곧바로 장비 동작으로 연결하기 전에 입력 품질, 상태 버전, 모델 적용 범위를 검증해야 한다는 개발자 관점을 적용했습니다. [논문·설계 분석](TRENDS.md)은 공개 원문 자료와 구현자의 해석을 분리합니다.

## 검증

```bash
python -m unittest discover -s . -p test_main.py -v
```

[이 저장소 검증 기록](VALIDATION.txt)과 이 폴더의 `example-output` 파일을 확인하세요. 테스트는 해당 프로그램의 실제 동작·경계 조건을 포함합니다.

## 한계

자체 데모 프로토콜입니다. Modbus·OPC UA·STM 펌웨어 또는 실물 보드 검증이 아닙니다. CRC는 전송 오류 검출이며 인증·암호화 기능은 없습니다. 순서 번호 wrap-around는 지원하지 않습니다.
