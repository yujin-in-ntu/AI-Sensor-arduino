# 설치 경로와 작업 폴더 기준

이 프로젝트에서 가장 자주 생기는 문제는 Arduino IDE, Arduino 라이브러리,
GitHub 프로젝트와 Python 가상환경을 같은 폴더로 생각하는 것입니다. 네 위치는
서로 역할이 다르며 **겹치면 안 됩니다.**

## 모든 운영체제의 공통 원칙

| 구분 | 역할 | 저장하면 안 되는 것 |
|---|---|---|
| 프로그램 설치 폴더 | Git, Python, Arduino IDE 실행 파일 | 촬영 데이터와 프로젝트 코드 |
| GitHub 프로젝트 폴더 | 이 저장소의 `README.md`, `arduino`, `python`, `data` | Arduino 라이브러리 복제본 |
| 프로젝트의 `.venv` | 이 프로젝트 전용 TensorFlow·NumPy·pyserial | 다른 프로젝트의 패키지 |
| Arduino Sketchbook | Arduino 사용자 스케치와 `libraries` | 이 GitHub 저장소 전체 |
| Arduino 보드 패키지 폴더 | Boards Manager가 자동 관리 | 사용자가 직접 받은 라이브러리 |

## 다운로드 폴더와 설치 폴더는 다릅니다

웹브라우저로 받은 Python·Git·Arduino IDE 설치 파일은 잠시 `Downloads`에 있어도
됩니다. 설치가 끝나면 실제 프로그램은 운영체제의 프로그램 폴더에 복사됩니다.
설치 파일이 있는 `Downloads`에서 프로젝트 명령을 실행하지 마세요.

| 운영체제 | 설치 파일을 받는 임시 위치 | 실제 프로그램 위치 | GitHub 프로젝트 위치 |
|---|---|---|---|
| Windows | `C:\Users\<사용자이름>\Downloads` | `C:\Program Files` 또는 사용자 `AppData\Local\Programs` | `C:\Users\<사용자이름>\Projects\AI-Sensor-arduino` |
| macOS | `~/Downloads` | `/Applications` 및 Python `/Library/Frameworks` | `~/Projects/AI-Sensor-arduino` |

설치가 끝난 `.exe`, `.pkg`, `.dmg`는 프로젝트의 일부가 아닙니다. Arduino IDE의
설치 파일과 GitHub 프로젝트를 같은 폴더에 섞지 마세요.

다음 세 가지를 하지 마세요.

1. GitHub 저장소를 `Arduino/libraries` 안에 복제하지 않습니다.
2. `Arduino_OV767X`나 `Arduino_TensorFlowLite`를 GitHub 프로젝트의
   `arduino` 폴더에 넣지 않습니다.
3. 사용자 홈 폴더에서 `git init`을 실행하지 않습니다. 이 저장소는 항상
   `git clone`으로 받습니다.

가능하면 GitHub의 `Code > Download ZIP`보다 아래의 `git clone` 명령을 사용하세요.
ZIP은 압축을 풀 때 `AI-Sensor-arduino-main` 또는 이중 폴더가 만들어져 문서의
경로와 달라지기 쉽습니다. ZIP을 사용해야 한다면 최종 폴더 이름과 위치를
`Projects/AI-Sensor-arduino`로 맞추고, 그 바로 아래에 `README.md`가 있는지
확인합니다.

## Windows 권장 경로

`<사용자이름>`은 자신의 Windows 계정 이름입니다. PowerShell 명령에서는
`$env:USERPROFILE`이 자동으로 `C:\Users\<사용자이름>`을 뜻합니다.

| 항목 | 권장 경로 |
|---|---|
| Git 실행 파일 | `C:\Program Files\Git\cmd\git.exe` |
| Arduino IDE 2 (`All users`) | `C:\Program Files\Arduino IDE\Arduino IDE.exe` |
| Arduino IDE 2 (`Only me`) | `C:\Users\<사용자이름>\AppData\Local\Programs\Arduino IDE\Arduino IDE.exe` |
| Python 3.11 | `C:\Users\<사용자이름>\AppData\Local\Programs\Python\Python311\python.exe` |
| GitHub 프로젝트 | `C:\Users\<사용자이름>\Projects\AI-Sensor-arduino` |
| Python 가상환경 | `C:\Users\<사용자이름>\Projects\AI-Sensor-arduino\.venv` |
| Arduino Sketchbook | `C:\Users\<사용자이름>\Documents\Arduino` |
| Arduino 라이브러리 | `C:\Users\<사용자이름>\Documents\Arduino\libraries` |
| OV767X 라이브러리 | `...\libraries\Arduino_OV767X` |
| TensorFlow Lite 라이브러리 | `...\libraries\Arduino_TensorFlowLite` |
| Boards Manager 패키지 | `C:\Users\<사용자이름>\AppData\Local\Arduino15\packages` |

Python이나 Arduino IDE 설치 프로그램에서 다른 위치를 직접 선택했다면 실행 파일
경로만 달라질 수 있습니다. 프로젝트·가상환경·Sketchbook 위치는 위 표대로
고정하는 것을 권장합니다.

