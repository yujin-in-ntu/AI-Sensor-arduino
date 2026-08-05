# Windows 설치 안내

이 문서는 Windows 10/11, PowerShell, Arduino IDE 2를 기준으로 합니다. 명령은 한 줄씩 복사해 실행하세요.

먼저 [설치 경로와 작업 폴더 기준](PATHS.md)의 Windows 경로표를 확인하세요.
이 문서는 프로젝트를 `$env:USERPROFILE\Projects\AI-Sensor-arduino`, Arduino
Sketchbook을 `$env:USERPROFILE\Documents\Arduino`로 고정합니다.

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

먼저 `py --list`를 실행합니다. Python 3.14만 있고 3.11이 없다면 3.14를 삭제하지 말고
`py install 3.11`로 3.11을 추가합니다. `py install`이 인식되지 않는 이전
launcher라면 [Python 3.11.9 공식 페이지](https://www.python.org/downloads/release/python-3119/)에서
`Windows installer (64-bit)`를 받아 설치합니다. 가상환경을 만들 때 `py -3.11`로
지정하므로 `Add python.exe to PATH`는 필수가 아닙니다.

```powershell
py --list
py -3.11 --version
```

`py list`처럼 하이픈 없이 입력하면 Python이 `list`라는 파일을 실행하려고 합니다.
설치된 Python 목록을 확인할 때는 반드시 `py --list`를 사용합니다.

Python 3.14가 함께 설치되어 있어도 삭제하지 않습니다. `py -3.11 --version` 결과는
`Python 3.11.x`여야 합니다. 수업에서는 Python 3.11.x와 TensorFlow 2.15.1 조합으로
통일합니다.

기본 사용자 설치 경로는 보통 다음과 같습니다.

```text
C:\Users\사용자이름\AppData\Local\Programs\Python\Python311\python.exe
```

Python 3.11의 실제 실행 경로를 확인합니다.

```powershell
py -3.11 -c "import sys; print(sys.executable)"
```

가상환경을 만들 때만 `py -3.11`로 버전을 지정하고, 활성화 후에는 `python`을
사용합니다.

### 1-3. Arduino IDE 2 설치

1. [Arduino IDE 공식 설치 안내](https://support.arduino.cc/hc/en-us/articles/360019833020-Download-and-install-Arduino-IDE)에서 Windows용 Arduino IDE 2를 설치합니다. `All users`를 선택할 수 있으면 `C:\Program Files\Arduino IDE`에 설치됩니다. `Only me`를 선택하면 `$env:LOCALAPPDATA\Programs\Arduino IDE`에 설치되며 이것도 정상입니다.
2. Arduino IDE를 한 번 실행합니다.
3. PowerShell에서 Sketchbook과 라이브러리 폴더를 미리 만듭니다.

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\Documents\Arduino\libraries" -Force
```

4. `File > Preferences`의 `Sketchbook location`을 다음 경로로 직접 설정합니다.

```text
C:\Users\사용자이름\Documents\Arduino
```

라이브러리는 이 Sketchbook 폴더 아래의 `libraries`에 설치해야 합니다. GitHub
프로젝트는 이 폴더가 아니라 `C:\Users\사용자이름\Projects` 아래에 둡니다.

## 2. GitHub 저장소 받기

PowerShell을 열고 프로젝트 전용 `Projects` 폴더를 만든 뒤 전체 경로를 지정해
복제합니다. 현재 터미널 위치와 관계없이 항상 같은 곳에 만들어집니다.

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\Projects" -Force
git clone https://github.com/yujin-in-ntu/AI-Sensor-arduino.git "$env:USERPROFILE\Projects\AI-Sensor-arduino"
Set-Location -LiteralPath "$env:USERPROFILE\Projects\AI-Sensor-arduino"
```

이미 복제했다면 새로 복제하지 말고 기존 폴더에서 업데이트합니다.

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Projects\AI-Sensor-arduino"
git pull
```

현재 위치가 맞는지 확인합니다.

```powershell
Get-Location
Test-Path -LiteralPath .\README.md
Test-Path -LiteralPath .\requirements.txt
Test-Path -LiteralPath .\arduino
Test-Path -LiteralPath .\python
```

경로와 네 개의 `True`가 보여야 합니다.

## 3. Python 환경 만들기

저장소 최상위 폴더에서 실행합니다.

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\.venv\Scripts\Activate.ps1
python --version
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`Set-ExecutionPolicy`는 현재 PowerShell 창에만 적용됩니다. 새 PowerShell을 열면
프로젝트 폴더로 이동해 위의 `Set-ExecutionPolicy`와 `Activate.ps1` 두 줄을 다시
실행합니다. 활성화되면 명령줄 앞에 `(.venv)`가 표시됩니다.

설치를 확인합니다.

```powershell
python -c "import tensorflow, numpy, serial, tkinter; print('Python 패키지 준비 완료')"
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

Arduino 라이브러리 폴더에서 프로젝트 루트로 돌아옵니다. 이후 Python 명령은 항상
이 위치에서 실행합니다.

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Projects\AI-Sensor-arduino"
Test-Path -LiteralPath .\README.md
```

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
