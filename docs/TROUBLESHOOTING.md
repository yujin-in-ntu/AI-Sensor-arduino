# 오류 해결 모음

오류가 생기면 메시지의 마지막 한 줄만 보지 말고 처음 등장한 `error`, `fatal error`, `Traceback`부터 확인하세요.

## 빠른 확인 목록

1. 올바른 스케치를 업로드했는가?
2. 보드가 `Arduino Nano 33 BLE`로 선택됐는가?
3. 포트 번호가 현재 연결과 같은가?
4. Arduino IDE 시리얼 모니터가 닫혀 있는가?
5. 명령을 저장소 최상위 폴더에서 실행했는가?
6. `.venv`의 Python을 사용했는가?
7. 모델 학습 후 `03`을 다시 업로드했는가?

## 어떤 폴더에서 실행해야 하는지 모르겠음

권장 경로는 GitHub 프로젝트와 Arduino 라이브러리를 완전히 분리합니다.

```text
Windows 프로젝트:          C:\Users\<사용자이름>\Projects\AI-Sensor-arduino
Windows Arduino 라이브러리: C:\Users\<사용자이름>\Documents\Arduino\libraries

macOS/Ubuntu 프로젝트:          ~/Projects/AI-Sensor-arduino
macOS/Ubuntu Arduino 라이브러리: ~/Documents/Arduino/libraries
```

Python 학습·전처리·GUI 명령은 프로젝트 폴더에서 실행합니다. Arduino 라이브러리
폴더에서는 실행하지 않습니다. 자세한 구분은 [설치 경로와 작업 폴더 기준](PATHS.md)을
확인하세요.

