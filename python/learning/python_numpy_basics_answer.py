"""0단계 정답: AI 코드에서 자주 쓰는 Python·NumPy 문법입니다."""

import numpy as np


def make_array(numbers):
    """Python 리스트를 NumPy 배열로 바꿉니다."""
    return np.array(numbers, dtype=np.float32)


def get_shape(values):
    """배열이 몇 행 몇 열인지 확인합니다."""
    return values.shape


def relu_one_line(values):
    """0과 각 숫자 중 큰 값을 선택합니다."""
    return np.maximum(0, values)


def maximum_per_row(values):
    """각 행에서 가장 큰 값을 찾습니다."""
    return np.max(values, axis=1, keepdims=True)


def sum_per_row(values):
    """각 행의 숫자를 더합니다."""
    return np.sum(values, axis=1, keepdims=True)


def transpose(values):
    """행과 열을 뒤집습니다."""
    return values.T


def matrix_multiply(left, right):
    """두 배열을 행렬 곱셈합니다. left @ right와 같습니다."""
    return np.matmul(left, right)


def get_first_weight(parameters):
    """딕셔너리에서 w1이라는 이름의 값을 꺼냅니다."""
    return parameters["w1"]


def select_correct_probabilities(probabilities, labels):
    """각 사진에서 정답 위치의 확률만 선택합니다."""
    rows = np.arange(len(labels))
    return probabilities[rows, labels]


def negative_log(values):
    """확률에 자연로그를 적용하고 부호를 바꿉니다."""
    return -np.log(values)


def average(values):
    """여러 손실의 평균을 구합니다."""
    return np.mean(values)


def best_class(probabilities):
    """각 행에서 가장 큰 값이 있는 위치를 찾습니다."""
    return np.argmax(probabilities, axis=1)


def sgd_step(weight, gradient, learning_rate):
    """기울기의 반대 방향으로 가중치를 한 번 움직입니다."""
    return np.subtract(weight, learning_rate * gradient)
