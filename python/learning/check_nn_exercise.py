"""TODO 1~8을 자동 확인하는 간단한 채점 프로그램입니다."""

from __future__ import annotations

import sys
import traceback
from collections.abc import Callable

import numpy as np

import nn_from_scratch_answer as answer
import nn_from_scratch_exercise as student
from nn_data import configure_console


def assert_close(actual: np.ndarray | float, expected: np.ndarray | float) -> None:
    if not np.allclose(actual, expected, atol=1e-6, rtol=1e-5):
        raise AssertionError(f"계산값이 정답과 다릅니다.\n계산: {actual}\n기대: {expected}")


def make_case() -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray]:
    parameters = answer.initialize_parameters(4, 3, 2, seed=7)
    x = np.asarray(
        [[0.0, 0.5, 1.0, 0.2], [1.0, 0.1, 0.0, 0.8], [0.3, 0.7, 0.2, 0.9]],
        dtype=np.float32,
    )
    y = np.asarray([0, 1, 0], dtype=np.int64)
    return parameters, x, y


def check_relu() -> None:
    z = np.asarray([[-2.0, 0.0, 3.0]], dtype=np.float32)
    assert_close(student.relu(z), answer.relu(z))


def check_softmax() -> None:
    # 큰 점수를 넣어도 overflow 없이 계산되어야 합니다.
    logits = np.asarray([[1000.0, 1001.0], [-2.0, 3.0]], dtype=np.float32)
    actual = student.softmax(logits)
    assert_close(actual, answer.softmax(logits))
    assert_close(np.sum(actual, axis=1), np.ones(2))


def check_cross_entropy() -> None:
    probs = np.asarray([[0.8, 0.2], [0.25, 0.75]], dtype=np.float32)
    y = np.asarray([0, 1], dtype=np.int64)
    assert_close(student.cross_entropy(probs, y), answer.cross_entropy(probs, y))


def check_forward() -> None:
    parameters, x, _ = make_case()
    actual = student.forward(parameters, x)
    expected = answer.forward(parameters, x)
    for name in ("z1", "a1", "logits", "probs"):
        assert_close(actual[name], expected[name])


def check_output_gradients() -> None:
    parameters, x, y = make_case()
    cache = answer.forward(parameters, x)
    actual = student.output_layer_gradients(parameters, cache, y)
    expected = answer.output_layer_gradients(parameters, cache, y)
    for actual_item, expected_item in zip(actual, expected):
        assert_close(actual_item, expected_item)


def check_hidden_gradients() -> None:
    parameters, x, y = make_case()
    cache = answer.forward(parameters, x)
    d_a1, _, _ = answer.output_layer_gradients(parameters, cache, y)
    actual = student.hidden_layer_gradients(cache, d_a1)
    expected = answer.hidden_layer_gradients(cache, d_a1)
    for actual_item, expected_item in zip(actual, expected):
        assert_close(actual_item, expected_item)


def check_update() -> None:
    parameters, _, _ = make_case()
    student_parameters = {name: value.copy() for name, value in parameters.items()}
    answer_parameters = {name: value.copy() for name, value in parameters.items()}
    gradients = {name: np.full_like(value, 0.25) for name, value in parameters.items()}
    student.update_parameters(student_parameters, gradients, learning_rate=0.1)
    answer.update_parameters(answer_parameters, gradients, learning_rate=0.1)
    for name in parameters:
        assert_close(student_parameters[name], answer_parameters[name])


def check_predict() -> None:
    parameters, x, _ = make_case()
    actual_classes, actual_probs = student.predict(parameters, x)
    expected_classes, expected_probs = answer.predict(parameters, x)
    assert_close(actual_classes, expected_classes)
    assert_close(actual_probs, expected_probs)


def main() -> None:
    configure_console()
    checks: list[tuple[str, Callable[[], None]]] = [
        ("TODO 1 ReLU", check_relu),
        ("TODO 2 Softmax", check_softmax),
        ("TODO 3 교차엔트로피", check_cross_entropy),
        ("TODO 4 순전파", check_forward),
        ("TODO 5 출력층 역전파", check_output_gradients),
        ("TODO 6 은닉층 역전파", check_hidden_gradients),
        ("TODO 7 SGD 업데이트", check_update),
        ("TODO 8 추론", check_predict),
    ]

    passed = 0
    for name, check in checks:
        try:
            check()
        except NotImplementedError as error:
            print(f"[빈칸] {name}: {error}")
        except Exception as error:  # 학생에게 긴 traceback 대신 핵심만 먼저 보여 줍니다.
            print(f"[수정 필요] {name}: {error}")
            if "--debug" in sys.argv:
                traceback.print_exc()
        else:
            passed += 1
            print(f"[통과] {name}")

    print(f"\n결과: {passed}/8 통과")
    if passed == len(checks):
        print("모든 핵심 계산이 맞습니다. 이제 실제 데이터 학습을 실행하세요!")
    else:
        print("빈칸을 하나씩 채운 뒤 이 명령을 다시 실행하세요.")


if __name__ == "__main__":
    main()