Windows 확인:

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Projects\AI-Sensor-arduino"
Test-Path -LiteralPath .\requirements.txt
Test-Path -LiteralPath .\.venv\Scripts\python.exe
```

macOS/Ubuntu 확인:

```bash
cd ~/Projects/AI-Sensor-arduino
test -f requirements.txt && test -x .venv/bin/python && echo "경로 정상"
```

## `py` 또는 `python`을 찾을 수 없음

예시:

```text
py is not recognized
python is not recognized
```

Python 3.11을 설치하고 새 터미널을 엽니다. Windows 설치 시 `Add python.exe to PATH`를 체크합니다.

확인:

```powershell
python --version
```

## `Activate.ps1`을 실행할 수 없음

이 프로젝트는 가상환경 활성화가 필요 없습니다. 다음처럼 가상환경 Python을 직접 실행하세요.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## `requirements.txt`를 찾을 수 없음

현재 위치가 저장소 최상위 폴더가 아닙니다.

Windows:

```powershell
Get-Location
Get-ChildItem
```

macOS/Ubuntu:

```bash
pwd
ls
```

`requirements.txt`, `arduino`, `python`이 함께 보여야 합니다.

## 포트를 열 수 없음

예시:

```text
PermissionError(13, 'Access is denied')
Resource busy
could not open port
```

다른 프로그램이 포트를 사용 중입니다.

1. Arduino IDE 시리얼 모니터를 닫습니다.
2. 시리얼 플로터도 닫습니다.
3. 다른 Python 카메라 창을 닫습니다.
4. 잠시 기다렸다 다시 실행합니다.
5. 계속 실패하면 USB를 다시 연결하고 포트를 재확인합니다.

Ubuntu라면 `dialout` 그룹과 udev 규칙도 확인합니다.

## Arduino가 `HELLO`에 응답하지 않음

예시:

```text
Arduino 준비 신호를 받지 못했습니다
카메라 응답 시간이 초과되었습니다
```

- 미리보기·수집에는 `camera_02_collect`가 업로드되어 있어야 합니다.
- 추론 GUI에는 `camera_03_inference`가 업로드되어 있어야 합니다.
- 업로드 직후 보드가 재시작할 시간을 2~5초 기다립니다.
- 포트를 다시 확인합니다.
- 시리얼 모니터를 닫습니다.

## `'OV7675' was not declared in this scope`

Library Manager의 오래된 Arduino_OV767X 버전을 사용했을 가능성이 큽니다. Arduino IDE를 닫고 운영체제별 설치 문서대로 공식 GitHub 저장소를 Sketchbook의 `libraries/Arduino_OV767X`에 설치합니다.

현재 코드는 다음 API를 사용합니다.

```cpp
Camera.begin(QQVGA, GRAYSCALE, 1, OV7675)
```

## `TensorFlowLite.h: No such file or directory`

Arduino TensorFlow Lite Micro 라이브러리가 없거나 잘못된 Sketchbook에 설치됐습니다.

공식 저장소를 실제 Sketchbook의 libraries 폴더에 다음 이름으로 복제합니다.

```text
Arduino_TensorFlowLite
```

저장소 주소:

```text
https://github.com/tensorflow/tflite-micro-arduino-examples
```

설치 후 Arduino IDE를 완전히 닫았다가 다시 엽니다.

## `tensorflow/lite/version.h`가 없음

예전 스케치를 열었을 가능성이 있습니다. GitHub의 최신 코드를 받고 현재 `camera_03_inference.ino`를 사용하세요. 현재 코드는 그 헤더를 요구하지 않습니다.

## `Precompiled library ... not found`

이 문구 뒤에 컴파일이 계속되고 마지막에 프로그램/RAM 사용량이 나오면 경고입니다. 라이브러리가 미리 컴파일된 바이너리 대신 소스에서 빌드된다는 의미입니다.

## `mbed`와 `mbed_nano` 호환 경고

예시:

```text
라이브러리 Arduino_OV767X가 mbed 아키텍처에서 실행되며
mbed_nano 아키텍처에서 실행되는 현재 보드에서는 호환되지 않을 수 있습니다
```

현재 프로젝트에서 컴파일과 실행을 확인한 경고입니다. 마지막에 컴파일·업로드가 성공하면 진행해도 됩니다.

## 업로드가 끝났는데 새 화면이 열리지 않음

Arduino 업로드는 보드 프로그램만 바꿉니다. PC GUI는 자동으로 열리지 않습니다. 시리얼 모니터를 닫고 Python GUI를 별도로 실행하세요.

```powershell
.\.venv\Scripts\python.exe python\run_inference_gui.py --port COM5
```

## 수집을 중간에 종료하거나 USB를 뺌

`이 사진 저장`을 누른 사진은 즉시 PGM 파일로 저장됩니다. 프로그램을 종료하거나 USB를 빼도 이미 저장한 사진은 남습니다. 같은 `--per-digit` 명령을 다시 실행하면 부족한 숫자부터 이어집니다.

## AI 입력이 숫자처럼 보이지 않음

예측 확률보다 오른쪽 28×28 화면을 먼저 봅니다.

- 빨간 상자에 종이가 들어와야 합니다.
- 초록 상자가 숫자 전체를 감싸야 합니다.
- 숫자가 프레임 밖으로 잘리지 않아야 합니다.
- 획이 너무 얇으면 검은색 굵은 펜을 사용합니다.
- 종이 줄이 숫자보다 진하면 다른 종이를 사용합니다.
- 원본에서 숫자가 너무 작으면 카메라를 가까이 하거나 글씨를 크게 씁니다.

## MNIST 정확도는 높은데 실제 카메라에서 틀림

MNIST와 실제 카메라는 데이터 분포가 다릅니다.

- MNIST: 깨끗한 28×28 디지털 이미지
- 카메라: 조명, 초점, 종이 무늬, 펜 굵기, 원근 포함

직접 촬영 모델과 MNIST 모델을 각각 업로드해 비교합니다. 수업의 중요한 관찰 지점입니다.

## `model_data.h`가 없거나 모델 준비 실패

다음 중 하나를 먼저 실행합니다.

```powershell
.\.venv\Scripts\python.exe python\train_camera_model.py --digits 0123
```

또는:

```powershell
.\.venv\Scripts\python.exe python\train_mnist_model.py --digits 0123 --per-digit 2000
```

그 뒤 `camera_03_inference.ino`를 다시 업로드합니다.

## TensorFlow의 긴 WARNING/INFO 출력

다음과 같은 출력은 변환이 계속 진행되고 마지막에 INT8 정확도와 헤더 생성 경로가 나오면 정상입니다.

```text
oneDNN custom operations are on
deprecated
Non-Converted Ops
Created TensorFlow Lite XNNPACK delegate
```

## 모델을 바꿨는데 결과가 그대로임

PC의 헤더만 바뀌고 보드에는 이전 프로그램이 남아 있습니다.

1. `model_data.h` 수정 시간을 확인합니다.
2. Arduino IDE에서 `03` 스케치를 닫았다가 다시 엽니다.
3. 다시 컴파일하고 업로드합니다.
4. 추론 GUI를 다시 시작합니다.

## Nano 보드 업로드 포트를 잃어버림

RESET 버튼을 빠르게 두 번 누르면 부트로더 포트가 나타날 수 있습니다. 포트 번호가 바뀔 수 있으므로 다시 선택하고 업로드합니다.

## Git 오류: `src refspec main does not match any`

빈 저장소에 아직 첫 커밋이 없다는 뜻입니다. 이 프로젝트를 사용하는 학생은 직접 `git init`하지 말고 `git clone`으로 시작하는 것이 가장 간단합니다.

```text
git clone https://github.com/yujin-in-ntu/AI-Sensor-arduino.git
```
