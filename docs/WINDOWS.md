# Windows 설치 안내

이 문서는 Windows 10/11, PowerShell, Arduino IDE 2를 기준으로 합니다. 명령은 한 줄씩 복사해 실행하세요.

## 1. 프로그램 설치

### 1-1. Git 설치

1. [Git for Windows](https://git-scm.com/download/win)를 설치합니다.
2. 설치 과정의 기본 선택값을 그대로 사용해도 됩니다.
3. 새 PowerShell을 열고 확인합니다.

```powershell
git --version
```

`git version ...`이 표시되어야 합니다.

### 1-2. Python 3.11 설치

1. [Python 공식 다운로드](https://www.python.org/downloads/)에서 Python 3.11 64-bit 설치 프로그램을 받습니다.
2. 설치 첫 화면에서 `Add python.exe to PATH`를 체크합니다.
3. 설치가 끝나면 새 PowerShell을 열고 확인합니다.

```powershell
python --version
```

권장 결과는 `Python 3.11.x`입니다. 이 프로젝트는 Python 3.10도 지원하지만 Python 3.12 이상은 고정된 TensorFlow 2.15.1과 맞지 않을 수 있습니다.

`py` 명령이 없어도 괜찮습니다. 이 문서는 `python`을 사용합니다.

### 1-3. Arduino IDE 2 설치

1. [Arduino IDE 공식 설치 안내](https://support.arduino.cc/hc/en-us/articles/360019833020-Download-and-install-Arduino-IDE)에서 Windows용 최신 Arduino IDE 2를 설치합니다.
2. Arduino IDE를 한 번 실행합니다.
3. `File > Preferences`에서 `Sketchbook location`을 확인합니다. 기본값은 보통 다음과 같습니다.

```text
C:\Users\사용자이름\Documents\Arduino
```

라이브러리는 이 Sketchbook 폴더 아래의 `libraries`에 설치해야 합니다.

## 2. GitHub 저장소 받기

PowerShell을 열고 원하는 작업 폴더로 이동합니다. 다음 예시는 `Documents`를 사용합니다.

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Documents"
git clone https://github.com/yujin-in-ntu/AI-Sensor-arduino.git
Set-Location -LiteralPath "$env:USERPROFILE\Documents\AI-Sensor-arduino"
```

이미 복제했다면 새로 복제하지 말고 기존 폴더에서 업데이트합니다.

```powershell
Set-Location -LiteralPath "저장소의 실제 경로"
git pull
```

현재 위치가 맞는지 확인합니다.

```powershell
Get-Location
Get-ChildItem
```

`arduino`, `python`, `docs`, `requirements.txt`가 보여야 합니다.

## 3. Python 환경 만들기

저장소 최상위 폴더에서 실행합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

이 문서에서는 가상환경을 활성화하지 않고 `.venv` 안의 Python을 직접 사용합니다. 따라서 `Activate.ps1` 실행 정책 오류를 피할 수 있습니다.

설치를 확인합니다.

```powershell
.\.venv\Scripts\python.exe -c "import tensorflow, numpy, serial, tkinter; print('Python 패키지 준비 완료')"
```

`Python 패키지 준비 완료`가 나오면 성공입니다. TensorFlow의 CPU 관련 안내 문구는 오류가 아닙니다.

## 4. Arduino 보드 패키지 설치

1. Arduino IDE 2를 엽니다.
2. 왼쪽의 `Boards Manager`를 엽니다.
3. `Arduino Mbed OS Nano Boards`를 검색해 설치합니다.
4. USB로 보드를 연결합니다.
5. 상단 보드 선택 메뉴에서 `Arduino Nano 33 BLE`를 선택합니다.
6. 연결된 COM 포트도 선택합니다.

Nano 33 BLE Sense Lite가 IDE에서 `Arduino Nano 33 BLE`로 표시될 수 있습니다. 이 프로젝트가 사용하는 FQBN은 `arduino:mbed_nano:nano33ble`입니다.

## 5. 카메라와 TensorFlow Lite 라이브러리 설치

이 프로젝트는 Library Manager의 오래된 OV767X 패키지 대신 GitHub의 최신 소스를 사용합니다. Arduino IDE를 먼저 닫습니다.

기본 Sketchbook 위치를 사용한다면 PowerShell에서 실행합니다.

```powershell
$arduinoLibraries = Join-Path $env:USERPROFILE "Documents\Arduino\libraries"
New-Item -ItemType Directory -Path $arduinoLibraries -Force | Out-Null
Set-Location -LiteralPath $arduinoLibraries
git clone https://github.com/arduino-libraries/Arduino_OV767X.git Arduino_OV767X
git clone https://github.com/tensorflow/tflite-micro-arduino-examples.git Arduino_TensorFlowLite
```

Sketchbook 위치가 OneDrive 등 다른 곳이라면 첫 줄의 경로를 실제 Sketchbook 경로로 바꿉니다.

이미 폴더가 존재한다는 오류가 나오면 새로 복제하지 말고 업데이트합니다.

```powershell
git -C "$arduinoLibraries\Arduino_OV767X" pull
git -C "$arduinoLibraries\Arduino_TensorFlowLite" pull
```

설치 후 Arduino IDE를 다시 시작합니다.

### 설치 확인

다음 두 폴더가 있어야 합니다.

```powershell
Get-ChildItem -LiteralPath $arduinoLibraries
```

```text
Arduino_OV767X
Arduino_TensorFlowLite
```

TensorFlow Lite Micro Arduino 저장소는 현재 읽기 전용 보관 상태이지만 이 프로젝트에서 사용한 Nano 33 BLE용 소스를 제공합니다.

## 6. COM 포트 확인

Arduino IDE 상단 보드 메뉴에서 COM 번호를 볼 수 있습니다. PowerShell에서도 확인할 수 있습니다.

```powershell
Get-CimInstance Win32_SerialPort | Select-Object DeviceID, Name
```

예시:

```text
COM5  Arduino Nano 33 BLE
```

앞으로 문서의 `COM5`는 자신의 번호로 바꾸세요. USB를 다시 꽂으면 번호가 바뀔 수 있습니다.

## 7. 다음 단계

설치가 끝났습니다. [공통 실습 문서](EXPERIMENT.md)의 `1단계: 카메라 확인`부터 진행하세요.

Arduino IDE 대신 터미널에서 스케치를 컴파일하고 업로드하려면 [Arduino CLI 문서](ARDUINO_CLI.md)를 사용하세요.
