# 실제 카메라 학습·Arduino 추론 코드 빈칸 실습

이 실습은 별도의 장난감 신경망을 만들지 않습니다. 학생이 채운 Python 코드가
실제 카메라 데이터를 CNN으로 학습하고, INT8 TFLite와 `model_data.h`를 생성합니다.
학생이 채운 Arduino 코드는 그 모델로 실제 카메라 추론을 수행합니다.

```text
공개 예제 또는 직접 촬영한 28x28 데이터
  → 학생이 완성한 CNN 학습 코드
  → INT8 TFLite
  → model_data.h
  → 학생이 완성한 Arduino 양자화·Softmax 코드
  → 기존 run_inference_gui.py
```

## 학생이 수정하는 파일

| 파일 | 학생이 작성하는 내용 |
|---|---|
| `python/learning/train_camera_model_exercise.py` | 정규화, CNN, compile, fit, argmax |
| `arduino/camera_03_inference_exercise/camera_03_inference_exercise.ino` | 입력 양자화, 출력 역양자화, Softmax, 최댓값 선택 |

다음 파일은 비교와 검사에 사용합니다.

| 파일 | 역할 |
|---|---|
| `python/learning/check_actual_pipeline_exercise.py` | 남은 빈칸과 Python 함수 동작 자동 검사 |
| `python/learning/train_camera_model_answer.py` | 교사용 Python 정답 실행 파일 |
| `python/train_camera_model.py` | 실제 완성 학습 코드 |
| `arduino/camera_03_inference/camera_03_inference.ino` | 실제 완성 Arduino 추론 코드 |

처음에는 정답 파일과 완성 코드를 열지 않고 학생용 파일의 힌트만 읽습니다.

## 시작 전 문법 준비

점, 괄호, 문자열, 리스트, `name=value`, 배열 축이 낯설다면 먼저
[실제 코드에 필요한 Python·NumPy 문법](PYTHON_NUMPY_START.md)을 읽습니다.

학생용 빈칸은 `____PY1____`, `____ARD1____`처럼 표시됩니다. 밑줄 일부만 지우지
말고 토큰 전체를 자신이 작성한 코드로 교체합니다.

## 1부: Python에서 실제 CNN 학습 코드 완성

### 1. 학생용 파일 열기

```text
python/learning/train_camera_model_exercise.py
```

편집기에서 `____PY`를 검색하면 TODO 10개를 차례대로 찾을 수 있습니다.

### 2. PY1: 데이터 정규화

카메라 PGM의 `uint8` 픽셀은 0~255입니다. CNN 입력은 `float32` 0~1로 사용합니다.

고민할 내용:

- 배열 전체에 같은 계산을 하는 데 반복문이 필요한가?
- 정수 `255`와 실수 `255.0` 중 어떤 표현이 의도를 더 잘 보여 주는가?
- `[..., np.newaxis]` 뒤 shape는 어떻게 변하는가?

### 3. PY2~PY4: CNN 구조

실제 완성 모델과 같은 구조를 만듭니다.

```text
28x28x1
→ Conv2D 8개
→ MaxPooling
→ Conv2D 16개
→ MaxPooling
→ Flatten
→ Dense 32개
→ 숫자 클래스 수만큼 logits
```

마지막 Dense에는 Softmax를 넣지 않습니다. Arduino에서 logits를 역양자화한 뒤
Softmax를 직접 계산하기 때문입니다.

### 4. PY5~PY7: compile

`compile()`은 학습 방법을 정하지만 아직 학습을 실행하지 않습니다.

- optimizer: 가중치를 어떤 방법으로 수정할지 결정
- loss: 예측 logits와 정답 차이를 계산
- metrics: 학습 중 사람이 확인할 평가값
- `from_logits`: 모델 출력이 이미 확률인지 원점수인지 표시

### 5. PY8~PY9: fit

`model.fit()`을 호출하는 순간 실제 학습이 시작됩니다.

```text
순전파
→ 손실 계산
→ 자동 미분으로 역전파
→ optimizer가 가중치 수정
→ 다음 batch에서 반복
```

현재 실제 코드는 TensorFlow가 역전파를 내부에서 계산합니다. 별도의 수동 MLP를
만들지 않아도 학생이 작성한 `fit()` 호출이 실제 CNN 가중치를 바꿉니다.

### 6. PY10: argmax

INT8 모델의 숫자별 출력 중 가장 큰 값의 위치를 선택합니다. 값 자체와 위치를
혼동하지 않도록 `[0.1, 0.7, 0.2]`의 답이 `0.7`인지 `1`인지 먼저 생각합니다.

### 7. Python 빈칸 검사

Windows:

```powershell
.\.venv\Scripts\python.exe python\learning\check_actual_pipeline_exercise.py --part python
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/learning/check_actual_pipeline_exercise.py --part python
```

빈칸이 남아 있으면 토큰별 힌트가 나옵니다. 모두 채우면 정규화, CNN 출력 크기,
Adam·logits 손실, 실제 1 epoch `fit()`, argmax를 작은 입력으로 검사합니다. 전체
5개가 통과해야 합니다.

### 8. 짧은 실제 학습

먼저 저장소의 공개 예제 0~3으로 3 epoch만 실행해 전체 연결을 확인합니다.

Windows:

```powershell
.\.venv\Scripts\python.exe python\learning\train_camera_model_exercise.py --epochs 3
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/learning/train_camera_model_exercise.py --epochs 3
```

성공하면 다음 파일들이 생성됩니다.

```text
models/learning_actual/camera_digit_model.keras
models/learning_actual/camera_digit_int8.tflite
arduino/camera_03_inference/model_data.h
arduino/camera_03_inference_exercise/model_data.h
```

