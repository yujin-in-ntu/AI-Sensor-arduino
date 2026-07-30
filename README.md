# Nano 33 BLE Sense Lite 손글씨 숫자 TinyML

Arduino Tiny Machine Learning Kit의 OV7675 카메라로 종이에 쓴 숫자를 촬영하고, 직접 만든 데이터 또는 MNIST로 작은 CNN을 학습한 뒤, Nano 33 BLE Sense Lite에서 추론하는 입문 프로젝트입니다.

이 저장소의 기본 실습 범위는 숫자 `0, 1, 2, 3`입니다. 명령의 `--digits` 값을 바꾸면 `0~9`로 확장할 수 있습니다.

## 이 프로젝트에서 해보는 것

1. OV7675 카메라가 정상 동작하는지 확인합니다.
2. 160×120 전체 화면을 보면서 숫자를 촬영합니다.
3. 종이와 숫자를 자동으로 찾아 28×28 AI 입력으로 만듭니다.
4. 직접 촬영한 숫자로 CNN을 학습합니다.
5. 모델을 INT8 TensorFlow Lite 형식으로 변환합니다.
6. 모델을 Arduino 헤더로 바꾸고 보드에 업로드합니다.
7. PC GUI에서 원본·AI 입력·예측 확률을 함께 확인합니다.
8. MNIST 모델과 직접 촬영 모델의 차이를 비교합니다.

## 필요한 하드웨어

- Arduino Nano 33 BLE Sense Lite
- Arduino Tiny Machine Learning Shield
- OV7675 카메라 모듈
- 데이터 통신이 가능한 USB-A ↔ Micro-USB 케이블
- 흰 종이 또는 줄이 옅은 공책
- 검은색 펜

충전 전용 USB 케이블은 전원만 공급하고 포트가 나타나지 않을 수 있습니다.

## 운영체제별 설치 안내

자신의 운영체제 문서를 먼저 끝까지 진행하세요.

- [Windows 설치](docs/WINDOWS.md)
- [macOS 설치](docs/MACOS.md)
- [Ubuntu 설치](docs/UBUNTU.md)
- [Arduino CLI로 컴파일·업로드](docs/ARDUINO_CLI.md) — 선택 사항

설치가 끝났다면 모든 운영체제에서 공통으로 사용하는 실습 문서로 이동합니다.

- [01 → 02 → 03 전체 실습](docs/EXPERIMENT.md)
- [0단계: Python·NumPy 문법 한 줄 빈칸](docs/PYTHON_NUMPY_START.md)
- [Softmax·역전파·추론 코드를 직접 채우는 AI 실습](docs/AI_CODE_LAB.md)
- [오류 해결 모음](docs/TROUBLESHOOTING.md)

## 세 개의 Arduino 단계

학생이 열어야 하는 Arduino 스케치는 세 개뿐입니다.

```text
arduino/
├─ camera_01_check/
│  └─ camera_01_check.ino       카메라 연결과 문자 미리보기 확인
├─ camera_02_collect/
│  └─ camera_02_collect.ino     160×120 Full View 미리보기·데이터 수집
└─ camera_03_inference/
   ├─ camera_03_inference.ino   보드에서 CNN 추론
   └─ model_data_placeholder.h  아직 모델이 없을 때 사용하는 자리표시자
```

`camera_02_collect`가 우리가 사용한 Full View 방식입니다. 과거의 28×28 전용 수집 스케치는 제거했습니다.

## 현재 사용하는 Python 파일

```text
python/
├─ camera_preprocess.py       종이·숫자 탐지와 28×28 전처리
├─ preview_camera.py          160×120 원본 미리보기 GUI
├─ collect_camera_data.py     Full View 데이터 수집 GUI
├─ train_camera_model.py      직접 촬영 데이터 CNN 학습
├─ train_mnist_model.py       MNIST 다운로드·학습
├─ run_inference_gui.py       Arduino 추론 결과 GUI
├─ rebuild_camera_digits.py   저장된 원본의 28×28 재생성 도구
└─ learning/
   ├─ python_numpy_basics_exercise.py  완전 초보자용 문법 빈칸
   ├─ check_python_numpy_basics.py     문법 빈칸 자동 확인
   ├─ python_numpy_basics_answer.py    문법 실습 정답
   ├─ nn_from_scratch_exercise.py  ReLU·Softmax·역전파 빈칸 실습
   ├─ check_nn_exercise.py         TODO 1~8 자동 확인
   ├─ nn_from_scratch_answer.py    실습 정답 코드
   └─ nn_data.py                   MNIST·카메라 데이터 읽기
```

CNN을 실행하는 것에서 한 단계 더 나아가 학습 원리를 코드로 이해하려면
[신경망 코딩 실습](docs/AI_CODE_LAB.md)을 진행하세요. TensorFlow는 MNIST를
내려받는 데만 사용하고, 순전파·Softmax·교차엔트로피·역전파·SGD·추론을
NumPy 코드로 직접 완성합니다.

