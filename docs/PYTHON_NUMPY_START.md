# 0단계: Python과 NumPy 문법부터 채우기

이 문서는 Python을 처음 보는 학생을 위한 준비 실습입니다. 신경망 수식보다 먼저 코드의 점(`.`), 괄호, 배열, 함수가 무엇인지 익힙니다.

## Arduino부터 배워야 하나요?

이 프로젝트의 역할은 다음처럼 나뉩니다.

| 하고 싶은 일 | 주로 수정할 언어·파일 |
|---|---|
| 학습 데이터 읽기·변형 | Python |
| 신경망 구조, Softmax, 손실함수, 역전파 수정 | Python |
| 학습률, epoch, batch 크기 실험 | Python |
| PC에서 학습·정확도 확인 | Python |
| 카메라에서 종이와 숫자 찾기 | Python과 Arduino 양쪽 |
| 학습 완료 모델을 보드에서 실행 | Arduino C++ |
| 센서 입력, 버튼, LED, 시리얼 출력 수정 | Arduino C++ |

따라서 **AI가 어떻게 학습하는지 직접 코딩하는 수업은 Python부터 시작하는 것이 맞습니다.** Arduino는 학습이 끝난 모델을 실제 기기에서 실행하는 단계에서 배워도 됩니다.

## `import numpy as np`는 무슨 뜻인가요?

```python
import numpy as np
```

- `numpy`: 배열과 행렬 계산 도구가 들어 있는 외부 라이브러리입니다.
- `import`: 다른 파일이나 라이브러리의 기능을 가져옵니다.
- `as np`: 긴 이름 `numpy` 대신 짧은 별명 `np`를 사용하겠다는 뜻입니다.

따라서 아래 두 표현은 같은 의미입니다.

```python
numpy.array([1, 2, 3])
np.array([1, 2, 3])
```

보통 전 세계 NumPy 예제에서 `np`라는 별명을 사용합니다.

## 점 `.`은 왜 사용하나요?

점은 **앞에 있는 대상이 가지고 있는 기능이나 정보에 접근한다**는 표시입니다.

```python
np.array
```

`np`라는 도구 상자 안에서 `array`라는 기능을 찾는다는 뜻입니다.

```python
image.shape
```

`image` 배열이 가지고 있는 `shape` 정보를 가져온다는 뜻입니다.

```python
image.reshape(1, 784)
```

`image` 배열이 가지고 있는 `reshape` 기능을 실행한다는 뜻입니다.

다음 세 종류를 구별하면 좋습니다.

| 코드 | 종류 | 의미 |
|---|---|---|
| `np.array(...)` | 라이브러리 함수 | NumPy 도구 상자의 배열 생성 기능 실행 |
| `image.reshape(...)` | 배열의 메서드 | `image`가 가진 모양 변경 기능 실행 |
| `image.shape` | 배열의 속성 | `image`가 가진 모양 정보 읽기 |

함수나 메서드를 실행할 때는 `()`가 붙지만 단순한 정보인 속성에는 보통 `()`가 없습니다.

## 함수 한 개 읽는 법

```python
def make_array(numbers):
    result = np.array(numbers)
    return result
```

한 줄씩 읽으면 다음과 같습니다.

1. `def`: 새로운 함수를 정의합니다.
2. `make_array`: 함수 이름입니다.
3. `numbers`: 함수가 받을 입력입니다.
4. `:`: 들여쓰기된 함수 내용이 시작됩니다.
5. `result =`: 오른쪽 계산 결과를 왼쪽 이름에 저장합니다.
6. `return`: 함수 밖으로 결과를 돌려줍니다.

함수 사용은 다음과 같습니다.

```python
answer = make_array([1, 2, 3])
```

## 괄호와 대괄호의 차이

### 소괄호 `()`

함수를 실행하거나 설정값을 전달합니다.

```python
np.sum(values, axis=1)
```

### 대괄호 `[]`

목록을 만들거나 특정 위치의 값을 선택합니다.

```python
numbers = [10, 20, 30]
print(numbers[0])
```

Python은 위치를 0부터 세므로 `numbers[0]`은 `10`입니다.

