# 신경망 학습·추론 코드를 직접 채우는 실습

이 실습은 TensorFlow의 `model.fit()` 안에서 자동으로 처리되던 계산을 NumPy로 직접 작성합니다. 목표는 높은 정확도의 Arduino 모델을 새로 만드는 것이 아니라, **학습이 어떤 숫자 계산을 반복하고 추론은 그중 어디까지만 사용하는지** 코드로 이해하는 것입니다.

Python의 점(`.`), 괄호, `np.array`, `.shape`, `axis`가 아직 낯설다면 먼저
[0단계 Python·NumPy 문법 실습](PYTHON_NUMPY_START.md)을 진행하세요. 이 문서는
0단계를 마친 학생을 위한 1단계 실습입니다.

## 준비된 파일

| 파일 | 역할 |
|---|---|
| `python/learning/nn_from_scratch_exercise.py` | 학생이 TODO 1~8을 채우는 파일 |
| `python/learning/check_nn_exercise.py` | 각 TODO를 작은 숫자로 자동 검사하는 파일 |
| `python/learning/nn_from_scratch_answer.py` | 같은 구조의 정답과 설명 |
| `python/learning/nn_data.py` | MNIST 또는 촬영한 PGM 파일을 읽는 공통 코드 |

처음에는 정답 파일을 열지 않고 학생용 파일에서 `TODO`를 검색합니다. 막혔을 때 힌트를 읽고, 자동 검사 후 마지막에 정답 파일과 비교하는 순서를 권장합니다.

## 우리가 직접 만들 신경망

```text
28×28 이미지
   │  펼치기: 784개 숫자
   ▼
z1 = x @ w1 + b1
   │
ReLU
   ▼
64개 은닉층 값
   │
logits = a1 @ w2 + b2
   │
Softmax
   ▼
0, 1, 2, 3일 확률
```

`@`는 행렬 곱셈입니다. 이미지 한 장을 예로 들면 배열 모양은 다음과 같습니다.

| 이름 | 모양 | 뜻 |
|---|---:|---|
| `x` | `1 × 784` | 입력 픽셀 |
| `w1` | `784 × 64` | 입력과 은닉층을 연결하는 학습 대상 |
| `b1` | `64` | 첫 번째 편향 |
| `a1` | `1 × 64` | ReLU를 통과한 은닉층 값 |
| `w2` | `64 × 4` | 은닉층과 네 숫자를 연결하는 학습 대상 |
| `b2` | `4` | 두 번째 편향 |
| `logits` | `1 × 4` | 확률로 바꾸기 전 숫자별 점수 |
| `probs` | `1 × 4` | 합이 1인 숫자별 확률 |

여러 이미지를 한 번에 계산하면 첫 번째 차원 `1`이 미니배치 크기로 바뀝니다.

## 학습과 추론의 차이

학습은 다음 네 단계를 여러 번 반복합니다.

```text
순전파 → 손실 계산 → 역전파 → 가중치 수정
```

- 순전파: 현재 가중치로 숫자별 확률을 계산합니다.
- 손실: 계산한 확률이 정답과 얼마나 다른지 하나의 수로 측정합니다.
- 역전파: 각 가중치가 손실에 얼마나 영향을 줬는지 미분합니다.
- 가중치 수정: 손실이 줄어드는 방향으로 가중치를 조금 움직입니다.

추론에는 정답 라벨이 없고 다음 계산만 합니다.

```text
새 이미지 → 순전파 → Softmax 확률 → argmax → 예측 숫자
```

따라서 추론할 때는 **손실 계산, 역전파, 가중치 수정이 전혀 일어나지 않습니다.** Arduino의 `camera_03_inference`도 이미 학습된 가중치로 이 부분만 실행합니다.

## TODO 1: ReLU

파일에서 `def relu`를 찾습니다.

```python
ReLU(z) = max(0, z)
```

음수 값은 0으로 바꾸고 양수는 그대로 둡니다. 신경망에 직선이 아닌 성질을 넣어 복잡한 숫자 모양을 배울 수 있게 합니다.

## TODO 2: 안정적인 Softmax

