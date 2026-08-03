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
| `python/train_camera_model.py` | 완성된 CNN·fit을 읽고 정규화, Softmax, Cross Entropy, argmax 수식을 작성 |
| `arduino/camera_03_inference_exercise/camera_03_inference_exercise.ino` | 입력 양자화, 출력 역양자화, Softmax, 최댓값 선택 |

다음 파일은 비교와 검사에 사용합니다.

| 파일 | 역할 |
|---|---|
| `python/check_exercises.py` | 실제 파일에 남은 빈칸과 Python 함수 동작 자동 검사 |
| `arduino/camera_03_inference/camera_03_inference.ino` | 실제 완성 Arduino 추론 코드 |

처음에는 이 문서 아래의 정답표와 Arduino 완성본을 보지 않고 TODO 위의 힌트만
읽습니다.

## 시작 전 문법 준비

점, 괄호, 문자열, 리스트, `name=value`, 배열 축이 낯설다면 먼저
[실제 코드에 필요한 Python·NumPy 문법](PYTHON_NUMPY_START.md)을 읽습니다.

학생용 빈칸은 `____PY1____`, `____ARD1____`처럼 표시됩니다. 밑줄 일부만 지우지
말고 토큰 전체를 자신이 작성한 코드로 교체합니다.

## 1부: Python에서 실제 CNN 학습 코드 완성

### 1. 학생용 파일 열기

```text
python/train_camera_model.py
```

편집기에서 `____PY`를 검색하면 `PY1~PY6`의 수식 TODO 6개를 찾을 수 있습니다.
CNN 구조와 `compile()`·`fit()` 호출은 학생이 API 이름을 추측하지 않도록 답과
설명을 완성해 두었습니다.

### 2. PY1: 데이터 정규화

카메라 PGM의 `uint8` 픽셀은 0~255입니다. CNN 입력은 `float32` 0~1로 사용합니다.

고민할 내용:

- 배열 전체에 같은 계산을 하는 데 반복문이 필요한가?
- 정수 `255`와 실수 `255.0` 중 어떤 표현이 의도를 더 잘 보여 주는가?
- `[..., np.newaxis]` 뒤 shape는 어떻게 변하는가?

### 3. 완성 코드로 읽는 CNN 구조

CNN 층은 빈칸으로 두지 않습니다. 실제 코드에는 `filters=`, `kernel_size=`,
`pool_size=`, `units=`처럼 인자의 이름을 모두 표시하고 각 층의 역할과 출력 크기를
주석으로 적었습니다.

```text
28×28×1 입력
→ 3×3 Conv2D 필터 8개: 26×26×8
→ 2×2 MaxPooling: 13×13×8
→ 3×3 Conv2D 필터 16개: 11×11×16
→ 2×2 MaxPooling: 5×5×16
→ Flatten: 400
→ Dense: 32
→ Dense: 숫자 클래스 수만큼 logits
```

`padding="valid"`인 3×3 합성곱은 바깥 여백을 추가하지 않으므로 가로와 세로가
각각 2씩 줄어듭니다. 2×2 MaxPooling은 각 영역의 최댓값만 남겨 크기를 약 절반으로
줄입니다. `Flatten`은 `5×5×16=400`개 값을 한 줄로 펼칩니다.

마지막 Dense에는 Softmax를 넣지 않습니다. Arduino에서 logits를 역양자화한 뒤
Softmax를 직접 계산하기 때문입니다.

### 4. PY2~PY5: 실제 학습 손실 수식

학생이 작성한 함수는 연습용 계산이 아니라 `model.compile(loss=...)`에 연결되어
실제 학습의 손실로 사용됩니다.

```text
logits에서 행별 최댓값 빼기                     PY2
→ exp를 적용해 Softmax 분자 만들기              PY3
→ 행별 전체 합으로 나눠 확률 만들기             PY4
→ 정답 클래스 확률에 -log 적용                  PY5
→ batch 손실의 평균
```

최댓값을 먼저 빼면 `exp()` 결과가 지나치게 커지는 것을 막을 수 있습니다. 정답
확률이 1에 가까우면 `-log(확률)`은 0에 가까워지고, 정답 확률이 0에 가까우면 손실이
커집니다. 이 손실을 작게 만드는 방향이 곧 학습 방향입니다.

### 5. 완성 코드로 읽는 fit과 역전파

