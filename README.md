# 🚗 졸지마라 (Zolzimala)
> **비전 기반 운전자 졸음 감지 및 도로 환경 통합 안전 제어 시스템**  
> *Smart Vision & Safety Motion Control System*

[![Platform](https://img.shields.io/badge/Platform-Jetson%20Orin%20Nano%20%7C%20STM32F4-blue.svg)]()
[![Language](https://img.shields.io/badge/Language-Python%203%20%7C%20C%20(Bare--metal)-green.svg)]()
[![Protocol](https://img.shields.io/badge/Interface-UART%20(115200bps)%20%7C%20Ethernet-orange.svg)]()

---

## 📌 프로젝트 소개
졸지마라(Zolzimala)는 Jetson Orin Nano의 **듀얼 비전 AI 관제**와 STM32F4의 **하드웨어 액추에이터 제어**, 그리고 PC 원격 GUI를 결합한 임베디드 안전 주행 보조 시스템입니다.

운전자의 안면 상태(졸음/하품)와 전방 도로 환경(터널 진출입/차간거리)을 실시간으로 추적·인지하여, 위험 상황 감지 시 **경고 부저 울림, 에어컨/환기 팬 가동, 창문 자동 개폐, LED 알림** 등의 하드웨어 제어를 즉각 실행합니다.

---

## 🏗️ 시스템 아키텍처

```text
[ CAM 0 (안면/운전자) ] ──(USB)──┐
                                 ├──> [ Jetson Orin Nano (AI 추론) ] ──(Ethernet / X11)──> [ PC GUI (XLaunch) ]
[ CAM 1 (전방/도로)   ] ──(USB)──┘                 │
                                            (UART 115200bps)
                                                   ▼
                                      [ STM32F4 (액추에이터 제어) ]
                                                   │
                 ┌─────────────────────────────────┼─────────────────────────────────┐
                 ▼                                 ▼                                 ▼
           [ 경고 부저 ]                 [ 공기청정 / 에어컨 모터 ]              [ 창문 제어 서보모터 ]
```

---

## ✨ 핵심 기능 (Key Features)

* **운전자 모니터링 (CAM0)**
  * 안면 랜드마크 기반 EAR(Eye Aspect Ratio) 연산으로 실시간 졸음 감지
  * 입 벌림 거리(Mouth Distance) 기반 하품 감지 및 장시간 운전 피로도 인지
* **전방 환경 및 차량 감지 (CAM1)**
  * YOLO 기반 전방/옆 차선 차량 검출 및 Bounding Box 기반 차간거리 위험 레벨 산출
  * 조도 변화 및 터널 입구 인식을 통한 자동 진입/탈출 판정
* **하드웨어 인터랙션 (STM32F4)**
  * **졸음 경고:** 지속적인 비프음 경고 패턴 출력
  * **차내 환기:** 하품 감지 시 에어컨 모터 구동 (10초 작동 후 정지)
  * **창문 제어:** 터널 진입 시 창문 UP(닫기) 및 공기청정 모터 가동 / 탈출 시 창문 DOWN(열기)
  * **차선 접근 경고:** 좌/우/중앙 위험 방향에 따른 LED 알림 점멸
* **원격 관제 및 최적화**
  * X11 Forwarding을 통한 PC 원격 GUI 영상 렌더링
  * `State Latch Manager` 적용으로 상태 변경 시에만 단 1회 UART 패킷 전송 (대역폭 최적화)

---

## 🛠️ 기술 스택 (Tech Stack)

| 구분 | 기술 / 도구 | 상세 역할 |
| :--- | :--- | :--- |
| **Edge AI (Main)** | `Jetson Orin Nano`, `Linux (Ubuntu)` | 듀얼 카메라 파이프라인 관리 및 AI 연산 |
| **Vision & AI** | `Python 3`, `OpenCV`, `YOLOv8/v11`, `MediaPipe/Dlib` | 영상 처리, 객체 탐지, 랜드마크 추적 |
| **Embedded Control** | `STM32F4`, `Bare-metal C`, `CMSIS` | 링버퍼 UART 파싱, PWM 모터/부저 제어 |
| **Monitoring** | `XLaunch (X11 Forwarding)`, `TCP/IP` | 분산 영상 모니터링 GUI 렌더링 |
| **Communication** | `UART (115200 8N1)`, `USB 2.0/3.0` | Jetson ↔ STM32F4 시리얼 패킷 전송 |

---

## 📂 프로젝트 구조 (Directory Structure)

```text
zolzimala/
├── orin_nano/                     # Jetson Orin Nano 실행 소스 (Python)
│   ├── main.py                    # 시스템 메인 실행 스크립트
│   ├── cam0.py                    # 운전자 안면/졸음 감지 스레드
│   ├── cam1.py                    # 전방 도로/객체/터널 감지 스레드
│   ├── video.py                   # 카메라 입력 및 프레임 스트림 제어
│   ├── uart.py                    # STM32 시리얼 통신 및 패킷 송신 (State Latch)
│   └── gui.py                     # PC X11 Forwarding 렌더링 화면
│
└── stm32/                         # STM32F4 펌웨어 소스 (C)
    ├── main.c                     # 시스템 초기화 및 메인 루프
    ├── app_process.c              # 시스템 시나리오 FSM(유한상태머신)
    ├── protocol.c                 # UART 링버퍼 기반 패킷 수신 및 파싱
    ├── motor_app.c / motor.c / motor_hw.c         # 모터 드라이버 및 제어
    ├── buzzer_app.c / buzzer.c / buzzer_hw.c     # 경고 부저 드라이버 및 주파수 제어
    ├── window_servo_motor.c       # 창문 개폐 서보 제어
    ├── led.c                      # 방향별 경고 LED 토글 제어
    ├── clock.c / timer.c          # RCC 클럭 및 하드웨어 타이머(TIM1)
    └── uart.c / exception.c       # UART 통신 인터럽트 및 예외 처리
```

---

## 📡 통신 프로토콜 (UART Packet)

Jetson에서 위험 상태 변경 시 STM32F4로 전달되는 ASCII 패킷 명세입니다.

| 명령 패킷 (ASCII) | 이벤트 조건 | STM32F4 동작 |
| :--- | :--- | :--- |
| `DROWSY_WARN\n` | 운전자 졸음 감지 (EAR 임계치 미달 지속) | 경고 부저 지속 패턴 출력 |
| `DROWSY_OK\n` | 운전자 정상 상태 복귀 | 경고 부저 정지 |
| `VENT_ON\n` | 하품 감지 (Mouth Distance 임계치 초과) | 에어컨 모터 10초 가동 후 자동 정지 |
| `WIN_CLOSE\n` | 터널 진입 감지 | 창문 서보 닫힘 + 공기청정 모터 정방향 |
| `WIN_OPEN\n` | 터널 탈출 감지 | 창문 서보 열림 + 공기청정 모터 정지 |
| `WARN_CENTER\n` / `CENTER_OK\n` | 전방 앞차 근접 / 안전 거리 확보 | 중앙 경고 LED 토글 / 소등 |
| `WARN_LEFT\n` / `LEFT_OK\n` | 좌측 차선 차량 근접 / 안전 거리 확보 | 좌측 경고 LED 토글 / 소등 |
| `WARN_RIGHT\n` / `RIGHT_OK\n` | 우측 차선 차량 근접 / 안전 거리 확보 | 우측 경고 LED 토글 / 소등 |

---

## 🚀 시작 가이드 (Getting Started)

### 1. Prerequisites
* **Hardware:** Jetson Orin Nano, STM32F4 개발 보드, USB WebCam 2대, DC 모터, 서보 모터, 피에조 부저, LED
* **Software:** JetPack (Ubuntu), Python 3.8+, VS Code (Make 툴체인), PC Xming/XLaunch

### 2. Jetson Orin Nano 환경 설정 및 실행

<details>
<summary><b>📦 Python 검증 환경 (Tested Packages) 펼치기</b></summary>

```text
absl-py==2.4.0
cffi==2.0.0
cvzone==1.6.1
flatbuffers==25.12.19
jax==0.6.2
jaxlib==0.6.2
mediapipe==0.10.18
ml_dtypes==0.5.4
numpy==1.26.4
opencv-contrib-python==4.11.0.86
opt_einsum==3.4.0
platformdirs==4.9.6
protobuf==4.25.9
pycparser==3.0
pycuda==2026.1
pytools==2026.1
scipy==1.15.3
sentencepiece==0.2.1
siphash24==1.8
sounddevice==0.5.5
typing_extensions==4.15.0
pyserial==3.5
```
</details>

```bash
# 1) 저장소 클론 및 디렉터리 이동
git clone [https://github.com/your-username/zolzimala.git](https://github.com/your-username/zolzimala.git)
cd zolzimala/orin_nano

# 2) 파이썬 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 3) 패키지 설치 (위 검증 버전 목록 기준 설치)
pip install -r requirements.txt

# 4) X11 Forwarding 디스플레이 설정 (PC 호스트 IP 지정)
export DISPLAY=<YOUR_PC_IP>:0.0

# 5) 메인 프로그램 실행
python3 main.py
```

### 3. STM32F4 펌웨어 빌드 및 플래싱
1. `stm32/` 디렉터리로 이동합니다.
2. 핀 맵 및 클럭 설정(`clock.c`, 각 `*_hw.c`)을 연결된 하드웨어 핀아웃에 맞게 확인합니다.
3. 타깃 보드(STM32F4)를 PC/작업 환경에 연결한 뒤 터미널에서 빌드 및 플래싱을 수행합니다.
   ```bash
   cd zolzimala/stm32
   make
   make run
   ```
4. Jetson의 시리얼 포트(예: `/dev/ttyTHS1` 또는 USB 시리얼)와 STM32 UART 핀(TX/RX/GND)을 교차(Cross) 연결합니다.