Softmax는 출력 점수 `logits`를 확률로 바꿉니다.

```text
exp(점수) / 모든 exp(점수)의 합
```

큰 값에 바로 `exp`를 적용하면 컴퓨터 숫자 범위를 넘을 수 있습니다. 각 행에서 최댓값을 먼저 빼도 최종 확률은 같으므로 다음 순서로 계산합니다.

1. 각 행의 모든 점수에서 그 행의 최댓값을 뺍니다.
2. `np.exp`를 계산합니다.
3. 각 행의 합으로 나눕니다.

`axis=1, keepdims=True`를 사용해야 여러 이미지가 들어와도 행별로 계산됩니다.

## TODO 3: 교차엔트로피 손실

정답 클래스의 확률만 골라 `-log`를 계산합니다.

```text
loss = -평균(log(정답 확률))
```

정답 확률이 `0.9`라면 벌점이 작고 `0.01`이라면 벌점이 큽니다. `log(0)`을 피하려고 아주 작은 값 `1e-12`를 더합니다.

## TODO 4: 순전파

다음 네 식을 순서대로 구현합니다.

```python
z1 = x @ w1 + b1
a1 = relu(z1)
logits = a1 @ w2 + b2
probs = softmax(logits)
```

역전파 때 다시 사용하도록 중간 결과를 `cache` 딕셔너리에 저장합니다.

## TODO 5: 출력층 역전파

정답 `y`를 `[0, 0, 1, 0]` 같은 one-hot 배열로 바꿉니다. Softmax와 교차엔트로피를 함께 사용하면 출력 점수의 기울기는 간단해집니다.

```python
d_logits = (probs - one_hot) / batch_size
d_w2 = a1.T @ d_logits
d_b2 = np.sum(d_logits, axis=0)
d_a1 = d_logits @ w2.T
```

`d_`는 “손실을 해당 값으로 미분한 결과”라는 뜻입니다. 예를 들어 `d_w2`는 `w2`를 조금 바꿀 때 손실이 어느 방향으로 얼마나 변하는지 나타냅니다.

## TODO 6: 은닉층 역전파

연쇄법칙을 이용해 ReLU 앞과 첫 번째 가중치까지 거꾸로 이동합니다.

```python
d_z1 = d_a1 * (z1 > 0)
d_w1 = x.T @ d_z1
d_b1 = np.sum(d_z1, axis=0)
```

ReLU는 입력이 양수인 구간에서 기울기가 1이고 음수인 구간에서 0입니다.

## TODO 7: SGD로 가중치 수정

기울기는 손실이 커지는 방향을 가리키므로 반대 방향으로 이동합니다.

```python
새 가중치 = 기존 가중치 - learning_rate * 기울기
```

`learning_rate`가 너무 크면 정답 근처를 계속 뛰어넘고, 너무 작으면 학습이 매우 느립니다.

## TODO 8: 추론

`forward()`로 확률을 얻은 뒤 `np.argmax(probs, axis=1)`로 가장 큰 확률의 클래스 번호를 고릅니다. 내부 클래스 번호를 실제 숫자로 바꾸는 작업은 `digits` 목록이 담당합니다.

## 빈칸 자동 확인