## 전체 흐름 한눈에 보기

```text
01 카메라 확인
    ↓
02 Full View 업로드
    ↓
PC에서 원본 확인 → 숫자별 20장 수집
    ↓
직접 촬영 모델 학습 → model_data.h 생성
    ↓
03 추론 업로드 → PC GUI로 실제 숫자 인식
    ↓
MNIST 모델 학습 → 03 다시 업로드 → 결과 비교
```

실제 촬영 데이터의 가중치 학습은 `python/train_camera_model.py`의
`model.fit()`에서 수행됩니다. `camera_03_inference.ino`는 학습된 모델로 보드에서
추론하고, `run_inference_gui.py`는 보드에 명령을 보내 결과를 화면에 표시합니다.
`python/learning/`은 이 실제 파이프라인에 자동 연결되지 않는 원리 학습용 코드입니다.

## 가장 중요한 사용 규칙

- Python 프로그램을 실행하기 전에 Arduino IDE의 **시리얼 모니터와 시리얼 플로터를 모두 닫습니다.** 한 포트는 한 프로그램만 열 수 있습니다.
- `02`를 업로드한 상태에서는 미리보기와 데이터 수집을 실행합니다.
- 모델을 학습하면 `arduino/camera_03_inference/model_data.h`가 새로 생성됩니다.
- 모델이 바뀔 때마다 `03`을 다시 컴파일하고 업로드해야 합니다.
- 빨간 상자는 종이, 초록 상자는 감지된 숫자입니다.
- 오른쪽 28×28 화면에서 사람 눈에도 숫자가 보여야 모델의 예측을 신뢰할 수 있습니다.
- 데이터는 촬영 버튼을 눌러 저장할 때마다 즉시 디스크에 기록됩니다. 프로그램 종료나 USB 분리로 이미 저장된 사진이 사라지지 않습니다.

## 데이터와 모델 저장 위치

```text
data/camera_full/<숫자>/       160×120 원본 PGM
data/camera_digits/<숫자>/     전처리된 28×28 PGM
models/camera/                 직접 촬영 모델
models/mnist/                  MNIST 모델
arduino/camera_03_inference/model_data.h
                               다음 업로드에 포함될 현재 모델
```

개인의 촬영 데이터, 학습 모델, 생성된 `model_data.h`는 Git에 올리지 않도록 `.gitignore`에 등록되어 있습니다. 저장소를 새로 복제한 학생은 직접 데이터를 모으거나 MNIST를 학습해 자신의 헤더를 생성합니다.

## 전처리 방식

1. 160×120 회색조 화면에서 가장 큰 밝은 종이 영역을 찾습니다.
2. 검은 책상, 종이 가장자리, 길게 이어진 공책 줄을 제외합니다.
3. 실제 검은 숫자 획의 범위를 찾습니다.
4. 숫자를 28×28 검은 배경 중앙에 밝은 획으로 놓습니다.
5. 카메라에서 지나치게 가늘게 보이는 곡선 숫자는 선택적으로 폭을 보정합니다.
6. Python 수집 화면과 Arduino 추론 코드가 같은 규칙을 사용합니다.

MNIST 검증 정확도가 높더라도 실제 카메라에서는 조명, 종이, 펜, 초점이 다르므로 성능이 낮아질 수 있습니다. 이 차이를 관찰하는 것도 실습 목표입니다.

## 검증된 환경

- Arduino IDE 2
- Arduino Mbed OS Nano Boards
- 보드 FQBN: `arduino:mbed_nano:nano33ble`
- Python 3.10 또는 3.11
- TensorFlow 2.15.1
- NumPy 1.26.4
- pyserial 3.5
- OV7675: QQVGA 160×120, GRAYSCALE
- 기본 클래스: 0, 1, 2, 3

## 공식 참고 자료

- [Arduino IDE 2 다운로드 및 설치](https://support.arduino.cc/hc/en-us/articles/360019833020-Download-and-install-Arduino-IDE)
- [Arduino IDE에서 보드 패키지 추가](https://support.arduino.cc/hc/en-us/articles/360016119519-Add-boards-to-Arduino-IDE)
- [Arduino 스케치 업로드](https://support.arduino.cc/hc/en-us/articles/4733418441116-Upload-a-sketch-in-Arduino-IDE)
- [Arduino_OV767X 공식 저장소](https://github.com/arduino-libraries/Arduino_OV767X)
- [TensorFlow Lite Micro Arduino 예제 저장소](https://github.com/tensorflow/tflite-micro-arduino-examples)
- [Python 가상환경 공식 문서](https://docs.python.org/3/library/venv.html)
- [Linux 포트 권한 해결](https://support.arduino.cc/hc/en-us/articles/360016495679-Fix-port-access-on-Linux)