`compile()`에는 Adam, 학생이 완성한 Cross Entropy 함수, 정확도 평가가 이미
연결되어 있습니다. `model.fit()`을 호출하면 실제 학습이 시작됩니다.

```text
순전파
→ 손실 계산
→ 자동 미분으로 역전파
→ optimizer가 가중치 수정
→ 다음 batch에서 반복
```

`fit()` 내부의 핵심은 개념적으로 다음 세 문장입니다.

```python
with tf.GradientTape() as tape:
    logits = model(images, training=True)            # 순전파
    loss = loss_function(labels, logits)             # 학생이 작성한 손실 수식

gradients = tape.gradient(loss, model.trainable_variables)  # 실제 역전파
optimizer.apply_gradients(zip(gradients, model.trainable_variables))
```

역전파 기울기를 계산하는 핵심 함수는 `tape.gradient()`입니다. 다만 Conv2D 전체의
미분식을 초보자가 직접 구현하면 코드가 지나치게 커지므로 TensorFlow 자동 미분을
사용합니다. 학생은 역전파가 최소화하려는 실제 손실 수식을 직접 작성합니다.

### 6. PY6: argmax

INT8 모델의 숫자별 출력 중 가장 큰 값의 위치를 선택합니다. 값 자체와 위치를
혼동하지 않도록 `[0.1, 0.7, 0.2]`의 답이 `0.7`인지 `1`인지 먼저 생각합니다.

### 7. Python 빈칸 검사

Windows:

```powershell
.\.venv\Scripts\python.exe python\check_exercises.py --part python
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/check_exercises.py --part python
```

빈칸이 남아 있으면 토큰별 힌트가 나옵니다. 모두 채우면 정규화, CNN 출력 크기,
학생의 Softmax·Cross Entropy와 TensorFlow 정답 손실의 일치 여부, 실제 1 epoch
`fit()`, argmax를 검사합니다. 전체 5개가 통과해야 합니다.

### 8. 짧은 실제 학습

먼저 저장소의 공개 예제 0~3으로 3 epoch만 실행해 전체 연결을 확인합니다.

Windows:

```powershell
.\.venv\Scripts\python.exe python\train_camera_model.py --data data\example_camera_digits --digits 0123 --epochs 3 --output-dir models\learning_actual
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/train_camera_model.py --data data/example_camera_digits --digits 0123 --epochs 3 --output-dir models/learning_actual
```

성공하면 다음 파일들이 생성됩니다.

```text
models/learning_actual/camera_digit_model.keras
models/learning_actual/camera_digit_int8.tflite
arduino/camera_03_inference/model_data.h
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
.\.venv\Scripts\python.exe python\check_exercises.py --part arduino
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/check_exercises.py --part arduino
```

검사 통과 후 Arduino IDE의 체크 버튼으로 실제 C++ 컴파일까지 확인합니다.

### 7. 업로드와 실제 추론

1. Python 학습으로 `arduino/camera_03_inference/model_data.h`가 생성됐는지 확인합니다.
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

Python은 충분히 시도한 뒤 이 문서 아래의 정답표와 비교합니다. 별도의 학습 코드
복사본은 두지 않습니다. 학생이 수정하는 `python/train_camera_model.py` 자체가
README의 기본 명령과 실제 카메라 데이터에 그대로 사용됩니다.

| 빈칸 | 정답 |
|---|---|
| PY1 | `255.0` |
| PY2 | `logits - maximum` |
| PY3 | `tf.exp(shifted_logits)` |
| PY4 | `exponentials / tf.reduce_sum(exponentials, axis=1, keepdims=True)` |
| PY5 | `-tf.math.log(answer_probabilities + 1e-7)` |
| PY6 | `argmax` |

Arduino 정답은 실제 완성 코드의 `prepareInput()`과 `sendPrediction()`에 있습니다.

```text
arduino/camera_03_inference/camera_03_inference.ino
```

처음부터 복사하지 말고 각 식이 정규화, 양자화, Softmax, argmax 중 어떤 역할인지
말로 설명한 다음 비교하는 것을 권장합니다.

## 토론 질문

1. 0~255 값을 정규화하지 않으면 학습에 어떤 변화가 생길까?
2. 마지막 Dense의 출력 개수를 `4`로 고정하지 않고 `class_count`로 쓰는 이유는?
3. Softmax 전에 logits의 최댓값을 빼도 최종 확률의 순위가 유지되는 이유는?
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