설치된 프로그램의 실제 경로를 확인합니다.

```powershell
Get-Command git | Select-Object Source
Get-Command python | Select-Object Source
Test-Path -LiteralPath "C:\Program Files\Arduino IDE\Arduino IDE.exe"
Test-Path -LiteralPath "$env:LOCALAPPDATA\Programs\Arduino IDE\Arduino IDE.exe"
```

마지막 두 명령 중 하나가 `True`이면 Arduino IDE가 정상 위치에 있습니다. Python 결과가
`WindowsApps\python.exe`이고 `python --version` 대신 Microsoft Store가 열리면
python.org의 Python 3.11을 다시 설치하고 `Add python.exe to PATH`를 체크합니다.

### Windows 프로젝트를 정확한 위치에 받기

처음 한 번만 실행합니다.

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\Projects" -Force
git clone https://github.com/yujin-in-ntu/AI-Sensor-arduino.git "$env:USERPROFILE\Projects\AI-Sensor-arduino"
Set-Location -LiteralPath "$env:USERPROFILE\Projects\AI-Sensor-arduino"
```

이미 받은 경우 `git clone`을 다시 실행하지 않습니다.

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Projects\AI-Sensor-arduino"
git pull
```

현재 위치를 검증합니다.

```powershell
Get-Location
Test-Path -LiteralPath .\README.md
Test-Path -LiteralPath .\requirements.txt
Test-Path -LiteralPath .\arduino
Test-Path -LiteralPath .\python
```

경로와 네 개의 `True`가 나오면 맞습니다. 이후 Python 명령은 이 위치에서만
실행합니다.

Arduino IDE의 `File > Preferences > Sketchbook location`은 다음으로 직접
설정합니다.

먼저 PowerShell에서 폴더를 만듭니다.

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\Documents\Arduino\libraries" -Force
```

```text
C:\Users\<사용자이름>\Documents\Arduino
```

OneDrive를 사용하더라도 이 문서의 명령과 맞추려면 `OneDrive\Documents\Arduino`가
아닌 위 경로를 권장합니다. 다른 Sketchbook을 사용하려면 모든 라이브러리 명령의
경로도 같은 위치로 바꿔야 합니다.

## macOS 권장 경로

| 항목 | 권장 경로 |
|---|---|
| Git | `/usr/bin/git` |
| Arduino IDE 2 | `/Applications/Arduino IDE.app` |
| Python 3.11 설치본 | `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11` |
| GitHub 프로젝트 | `~/Projects/AI-Sensor-arduino` |
| Python 가상환경 | `~/Projects/AI-Sensor-arduino/.venv` |
| Arduino Sketchbook | `~/Documents/Arduino` |
| Arduino 라이브러리 | `~/Documents/Arduino/libraries` |
| Boards Manager 패키지 | `~/Library/Arduino15/packages` |

```bash
mkdir -p ~/Projects
git clone https://github.com/yujin-in-ntu/AI-Sensor-arduino.git ~/Projects/AI-Sensor-arduino
cd ~/Projects/AI-Sensor-arduino
pwd
test -f README.md && test -f requirements.txt && echo "프로젝트 경로 정상"
```

Arduino IDE의 `Arduino IDE > Settings > Sketchbook location`을
`~/Documents/Arduino`로 설정합니다.

```bash
mkdir -p ~/Documents/Arduino/libraries
```

## 명령을 실행하기 전 매번 확인할 것

Python 명령을 실행하기 전 터미널의 현재 위치가 프로젝트 최상위인지 확인합니다.

Windows:

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Projects\AI-Sensor-arduino"
Test-Path -LiteralPath .\requirements.txt
```

macOS:

```bash
cd ~/Projects/AI-Sensor-arduino
test -f requirements.txt && echo "준비 완료"
```

Arduino IDE에서 `.ino`를 열 때는 Sketchbook이 아니라 GitHub 프로젝트 안의 다음
경로를 엽니다.

```text
AI-Sensor-arduino/arduino/camera_01_check/camera_01_check.ino
AI-Sensor-arduino/arduino/camera_02_collect/camera_02_collect.ino
AI-Sensor-arduino/arduino/camera_03_inference/camera_03_inference.ino
```

스케치 파일은 GitHub 프로젝트에 있고, 스케치가 사용하는 외부 라이브러리는
Arduino Sketchbook의 `libraries`에 있다는 점이 핵심입니다.

## 공식 경로 참고

- [Arduino Sketchbook 기본 위치](https://support.arduino.cc/hc/en-us/articles/4412950938514-Open-the-Sketchbook-folder)
- [Arduino IDE·라이브러리·보드 패키지 저장 위치](https://support.arduino.cc/hc/en-us/articles/4415103213714-Find-sketches-libraries-board-cores-and-other-files-on-your-computer)
- [Arduino IDE 설치 폴더](https://support.arduino.cc/hc/en-us/articles/4412943340178-Open-the-Arduino-IDE-installation-folder)
- [Python Windows 설치 및 PATH](https://docs.python.org/3.11/using/windows.html)
