# 카메라 CNN 학습 코드 읽기·작성 및 Arduino 추론 실습

`python/train_camera_model.py`는 언제든 실행할 수 있는 완성본입니다. 먼저 사진 한
장이 학습되는 흐름과 완성 코드를 함께 읽은 다음, 학생은
`python/train_camera_model_exercise.py`의 실제 CNN 구조를 작성합니다. Arduino에서는
별도의 학생용 스케치에서 실제 추론 수식을 작성합니다.

Python 명령을 실행하기 전에는 저장소 루트로 이동하고 가상환경을 활성화합니다.
Windows는 `$env:USERPROFILE\Projects\AI-Sensor-arduino`, macOS는
`~/Projects/AI-Sensor-arduino`로 이동한 뒤 각 운영체제의 활성화 명령을 실행합니다.

```text
28×28 숫자 사진과 정답
  → 0~1 정규화
  → Conv2D로 선·곡선 특징 찾기
  → MaxPooling으로 중요한 특징 압축
  → Dense에서 숫자별 logits 출력
  → Cross Entropy 손실 계산
  → fit() 내부 자동 역전파로 가중치 수정
  → 학습된 모델을 INT8 TFLite와 model_data.h로 변환
  → Arduino에서 실제 카메라 추론
```

## 사용하는 실제 파일

| 파일 | 수업에서 하는 일 |
|---|---|
| `python/train_camera_model.py` | 바로 실행하는 Python 학습 완성본 |
| `python/train_camera_model_exercise.py` | PY1~PY8을 작성하는 실제 CNN 학습 실습 |
| `arduino/camera_03_inference_exercise/camera_03_inference_exercise.ino` | 실제 추론 수식 8곳 직접 작성 |
| `python/check_exercises.py` | Arduino 빈칸 검사 |
| `arduino/camera_03_inference/camera_03_inference.ino` | Arduino 교사용 완성본 |

Python의 점, 괄호, 리스트, `name=value`가 낯설다면 먼저
[Python·NumPy 문법](PYTHON_NUMPY_START.md)을 읽습니다.

완성본으로 먼저 전체 학습이 되는지 확인한 뒤 `_exercise.py`를 엽니다. PY1~PY5는
숫자를 채우고, PY6과 PY7은 주어진 조건만 보고 층 함수 전체를 작성하며, PY8은
특징 지도를 Dense 층이 받을 수 있는 한 줄 배열로 펼치는 층을 작성합니다.

연습본의 PY6~PY8은 완성본을 그대로 베끼는 문제가 아닙니다. 주어진 `5×5` 필터와
`2×2` 이동 조건을 적용하면 크기가 다음처럼 변합니다.

```text
13×13×8 → Conv2D → 5×5×16 → MaxPooling → 2×2×16 → Flatten → 64
```

## 1부: 사진 학습 과정과 Python 코드 함께 보기

### 1. 사진을 숫자 배열로 읽고 정규화

수집한 사진은 `data/camera_digits/<숫자>/`의 28×28 PGM 파일입니다. 각 픽셀은
0~255 정수이므로 다음 코드가 0~1 실수로 바꿉니다.

```python
return np.asarray(images, dtype=np.float32)[..., np.newaxis] / 255.0
```

```text
사진 80장: (80, 28, 28)
채널 축 추가: (80, 28, 28, 1)
255.0으로 나누기: 픽셀 0~255 → 0~1
```

### 2. Convolution과 MaxPooling

`build_model()`에서 다음 층을 위에서 아래 순서로 연결합니다.

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

실제 합성곱 층은 다음처럼 보입니다.

```python
tf.keras.layers.Conv2D(
    filters=8,
    kernel_size=(3, 3),
    strides=(1, 1),
    padding="valid",
    activation="relu",
)
```

- `filters=8`: 서로 다른 선·모서리 특징을 찾는 필터 8개
- `kernel_size=(3, 3)`: 한 번에 살펴보는 영역
- `strides=(1, 1)`: 필터를 가로·세로 한 칸씩 이동
- `padding="valid"`: 사진 바깥에 여백을 추가하지 않음
- `activation="relu"`: 음수 결과를 0으로 변경

합성곱 한 출력값의 의미는 다음 수식입니다. 계산 자체는 TensorFlow가 수행합니다.

```text
출력[y,x,f]
= bias[f]
+ Σ 입력[y+ky, x+kx, c] × 필터[ky,kx,c,f]
```

MaxPooling에는 학습되는 가중치가 없습니다. 다음 한 줄이 각 2×2 영역에서 가장 큰
값만 남깁니다.

```python
tf.keras.layers.MaxPooling2D(pool_size=(2, 2))
```

### 3. Flatten과 Dense로 숫자 점수 만들기

`5×5×16=400`개 특징을 한 줄로 펼치고 숫자를 판단합니다.

```python
tf.keras.layers.Flatten()
tf.keras.layers.Dense(units=32, activation="relu")
tf.keras.layers.Dense(units=class_count)
```

0~3을 학습하면 `class_count=4`이므로 마지막 출력도 4개입니다. 이 값은 아직
확률이 아니라 숫자별 원점수인 logits입니다.

### 4. 손실함수와 Softmax

`compile_model()`은 Adam과 Cross Entropy를 학습에 연결합니다.

