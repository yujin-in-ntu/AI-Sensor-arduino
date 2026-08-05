# Nano 33 BLE Sense Lite 손글씨 숫자 TinyML

Arduino Tiny Machine Learning Kit의 OV7675 카메라로 종이에 쓴 숫자를 촬영하고, 직접 만든 데이터 또는 MNIST로 작은 CNN을 학습한 뒤, Nano 33 BLE Sense Lite에서 추론하는 입문 프로젝트입니다.

> **Python 설치가 관리자 권한 때문에 막히나요?**
>
> 기본 순서와 섞지 말고 [관리자 권한 없이 Python 3.11 환경 만들기](docs/NO_ADMIN_PYTHON.md)를 먼저 완료하세요.

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

## 이 README만 따라 진행합니다

Windows와 macOS 모두 아래의 **0단계부터 10단계까지 이 README만 위에서 아래로**
따라 하면 됩니다. 다음 문서는 추가 설명이 필요할 때만 보는 선택 자료입니다.

- [Windows 설치](docs/WINDOWS.md)
- [macOS 설치](docs/MACOS.md)
- [관리자 권한 없이 Python 3.11 환경 만들기](docs/NO_ADMIN_PYTHON.md)
- [프로그램·프로젝트·Arduino 라이브러리 정확한 경로](docs/PATHS.md)
- [Arduino CLI로 컴파일·업로드](docs/ARDUINO_CLI.md) — 선택 사항

- [기본: 직접 촬영하는 01 → 02 → 03 전체 실습](docs/EXPERIMENT.md)
- [대체: 촬영이 어려울 때 공개 예제 데이터로 학습](docs/EXAMPLE_DATA.md)
- [실제 CNN 코드에 필요한 Python·NumPy 문법](docs/PYTHON_NUMPY_START.md)
- [카메라 CNN 학습 코드 읽기·Arduino 추론 실습](docs/AI_CODE_LAB.md)
- [오류 해결 모음](docs/TROUBLESHOOTING.md)

## 중요: TensorFlow 2.15.1 사용

Windows와 macOS 모두 이 프로젝트의 모델 학습에는 **TensorFlow 2.15.1**을
사용합니다. `requirements.txt`에도 `tensorflow==2.15.1`로 고정되어 있습니다.
TensorFlow 2.21.0 등 다른 버전으로 모델을 만들면 Arduino에서 `SHAPE` 연산 오류가
날 수 있습니다. 학습하기 전에 반드시 2단계의 버전 확인 결과가 `2.15.1`인지
확인하세요.

## 처음부터 끝까지 README 하나로 따라 하기

0 ~ 2단계에서 프로그램과 프로젝트를 준비하고, 3~9단계에서 학생이 자기 손글씨를
직접 촬영·학습·추론합니다. 촬영이 불가능한 학생만 마지막 10단계의 GitHub 예제
데이터를 사용합니다. 처음 실습할 때는 이 순서대로 위에서 아래로 진행하세요.

명령은 저장소 최상위 폴더의 터미널에서 **한 줄씩 입력하고 Enter**를 누릅니다.
앞 명령이 끝난 뒤 다음 명령을 실행하세요. 명령 앞의 `PS C:\...>` 같은 터미널
표시는 입력하지 않습니다.

### 0단계: Git, Python 3.11.9, Arduino IDE 2 설치

이미 세 프로그램이 모두 설치되어 있다면 버전만 확인하고 1단계로 이동합니다.
수업용 PC를 처음 준비한다면 아래 순서대로 설치하세요.

#### 0-0. 먼저 폴더 역할을 분리합니다

GitHub 프로젝트와 Arduino 라이브러리를 같은 폴더에 넣지 않습니다. 이 문서의
권장 경로는 다음과 같습니다.

| 용도 | Windows | macOS |
|---|---|---|
| GitHub 프로젝트 | `C:\Users\<사용자이름>\Projects\AI-Sensor-arduino` | `~/Projects/AI-Sensor-arduino` |
| 프로젝트 가상환경 | `...\AI-Sensor-arduino\.venv` | `.../AI-Sensor-arduino/.venv` |
| Arduino Sketchbook | `C:\Users\<사용자이름>\Documents\Arduino` | `~/Documents/Arduino` |
| Arduino 라이브러리 | `...\Documents\Arduino\libraries` | `~/Documents/Arduino/libraries` |

Python 명령을 실행할 때 터미널의 현재 위치는 항상 GitHub 프로젝트 행의 경로여야
합니다. 현재 경로가 `Documents/Arduino/libraries`로 끝나면 Python 명령을 실행하지
말고 프로젝트 루트로 돌아오세요. `.venv`를 만든 뒤에는 프로젝트 폴더의 이름이나
위치를 바꾸지 않습니다. 옮겼다면 이전 `.venv`를 재사용하지 말고 새 위치에서 다시
만들어야 합니다.

Arduino IDE와 Python 본체는 운영체제의 프로그램 영역에 설치하고, 촬영 데이터와
모델은 GitHub 프로젝트 안에 둡니다. 경로 문제가 생겼을 때만 선택 자료인
[설치 경로와 작업 폴더 기준](docs/PATHS.md)을 참고합니다.

#### 0-1. Git 확인 및 설치

Windows PowerShell에서 확인합니다.

```powershell
git --version
```

