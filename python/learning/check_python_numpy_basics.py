"""0단계 Python·NumPy 문법 빈칸 13개를 자동 확인합니다."""

import traceback

import numpy as np

import python_numpy_basics_answer as answer
import python_numpy_basics_exercise as student
from nn_data import configure_console


def same(actual, expected):
    if isinstance(expected, tuple):
        if actual != expected:
            raise AssertionError(f"결과가 다릅니다: {actual} != {expected}")
    elif not np.allclose(actual, expected):
        raise AssertionError(f"결과가 다릅니다: {actual} != {expected}")


def cases():
    values = np.array([[-2.0, 0.0, 3.0], [4.0, 1.0, -1.0]])
    probabilities = np.array([[0.7, 0.2, 0.1], [0.1, 0.3, 0.6]])
    labels = np.array([0, 2])
    left = np.array([[1.0, 2.0]])
    right = np.array([[3.0, 4.0], [5.0, 6.0]])
    parameters = {"w1": np.array([1.0, 2.0]), "b1": np.array([0.0])}
    weight = np.array([1.0, 2.0])
    gradient = np.array([0.2, -0.4])

    return [
        ("빈칸 1 np.array", lambda: student.make_array([1, 2, 3]), lambda: answer.make_array([1, 2, 3])),
        ("빈칸 2 .shape", lambda: student.get_shape(values), lambda: answer.get_shape(values)),
        ("빈칸 3 np.maximum", lambda: student.relu_one_line(values), lambda: answer.relu_one_line(values)),
        ("빈칸 4 np.max", lambda: student.maximum_per_row(values), lambda: answer.maximum_per_row(values)),
        ("빈칸 5 np.sum", lambda: student.sum_per_row(values), lambda: answer.sum_per_row(values)),
        ("빈칸 6 .T", lambda: student.transpose(values), lambda: answer.transpose(values)),
        ("빈칸 7 np.matmul", lambda: student.matrix_multiply(left, right), lambda: answer.matrix_multiply(left, right)),
        ("빈칸 8 딕셔너리", lambda: student.get_first_weight(parameters), lambda: answer.get_first_weight(parameters)),
        ("빈칸 9 np.arange", lambda: student.select_correct_probabilities(probabilities, labels), lambda: answer.select_correct_probabilities(probabilities, labels)),
        ("빈칸 10 np.log", lambda: student.negative_log(np.array([0.8, 0.2])), lambda: answer.negative_log(np.array([0.8, 0.2]))),
        ("빈칸 11 np.mean", lambda: student.average(np.array([1.0, 2.0, 3.0])), lambda: answer.average(np.array([1.0, 2.0, 3.0]))),
        ("빈칸 12 np.argmax", lambda: student.best_class(probabilities), lambda: answer.best_class(probabilities)),
        ("빈칸 13 np.subtract", lambda: student.sgd_step(weight, gradient, 0.1), lambda: answer.sgd_step(weight, gradient, 0.1)),
    ]


def main():
    configure_console()
    passed = 0
    all_cases = cases()

    for name, student_call, answer_call in all_cases:
        try:
            same(student_call(), answer_call())
        except Exception as error:
            print(f"[아직 빈칸] {name}: {type(error).__name__}")
            if "--debug" in __import__("sys").argv:
                traceback.print_exc()
        else:
            passed += 1
            print(f"[통과] {name}")

    print(f"\n결과: {passed}/{len(all_cases)} 통과")
    if passed == len(all_cases):
        print("0단계 완료! 이제 nn_from_scratch_exercise.py의 TODO 1로 이동하세요.")
    else:
        print("학생용 파일에서 해당 ____ 한 곳만 채우고 다시 실행하세요.")


if __name__ == "__main__":
    main()