딕셔너리에서는 위치 대신 이름으로 값을 찾습니다.

```python
parameters = {"w1": 0.5, "b1": 0.1}
weight = parameters["w1"]
```

## `np.array`는 무엇인가요?

Python 리스트를 빠른 숫자 계산용 NumPy 배열로 바꿉니다.

```python
python_list = [1, 2, 3]
numpy_array = np.array(python_list)
```

NumPy 배열은 모든 원소에 계산을 한 번에 적용할 수 있습니다.

```python
numpy_array * 2
# [2, 4, 6]
```

## `.shape`는 무엇인가요?

배열의 모양을 알려주는 속성입니다.

```python
image = np.zeros((28, 28))
print(image.shape)
# (28, 28)
```

숫자 사진 32장을 한 번에 펼쳐 넣으면 다음 모양을 가질 수 있습니다.

```text
(32, 784)
```

- `32`: 이미지 개수, 즉 미니배치 크기
- `784`: 이미지 한 장의 `28 × 28` 픽셀

## `axis`는 무엇인가요?

어느 방향으로 계산할지 지정합니다.

```python
values = np.array([
    [1, 2, 3],
    [4, 5, 6],
])
```

```python
np.sum(values, axis=0)  # 위아래로 더함: [5, 7, 9]
np.sum(values, axis=1)  # 각 가로줄을 더함: [6, 15]
```

Softmax에서는 이미지 한 장의 숫자별 점수들을 더해야 하므로 주로 `axis=1`을 사용합니다.

## `=`와 `==`는 다릅니다

```python
score = 10
```

`=`은 값을 저장합니다.

```python
score == 10
```

`==`는 두 값이 같은지 질문하며 결과는 `True` 또는 `False`입니다.

```python
z > 0
```

이 비교는 ReLU 역전파에서 양수였던 위치를 찾을 때 사용합니다.

## `*`, `@`, `.T`의 차이

```python
a * b
```

`*`는 같은 위치의 원소끼리 곱합니다.

```python
a @ b
```

`@`는 행렬 곱셈입니다. 신경망에서 입력과 가중치를 연결할 때 사용합니다.

```python
a.T
```

`.T`는 행과 열을 바꿉니다. 역전파에서 가중치와 같은 모양의 기울기를 만들 때 사용합니다.

## 0단계 학생용 빈칸

다음 파일을 엽니다.

```text
python/learning/python_numpy_basics_exercise.py
```

각 함수에는 `____`가 딱 한 곳씩 있습니다.

```python
def get_shape(values):
    return values.____
```

점 뒤에 배열의 모양을 알려주는 이름을 넣는 식입니다. 복잡한 신경망 수식을 한꺼번에 작성하지 않고 다음 문법을 하나씩 연습합니다.

1. `np.array`
2. `.shape`
3. `np.maximum`
4. `np.max`
5. `np.sum`
6. `.T`
7. `np.matmul`
8. 딕셔너리의 `"w1"`
9. `np.arange`
10. `np.log`
11. `np.mean`
12. `np.argmax`
13. `np.subtract`

## 0단계 자동 확인

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\learning\check_python_numpy_basics.py
```

macOS/Ubuntu:

```bash
./.venv/bin/python python/learning/check_python_numpy_basics.py
```

처음에는 `0/13 통과`가 정상입니다. 위에서부터 빈칸 하나만 채우고 저장한 다음 같은 명령을 다시 실행합니다.

정답은 다음 파일에 있습니다.

```text
python/learning/python_numpy_basics_answer.py
```

직접 생각하고 자동 확인을 해본 뒤에 정답을 비교하세요.

## 다음 단계

0단계에서 `13/13 통과`가 나오면 [Softmax·역전파·추론 실습](AI_CODE_LAB.md)으로 이동합니다.

```text
0단계: Python·NumPy 한 줄 문법 빈칸
   ↓
1단계: ReLU·Softmax·손실·역전파 함수 빈칸
   ↓
2단계: MNIST 또는 카메라 사진 실제 학습
   ↓
3단계: Arduino에서 학습 완료 모델 추론
```
