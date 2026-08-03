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
- [프로그램·프로젝트·Arduino 라이브러리 정확한 경로](docs/PATHS.md)
- [Arduino CLI로 컴파일·업로드](docs/ARDUINO_CLI.md) — 선택 사항

설치가 끝났다면 모든 운영체제에서 공통으로 사용하는 실습 문서로 이동합니다.

- [기본: 직접 촬영하는 01 → 02 → 03 전체 실습](docs/EXPERIMENT.md)
- [대체: 촬영이 어려울 때 공개 예제 데이터로 학습](docs/EXAMPLE_DATA.md)
- [실제 CNN 코드에 필요한 Python·NumPy 문법](docs/PYTHON_NUMPY_START.md)
- [실제 학습·Arduino 추론 코드 빈칸 실습](docs/AI_CODE_LAB.md)
- [오류 해결 모음](docs/TROUBLESHOOTING.md)

## 처음부터 따라 하는 설치와 환경 준비

아래 0~2단계는 직접 촬영 실습과 공개 예제 데이터 실습에 공통으로 필요한
설치 과정입니다. 환경 준비가 끝나면 기본적으로 학생이 자기 손글씨를 직접
촬영하고 학습합니다. GitHub의 예제 데이터는 촬영이 되지 않을 때만 사용합니다.

명령은 저장소 최상위 폴더의 터미널에서 **한 줄씩 입력하고 Enter**를 누릅니다.
앞 명령이 끝난 뒤 다음 명령을 실행하세요. 명령 앞의 `PS C:\...>` 같은 터미널
표시는 입력하지 않습니다.

### 0단계: Git, Python 3.11, Arduino IDE 2 설치

이미 세 프로그램이 모두 설치되어 있다면 버전만 확인하고 1단계로 이동합니다.
수업용 PC를 처음 준비한다면 아래 순서대로 설치하세요.

#### 0-0. 먼저 폴더 역할을 분리합니다

GitHub 프로젝트와 Arduino 라이브러리를 같은 폴더에 넣지 않습니다. 이 문서의
권장 경로는 다음과 같습니다.

| 용도 | Windows | macOS/Ubuntu |
|---|---|---|
| GitHub 프로젝트 | `C:\Users\<사용자이름>\Projects\AI-Sensor-arduino` | `~/Projects/AI-Sensor-arduino` |
| 프로젝트 가상환경 | `...\AI-Sensor-arduino\.venv` | `.../AI-Sensor-arduino/.venv` |
| Arduino Sketchbook | `C:\Users\<사용자이름>\Documents\Arduino` | `~/Documents/Arduino` |
| Arduino 라이브러리 | `...\Documents\Arduino\libraries` | `~/Documents/Arduino/libraries` |

Arduino IDE와 Python 본체는 운영체제의 프로그램 영역에 설치하고, 촬영 데이터와
모델은 GitHub 프로젝트 안에 둡니다. 전체 경로표와 확인 명령은
[설치 경로와 작업 폴더 기준](docs/PATHS.md)을 먼저 확인하세요.

#### 0-1. Git 확인 및 설치

Windows PowerShell에서 확인합니다.

```powershell
git --version
```