저장소 최상위 폴더의 터미널에서 실행합니다.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\learning\check_nn_exercise.py
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/learning/check_nn_exercise.py
```

처음에는 `0/8 통과`가 정상입니다. TODO를 하나씩 채울 때마다 해당 줄이 `[통과]`로 바뀝니다. 식은 맞아 보이는데 실패하면 배열의 `axis`, `.T`, 배치 크기로 나누는 부분을 확인합니다.

## MNIST로 직접 학습

8개를 모두 통과한 뒤 학생용 코드를 실행합니다.

Windows:

```powershell
.\.venv\Scripts\python.exe python\learning\nn_from_scratch_exercise.py --source mnist --digits 0123 --per-digit 500 --epochs 15
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/learning/nn_from_scratch_exercise.py --source mnist --digits 0123 --per-digit 500 --epochs 15
```

매 epoch마다 손실, 학습 정확도, 검증 정확도가 출력됩니다. 정상적인 학습에서는 대체로 손실이 내려가고 정확도가 올라갑니다. 결과 가중치는 다음 위치에 저장됩니다.

```text
models/learning/manual_mlp.npz
```

## 우리가 촬영한 데이터로 학습

`02` 단계에서 `data/camera_digits/0`부터 `3`까지 사진을 저장했다면 다음을 실행합니다. 사진 수가 적으므로 더 많은 epoch와 작은 미니배치를 사용합니다.

Windows:

```powershell
.\.venv\Scripts\python.exe python\learning\nn_from_scratch_exercise.py --source camera --digits 0123 --epochs 150 --batch-size 16 --learning-rate 0.05
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/learning/nn_from_scratch_exercise.py --source camera --digits 0123 --epochs 150 --batch-size 16 --learning-rate 0.05
```

촬영 데이터가 20장씩뿐이면 검증 정확도는 사진 한두 장에 따라 크게 변합니다. 학습 정확도만 100%이고 검증 정확도가 낮다면 사진을 외운 과적합 상태입니다.

## 저장한 가중치로 사진 한 장 추론

먼저 `data/camera_digits/2` 등에 있는 실제 PGM 파일 경로 하나를 고릅니다.

Windows:

```powershell
.\.venv\Scripts\python.exe python\learning\nn_from_scratch_exercise.py `
  --load-model models\learning\manual_mlp.npz `
  --predict data\camera_digits\2\실제파일이름.pgm
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/learning/nn_from_scratch_exercise.py \
  --load-model models/learning/manual_mlp.npz \
  --predict data/camera_digits/2/실제파일이름.pgm
```

여기서는 가중치를 변경하지 않습니다. 저장된 `w1`, `b1`, `w2`, `b2`를 불러와 순전파와 `argmax`만 실행합니다.

## 정답 확인

먼저 직접 시도하고 자동 검사 결과를 고친 뒤 다음 파일을 비교합니다.

```text
python/learning/nn_from_scratch_answer.py
```

정답 프로그램도 똑같이 실행할 수 있습니다.

Windows:

```powershell
.\.venv\Scripts\python.exe python\learning\nn_from_scratch_answer.py --source mnist --digits 0123 --per-digit 500 --epochs 15
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/learning/nn_from_scratch_answer.py --source mnist --digits 0123 --per-digit 500 --epochs 15
```

## 직접 바꿔 볼 실험

코드를 완성했다면 한 번에 하나만 바꾸고 결과를 기록합니다.

| 바꿀 값 | 시험할 값 | 관찰할 것 |
|---|---|---|
| `--learning-rate` | `0.001`, `0.1`, `1.0` | 손실이 느리게 감소하는지, 튀거나 `nan`이 되는지 |
| `--hidden-size` | `8`, `64`, `256` | 표현력, 학습 시간, 과적합 변화 |
| `--batch-size` | `1`, `16`, `128` | 손실의 흔들림과 학습 속도 |
| `--epochs` | `1`, `15`, `100` | 부족한 학습과 과적합 차이 |
| `--per-digit` | `20`, `100`, `1000` | 데이터 수가 검증 정확도에 주는 영향 |

추가 코드 실험도 가능합니다.

1. `relu`를 단순히 `return z`로 바꿔 정확도를 비교합니다.
2. 가중치 수정에서 `-`를 `+`로 바꾸면 손실이 어떻게 되는지 확인한 뒤 즉시 되돌립니다.
3. 입력을 `/ 255.0`으로 정규화하지 않았을 때 Softmax와 학습 안정성을 비교합니다.
4. `seed`를 바꾸어 초기 가중치와 데이터 순서가 결과에 주는 영향을 봅니다.

## 기존 CNN 및 Arduino 코드와의 관계

이 실습의 MLP는 원리를 눈으로 보기 위해 단순하게 만든 PC 학습 모델입니다. 실제 프로젝트의 `train_camera_model.py`는 이미지의 공간적 모양을 더 잘 배우는 CNN을 TensorFlow로 학습하고, INT8 TFLite 모델과 `model_data.h`를 생성합니다.

### 현재 실제 프로젝트에서 데이터가 학습되는 위치

실제 촬영 데이터를 학습하는 코드는 `python/train_camera_model.py`이며, 실제
가중치 학습이 시작되는 호출은 다음 `model.fit()`입니다.

```python
history = model.fit(
    x_aug,
    y_aug,
    validation_data=(x_val, y_val),
    epochs=args.epochs,
    batch_size=32,
    callbacks=[...],
)
```

- `x_aug`: 촬영한 28×28 이미지를 위치·밝기·노이즈로 증강한 학습 입력
- `y_aug`: 각 이미지의 정답 클래스
- `x_val`, `y_val`: 가중치를 수정하지 않고 성능만 확인하는 검증 데이터
- `epochs`: 전체 학습 데이터를 반복해서 보는 횟수
- `batch_size`: 가중치를 한 번 수정할 때 사용하는 이미지 수

이 호출 안에서 TensorFlow가 순전파, 교차엔트로피 손실, 역전파, Adam 가중치
수정을 자동으로 반복합니다. 학습이 끝나면 같은 스크립트가 모델을 INT8
TFLite로 바꾸고 Arduino용 `model_data.h`를 생성합니다.

### 실제 실행 파일 세 개의 연결

```text
train_camera_model.py
    └─ PC에서 CNN 학습 → model_data.h 생성
                              ↓ Arduino IDE로 03 업로드