```python
model.compile(
    optimizer=tf.keras.optimizers.Adam(),
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=["accuracy"],
)
```

`from_logits=True`는 마지막 Dense 출력이 아직 Softmax 확률이 아니라는 뜻입니다.
TensorFlow 손실함수는 내부에서 안정적인 Softmax와 Cross Entropy를 계산합니다.

```text
확률 = exp(logit) / 모든 exp(logit)의 합
손실 = -log(정답 클래스의 확률)
```

정답 확률이 높으면 손실이 작고, 정답 확률이 낮으면 손실이 커집니다.

### 5. fit과 Backpropagation

실제 학습을 시작하는 호출은 다음입니다.

```python
history = model.fit(
    x_train,
    y_train,
    validation_data=(x_val, y_val),
    epochs=epochs,
    batch_size=32,
)
```

`fit()` 내부에서는 개념적으로 다음 순서가 반복됩니다.

```python
with tf.GradientTape() as tape:
    logits = model(images, training=True)            # 순전파
    loss = loss_function(labels, logits)             # 손실 계산

gradients = tape.gradient(loss, model.trainable_variables)  # 역전파
optimizer.apply_gradients(zip(gradients, model.trainable_variables))
```

`tape.gradient()`가 Chain Rule을 사용해 `∂Loss/∂Weight`를 계산합니다. Adam은 그
기울기로 Conv2D 필터와 Dense 가중치를 수정합니다. 전체 Conv2D 미분을 학생이 직접
구현하지 않고, 사진 → 예측 → 손실 → 기울기 → 가중치 수정의 연결을 코드에서 찾는
것이 이 수업의 목표입니다.

### 6. 학습된 모델을 Arduino용으로 변환

학습 뒤 `convert_int8()`이 float 모델을 INT8 TFLite로 변환하고 `write_header()`가
바이트 배열 `model_data.h`를 만듭니다.

```text
학습된 Keras 모델
→ camera_digit_int8.tflite
→ arduino/camera_03_inference/model_data.h
```

### 7. 공개 예제로 짧게 실행

먼저 아래 명령으로 완성본이 정상적으로 학습되는지 확인합니다.

Windows:

```powershell
python python\train_camera_model.py --data data\example_camera_digits --digits 0123 --epochs 3 --output-dir models\example_camera
```

macOS:

```bash
python python/train_camera_model.py --data data/example_camera_digits --digits 0123 --epochs 3 --output-dir models/example_camera
```

그다음 `train_camera_model_exercise.py`의 PY1~PY8을 완성했다면 파일 이름만 바꿔
같은 데이터로 실습 코드를 실행합니다.

Windows:

```powershell
python python\train_camera_model_exercise.py --data data\example_camera_digits --digits 0123 --epochs 3 --output-dir models\exercise_camera
```

macOS:

```bash
python python/train_camera_model_exercise.py --data data/example_camera_digits --digits 0123 --epochs 3 --output-dir models/exercise_camera
```

## 2부: Arduino에서 실제 추론 수식 완성

Arduino IDE 2에서 다음 파일을 엽니다.

```text
arduino/camera_03_inference_exercise/camera_03_inference_exercise.ino
```

`____ARD`를 검색하면 실제 추론 흐름 안의 학생 작성 구역 8개를 찾을 수 있습니다.

```cpp
runInference() // 입력 양자화 → Invoke() → 출력 역양자화 → Softmax → 최댓값 선택
```

### ARD1~ARD2: 입력 정규화와 양자화

```text
카메라 byte 0~255
→ float 0~1
→ 모델 scale과 zeroPoint로 INT8 -128~127
```

### ARD3: 출력 역양자화

```text
실수값 = (INT8값 - zeroPoint) × scale
```

### ARD4~ARD5: 안정적인 Softmax

`expf(logit - maxLogit)`으로 지수값이 지나치게 커지는 것을 막고, 모든 분자의
합으로 나누어 확률을 만듭니다.

### ARD6~ARD8: 가장 큰 확률의 숫자 선택

현재 확률이 지금까지의 최고 확률보다 크면 최고 확률과 숫자 위치를 함께
갱신합니다.

### Arduino 빈칸 검사

Windows:

```powershell
python python\check_exercises.py --part arduino
```

macOS:

```bash
python python/check_exercises.py --part arduino
```

검사 통과 후 Arduino IDE에서 학생용 스케치를 컴파일하고 업로드합니다. 모델은
`arduino/camera_03_inference/model_data.h`에 생성되므로 학생용 스케치 폴더에도
같은 헤더를 복사합니다.

Windows:

```powershell
Copy-Item arduino\camera_03_inference\model_data.h arduino\camera_03_inference_exercise\model_data.h -Force
```

macOS:

```bash
cp arduino/camera_03_inference/model_data.h arduino/camera_03_inference_exercise/model_data.h
```

## 토론 질문

1. Conv2D 필터는 학습 전과 후에 같은 값을 가질까?
2. MaxPooling에는 수정되는 가중치가 없는 이유는 무엇일까?
3. 정답 클래스 확률이 낮을수록 Cross Entropy가 커지는 이유는 무엇일까?
4. `fit()` 전후 Dense와 Conv2D 가중치는 같을까?
5. 학습의 `tape.gradient()`와 추론의 `interpreter->Invoke()`는 무엇이 다를까?
