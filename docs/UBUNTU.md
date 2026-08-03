# Ubuntu 설치 안내

Ubuntu는 Python 명령이 macOS와 비슷하지만 시리얼 포트 권한 설정이 추가로 필요합니다. 처음 수업 환경이라면 Ubuntu 22.04와 Python 3.10/3.11 조합을 권장합니다.

먼저 [설치 경로와 작업 폴더 기준](PATHS.md)의 Ubuntu 경로표를 확인하세요.
이 문서는 프로젝트를 `~/Projects/AI-Sensor-arduino`, Arduino Sketchbook을
`~/Documents/Arduino`로 고정합니다.

## 1. 기본 도구 설치

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip python3-tk
```

확인:

```bash
git --version
python3 --version
python3 -m tkinter
```

Python은 3.10 또는 3.11이어야 합니다. Ubuntu 24.04의 기본 Python 3.12를 사용하는 경우 TensorFlow 2.15.1 설치가 실패할 수 있으므로 Python 3.11 환경을 별도로 준비하세요.

## 2. Arduino IDE 2 설치

1. [Arduino IDE 공식 설치 안내](https://support.arduino.cc/hc/en-us/articles/360019833020-Download-and-install-Arduino-IDE)에서 Linux AppImage를 받습니다.
2. `~/Applications` 폴더를 만들고 AppImage를 `arduino-ide.AppImage`라는 고정 이름으로 옮깁니다.

```bash
mkdir -p ~/Applications
mkdir -p ~/Documents/Arduino/libraries
mv ~/Downloads/arduino-ide_*_Linux_64bit.AppImage ~/Applications/arduino-ide.AppImage
chmod +x ~/Applications/arduino-ide.AppImage
~/Applications/arduino-ide.AppImage
```

FUSE 관련 오류가 나면 공식 설치 안내의 Linux 문제 해결 절을 확인합니다.
Arduino IDE의 `File > Preferences > Sketchbook location`을
`~/Documents/Arduino`로 설정합니다.

## 3. 저장소 받기

```bash
mkdir -p ~/Projects
git clone https://github.com/yujin-in-ntu/AI-Sensor-arduino.git ~/Projects/AI-Sensor-arduino
cd ~/Projects/AI-Sensor-arduino
```

이미 복제했다면 `git clone`을 다시 실행하지 않습니다.

```bash
cd ~/Projects/AI-Sensor-arduino
git pull
```

경로를 확인합니다.

```bash
pwd
test -f README.md && test -f requirements.txt && echo "프로젝트 경로 정상"
```

## 4. Python 환경 만들기

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
```

확인:

```bash
./.venv/bin/python -c "import tensorflow, numpy, serial, tkinter; print('Python 패키지 준비 완료')"
```

## 5. 보드 패키지 설치

Arduino IDE에서:

1. `Boards Manager`를 엽니다.
2. `Arduino Mbed OS Nano Boards`를 설치합니다.
3. 보드 메뉴에서 `Arduino Nano 33 BLE`를 선택합니다.

## 6. Arduino 라이브러리 설치

Arduino IDE를 닫고 실행합니다.

```bash
mkdir -p ~/Documents/Arduino/libraries
cd ~/Documents/Arduino/libraries
git clone https://github.com/arduino-libraries/Arduino_OV767X.git Arduino_OV767X
git clone https://github.com/tensorflow/tflite-micro-arduino-examples.git Arduino_TensorFlowLite
```

라이브러리 경로와 Arduino IDE의 Sketchbook 위치가 모두 `~/Documents/Arduino`를
가리켜야 합니다. 프로젝트 저장소는 `~/Projects/AI-Sensor-arduino`에 별도로 둡니다.

## 7. 시리얼 포트 권한

보드를 연결하고 포트를 확인합니다.

```bash
ls /dev/ttyACM*
```

권한 오류가 나면 현재 사용자를 `dialout` 그룹에 추가합니다.

```bash
sudo usermod -a -G dialout "$USER"
```

그다음 반드시 로그아웃 후 다시 로그인하거나 컴퓨터를 재시작합니다. Arduino 공식 안내는 [Linux 포트 권한 해결](https://support.arduino.cc/hc/en-us/articles/360016495679-Fix-port-access-on-Linux)을 참고하세요.

업로드 중 부트로더 권한 오류가 계속되면 [Arduino udev 규칙 안내](https://support.arduino.cc/hc/en-us/articles/9005041052444-Fix-udev-rules-on-Linux)를 적용합니다.

## 8. 다음 단계

[공통 실습 문서](EXPERIMENT.md)의 `1단계: 카메라 확인`부터 진행하세요. 문서의 `<PORT>`에는 `/dev/ttyACM0` 같은 실제 포트를 넣습니다.