camera_03_inference.ino
    └─ 보드에서 카메라 전처리 → interpreter->Invoke()로 실제 추론
                              ↓ 시리얼 결과 전송
run_inference_gui.py
    └─ 촬영 명령 전송 → 원본·AI 입력·확률·예측 숫자 화면 표시
```

`run_inference_gui.py`는 AI 모델을 직접 실행하지 않습니다. 실제 추론은 보드의
`camera_03_inference.ino`가 수행하고 GUI는 명령과 결과를 주고받아 보여 줍니다.

### learning 폴더는 자동으로 연결되지 않음

`python/learning/`의 파일은 위 실제 파이프라인에 자동으로 import되거나 실행되지
않습니다. 학생이 터미널에서 해당 파일을 직접 실행할 때만 작동합니다.

```text
python/learning의 수동 MLP → models/learning/manual_mlp.npz → PC 실습용 추론
```

이 `.npz` 파일은 `model_data.h`로 자동 변환되지 않으므로 현재 Arduino 추론에는
영향을 주지 않습니다. `learning`은 `model.fit()`이 내부에서 자동으로 수행하는
계산을 학생 눈에 보이게 풀어 쓴 준비 실습입니다.

두 모델의 개념적 흐름은 같습니다.

| 직접 구현 실습 | 실제 프로젝트 |
|---|---|
| `forward()` | TensorFlow/TFLite 모델 실행 |
| `cross_entropy()` | `SparseCategoricalCrossentropy` |
| 직접 작성한 역전파 | TensorFlow 자동 미분 |
| 직접 작성한 SGD | Adam optimizer |
| `.npz` 가중치 | `.keras`, `.tflite`, `model_data.h` |
| PC에서 `predict()` | Nano 33 BLE Sense에서 `interpreter->Invoke()` |

직접 구현한 `.npz` 파일은 Arduino가 바로 읽는 모델 형식이 아닙니다. 원리를 익힌 다음 실제 보드 배포는 기존 `train_camera_model.py` 또는 `train_mnist_model.py`로 생성한 `model_data.h`를 사용합니다.

## 실습 후 답해야 할 질문

1. Softmax 전에 최댓값을 빼도 확률이 바뀌지 않는 이유는 무엇인가?
2. 정답 확률이 올라가면 교차엔트로피 손실은 어떻게 변하는가?
3. 왜 가중치에서 기울기를 더하지 않고 빼는가?
4. 학습에는 정답 라벨이 필요하지만 추론에는 필요하지 않은 이유는 무엇인가?
5. 학습 정확도와 검증 정확도의 차이가 커지는 것은 무엇을 뜻하는가?
6. Arduino 추론 중에는 어떤 TODO 단계가 실행되고 어떤 단계는 실행되지 않는가?