`git version ...`이 나오면 설치되어 있습니다. `git`을 찾을 수 없다는 오류가
나오면 [Git for Windows](https://git-scm.com/download/win)를 설치한 뒤 열려 있던
PowerShell을 모두 닫고 새 PowerShell을 엽니다.

macOS Terminal에서는 다음 명령으로 확인합니다.

```bash
git --version
```

처음 실행할 때 Command Line Tools 설치 창이 나오면 설치합니다. 아무 창도 나오지
않고 `git`을 찾지 못하면 `xcode-select --install`을 실행하고 설치가 끝난 뒤 새
Terminal을 엽니다.

#### 0-2. Python 3.11 확인 및 설치

이 프로젝트는 `TensorFlow 2.15.1`을 사용하므로 **Python 3.11.x 64비트**를
사용합니다. Python 3.14가 이미 설치되어 있어도 삭제할 필요가 없습니다.

Windows PowerShell에서 설치된 버전을 먼저 확인합니다. Python 3.14가 이미 있어도
삭제하지 않습니다.

```powershell
py list
py -3.11 --version
```

`py -3.11 --version`에서 `Python 3.11.x`가 나오면 준비가 끝난 것입니다. 3.11이
없고 최신 [Python Install Manager](https://docs.python.org/3/using/windows.html)가
설치되어 있다면 다음 명령으로 3.11을 추가합니다.

```powershell
py install 3.11
py -3.11 --version
```

`py install`이 인식되지 않는 이전 launcher라면 설치 파일을 사용합니다.

1. [Python 3.11.9 공식 페이지](https://www.python.org/downloads/release/python-3119/)를 엽니다.
2. 페이지 아래 `Files`에서 `Windows installer (64-bit)`를 내려받습니다.
3. Python 3.14와 함께 사용해도 되므로 기존 버전을 삭제하지 않습니다.
4. 이 프로젝트는 `py -3.11`로 버전을 지정하므로 `Add python.exe to PATH`는 필수가 아닙니다.
5. `Install Now`를 누르고 설치를 완료합니다.
6. 열려 있던 PowerShell을 모두 닫고 새 PowerShell을 엽니다.
7. `py -3.11 --version`을 실행해 `Python 3.11.x`가 나오는지 확인합니다.

전역 `python` 명령이 Python 3.14를 가리켜도 괜찮습니다. 2단계에서 `py -3.11`로
가상환경을 만든 다음부터는 가상환경을 활성화하고 `python`만 사용합니다.

macOS 설치 순서:

1. [Python 3.11.9 공식 페이지](https://www.python.org/downloads/release/python-3119/)를 엽니다.
2. 페이지 아래 `Files`에서 `macOS 64-bit universal2 installer`를 받습니다.
3. 설치 프로그램을 완료하고 새 Terminal을 엽니다.
4. 다음 명령 결과가 `Python 3.11.9`인지 확인합니다.

```bash
python3.11 --version
```

`python3 --version`이 3.12 이상이어도 괜찮지만 이 프로젝트의 가상환경은 반드시
아래 2단계에서 `python3.11` 명령으로 만듭니다.

#### 0-3. Arduino IDE 2 설치

1. [Arduino IDE 2 공식 설치 안내](https://support.arduino.cc/hc/en-us/articles/360019833020-Download-and-install-Arduino-IDE)에서 Windows 또는 macOS용 설치 파일을 받습니다.
2. Arduino IDE 2를 실행합니다.
3. 설정에서 Sketchbook 위치를 Windows는 `C:\Users\<사용자이름>\Documents\Arduino`, macOS는 `~/Documents/Arduino`로 지정합니다.

보드 패키지와 외부 라이브러리는 하드웨어를 조립한 뒤 3~4단계에서 설치합니다.

아래 운영체제별 문서는 추가 설명이 필요할 때만 보고, 기본 실습은 계속 이
README의 1단계로 진행합니다.

- [Windows: Arduino IDE, 보드 패키지, 카메라·TensorFlow Lite 라이브러리 설치](docs/WINDOWS.md)
- [macOS: Arduino IDE, 보드 패키지, 카메라·TensorFlow Lite 라이브러리 설치](docs/MACOS.md)

여기까지 끝나면 GitHub 저장소를 받는 1단계로 이동합니다.

### 1단계: 저장소 받기와 폴더 이동

처음 받는 경우 다음 명령을 실행합니다.

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\Projects" -Force
git clone https://github.com/yujin-in-ntu/AI-Sensor-arduino.git "$env:USERPROFILE\Projects\AI-Sensor-arduino"
Set-Location -LiteralPath "$env:USERPROFILE\Projects\AI-Sensor-arduino"
```

macOS:

```bash
mkdir -p ~/Projects
git clone https://github.com/yujin-in-ntu/AI-Sensor-arduino.git ~/Projects/AI-Sensor-arduino
cd ~/Projects/AI-Sensor-arduino
```

이미 저장소를 받은 경우 `git clone`은 다시 실행하지 말고, 기존 저장소 폴더로만
이동합니다. 현재 위치가 맞는지 다음 명령으로 확인할 수 있습니다.

권장 경로에 이미 받은 경우 먼저 이동합니다.

Windows:

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Projects\AI-Sensor-arduino"
```

macOS:

```bash
cd ~/Projects/AI-Sensor-arduino
```

Windows:

```powershell
Get-Location
Test-Path -LiteralPath .\README.md
Test-Path -LiteralPath .\requirements.txt
Test-Path -LiteralPath .\arduino
Test-Path -LiteralPath .\python
```

macOS:

```bash
pwd
test -f README.md && test -f requirements.txt && test -d arduino && test -d python && echo "프로젝트 경로 정상"
```

Windows에서는 프로젝트 경로와 네 개의 `True`, macOS에서는
`프로젝트 경로 정상`이 나오면 올바른 위치입니다.

### 2단계: Python 가상환경과 라이브러리 설치

Python 3.11.x를 사용합니다. 먼저 버전을 확인합니다.

Windows PowerShell에서는 Python 3.11을 명시해 `.venv`를 만들고 활성화합니다.
`Set-ExecutionPolicy`는 현재 PowerShell 창에만 적용되며 관리자 권한이 필요하지
않습니다.

```powershell
py -3.11 --version
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\.venv\Scripts\Activate.ps1
python --version
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

활성화되면 명령줄 앞에 `(.venv)`가 표시되고 `python --version`은 Python 3.11.x가
나옵니다. 이후 Windows 명령도 macOS와 마찬가지로 모두 `python`으로 시작합니다.
새 PowerShell을 열 때마다 프로젝트 폴더에서 다음 세 줄을 다시 실행합니다.

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Projects\AI-Sensor-arduino"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\.venv\Scripts\Activate.ps1
```

기관 정책 때문에 `Activate.ps1`이 계속 차단된다면 명령 프롬프트에서
`.venv\Scripts\activate.bat`을 실행하는 방법도 있습니다.

macOS:

```bash
python3.11 --version
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`source .venv/bin/activate`를 실행하면 터미널 앞에 `(.venv)` 같은 표시가 생깁니다.
이 README의 이후 macOS 명령은 가상환경이 활성화되었다고 가정하고 모두 `python`으로
시작합니다. 새 터미널을 열었다면 다음 두 줄을 다시 실행합니다.

```bash
cd ~/Projects/AI-Sensor-arduino
source .venv/bin/activate
```

마지막 `requirements.txt` 설치 명령은 이 프로젝트에 필요한 다음 세 패키지를
처음부터 함께 설치합니다.

| 설치되는 패키지 | Python 코드에서 사용하는 이름 | 역할 |
|---|---|---|
| `numpy` | `numpy` | 이미지 배열과 수치 계산 |
| `pyserial` | `serial` | USB 시리얼 포트로 Arduino와 통신 |
| `tensorflow` | `tensorflow` | CNN 학습과 INT8 모델 변환 |

특히 설치 이름은 `pyserial`이지만 코드에서는 `import serial`로 불러옵니다.
따라서 `No module named 'serial'`은 Arduino 코드 문제가 아니라 현재 Python
가상환경에 `pyserial`이 설치되지 않았다는 뜻입니다. NumPy만 따로 설치하지 말고
반드시 `requirements.txt` 전체를 설치하세요.

설치 확인:

Windows:

```powershell
python -c "import numpy; print('NumPy ready:', numpy.__version__)"
python -c "import serial; print('PySerial ready:', serial.__version__)"
python -c "import tensorflow as tf; print('TensorFlow ready:', tf.__version__)"
```

macOS:

```bash
python -c "import numpy; print('NumPy ready:', numpy.__version__)"
python -c "import serial; print('PySerial ready:', serial.__version__)"
python -c "import tensorflow as tf; print('TensorFlow ready:', tf.__version__)"
```

결과가 각각 `NumPy ready: 1.26.4`, `PySerial ready: 3.5`,
`TensorFlow ready: 2.15.1`이면 다음 단계로 이동합니다. 하나라도 없거나 다른 버전이면
모델을 학습하지 말고 운영체제에 맞는 명령으로 세 패키지를 한꺼번에 다시 맞춥니다.

Windows:

```powershell
python -m pip install --upgrade --force-reinstall -r requirements.txt
```

macOS:

```bash
python -m pip install --upgrade --force-reinstall -r requirements.txt
```

설치 후 위의 TensorFlow 확인 명령을 다시 실행합니다. 이미 다른 TensorFlow 버전으로
학습했다면 패키지만 바꿔서는 기존 모델이 바뀌지 않습니다. 2.15.1 확인 후
`train_camera_model.py`를 다시 실행하고, 새로 생성된 모델을 포함하도록 03 스케치를
다시 업로드해야 합니다.

#### macOS: 다른 가상환경 이름이 보이거나 패키지를 찾지 못할 때

터미널 앞에 `(python-test)`처럼 다른 이름이 보인다면 현재 프로젝트가 아닌 다른
가상환경일 수 있습니다. 프로젝트 가상환경으로 다시 들어갑니다.

```bash
deactivate
cd ~/Projects/AI-Sensor-arduino
source .venv/bin/activate
which python
python -m pip install -r requirements.txt
python -c "import tensorflow as tf; print('TensorFlow ready:', tf.__version__)"
```

`deactivate: command not found`가 나오면 첫 줄만 건너뜁니다. `.venv/bin/activate`가
없다면 위의 **2단계**에서 `python3.11 -m venv .venv`부터 다시 실행합니다.
`No module named 'numpy'` 또는 `No module named 'serial'`이 나오면 NumPy만 따로
설치하지 말고 `python -m pip install -r requirements.txt`를 다시 실행합니다.

`~/Documents/Arduino/libraries`는 `Arduino_OV767X`와 `Arduino_TensorFlowLite`를
설치하는 **Arduino 라이브러리 폴더**입니다. Python 프로그램은 그곳이 아니라
`~/Projects/AI-Sensor-arduino/python`에 있으므로, 카메라 명령은 항상
`~/Projects/AI-Sensor-arduino`로 이동한 뒤 실행합니다.

## 기본 실습: 직접 촬영부터 추론까지 README 하나로 진행

여기부터는 다른 문서를 열지 않고 3~9단계를 차례대로 진행할 수 있습니다.

```text
3 하드웨어 조립·포트 확인
→ 4 카메라·TensorFlow Lite GitHub 라이브러리 설치
→ 5 카메라 확인 스케치(01)
→ 6 Full View 촬영·데이터 저장(02)
→ 7 자기 데이터로 CNN 학습
→ 8 추론 스케치 업로드(03)
→ 9 GUI에서 자기 손글씨 추론
```

### 3단계: 하드웨어 조립과 포트 확인

#### 3-1. 전원을 뺀 상태에서 조립

1. Nano 33 BLE Sense Lite에서 USB 케이블을 뺍니다.
2. Nano 보드를 Tiny Machine Learning Shield의 방향에 맞춰 끝까지 꽂습니다.
3. OV7675 카메라를 Shield의 카메라 커넥터에 정확한 방향으로 연결합니다.
4. 연결을 다시 확인한 뒤 데이터 통신이 가능한 USB 케이블을 PC에 연결합니다.

전원이 연결된 상태에서 카메라를 뽑거나 다시 꽂지 마세요.

#### 3-2. Arduino IDE 보드와 포트 선택

1. Arduino IDE 2를 실행합니다.
2. 왼쪽 `Boards Manager`를 엽니다.
3. `Arduino Mbed OS Nano Boards`를 검색해 설치합니다.
4. 상단 보드 메뉴에서 `Arduino Nano 33 BLE`를 선택합니다.
5. 보드 이름 옆에 표시된 포트를 선택합니다.

터미널에서도 포트를 확인할 수 있습니다.

Windows:

```powershell
Get-CimInstance Win32_SerialPort | Select-Object DeviceID, Name
```

macOS:

```bash
ls /dev/cu.usbmodem*
```

아래 명령의 `COM5` 또는 `<PORT>`는 자기 컴퓨터에 표시된 포트로 바꿉니다.

### 4단계: 카메라와 TensorFlow Lite 라이브러리 설치

이 프로젝트는 Library Manager의 오래된 OV767X 패키지 대신 GitHub의 최신 소스를
사용합니다. Arduino IDE를 먼저 닫습니다.

기본 Sketchbook 위치를 사용한다면 Windows PowerShell에서 실행합니다.

```powershell
$arduinoLibraries = Join-Path $env:USERPROFILE "Documents\Arduino\libraries"
New-Item -ItemType Directory -Path $arduinoLibraries -Force | Out-Null
Set-Location -LiteralPath $arduinoLibraries
git clone https://github.com/arduino-libraries/Arduino_OV767X.git Arduino_OV767X
git clone https://github.com/tensorflow/tflite-micro-arduino-examples.git Arduino_TensorFlowLite
```

macOS Terminal:

```bash
mkdir -p ~/Documents/Arduino/libraries
cd ~/Documents/Arduino/libraries
git clone https://github.com/arduino-libraries/Arduino_OV767X.git Arduino_OV767X
git clone https://github.com/tensorflow/tflite-micro-arduino-examples.git Arduino_TensorFlowLite
```

Sketchbook 위치가 OneDrive 등 다른 곳이라면 첫 경로를 실제 Sketchbook의
`libraries` 경로로 바꿉니다.

이미 폴더가 존재한다는 오류가 나오면 새로 복제하지 말고 업데이트합니다.

Windows:

```powershell
git -C "$arduinoLibraries\Arduino_OV767X" pull
git -C "$arduinoLibraries\Arduino_TensorFlowLite" pull
```

macOS:

```bash
git -C ~/Documents/Arduino/libraries/Arduino_OV767X pull
git -C ~/Documents/Arduino/libraries/Arduino_TensorFlowLite pull
```

설치 후 Arduino IDE를 다시 시작합니다.

#### 4-1. 설치 확인

Windows에서는 다음 명령을 실행합니다.

```powershell
Get-ChildItem -LiteralPath $arduinoLibraries
Test-Path -LiteralPath "$arduinoLibraries\Arduino_OV767X\src\Arduino_OV767X.h"
Test-Path -LiteralPath "$arduinoLibraries\Arduino_TensorFlowLite\src\TensorFlowLite.h"
```

목록에 다음 두 폴더가 있고 `Test-Path` 결과가 모두 `True`여야 합니다.

```text
Arduino_OV767X
Arduino_TensorFlowLite
```

macOS:

```bash
test -f ~/Documents/Arduino/libraries/Arduino_OV767X/src/Arduino_OV767X.h && echo "OV767X 준비 완료"
test -f ~/Documents/Arduino/libraries/Arduino_TensorFlowLite/src/TensorFlowLite.h && echo "TensorFlow Lite 준비 완료"
```

#### 4-2. Python 작업 폴더로 반드시 돌아오기

라이브러리 설치 과정에서 현재 위치가 Arduino의 `libraries` 폴더로 바뀌었습니다.
이후 Python 명령은 모두 프로젝트 루트에서 실행해야 하므로 다음 명령으로 돌아옵니다.

Windows PowerShell:

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Projects\AI-Sensor-arduino"
Test-Path -LiteralPath .\README.md
```

macOS Terminal:

```bash
cd ~/Projects/AI-Sensor-arduino
test -f README.md && echo "프로젝트 경로 정상"
```

Windows에서는 `True`, macOS에서는 `프로젝트 경로 정상`이 나와야 합니다.

이 두 라이브러리는 `AI-Sensor-arduino` 저장소 안에 포함되어 있지 않습니다.
TensorFlow Lite Micro Arduino 저장소는 현재 읽기 전용 보관 상태이지만 이
프로젝트에서 사용한 Nano 33 BLE용 소스를 제공합니다.

대표 오류의 의미:

| 오류 | 원인과 조치 |
|---|---|
| `Arduino_OV767X.h: No such file or directory` | `Arduino_OV767X` 폴더가 Sketchbook의 `libraries`에 없거나 Sketchbook 위치가 다름 |
| `TensorFlowLite.h: No such file or directory` | `Arduino_TensorFlowLite` GitHub 저장소를 받지 않았거나 폴더 이름이 다름 |
| `'OV7675' was not declared` | 오래되거나 중복된 OV767X 라이브러리가 먼저 선택됨. Arduino IDE를 닫고 `libraries`의 중복 폴더를 확인한 뒤 위 GitHub 버전만 남김 |
| `Didn't find op ... 'SHAPE'` | TensorFlow 2.21.0 등 다른 버전으로 모델을 생성했을 수 있음. TensorFlow 2.15.1을 다시 설치하고 모델 재학습 후 03을 다시 업로드 |

컴파일할 때 `Precompiled library ... not found`가 표시되더라도 마지막에 메모리
사용량이 나오면 오류가 아니라 소스 코드로 대신 컴파일했다는 경고입니다.

### 5단계: 01 카메라 연결 확인

Arduino IDE 2에서 다음 파일을 엽니다.

```text
arduino/camera_01_check/camera_01_check.ino
```

1. 체크 표시 버튼으로 컴파일합니다.
2. 화살표 버튼으로 보드에 업로드합니다.
3. Arduino IDE의 시리얼 모니터와 시리얼 플로터가 열려 있다면 닫습니다.
4. 터미널에서 운영체제에 맞는 명령을 실행합니다.

Windows 예시:

```powershell
python python\preview_camera.py --port COM5
```

macOS:

```bash
python python/preview_camera.py --port /dev/cu.usbmodem1101
```

`OV7675 원본 160x120 미리보기` 창이 열리고 실제 카메라 영상이 나타나면 통신에
성공한 것입니다. `한 장 촬영`을 누르면 현재 영상이 갱신됩니다. 빨간 사각형은
AI가 사용하는 중앙 영역을 보여주며, 창 아래에는 명암 차이가 표시됩니다.
확인이 끝나면 창을 닫아 포트를 해제한 뒤 다음 단계로 이동합니다.

### 6단계: 02 Full View에서 자기 숫자 촬영

#### 6-1. 데이터 수집 스케치 업로드

Arduino IDE에서 다음 파일을 엽니다.

```text
arduino/camera_02_collect/camera_02_collect.ino
```

컴파일하고 업로드합니다. 업로드가 끝나면 Arduino IDE의 **시리얼 모니터와
시리얼 플로터를 모두 닫습니다.** 열어 두면 Python이 포트를 사용할 수 없어
`PermissionError`, `Access is denied`, `Resource busy`가 발생합니다.

#### 6-2. 저장하기 전에 전체 화면 확인

Windows 예시:

```powershell
python python\preview_camera.py --port COM5
```

macOS:

```bash
python python/preview_camera.py --port /dev/cu.usbmodem1101
```

다음을 화면으로 확인합니다.

- 밝은 종이 영역이 화면 안에 충분히 들어오는가?
- 검은 숫자가 프레임 밖으로 잘리지 않는가?
- 숫자 상하좌우에 여백이 있는가?
- 펜 획이 여러 픽셀 두께로 보이는가?
- 조명이 너무 어둡거나 종이가 하얗게 날아가지 않는가?

거리의 숫자보다 화면 상태가 중요합니다. 확인 창을 닫아 포트를 해제합니다.

#### 6-3. 숫자 0~3을 각 20장 저장

Windows:

```powershell
python python\collect_camera_data.py --port COM5 --digits 0123 --per-digit 20
```

macOS:

```bash
python python/collect_camera_data.py --port /dev/cu.usbmodem1101 --digits 0123 --per-digit 20
```

수집 GUI의 의미는 다음과 같습니다.

| 화면 요소 | 역할 |
|---|---|
| 왼쪽 영상 | OV7675 원본 160×120 화면 |
| 빨간 상자 | 자동으로 찾은 밝은 종이 영역 |
| 초록 상자 | 자동으로 찾은 검은 숫자 영역 |
| 오른쪽 영상 | CNN이 실제로 학습하는 28×28 입력 |
| `촬영` | 카메라에서 새 프레임 가져오기 |
| `이 사진 저장` | 품질을 확인한 현재 사진 저장 |
| `종료` | 수집 프로그램 닫기 |

오른쪽 28×28 영상에서 사람 눈에도 숫자가 보여야 저장합니다. 저장 버튼을 누를
때마다 다음 두 파일이 즉시 만들어집니다.

```text
data/camera_full/<숫자>/<시간>.pgm     160×120 원본
data/camera_digits/<숫자>/<시간>.pgm   학습용 28×28
```

중간에 종료하거나 USB를 빼도 이미 저장된 사진은 남습니다. 같은 명령을 다시
실행하면 기존 사진 수를 세고 부족한 숫자부터 이어서 수집합니다.

Windows에서 저장 수를 확인합니다.

```powershell
Get-ChildItem data\camera_digits -Directory | ForEach-Object { "숫자 $($_.Name): $((Get-ChildItem $_.FullName -Filter '*.pgm').Count)장" }
```

macOS:

```bash
for d in 0 1 2 3; do echo "숫자 $d: $(find data/camera_digits/$d -name '*.pgm' | wc -l)장"; done
```

### 7단계: 직접 촬영한 데이터로 CNN 학습

수집 GUI를 닫습니다. Arduino에 02 스케치가 올라가 있어도 PC 학습에는 문제가
없습니다.

일반 학습에서는 완성된 `train_camera_model.py`를 수정하지 않고 실행합니다. 학생이
CNN 구조를 직접 작성하는 활동은 별도의 `train_camera_model_exercise.py`에서
진행합니다. CNN 원리를 함께 공부할 때만 선택 자료인
[카메라 CNN 학습 코드 실습](docs/AI_CODE_LAB.md)을 봅니다.

Windows:

```powershell
python python\train_camera_model.py --digits 0123 --data data\camera_digits --output-dir models\camera
```

macOS:

```bash
python python/train_camera_model.py --digits 0123 --data data/camera_digits --output-dir models/camera
```

이 명령은 데이터 분리, 증강, CNN 학습, INT8 변환, 검증, Arduino 헤더 생성을
자동으로 수행합니다. 실제 가중치 학습은 `train_camera_model.py`의 `model.fit()`에서
진행됩니다.

성공하면 마지막에 다음 내용이 표시됩니다.

```text
INT8 검증 정확도: ...%
모델 크기: ... KiB
Arduino 헤더 생성: .../arduino/camera_03_inference/model_data.h
```

Windows에서 생성된 헤더를 확인합니다.

```powershell
Test-Path -LiteralPath .\arduino\camera_03_inference\model_data.h
Get-Item -LiteralPath .\arduino\camera_03_inference\model_data.h | Select-Object FullName, Length, LastWriteTime
```

macOS:

```bash
test -f arduino/camera_03_inference/model_data.h && echo "model_data.h 생성 완료"
ls -lh arduino/camera_03_inference/model_data.h
```

사진이 없는 상태에서 학습 명령부터 실행하지 마세요. 숫자마다 최소 10장이
필요하고 처음 실습에서는 각 20장을 권장합니다.

### 8단계: 03 추론 스케치 컴파일·업로드

Arduino IDE에서 다음 파일을 엽니다.

```text
arduino/camera_03_inference/camera_03_inference.ino
```

이미 열려 있었다면 새로 생성된 `model_data.h`를 다시 읽도록 스케치를 닫았다가
다시 엽니다.

1. `Arduino Nano 33 BLE`와 올바른 포트를 다시 선택합니다.
2. 체크 표시 버튼으로 컴파일합니다.
3. 화살표 버튼으로 업로드합니다.
4. 업로드가 끝나면 시리얼 모니터와 시리얼 플로터를 닫습니다.

`Arduino_OV767X가 mbed 아키텍처에서 실행...` 또는 `Precompiled library ... not
found`가 보여도 마지막에 메모리 사용량과 업로드 성공이 표시되면 정상입니다.
학습만 하고 03을 다시 업로드하지 않으면 보드는 이전 모델을 계속 사용합니다.

### 9단계: GUI에서 자기 손글씨 추론

Windows 포트 확인과 실행:

```powershell
Get-CimInstance Win32_SerialPort | Select-Object DeviceID, Name
python python\run_inference_gui.py --port COM5
```

macOS:

```bash
ls /dev/cu.usbmodem*
python python/run_inference_gui.py --port /dev/cu.usbmodem1101
```

GUI에서 숫자를 카메라에 보여 주고 `촬영 및 인식`을 누릅니다. 추론은 PC가 아니라
Arduino 내부의 INT8 모델이 수행하며 PC GUI는 원본, 28×28 입력, 예측 확률을
받아 표시합니다.

## 촬영이 안 될 때만: GitHub 예제 데이터 대체 경로

카메라 불량, USB 포트 문제 또는 수업 시간 부족으로 직접 데이터를 모을 수 없는
학생만 아래 A/B 중 하나를 선택합니다. 두 방법 모두 새 사진을 찍는 과정이 아니라
GitHub 저장소에 이미 포함된 숫자 `0~3` 예제 데이터를 사용합니다.

### 10-1단계: 사용할 예제 데이터 방식 선택

다음 두 방법 중 하나를 선택합니다.

| 방법 | 사용할 폴더 | 언제 선택하나요? |
|---|---|---|
| A. 예제 전처리본으로 바로 학습 | `data/example_camera_digits` | 카메라 수집 없이 가장 빨리 학습할 때 |
| B. 예제 원본을 다시 전처리 | `data/example_camera_full` | 카메라 수집 없이 전처리 과정도 체험할 때 |

방법 A를 선택하면 별도 명령 없이 바로 10-2단계로 이동합니다.

방법 B를 선택하면 160×120 원본 80장을 28×28로 다시 전처리합니다.

Windows 한 줄 명령:

```powershell
python python\rebuild_camera_digits.py --digits 0123 --input data\example_camera_full --output work\example_camera_digits_rebuilt
```

macOS 한 줄 명령:

```bash
python python/rebuild_camera_digits.py --digits 0123 --input data/example_camera_full --output work/example_camera_digits_rebuilt
```

정상 결과:

```text
숫자 0: 사용 20장, 제외 0장
숫자 1: 사용 20장, 제외 0장
숫자 2: 사용 20장, 제외 0장
숫자 3: 사용 20장, 제외 0장
```

명령의 각 부분은 다음 뜻입니다.

| 명령 부분 | 역할 |
|---|---|
| `python` | 활성화된 프로젝트 가상환경의 Python 실행 |
| `python\rebuild_camera_digits.py` | 저장된 원본을 다시 전처리하는 프로그램 |
| `--digits 0123` | 숫자 0, 1, 2, 3만 처리 |
| `--input data\example_camera_full` | 160×120 원본이 있는 입력 폴더 |
| `--output work\example_camera_digits_rebuilt` | 새 28×28 결과를 저장할 폴더 |

`work/`는 실험 중간 결과 폴더이며 GitHub에 올라가지 않습니다. 원래 공개 예제
데이터도 변경하지 않습니다.

### 10-2단계: 예제 데이터로 실제 CNN 학습

방법 A를 선택했다면 다음 명령을 실행합니다.

Windows:

```powershell
python python\train_camera_model.py --digits 0123 --data data\example_camera_digits --output-dir models\example_camera
```

macOS:

```bash
python python/train_camera_model.py --digits 0123 --data data/example_camera_digits --output-dir models/example_camera
```

방법 B에서 원본을 다시 전처리했다면 다음 명령을 사용합니다.

Windows:

```powershell
python python\train_camera_model.py --digits 0123 --data work\example_camera_digits_rebuilt --output-dir models\example_camera_rebuilt
```

macOS:

```bash
python python/train_camera_model.py --digits 0123 --data work/example_camera_digits_rebuilt --output-dir models/example_camera_rebuilt
```

이 명령은 다음 순서로 동작합니다.

1. 숫자별 20장의 28×28 PGM을 읽습니다.
2. 학습용 64장과 검증용 16장으로 분리합니다.
3. 위치·밝기·노이즈가 조금 다른 증강 데이터를 만듭니다.
4. `model.fit()`에서 CNN의 가중치를 학습합니다.
5. 학습 모델을 INT8 TFLite로 변환합니다.
6. Arduino가 읽을 `model_data.h`를 생성합니다.

기본값은 최대 80 epoch이며 컴퓨터에 따라 몇 분 걸릴 수 있습니다. 출력이 잠시
멈춘 것처럼 보여도 새 오류와 PowerShell 입력 프롬프트가 나오지 않았다면 기다립니다.

성공하면 마지막에 다음 세 줄이 나옵니다.

```text
INT8 검증 정확도: ...%
모델 크기: ... KiB
Arduino 헤더 생성: .../arduino/camera_03_inference/model_data.h
```

검증 데이터가 16장뿐이므로 한 장 차이로 정확도가 6.25% 변할 수 있습니다.

### 10-3단계: 예제 모델 파일 확인

Windows:

```powershell
Test-Path -LiteralPath .\arduino\camera_03_inference\model_data.h
Get-Item -LiteralPath .\arduino\camera_03_inference\model_data.h | Select-Object FullName, Length, LastWriteTime
```

첫 명령이 `True`를 출력하고 두 번째 명령에 파일 크기와 수정 시간이 나오면
Arduino용 모델이 생성된 것입니다.

macOS:

```bash
test -f arduino/camera_03_inference/model_data.h && echo "model_data.h 생성 완료"
ls -lh arduino/camera_03_inference/model_data.h
```

모델별 보관 파일도 다음 위치에 만들어집니다.

```text
models/example_camera/camera_digit_model.keras
models/example_camera/camera_digit_int8.tflite
models/example_camera/model_data.h
```

방법 B에서는 폴더 이름이 `models/example_camera_rebuilt`입니다.

### 10-4단계: 예제 모델을 Arduino IDE에서 03으로 업로드

1. Arduino IDE 2를 실행합니다.
2. `arduino/camera_03_inference/camera_03_inference.ino`를 엽니다.
3. 이미 열려 있었다면 새 `model_data.h`를 다시 읽도록 스케치를 닫았다가 다시 엽니다.
4. 보드를 `Arduino Nano 33 BLE`로 선택합니다.
5. 연결된 포트를 선택합니다.
6. 체크 표시 버튼으로 컴파일합니다.
7. 화살표 버튼으로 업로드합니다.
8. 업로드가 끝나면 Arduino IDE의 시리얼 모니터와 시리얼 플로터를 닫습니다.

학습만 하고 03을 다시 업로드하지 않으면 보드는 이전 모델을 계속 사용합니다.

### 10-5단계: 예제 모델로 추론 GUI 실행

Windows 포트 확인:

```powershell
Get-CimInstance Win32_SerialPort | Select-Object DeviceID, Name
```

예를 들어 `COM5`로 나온 경우:

```powershell
python python\run_inference_gui.py --port COM5
```

macOS 포트 확인과 실행:

```bash
ls /dev/cu.usbmodem*
python python/run_inference_gui.py --port /dev/cu.usbmodem1101
```

예시 포트는 자신의 컴퓨터에 표시된 값으로 바꿉니다. `PermissionError`,
`Access is denied`, `Resource busy`가 나오면 Arduino IDE 시리얼 모니터와 다른
Python 카메라 창을 모두 닫고 다시 실행합니다.

GUI에서 종이에 쓴 숫자를 카메라에 보여 주고 `촬영 및 인식`을 누릅니다. 실제
추론은 Arduino 내부의 `camera_03_inference.ino`가 수행하고, GUI는 원본·28×28
입력·숫자별 확률을 받아 표시합니다.

### 10-6단계: 다시 학습하거나 모델을 바꿀 때

`train_camera_model.py` 또는 `train_mnist_model.py`를 다시 실행하면
`arduino/camera_03_inference/model_data.h`가 새 모델로 교체됩니다. 그때마다
반드시 다음 순서를 반복합니다.

```text
학습 완료
→ model_data.h 수정 시간 확인
→ Arduino IDE에서 03 닫았다가 다시 열기
→ 03 컴파일·업로드
→ 시리얼 모니터 닫기
→ run_inference_gui.py 실행
```

### PowerShell의 백틱(`)은 무엇인가요?

다른 문서에서 다음처럼 줄 끝에 백틱이 붙은 명령을 볼 수 있습니다.

```powershell
python python\rebuild_camera_digits.py `
  --digits 0123 `
  --input data\example_camera_full `
  --output work\example_camera_digits_rebuilt
```

백틱은 “명령이 다음 줄에 계속된다”는 PowerShell 표시입니다. 백틱 뒤에 공백이
있으면 작동하지 않을 수 있습니다. 처음 실습에서는 위 3단계에 적힌 **한 줄 명령**을
복사하는 것이 가장 안전합니다. 한 줄 명령과 여러 줄 명령의 동작은 같습니다.

### 카메라나 보드가 불량한 경우

- 카메라 수집만 안 되면 10단계의 공개 예제 데이터로 학습할 수 있습니다.
- 보드 연결도 안 되면 10-3단계의 PC 학습과 모델 생성까지만 진행할 수 있습니다.
- 실제 실시간 카메라 추론에는 정상 Arduino와 카메라가 필요합니다.
- 상세 명령과 대체 경로는 [공개 예제 데이터 실습](docs/EXAMPLE_DATA.md)을 확인하세요.

## 세 개의 Arduino 단계와 학생용 추론 실습

기본 실습에서 여는 Arduino 스케치는 세 개입니다. 실제 추론 수학을 직접 작성하는
수업에서는 네 번째 학생용 스케치를 사용합니다.

```text
arduino/
├─ camera_01_check/
│  └─ camera_01_check.ino       실제 160×120 카메라 확인 창에 원본 전송
├─ camera_02_collect/
│  └─ camera_02_collect.ino     160×120 Full View 미리보기·데이터 수집
├─ camera_03_inference/
│  ├─ camera_03_inference.ino   보드에서 CNN 추론 완성본
│  └─ model_data_placeholder.h  아직 모델이 없을 때 사용하는 자리표시자
└─ camera_03_inference_exercise/
   ├─ camera_03_inference_exercise.ino  실제 추론 수식 8곳을 채우는 학생용 복사본
   └─ model_data_placeholder.h          모델 생성 전 자리표시자
```

`camera_02_collect`가 우리가 사용한 Full View 방식입니다. 과거의 28×28 전용 수집 스케치는 제거했습니다.

## 현재 사용하는 Python 파일

```text
python/
├─ camera_preprocess.py       종이·숫자 탐지와 28×28 전처리
├─ preview_camera.py          160×120 원본 미리보기 GUI
├─ collect_camera_data.py     Full View 데이터 수집 GUI
├─ train_camera_model.py      바로 실행하는 완성된 카메라 CNN 학습
├─ train_camera_model_exercise.py  학생이 CNN 구조를 작성하는 실제 학습 실습
├─ train_mnist_model.py       MNIST 다운로드·학습
├─ run_inference_gui.py       Arduino 추론 결과 GUI
├─ rebuild_camera_digits.py   저장된 원본의 28×28 재생성 도구
└─ check_exercises.py         Arduino 실제 추론 빈칸 검사
```

기본 실습과 모델 생성에는 완성된 `python/train_camera_model.py`를 사용합니다.
CNN 층을 직접 작성할 때는 같은 실제 학습 흐름을 가진
`python/train_camera_model_exercise.py`의 PY1~PY8을 완성합니다. Arduino에서는
학생용 스케치의 양자화·Softmax·최댓값 선택 수식을 직접 작성합니다.

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
`train_camera_model.py`는 빈칸 없이 바로 실행할 수 있고,
`train_camera_model_exercise.py`는 Python CNN 작성 수업용입니다.

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
data/example_camera_full/      공개 예제 원본 0~3, 각 20장
data/example_camera_digits/    공개 예제 전처리본 0~3, 각 20장
models/camera/                 직접 촬영 모델
models/mnist/                  MNIST 모델
arduino/camera_03_inference/model_data.h
                               다음 업로드에 포함될 현재 모델
```

개인의 촬영 데이터, 학습 모델, 생성된 `model_data.h`는 Git에 올리지 않도록 `.gitignore`에 등록되어 있습니다. 저장소를 새로 복제한 학생은 직접 데이터를 모으거나 MNIST를 학습해 자신의 헤더를 생성합니다.

카메라 데이터 수집이 어려운 학생은 저장소에 포함된 공개 예제 원본과 28×28
전처리본으로 전처리·CNN 학습·모델 생성을 실행할 수 있습니다. 명령은
[공개 예제 데이터 실습](docs/EXAMPLE_DATA.md)에 정리되어 있습니다.

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
- Python 3.11.9
- TensorFlow 2.15.1
- NumPy 1.26.4
- pyserial 3.5
- Arduino_OV767X
- Arduino_TensorFlowLite
- OV7675: QQVGA 160×120, GRAYSCALE
- 기본 클래스: 0, 1, 2, 3

## 공식 참고 자료

- [Arduino IDE 2 다운로드 및 설치](https://support.arduino.cc/hc/en-us/articles/360019833020-Download-and-install-Arduino-IDE)
- [Arduino IDE에서 보드 패키지 추가](https://support.arduino.cc/hc/en-us/articles/360016119519-Add-boards-to-Arduino-IDE)
- [Arduino 스케치 업로드](https://support.arduino.cc/hc/en-us/articles/4733418441116-Upload-a-sketch-in-Arduino-IDE)
- [Arduino_OV767X 공식 저장소](https://github.com/arduino-libraries/Arduino_OV767X)
- [TensorFlow Lite Micro Arduino 예제 저장소](https://github.com/tensorflow/tflite-micro-arduino-examples)
- [Python 가상환경 공식 문서](https://docs.python.org/3/library/venv.html)
