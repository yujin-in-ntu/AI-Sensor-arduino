# 관리자 권한 없이 Python 3.11 환경 만들기

학교·기관 컴퓨터에서 Python 설치 프로그램이 관리자 암호를 요구할 때만 이 문서를
사용합니다. 일반 설치가 되는 컴퓨터는 이 문서를 건너뛰고 [README 기본 순서](../README.md)를
따릅니다.

이 방법은 `uv`로 Python 3.11.9와 프로젝트 가상환경을 **현재 사용자 영역**에
설치합니다. 기관 정책이 외부 다운로드나 설치 스크립트까지 차단한다면 담당
관리자의 허가가 필요합니다.

## 절대 섞지 않는 두 폴더

| 용도 | Windows | macOS |
|---|---|---|
| Python 명령을 실행하는 프로젝트 루트 | `C:\Users\<사용자이름>\Projects\AI-Sensor-arduino` | `~/Projects/AI-Sensor-arduino` |
| Arduino 라이브러리 설치 폴더 | `C:\Users\<사용자이름>\Documents\Arduino\libraries` | `~/Documents/Arduino/libraries` |

`.venv`, `requirements.txt`, `python/`, `data/`, `models/`는 모두 프로젝트 루트
안에 있습니다. Python 명령은 Arduino 라이브러리 폴더에서 실행하지 않습니다.

## 1. uv 설치

Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS Terminal:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

PowerShell 또는 Terminal을 완전히 닫았다가 다시 열고 확인합니다.

```text
uv --version
```

## 2. 사용자 영역에 Python 3.11.9 설치

Windows와 macOS 모두 다음 명령을 사용합니다.

```text
uv python install 3.11.9
```

## 3. 반드시 프로젝트 루트로 이동

저장소를 아직 받지 않았다면 README의 **1단계: 저장소 받기**를 먼저 완료합니다.

Windows PowerShell:

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Projects\AI-Sensor-arduino"
Get-Location
Test-Path -LiteralPath .\README.md
Test-Path -LiteralPath .\requirements.txt
```

macOS Terminal:

```bash
cd ~/Projects/AI-Sensor-arduino
pwd
test -f README.md && test -f requirements.txt && echo "프로젝트 경로 정상"
```

Windows에서는 `True` 두 개, macOS에서는 `프로젝트 경로 정상`이 나와야 합니다.

## 4. 프로젝트 가상환경 생성과 활성화

Windows PowerShell:

```powershell
uv venv --python 3.11.9 --seed .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\.venv\Scripts\Activate.ps1
python --version
```

macOS Terminal:

```bash
uv venv --python 3.11.9 --seed .venv
source .venv/bin/activate
python --version
```

결과는 `Python 3.11.9`이고 명령줄 앞에는 `(.venv)`가 표시되어야 합니다.

## 5. 프로젝트 패키지 세 개를 한꺼번에 설치

가상환경이 활성화된 같은 터미널에서 실행합니다.

```text
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

설치되는 직접 패키지는 TensorFlow 2.15.1, NumPy 1.26.4, PySerial 3.5입니다.

```text
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import serial; print('PySerial:', serial.__version__)"
python -c "import tensorflow as tf; print('TensorFlow:', tf.__version__)"
```

## 6. Python이 올바른 폴더에서 실행되는지 확인

Windows PowerShell:

```powershell
Get-Location
(Get-Command python).Source
```

정상 경로의 끝은 다음과 같습니다.

```text
Projects\AI-Sensor-arduino\.venv\Scripts\python.exe
```

macOS Terminal:

```bash
pwd
which python
```

정상 경로의 끝은 다음과 같습니다.

```text
Projects/AI-Sensor-arduino/.venv/bin/python
```

## 새 터미널을 열 때마다 실행

Windows PowerShell:

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Projects\AI-Sensor-arduino"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\.venv\Scripts\Activate.ps1
```

macOS Terminal:

```bash
cd ~/Projects/AI-Sensor-arduino
source .venv/bin/activate
```

이제 [README 2단계의 설치 확인](../README.md#2단계-python-가상환경과-라이브러리-설치)부터
기본 실습으로 돌아갑니다.
