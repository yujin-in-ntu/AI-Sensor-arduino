"""0단계 학생용: AI에 필요한 Python·NumPy 문법 한 줄 빈칸입니다.

각 함수에는 `____` 빈칸이 하나 있습니다. 위에서부터 하나씩 바꾸고
check_python_numpy_basics.py를 다시 실행하세요.
"""

import numpy as np


def make_array(numbers):
    """빈칸 1: Python 리스트를 NumPy 배열로 바꾸는 함수 이름은?"""
    return np.____(numbers, dtype=np.float32)


def get_shape(values):
    """빈칸 2: 배열의 모양을 알려주는 점(.) 뒤의 이름은?"""
    return values.____


def relu_one_line(values):
    """빈칸 3: 0과 각 숫자 중 큰 값을 선택하는 NumPy 함수는?"""
    return np.____(0, values)


def maximum_per_row(values):
    """빈칸 4: 최댓값을 구하는 NumPy 함수는?"""
    return np.____(values, axis=1, keepdims=True)


def sum_per_row(values):
    """빈칸 5: 합계를 구하는 NumPy 함수는?"""
    return np.____(values, axis=1, keepdims=True)


def transpose(values):
    """빈칸 6: 행과 열을 바꾸는 점(.) 뒤의 한 글자는?"""
    return values.____


def matrix_multiply(left, right):
    """빈칸 7: 행렬 곱셈 함수 이름은? 이 계산은 left @ right와 같습니다."""
    return np.____(left, right)


def get_first_weight(parameters):
    """빈칸 8: 딕셔너리에서 첫 번째 가중치를 꺼낼 문자열은?"""
    return parameters["____"]


def select_correct_probabilities(probabilities, labels):
    """빈칸 9: 0부터 순서대로 행 번호를 만드는 NumPy 함수는?"""
    rows = np.____(len(labels))
    return probabilities[rows, labels]


def negative_log(values):
    """빈칸 10: 자연로그를 계산하는 NumPy 함수는?"""
    return -np.____(values)


def average(values):
    """빈칸 11: 평균을 계산하는 NumPy 함수는?"""
    return np.____(values)


def best_class(probabilities):
    """빈칸 12: 가장 큰 값의 위치를 찾는 NumPy 함수는?"""
    return np.____(probabilities, axis=1)


def sgd_step(weight, gradient, learning_rate):
    """빈칸 13: 첫 번째 배열에서 두 번째 배열을 빼는 NumPy 함수는?"""
    return np.____(weight, learning_rate * gradient)