연결을 확인한 뒤 최종 학습은 `--epochs 80`으로 실행합니다. 직접 촬영 데이터를
사용하려면 `--data data\camera_digits` 또는 `--data data/camera_digits`를 추가합니다.

## 2부: Arduino에서 실제 추론 수학 완성

### 1. 학생용 스케치 열기

Arduino IDE 2에서 다음 파일을 엽니다.

```text
arduino/camera_03_inference_exercise/camera_03_inference_exercise.ino
```

`____ARD`를 검색하면 TODO 8개를 찾을 수 있습니다. 긴 카메라 전처리와 시리얼
통신은 완성된 상태입니다. 별도로 만든 연습 함수가 아니라 완성본에서도 실제로
사용하는 다음 두 함수 안의 수식을 학생이 직접 완성합니다.

```cpp
prepareInput()    // 입력 정규화와 INT8 양자화
sendPrediction() // 역양자화, Softmax, 최댓값 선택
```

학생이 빈칸을 채운 뒤 이 스케치를 보드에 업로드하면 작성한 문장이 실제 카메라
추론 때 그대로 실행됩니다. `interpreter->Invoke()`도 같은 파일의 `loop()`에서
호출되므로 별도의 모의 계산 코드가 아닙니다.

### 2. ARD1~ARD2: 입력 정규화와 양자화

```text
카메라 byte 0~255
→ float 0~1
→ 모델 scale과 zeroPoint로 INT8 -128~127
```

`=`는 값을 저장하고 `/`는 나눗셈을 합니다. `255.0f`처럼 실수임을 표시해야
Arduino에서 의도한 실수 나눗셈이 됩니다. `a /= b`는 `a = a / b`를 짧게 쓴
복합 대입 연산입니다.

### 3. ARD3: 출력 역양자화

모델의 INT8 출력을 Softmax에 넣기 전에 다음 관계를 반대로 적용합니다.

```text
실수값 = (INT8값 - zeroPoint) × scale
```

### 4. ARD4~ARD5: 안정적인 Softmax

Softmax는 logits를 양수 분자로 바꾸고 전체 합으로 나눕니다. `expf(logit)` 대신
`expf(logit - maxLogit)`을 사용하면 지수값이 지나치게 커지는 것을 막을 수 있습니다.

### 5. ARD6~ARD8: 최댓값 선택

C++의 조건문과 대입을 사용합니다.

```cpp
if (조건) {
  변수 = 값;
}
```

현재 확률이 최고 확률보다 클 때 최고 확률과 최고 위치를 함께 바꿔야 합니다.

### 6. Arduino 빈칸 검사

Windows:

```powershell
.\.venv\Scripts\python.exe python\learning\check_actual_pipeline_exercise.py --part arduino
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/learning/check_actual_pipeline_exercise.py --part arduino
```

검사 통과 후 Arduino IDE의 체크 버튼으로 실제 C++ 컴파일까지 확인합니다.

### 7. 업로드와 실제 추론

1. Python 학습으로 학생용 폴더에 `model_data.h`가 생성됐는지 확인합니다.
2. `Arduino Nano 33 BLE`와 실제 포트를 선택합니다.
3. 학생용 스케치를 컴파일하고 업로드합니다.
4. Arduino IDE 시리얼 모니터를 닫습니다.
5. 기존 GUI를 실행합니다.

Windows 예시:

```powershell
.\.venv\Scripts\python.exe python\run_inference_gui.py --port COM5
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/run_inference_gui.py --port <PORT>
```

학생용 스케치도 완성본과 같은 `PING`, `PREDICT`, `RESULT` 통신 규칙을 사용하므로
GUI를 수정할 필요가 없습니다.

## 정답 확인 방법

Python은 충분히 시도한 뒤 다음 파일과 비교합니다.

```text
python/learning/train_camera_model_answer.py
```

교사가 정답 흐름을 실행하려면 학생용과 같은 명령에서 파일 이름만 바꿉니다.

```powershell
.\.venv\Scripts\python.exe python\learning\train_camera_model_answer.py --epochs 3
```

Arduino 정답은 실제 완성 코드의 `prepareInput()`과 `sendPrediction()`에 있습니다.

```text
arduino/camera_03_inference/camera_03_inference.ino
```

처음부터 복사하지 말고 각 식이 정규화, 양자화, Softmax, argmax 중 어떤 역할인지
말로 설명한 다음 비교하는 것을 권장합니다.

## 토론 질문

1. 0~255 값을 정규화하지 않으면 학습에 어떤 변화가 생길까?
2. 마지막 Dense의 출력 개수를 `4`로 고정하지 않고 `class_count`로 쓰는 이유는?
3. `from_logits=False`로 잘못 지정하면 손실 계산은 무엇을 오해할까?
4. `fit()` 전후 모델 가중치는 같을까?
5. Arduino의 `Invoke()` 전후 중 어느 시점에 모델 계산이 실제로 일어날까?
6. Softmax에서 모든 logits에 같은 `maxLogit`을 빼도 최종 순위가 유지되는 이유는?
7. 최고 확률만 갱신하고 `bestIndex`를 갱신하지 않으면 어떤 결과가 나올까?

## 의도적으로 빈칸에서 제외한 부분

- 종이·숫자 자동 탐지와 28x28 전처리
- 카메라 프레임 수신과 시리얼 프로토콜
- TensorFlow Lite 연산 등록과 텐서 메모리 할당
- C 헤더 바이트 배열 생성

이 부분은 실제로 사용되지만 첫 수업에서 빈칸으로 만들면 AI 학습보다 배열 경계,
메모리, 통신 오류 해결에 시간이 더 많이 듭니다. 학생이 작성한 핵심 문장은
`Invoke()` 전후의 실제 텐서 처리 흐름 안에 있으므로 실제 모델과 보드에서
그대로 실행됩니다.
