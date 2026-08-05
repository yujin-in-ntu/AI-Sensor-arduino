# macOS 설치 안내

이 문서는 Intel Mac과 Apple Silicon Mac에서 Terminal, Arduino IDE 2를 사용하는 방법을 설명합니다.

먼저 [설치 경로와 작업 폴더 기준](PATHS.md)의 macOS 경로표를 확인하세요.
이 문서는 프로젝트를 `~/Projects/AI-Sensor-arduino`, Arduino Sketchbook을
`~/Documents/Arduino`로 고정합니다.

## 1. Git 준비

Terminal을 열고 확인합니다.

```bash
git --version
```

설치 안내 창이 나타나면 Apple Command Line Tools를 설치합니다.

```bash
xcode-select --install
```

설치 후 Terminal을 다시 열고 `git --version`을 확인합니다.

## 2. Python 3.11 설치

[Python 공식 다운로드](https://www.python.org/downloads/)에서 macOS용 Python 3.11 설치 파일을 받는 방법을 권장합니다.

확인:

```bash
python3.11 --version
```

결과는 `Python 3.11.x`여야 합니다. 수업에서는 Python 3.11.9와 TensorFlow 2.15.1 조합으로 통일합니다.

Tkinter 확인:

```bash
python3 -m tkinter
```

작은 테스트 창이 열리면 정상입니다. 창을 닫습니다. Tkinter가 없다는 오류가 나면 python.org 설치본을 사용하거나, Homebrew Python을 사용 중이라면 해당 Python 버전의 Tk 패키지를 설치합니다.

## 3. Arduino IDE 2 설치

1. [Arduino IDE 공식 설치 안내](https://support.arduino.cc/hc/en-us/articles/360019833020-Download-and-install-Arduino-IDE)에서 자신의 Mac에 맞는 버전을 받습니다.
2. Apple Silicon은 ARM64, Intel Mac은 Intel 버전을 선택합니다.
3. Arduino IDE를 Applications 폴더로 옮겨 `/Applications/Arduino IDE.app`에 설치하고 실행합니다.
4. macOS가 실행 여부를 묻는다면 `Open`을 선택합니다.
5. Terminal에서 Sketchbook과 라이브러리 폴더를 만듭니다.

```bash
mkdir -p ~/Documents/Arduino/libraries
```

6. `Arduino IDE > Settings`에서 Sketchbook 위치를 `~/Documents/Arduino`로 설정합니다.

## 4. 저장소 받기

```bash
mkdir -p ~/Projects
git clone https://github.com/yujin-in-ntu/AI-Sensor-arduino.git ~/Projects/AI-Sensor-arduino
cd ~/Projects/AI-Sensor-arduino
```

이미 복제했다면:

```bash
cd ~/Projects/AI-Sensor-arduino
git pull
```

경로를 확인합니다.

```bash
pwd
test -f README.md && test -f requirements.txt && echo "프로젝트 경로 정상"
```

## 5. Python 환경 만들기

저장소 최상위 폴더에서 실행합니다.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

확인:

```bash
python -c "import tensorflow as tf, numpy, serial, tkinter; print('TensorFlow:', tf.__version__)"
```

결과가 반드시 `TensorFlow: 2.15.1`이어야 합니다. `2.21.0`처럼 다른 버전이면
`python -m pip install --force-reinstall -r requirements.txt`를 실행하고 다시
확인합니다. 다른 버전으로 만든 `model_data.h`는 Arduino의 TensorFlow Lite
Micro와 호환되지 않을 수 있습니다.

이후 명령은 가상환경이 활성화된 상태에서 `python`으로 실행합니다. 새 터미널을
열었다면 프로젝트 폴더에서 `source .venv/bin/activate`를 다시 실행하세요.

## 6. Arduino 보드 패키지 설치

1. Arduino IDE 2의 `Boards Manager`를 엽니다.
2. `Arduino Mbed OS Nano Boards`를 검색해 설치합니다.
3. 보드를 USB로 연결합니다.
4. 보드 선택 메뉴에서 `Arduino Nano 33 BLE`와 `/dev/cu.usbmodem...` 포트를 선택합니다.

## 7. Arduino 라이브러리 설치

Arduino IDE를 닫고 Terminal에서 실행합니다.

```bash
mkdir -p ~/Documents/Arduino/libraries
cd ~/Documents/Arduino/libraries
git clone https://github.com/arduino-libraries/Arduino_OV767X.git Arduino_OV767X
git clone https://github.com/tensorflow/tflite-micro-arduino-examples.git Arduino_TensorFlowLite
```

이미 폴더가 있다면 업데이트합니다.

```bash
git -C ~/Documents/Arduino/libraries/Arduino_OV767X pull
git -C ~/Documents/Arduino/libraries/Arduino_TensorFlowLite pull
```

Sketchbook 위치를 바꿨다면 `~/Documents/Arduino` 대신 실제 위치를 사용합니다. 설치 후 Arduino IDE를 다시 시작합니다.

Arduino 라이브러리 폴더에서 프로젝트 루트로 돌아옵니다. 이후 Python 명령은 항상
이 위치에서 실행합니다.

```bash
cd ~/Projects/AI-Sensor-arduino
test -f README.md && echo "프로젝트 경로 정상"
```

## 8. 포트 확인

```bash
ls /dev/cu.usbmodem*
```

예시:

```text
/dev/cu.usbmodem1101
```

문서의 `<PORT>` 자리에 이 전체 경로를 사용합니다.

## 9. 다음 단계

[공통 실습 문서](EXPERIMENT.md)의 `1단계: 카메라 확인`부터 진행하세요.
