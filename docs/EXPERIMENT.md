# 01 → 02 → 03 전체 실습

운영체제별 설치를 끝낸 뒤 진행하는 공통 실습입니다. 처음에는 숫자 `0~3`을 각 20장씩 촬영합니다.

## 시작 전 확인

### 하드웨어 조립

1. USB 케이블을 분리합니다.
2. Nano 33 BLE Sense Lite를 Tiny Machine Learning Shield의 방향에 맞춰 끝까지 꽂습니다.
3. OV7675 카메라 리본 케이블 또는 모듈을 Shield의 카메라 커넥터에 정확한 방향으로 연결합니다.
4. 연결 상태를 확인한 뒤 USB 케이블을 PC에 연결합니다.

전원이 연결된 상태에서 카메라를 뽑거나 다시 꽂지 마세요.

### 저장소 최상위 폴더로 이동

Windows PowerShell:

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Projects\AI-Sensor-arduino"
Test-Path -LiteralPath .\requirements.txt
```

macOS/Ubuntu Terminal:

```bash
cd ~/Projects/AI-Sensor-arduino
test -f requirements.txt && echo "프로젝트 경로 정상"
```

Windows에서 `True`, macOS/Ubuntu에서 `프로젝트 경로 정상`이 나와야 합니다.
다른 위치에 이미 저장소를 받은 사용자는 자신의 실제 경로를 사용할 수 있지만,
한 실습 도중에는 저장소를 옮기거나 두 복사본을 번갈아 사용하지 마세요.

### 포트 확인

Windows:

```powershell
Get-CimInstance Win32_SerialPort | Select-Object DeviceID, Name
```

macOS:

```bash
ls /dev/cu.usbmodem*
```

Ubuntu:

```bash
ls /dev/ttyACM*
```

아래 예제의 `COM5` 또는 `<PORT>`를 자신의 포트로 바꾸세요.

## 1단계: 카메라 연결 확인

### Arduino 스케치 열기

Arduino IDE 2에서 다음 파일을 엽니다.

```text
arduino/camera_01_check/camera_01_check.ino
```

### 보드와 포트 선택

1. 상단 보드 선택 메뉴를 누릅니다.
2. `Arduino Nano 33 BLE`를 선택합니다.
3. 연결된 포트를 선택합니다.
4. 체크 표시 버튼으로 컴파일합니다.
5. 화살표 버튼으로 업로드합니다.

### 문자 미리보기 확인

1. Arduino IDE의 시리얼 모니터를 엽니다.
2. 전송 속도를 `115200 baud`로 설정합니다.
3. 메시지 입력창에 `p`를 입력하고 전송합니다.
4. 28줄짜리 문자 그림이 나오면 카메라 통신이 성공한 것입니다.

문자 그림은 정밀한 영상 확인용이 아닙니다. 카메라가 응답하는지만 확인하고 다음 단계로 이동합니다.

## 2단계: Full View 미리보기와 데이터 수집

### 2-1. 수집 스케치 업로드

Arduino IDE에서 다음 파일을 엽니다.

```text
arduino/camera_02_collect/camera_02_collect.ino
```

컴파일하고 업로드합니다. 이 스케치는 160×120 회색조 화면을 `921600 baud`로 PC에 보냅니다.

업로드가 끝나면 Arduino IDE의 **시리얼 모니터와 시리얼 플로터를 닫습니다.** 열어 둔 채 Python을 실행하면 `PermissionError`, `Access is denied`, `Resource busy`가 발생합니다.

### 2-2. 저장하지 않고 원본 먼저 확인

Windows:

```powershell
.\.venv\Scripts\python.exe python\preview_camera.py --port COM5
```

macOS:

```bash
./.venv/bin/python python/preview_camera.py --port /dev/cu.usbmodem1101
```

Ubuntu:

```bash
./.venv/bin/python python/preview_camera.py --port /dev/ttyACM0
```

카메라 원본 창이 열리면 다음을 확인합니다.

- 종이 전체가 화면에 들어오는가?
- 숫자가 너무 작거나 프레임 밖으로 잘리지 않는가?
- 조명이 너무 어둡거나 종이가 새하얗게 날아가지 않는가?
- 카메라가 흔들리지 않게 고정되었는가?

거리의 숫자보다 화면을 기준으로 맞추는 것이 정확합니다. 숫자 상하좌우에 여백이 있고, 검은 획이 원본에서 여러 픽셀 두께로 보여야 합니다.

창을 닫으면 포트가 해제됩니다.

### 2-3. 숫자 0~3을 각 20장 수집

Windows:

```powershell
.\.venv\Scripts\python.exe python\collect_camera_data.py --port COM5 --digits 0123 --per-digit 20
```

macOS:

```bash
./.venv/bin/python python/collect_camera_data.py --port /dev/cu.usbmodem1101 --digits 0123 --per-digit 20
```

Ubuntu:

```bash
./.venv/bin/python python/collect_camera_data.py --port /dev/ttyACM0 --digits 0123 --per-digit 20
```

### 수집 GUI 읽는 법

- 왼쪽: 카메라 원본 160×120
- 빨간 상자: 자동으로 찾은 밝은 종이
- 초록 상자: 자동으로 찾은 검은 숫자
- 오른쪽: AI와 학습 코드가 실제로 사용하는 28×28 이미지
- `촬영`: 새 프레임을 한 장 가져오기
- `이 사진 저장`: 품질 검사를 통과한 현재 사진 저장
- `종료`: 프로그램 닫기

오른쪽 28×28에서 사람 눈에도 현재 숫자가 보여야 저장합니다. 선이 하나로 붙거나 다른 숫자처럼 보이면 종이 위치, 숫자 크기, 조명을 바꿔 다시 촬영합니다.

각 저장 동작은 다음 두 파일을 즉시 만듭니다.

```text
data/camera_full/<숫자>/<시간>.pgm
data/camera_digits/<숫자>/<시간>.pgm
```

중간에 종료하거나 USB를 빼도 이미 저장한 파일은 남습니다. 같은 명령을 다시 실행하면 기존 파일 수를 세고 부족한 숫자부터 이어서 수집합니다.

### 데이터 수 확인

Windows:

```powershell
Get-ChildItem data\camera_digits -Directory | ForEach-Object { "숫자 $($_.Name): $((Get-ChildItem $_.FullName -Filter '*.pgm').Count)장" }
```

macOS/Ubuntu:

```bash
for d in 0 1 2 3; do echo "숫자 $d: $(find data/camera_digits/$d -name '*.pgm' | wc -l)장"; done
```

## 3단계: 직접 촬영한 데이터로 학습

카메라 수집이 되지 않거나 실습 시간을 줄여야 한다면
[공개 예제 데이터로 전처리·학습하기](EXAMPLE_DATA.md)의 숫자 `0~3` 원본 및
전처리 데이터로 이 단계부터 시작할 수 있습니다.

수집 GUI를 닫습니다. Arduino에는 아직 `02`가 올라가 있어도 괜찮습니다. 학습은 PC에서 진행됩니다.

Windows:

```powershell
.\.venv\Scripts\python.exe python\train_camera_model.py --digits 0123
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/train_camera_model.py --digits 0123
```

학습 스크립트는 다음 작업을 자동으로 수행합니다.

1. 숫자별 파일을 읽습니다.
2. 학습용과 검증용으로 나눕니다.
3. 위치·밝기·노이즈를 조금 바꾼 데이터를 추가합니다.
4. 작은 CNN을 학습합니다.
5. 모델을 INT8로 양자화합니다.
6. 양자화 모델의 검증 정확도를 계산합니다.
7. PC 보관용 모델을 `models/camera/`에 저장합니다.
8. Arduino용 `model_data.h`를 생성합니다.

성공하면 마지막에 다음 세 줄이 나옵니다.

```text
INT8 검증 정확도: ...%
모델 크기: ... KiB
Arduino 헤더 생성: .../arduino/camera_03_inference/model_data.h
```

20장씩 수집하면 검증 이미지는 총 16장 정도이므로 정확도가 한 장마다 크게 변합니다. 예를 들어 87.5%는 16장 중 14장을 맞힌 결과입니다.

## 4단계: 직접 촬영 모델을 Arduino에서 추론

### 4-1. 추론 스케치 다시 열기

학습이 끝난 뒤 Arduino IDE에서 다음 파일을 엽니다.

```text
arduino/camera_03_inference/camera_03_inference.ino
```

이미 열어 둔 상태였다면 외부에서 생성된 `model_data.h`를 IDE가 다시 읽도록 스케치를 닫았다가 다시 여는 것이 안전합니다.

### 4-2. 컴파일과 업로드

1. 보드와 포트를 확인합니다.
2. 컴파일합니다.
3. 업로드합니다.
4. 업로드 완료 후 시리얼 모니터를 닫습니다.

`Arduino_OV767X가 mbed 아키텍처에서 실행...` 경고 또는 `Precompiled library ... not found` 문구가 나와도 마지막에 메모리 사용량과 업로드 성공이 표시되면 괜찮습니다.

### 4-3. 추론 GUI 실행

Windows:

```powershell
.\.venv\Scripts\python.exe python\run_inference_gui.py --port COM5
```

macOS:

```bash
./.venv/bin/python python/run_inference_gui.py --port /dev/cu.usbmodem1101
```

Ubuntu:

```bash
./.venv/bin/python python/run_inference_gui.py --port /dev/ttyACM0
```

숫자를 놓고 `촬영 및 인식`을 누릅니다. 추론은 PC TensorFlow가 아니라 Arduino 보드 안의 INT8 모델이 수행합니다. PC는 원본과 결과를 받아 화면에 보여 줍니다.

## 5단계: MNIST로 다시 학습해 비교

MNIST는 28×28 손글씨 숫자 데이터셋입니다. 처음 실행할 때 인터넷에서 약 11MB를 자동으로 받습니다.

Windows:

```powershell
.\.venv\Scripts\python.exe python\train_mnist_model.py --digits 0123 --per-digit 2000
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/train_mnist_model.py --digits 0123 --per-digit 2000
```

이 스크립트는 카메라에서 숫자가 가늘게 보이는 상황을 반영해 여러 가로폭의 MNIST 변형도 함께 학습합니다.

성공하면 `models/mnist/`와 Arduino의 `model_data.h`가 생성됩니다. 이제 `camera_03_inference.ino`를 다시 업로드하고 추론 GUI를 실행합니다.

MNIST 검증 정확도와 실제 카메라 성능은 다를 수 있습니다. MNIST는 깨끗한 디지털 이미지이고 OV7675는 종이, 그림자, 초점, 펜 굵기의 영향을 받기 때문입니다.

## 6단계: 저장된 모델 교체

학습 스크립트는 모델별 Arduino 헤더를 보관합니다.

```text
models/camera/model_data.h
models/mnist/model_data.h
```

### 직접 촬영 모델로 교체

Windows:

```powershell
Copy-Item models\camera\model_data.h arduino\camera_03_inference\model_data.h -Force
```

macOS/Ubuntu:

```bash
cp models/camera/model_data.h arduino/camera_03_inference/model_data.h
```

### MNIST 모델로 교체

Windows:

```powershell
Copy-Item models\mnist\model_data.h arduino\camera_03_inference\model_data.h -Force
```

macOS/Ubuntu:

```bash
cp models/mnist/model_data.h arduino/camera_03_inference/model_data.h
```

헤더를 복사하는 것만으로 보드의 모델이 즉시 바뀌지는 않습니다. 반드시 `03` 스케치를 다시 업로드합니다.

## 7단계: 0~9로 확장

숫자당 20장을 모두 촬영하려면:

Windows:

```powershell
.\.venv\Scripts\python.exe python\collect_camera_data.py --port COM5 --digits 0123456789 --per-digit 20
.\.venv\Scripts\python.exe python\train_camera_model.py --digits 0123456789
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/collect_camera_data.py --port <PORT> --digits 0123456789 --per-digit 20
./.venv/bin/python python/train_camera_model.py --digits 0123456789
```

모델 클래스 수와 실제 숫자 라벨은 생성된 헤더에 자동으로 기록됩니다.

## 8단계: 전처리 방식이 바뀌었을 때 원본 재처리

160×120 원본을 보관했기 때문에 다시 촬영하지 않고 새 전처리를 시험할 수 있습니다.

Windows:

```powershell
.\.venv\Scripts\python.exe python\rebuild_camera_digits.py --digits 0123 --input data\camera_full --output data\camera_digits_rebuilt
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/rebuild_camera_digits.py --digits 0123 --input data/camera_full --output data/camera_digits_rebuilt
```

새 폴더로 학습하려면 `--data`를 지정합니다.

Windows:

```powershell
.\.venv\Scripts\python.exe python\train_camera_model.py --digits 0123 --data data\camera_digits_rebuilt --output-dir models\camera_rebuilt
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/train_camera_model.py --digits 0123 --data data/camera_digits_rebuilt --output-dir models/camera_rebuilt
```

문제가 생기면 [오류 해결 문서](TROUBLESHOOTING.md)를 확인하세요.
