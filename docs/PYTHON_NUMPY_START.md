# 실제 AI 코드에 필요한 Python·NumPy 문법

이 문서는 별도의 장난감 문법 문제를 풀기 위한 문서가 아닙니다. 바로 다음 단계의
`python/train_camera_model.py`에서 실제 카메라 학습 수식을 완성할 때 필요한 문법만
먼저 익힙니다.

문법을 모두 외운 뒤 시작할 필요는 없습니다. 아래 예제를 한 번 읽고, 학생용
코드의 각 TODO 바로 위에 있는 `문법 미니 노트`를 다시 보면서 작성하세요.

## 문자열, 숫자, 불리언, 변수

```python
activation = "relu"   # 문자열: 따옴표 필요
batch_size = 32       # 정수: 따옴표 없음
pixel_max = 255.0     # 실수: 소수점 있음
from_logits = True    # 불리언: True 또는 False
class_count = 4       # 변수 이름: 따옴표 없음
```

`"class_count"`는 글자 자체이고, `class_count`는 변수 안에 저장된 값입니다.
CNN의 마지막 출력 수에는 글자가 아니라 변수 `class_count`가 들어가야 합니다.

## 점과 괄호

```python
np.asarray(images)
model.compile(...)
model.fit(...)
```

- `np.asarray`: `np`라는 NumPy 도구 상자에서 `asarray` 함수를 찾습니다.
- `model.compile`: `model` 객체가 가진 학습 설정 기능을 찾습니다.
- 괄호 `()` 안에는 함수에 전달할 값을 씁니다.

즉, 점 `.`은 “앞의 대상이 가진 기능이나 정보에 접근한다”는 뜻입니다.

## 위치인자와 키워드 인자

```python
tf.keras.layers.Conv2D(
    filters=8,
    kernel_size=(3, 3),
    activation="relu",
)
```

- `filters=8`: 필터 개수를 이름과 함께 전달하는 키워드 인자
- `kernel_size=(3, 3)`: 필터의 높이와 너비를 이름과 함께 전달
- `activation="relu"`: 활성화 함수 이름을 직접 지정
- `=`: 오른쪽 값을 왼쪽 이름에 전달하거나 저장

비교할 때는 `==`, 더 큰지 확인할 때는 `>`를 사용합니다. 저장하는 `=`와
같은지 비교하는 `==`는 역할이 다릅니다.

## 리스트와 튜플

```python
layers = [layer1, layer2, layer3]
shape = (28, 28, 1)
```

- 대괄호 `[]`: 여러 항목을 순서대로 담는 리스트
- 소괄호 `(28, 28, 1)`: 이미지의 높이·너비·채널 모양을 나타내는 튜플
- `metrics=["accuracy"]`: 평가 기준을 하나 이상 받을 수 있어 리스트로 전달

## 배열과 shape

```python
images.shape
```

이미지가 80장이라면 처음 읽은 배열은 보통 `(80, 28, 28)`입니다. CNN은 채널
축까지 필요하므로 `(80, 28, 28, 1)`로 바꿉니다.

```python
array[..., np.newaxis]
```

- `...`: 앞쪽 축은 그대로 유지
- `np.newaxis`: 길이가 1인 새 축 추가

## 배열 전체에 한 번에 계산하기

```python
normalized = pixels / 255.0
```

NumPy 배열을 실수 하나로 나누면 반복문을 직접 쓰지 않아도 모든 픽셀에 같은
나눗셈이 적용됩니다. 0~255 픽셀이 0~1 범위로 바뀝니다.

## TensorFlow 배열 전체에 학습 수식 적용하기

```python
maximum = tf.reduce_max(logits, axis=1, keepdims=True)
exponentials = tf.exp(logits - maximum)
total = tf.reduce_sum(exponentials, axis=1, keepdims=True)
probabilities = exponentials / total
losses = -tf.math.log(answer_probabilities + 1e-7)
```

- `tf.reduce_max`: 지정한 방향에서 가장 큰 값을 선택
- `tf.exp`: 배열의 모든 값에 지수함수를 적용
- `tf.reduce_sum`: 지정한 방향의 값들을 더함
- `axis=1`: 각 이미지가 가진 클래스 점수 방향으로 계산
- `keepdims=True`: 나중에 원래 배열과 뺄셈·나눗셈할 수 있도록 차원을 유지
- `tf.math.log`: 자연로그 계산
- 앞의 `-`: 정답 확률이 작을수록 손실이 커지도록 부호를 바꿈

이 연산들은 실제 `model.compile(loss=...)`에 전달되는 손실함수 안에서 실행됩니다.
TensorFlow는 이 계산 과정을 기록한 뒤 `tape.gradient()`로 각 가중치의 기울기를
자동 계산합니다.

## 함수 만들기와 결과 돌려주기

```python
def select_best_index(scores):
    return int(np.argmax(scores))
```

- `def`: 함수를 정의
- `scores`: 함수가 받는 값
- `return`: 계산 결과를 함수 밖으로 돌려줌
- `np.argmax`: 가장 큰 값의 위치를 반환
- `int(...)`: NumPy 정수를 일반 Python 정수로 변환

## 들여쓰기

Python은 들여쓰기로 코드의 소속을 구분합니다.

```python
if confidence > best_confidence:
    best_confidence = confidence
```

두 번째 줄은 `if` 안에 있으므로 공백 4칸을 유지해야 합니다. 탭과 공백을 섞지
않는 것이 안전합니다.

## Arduino C++에서 추가되는 문법

```cpp
float normalizePixel(byte pixel) {
  return pixel / 255.0f;
}
```

- `float`: 함수가 소수를 반환한다는 뜻
- `byte pixel`: `pixel`이라는 0~255 정수를 받음
- `{}`: 함수나 조건문의 범위
- `;`: 한 문장의 끝
- `255.0f`: Arduino에서 사용하는 float 실수

참조 기호 `&`가 붙은 매개변수를 수정하면 함수 밖의 원래 변수도 바뀝니다.

```cpp
void updateBest(float probability, float& bestProbability) {
  if (probability > bestProbability) {
    bestProbability = probability;
  }
}
```

## 이제 실제 코드로 이동

문법을 읽었다면 [카메라 CNN 학습 코드 읽기·Arduino 추론 실습](AI_CODE_LAB.md)으로
이동합니다. Python은 수정하지 않고 실제 학습 흐름을 함께 읽습니다. 학생이 직접
수정하는 파일은 Arduino 추론 연습 스케치입니다.

```text
arduino/camera_03_inference_exercise/camera_03_inference_exercise.ino
```

완성된 Python 코드로 공개 예제나 직접 촬영한 데이터를 학습하고, 생성된 INT8
모델을 Nano 33 BLE Sense Lite에 업로드해 같은 추론 GUI로 확인할 수 있습니다.