`git version ...`이 나오면 설치되어 있습니다. `git`을 찾을 수 없다는 오류가
나오면 [Git for Windows](https://git-scm.com/download/win)를 설치한 뒤 열려 있던
PowerShell을 모두 닫고 새 PowerShell을 엽니다.

macOS와 Ubuntu의 Git 설치 방법은 각각 [macOS 설치 안내](docs/MACOS.md),
[Ubuntu 설치 안내](docs/UBUNTU.md)를 참고합니다.

#### 0-2. Python 3.11 확인 및 설치

이 프로젝트는 `TensorFlow 2.15.1`을 사용하므로 **Python 3.11 64비트**를
권장합니다. 최신 버전이라는 이유로 Python 3.12 이상을 설치하지 마세요.

Windows PowerShell에서 먼저 확인합니다.

```powershell
python --version
```

`Python 3.11.x`가 나오면 Python 설치는 끝난 것입니다. 다음과 같은 경우에는
Python을 새로 설치합니다.

- `python`을 찾을 수 없다는 오류가 나옵니다.
- Microsoft Store만 열리고 버전이 표시되지 않습니다.
- Python 3.12 이상의 버전이 표시됩니다.

Windows 설치 순서:

1. [Python 3.11.9 공식 페이지](https://www.python.org/downloads/release/python-3119/)를 엽니다.
2. 페이지 아래 `Files`에서 `Windows installer (64-bit)`를 내려받습니다.
3. 설치 프로그램 첫 화면에서 **`Add python.exe to PATH`를 반드시 체크**합니다.
4. `Install Now`를 누르고 설치를 완료합니다.
5. 열려 있던 PowerShell을 모두 닫고 새 PowerShell을 엽니다.
6. `python --version`을 다시 실행해 `Python 3.11.x`가 나오는지 확인합니다.

설치했는데도 `python`을 찾지 못하면 설치 프로그램을 다시 실행해 `Modify`에서
PATH 관련 항목을 활성화합니다. `py -3.11 --version`만 정상 동작하는 경우에는
2단계의 첫 명령을 `py -3.11 -m venv .venv`로 실행해도 됩니다. 가상환경을 만든
뒤에는 문서에 적힌 `\.venv\Scripts\python.exe` 명령을 그대로 사용합니다.

macOS에서는 `python3 --version`을 사용합니다. Ubuntu를 포함한 자세한 설치법은
[macOS 설치 안내](docs/MACOS.md)와 [Ubuntu 설치 안내](docs/UBUNTU.md)를 따릅니다.

#### 0-3. Arduino IDE 2 설치 및 보드 준비

1. [Arduino IDE 2 공식 설치 안내](https://support.arduino.cc/hc/en-us/articles/360019833020-Download-and-install-Arduino-IDE)에서 운영체제에 맞는 Arduino IDE 2를 설치합니다.
2. Arduino IDE 2를 실행합니다.
3. 설정에서 Sketchbook 위치를 Windows는 `C:\Users\<사용자이름>\Documents\Arduino`, macOS/Ubuntu는 `~/Documents/Arduino`로 지정합니다.
4. 왼쪽 `Boards Manager`에서 `Arduino Mbed OS Nano Boards`를 검색해 설치합니다.
5. Nano 33 BLE Sense Lite를 데이터 통신용 USB 케이블로 연결합니다.
6. IDE 상단 보드 메뉴에서 `Arduino Nano 33 BLE`와 연결된 포트를 선택합니다.
7. 카메라와 TensorFlow Lite 라이브러리는 운영체제별 설치 문서의 안내대로 설치합니다.

운영체제별 전체 설치 과정:

- [Windows: Arduino IDE, 보드 패키지, 카메라·TensorFlow Lite 라이브러리 설치](docs/WINDOWS.md)
- [macOS: Arduino IDE, 보드 패키지, 카메라·TensorFlow Lite 라이브러리 설치](docs/MACOS.md)
- [Ubuntu: Arduino IDE, 보드 패키지, 카메라·TensorFlow Lite 라이브러리 설치](docs/UBUNTU.md)

여기까지 끝나면 GitHub 저장소를 받는 1단계로 이동합니다.

### 1단계: 저장소 받기와 폴더 이동

처음 받는 경우 다음 명령을 실행합니다.

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\Projects" -Force
git clone https://github.com/yujin-in-ntu/AI-Sensor-arduino.git "$env:USERPROFILE\Projects\AI-Sensor-arduino"
Set-Location -LiteralPath "$env:USERPROFILE\Projects\AI-Sensor-arduino"
```

macOS/Ubuntu:

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

macOS/Ubuntu:

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

macOS/Ubuntu:

```bash
pwd
test -f README.md && test -f requirements.txt && test -d arduino && test -d python && echo "프로젝트 경로 정상"
```

Windows에서는 프로젝트 경로와 네 개의 `True`, macOS/Ubuntu에서는
`프로젝트 경로 정상`이 나오면 올바른 위치입니다.

### 2단계: Python 가상환경과 라이브러리 설치

Python 3.10 또는 3.11을 권장합니다. 먼저 버전을 확인합니다.

Windows:

```powershell
python --version
```

가상환경을 만들고 필요한 라이브러리를 설치합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Windows에서는 PowerShell 실행 정책 문제를 피하기 위해 `Activate.ps1`을 실행하지
않습니다. 이후에도 항상 `.\.venv\Scripts\python.exe`로 가상환경 Python을 직접
실행합니다.

macOS/Ubuntu:

```bash
python3 --version
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
```

설치 확인:

Windows:

```powershell
.\.venv\Scripts\python.exe -c "import numpy, serial, tensorflow; print('Python ready')"
```

macOS/Ubuntu:

```bash
./.venv/bin/python -c "import numpy, serial, tensorflow; print('Python ready')"
```

`Python ready`가 나오면 다음 단계로 이동합니다. TensorFlow 정보나 경고가 함께
출력되어도 마지막에 `Python ready`가 있으면 설치가 완료된 것입니다.

## 기본 실습: 학생이 직접 촬영한 데이터로 학습

이 프로젝트의 주 실습은 다음 흐름입니다.

```text
01 카메라 확인
→ 02 Full View에서 자기 숫자 0~3을 각 20장 촬영
→ data/camera_full과 data/camera_digits에 즉시 저장
→ data/camera_digits로 CNN 학습
→ model_data.h 생성
→ 03 추론 스케치 업로드
→ 자기 손글씨를 다시 보여 주며 추론 확인
```

운영체제별 환경 준비를 마쳤다면
[01 → 02 → 03 전체 실습](docs/EXPERIMENT.md)을 1단계부터 순서대로 진행합니다.

직접 촬영 데이터의 기본 학습 명령은 다음과 같습니다.

Windows:

```powershell
.\.venv\Scripts\python.exe python\train_camera_model.py --digits 0123 --data data\camera_digits --output-dir models\camera
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/train_camera_model.py --digits 0123 --data data/camera_digits --output-dir models/camera
```

`data/camera_digits`에는 학생이 수집 GUI에서 저장한 28×28 이미지가 들어갑니다.
사진이 없는 상태에서 이 학습 명령부터 실행하지 마세요.

## 촬영이 안 될 때만: GitHub 예제 데이터 대체 경로

카메라 불량, USB 포트 문제 또는 수업 시간 부족으로 직접 데이터를 모을 수 없는
학생만 아래 A/B 중 하나를 선택합니다. 두 방법 모두 새 사진을 찍는 과정이 아니라
GitHub 저장소에 이미 포함된 숫자 `0~3` 예제 데이터를 사용합니다.

### 3단계: 사용할 데이터 방식 선택

다음 두 방법 중 하나를 선택합니다.

| 방법 | 사용할 폴더 | 언제 선택하나요? |
|---|---|---|
| A. 예제 전처리본으로 바로 학습 | `data/example_camera_digits` | 카메라 수집 없이 가장 빨리 학습할 때 |
| B. 예제 원본을 다시 전처리 | `data/example_camera_full` | 카메라 수집 없이 전처리 과정도 체험할 때 |

방법 A를 선택하면 별도 명령 없이 바로 4단계로 이동합니다.

방법 B를 선택하면 160×120 원본 80장을 28×28로 다시 전처리합니다.

Windows 한 줄 명령:

```powershell
.\.venv\Scripts\python.exe python\rebuild_camera_digits.py --digits 0123 --input data\example_camera_full --output work\example_camera_digits_rebuilt
```

macOS/Ubuntu 한 줄 명령:

```bash
./.venv/bin/python python/rebuild_camera_digits.py --digits 0123 --input data/example_camera_full --output work/example_camera_digits_rebuilt
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
| `.\.venv\Scripts\python.exe` | 이 프로젝트의 Windows 가상환경 Python 실행 |
| `python\rebuild_camera_digits.py` | 저장된 원본을 다시 전처리하는 프로그램 |
| `--digits 0123` | 숫자 0, 1, 2, 3만 처리 |
| `--input data\example_camera_full` | 160×120 원본이 있는 입력 폴더 |
| `--output work\example_camera_digits_rebuilt` | 새 28×28 결과를 저장할 폴더 |

`work/`는 실험 중간 결과 폴더이며 GitHub에 올라가지 않습니다. 원래 공개 예제
데이터도 변경하지 않습니다.

### 4단계: 실제 CNN 학습

방법 A를 선택했다면 다음 명령을 실행합니다.

Windows:

```powershell
.\.venv\Scripts\python.exe python\train_camera_model.py --digits 0123 --data data\example_camera_digits --output-dir models\example_camera
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/train_camera_model.py --digits 0123 --data data/example_camera_digits --output-dir models/example_camera
```

방법 B에서 원본을 다시 전처리했다면 다음 명령을 사용합니다.

Windows:

```powershell
.\.venv\Scripts\python.exe python\train_camera_model.py --digits 0123 --data work\example_camera_digits_rebuilt --output-dir models\example_camera_rebuilt
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/train_camera_model.py --digits 0123 --data work/example_camera_digits_rebuilt --output-dir models/example_camera_rebuilt
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

### 5단계: 생성된 파일 확인

Windows:

```powershell
Test-Path -LiteralPath .\arduino\camera_03_inference\model_data.h
Get-Item -LiteralPath .\arduino\camera_03_inference\model_data.h | Select-Object FullName, Length, LastWriteTime
```

첫 명령이 `True`를 출력하고 두 번째 명령에 파일 크기와 수정 시간이 나오면
Arduino용 모델이 생성된 것입니다.

macOS/Ubuntu:

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

### 6단계: Arduino IDE에서 03 추론 업로드

1. Arduino IDE 2를 실행합니다.
2. `arduino/camera_03_inference/camera_03_inference.ino`를 엽니다.
3. 이미 열려 있었다면 새 `model_data.h`를 다시 읽도록 스케치를 닫았다가 다시 엽니다.
4. 보드를 `Arduino Nano 33 BLE`로 선택합니다.
5. 연결된 포트를 선택합니다.
6. 체크 표시 버튼으로 컴파일합니다.
7. 화살표 버튼으로 업로드합니다.
8. 업로드가 끝나면 Arduino IDE의 시리얼 모니터와 시리얼 플로터를 닫습니다.

학습만 하고 03을 다시 업로드하지 않으면 보드는 이전 모델을 계속 사용합니다.

### 7단계: 포트 확인과 추론 GUI 실행

Windows 포트 확인:

```powershell
Get-CimInstance Win32_SerialPort | Select-Object DeviceID, Name
```

예를 들어 `COM5`로 나온 경우:

```powershell
.\.venv\Scripts\python.exe python\run_inference_gui.py --port COM5
```

macOS 포트 확인과 실행:

```bash
ls /dev/cu.usbmodem*
./.venv/bin/python python/run_inference_gui.py --port /dev/cu.usbmodem1101
```

Ubuntu 포트 확인과 실행:

```bash
ls /dev/ttyACM*
./.venv/bin/python python/run_inference_gui.py --port /dev/ttyACM0
```

예시 포트는 자신의 컴퓨터에 표시된 값으로 바꿉니다. `PermissionError`,
`Access is denied`, `Resource busy`가 나오면 Arduino IDE 시리얼 모니터와 다른
Python 카메라 창을 모두 닫고 다시 실행합니다.

GUI에서 종이에 쓴 숫자를 카메라에 보여 주고 `촬영 및 인식`을 누릅니다. 실제
추론은 Arduino 내부의 `camera_03_inference.ino`가 수행하고, GUI는 원본·28×28
입력·숫자별 확률을 받아 표시합니다.

### 8단계: 다시 학습하거나 모델을 바꿀 때

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
.\.venv\Scripts\python.exe python\rebuild_camera_digits.py `
  --digits 0123 `
  --input data\example_camera_full `
  --output work\example_camera_digits_rebuilt
```

백틱은 “명령이 다음 줄에 계속된다”는 PowerShell 표시입니다. 백틱 뒤에 공백이
있으면 작동하지 않을 수 있습니다. 처음 실습에서는 위 3단계에 적힌 **한 줄 명령**을
복사하는 것이 가장 안전합니다. 한 줄 명령과 여러 줄 명령의 동작은 같습니다.

### 카메라나 보드가 불량한 경우

- 카메라 수집만 안 되면 공개 예제 데이터로 1~6단계를 진행할 수 있습니다.
- 보드 연결도 안 되면 1~5단계의 PC 학습과 모델 생성까지 진행할 수 있습니다.
- 실제 실시간 카메라 추론인 6~7단계는 정상 Arduino와 카메라가 필요합니다.
- 상세 명령과 대체 경로는 [공개 예제 데이터 실습](docs/EXAMPLE_DATA.md)을 확인하세요.

## 세 개의 Arduino 단계와 학생용 추론 실습

기본 실습에서 여는 Arduino 스케치는 세 개입니다. 실제 추론 수학을 직접 작성하는
수업에서는 네 번째 학생용 스케치를 사용합니다.

```text
arduino/
├─ camera_01_check/
│  └─ camera_01_check.ino       카메라 연결과 문자 미리보기 확인
├─ camera_02_collect/
│  └─ camera_02_collect.ino     160×120 Full View 미리보기·데이터 수집
├─ camera_03_inference/
│  ├─ camera_03_inference.ino   보드에서 CNN 추론 완성본
│  └─ model_data_placeholder.h  아직 모델이 없을 때 사용하는 자리표시자
└─ camera_03_inference_exercise/
   ├─ camera_03_inference_exercise.ino  양자화·Softmax·argmax 학생용
   └─ model_data_placeholder.h          모델 생성 전 자리표시자
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
   ├─ train_camera_model_exercise.py       실제 CNN 핵심 빈칸
   ├─ check_actual_pipeline_exercise.py    Python·Arduino 자동 검사
   └─ train_camera_model_answer.py         실제 CNN 교사용 정답
```

학생용 Python 파일은 실제 데이터 분리·증강·INT8 변환·Arduino 헤더 생성을
`train_camera_model.py`에서 재사용합니다. 학생용 Arduino 스케치도 기존 GUI와 같은
통신 규칙을 사용합니다. [실제 코드 빈칸 실습](docs/AI_CODE_LAB.md)을 완료하면
학생이 작성한 코드가 실제 모델 학습부터 보드 추론까지 그대로 실행됩니다.

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
`python/learning/train_camera_model_exercise.py`는 같은 실제 학습·변환 함수를
사용하므로 완성 후 별도의 장난감 모델이 아니라 Arduino용 `model_data.h`를 만듭니다.

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
arduino/camera_03_inference_exercise/model_data.h
                               학생용 추론 스케치에 포함될 같은 모델
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
