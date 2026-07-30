# 공개 예제 데이터로 전처리·학습·추론하기

카메라 수집이 되지 않는 학생도 학습 코드를 실행할 수 있도록 숫자 `0~3`의
원본과 전처리 데이터를 저장소에 포함했습니다.

| 폴더 | 해상도 | 숫자별 수량 | 용도 |
|---|---:|---:|---|
| `data/example_camera_full/0~3` | 160×120 | 각 20장 | 전처리 다시 실행 |
| `data/example_camera_digits/0~3` | 28×28 | 각 20장 | CNN에 바로 학습 |

예제 데이터는 자신의 `data/camera_full`, `data/camera_digits`와 분리되어
있습니다. 따라서 수집 프로그램이 예제 20장을 자신이 촬영한 사진으로 잘못
계산하지 않습니다.

## 방법 A: 전처리된 28×28 데이터로 바로 CNN 학습

가장 간단한 방법입니다. 저장소 최상위 폴더에서 실행합니다.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\train_camera_model.py `
  --digits 0123 `
  --data data\example_camera_digits `
  --output-dir models\example_camera
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/train_camera_model.py \
  --digits 0123 \
  --data data/example_camera_digits \
  --output-dir models/example_camera
```

이 명령은 다음 작업을 수행합니다.

1. 숫자별 20장의 28×28 이미지를 읽습니다.
2. 학습용 64장과 검증용 16장으로 나눕니다.
3. 위치·밝기·노이즈를 바꾼 학습 이미지를 추가합니다.
4. `model.fit()`에서 CNN을 학습합니다.
5. INT8 TFLite 모델을 만듭니다.
6. `models/example_camera/`에 모델을 보관합니다.
7. `arduino/camera_03_inference/model_data.h`를 생성합니다.

성공하면 마지막에 다음 내용이 출력됩니다.

```text
INT8 검증 정확도: ...%
모델 크기: ... KiB
Arduino 헤더 생성: .../arduino/camera_03_inference/model_data.h
```

검증 이미지는 총 16장뿐이므로 한 장을 더 맞히거나 틀릴 때 정확도가 6.25%씩
변할 수 있습니다.

## 방법 B: 160×120 원본을 다시 전처리한 뒤 학습

전처리 코드를 수정하거나 원본에서 28×28이 어떻게 만들어지는지 확인할 때
사용합니다. 결과는 Git에서 무시되는 `work/` 폴더에 만들어 예제 원본을
변경하지 않습니다.

Windows:

```powershell
.\.venv\Scripts\python.exe python\rebuild_camera_digits.py `
  --digits 0123 `
  --input data\example_camera_full `
  --output work\example_camera_digits_rebuilt
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/rebuild_camera_digits.py \
  --digits 0123 \
  --input data/example_camera_full \
  --output work/example_camera_digits_rebuilt
```

각 숫자의 `사용 ...장, 제외 ...장` 결과를 확인한 뒤 새 전처리 결과로
학습합니다.

Windows:

```powershell
.\.venv\Scripts\python.exe python\train_camera_model.py `
  --digits 0123 `
  --data work\example_camera_digits_rebuilt `
  --output-dir models\example_camera_rebuilt
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/train_camera_model.py \
  --digits 0123 \
  --data work/example_camera_digits_rebuilt \
  --output-dir models/example_camera_rebuilt
```

## 학습한 모델을 Arduino에 업로드

학습이 성공하면 `model_data.h`가 이미 추론 스케치 폴더에 생성되어 있습니다.

1. Arduino IDE 2에서 `arduino/camera_03_inference/camera_03_inference.ino`를
   닫았다가 다시 엽니다.
2. 보드를 `Arduino Nano 33 BLE`로 선택합니다.
3. 자신의 포트를 선택합니다.
4. 컴파일하고 업로드합니다.
5. 업로드 완료 후 시리얼 모니터를 닫습니다.

Windows에서 추론 GUI 실행:

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

포트 이름은 자신의 컴퓨터에서 확인한 값으로 바꿉니다.

## 예제 데이터로 수동 신경망 원리 실습

Softmax와 역전파 정답 코드로 예제 사진을 학습하려면 다음처럼 실행합니다.
이 결과는 PC 실습용 `.npz`이며 Arduino용 모델을 만들지는 않습니다.

Windows:

```powershell
.\.venv\Scripts\python.exe python\learning\nn_from_scratch_answer.py `
  --source camera `
  --digits 0123 `
  --data data\example_camera_digits `
  --epochs 150 `
  --batch-size 16 `
  --learning-rate 0.05
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/learning/nn_from_scratch_answer.py \
  --source camera \
  --digits 0123 \
  --data data/example_camera_digits \
  --epochs 150 \
  --batch-size 16 \
  --learning-rate 0.05
```

학생용 `nn_from_scratch_exercise.py`의 TODO 8개를 모두 채운 뒤에는 파일 이름만
바꾸어 같은 명령을 실행할 수 있습니다.

## 하드웨어가 불량일 때 가능한 범위

- 데이터 수집이나 포트 연결만 실패한다면 예제 데이터로 PC 학습을 먼저 진행할
  수 있습니다.
- 카메라 촬영은 되지만 수집 GUI만 실패한다면 예제 모델을 업로드해 실제 추론을
  시험할 수 있습니다.
- 카메라 모듈이나 Arduino 보드 자체가 동작하지 않으면 PC 학습과 저장된 PGM
  추론까지만 가능하며 실제 카메라 추론은 정상 하드웨어가 필요합니다.

