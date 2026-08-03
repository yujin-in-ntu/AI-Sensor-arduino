"""실제로 실행되는 Python 학습·Arduino 추론 파일의 빈칸을 검사합니다."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

PYTHON_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PYTHON_DIR.parent
PYTHON_TRAINING = PYTHON_DIR / "train_camera_model.py"
ARDUINO_EXERCISE = (
    PROJECT_ROOT
    / "arduino"
    / "camera_03_inference_exercise"
    / "camera_03_inference_exercise.ino"
)

PYTHON_HINTS = {
    "____PY1____": "픽셀 0~255를 0~1로 만드는 나눗셈의 오른쪽 값",
    "____PY2____": "음수를 0으로 만드는 활성화 함수 이름을 문자열로 작성",
    "____PY3____": "2x2 풀링 크기를 정수로 작성",
    "____PY4____": "마지막 출력 개수는 함수가 받은 클래스 수 변수",
    "____PY5____": "Adam 최적화 방법의 이름을 문자열로 작성",
    "____PY6____": "마지막 층이 logits를 출력하는지 나타내는 불리언",
    "____PY7____": "정확도를 뜻하는 Keras 평가 이름을 문자열로 작성",
    "____PY8____": "model 객체의 실제 학습 메서드 이름",
    "____PY9____": "한 번에 학습하는 이미지 수",
    "____PY10____": "가장 큰 값의 위치를 반환하는 NumPy 함수 이름",
}

ARDUINO_HINTS = {
    "____ARD1____": "byte 픽셀을 0~1 실수로 만드는 식",
    "____ARD2____": "정규화 값을 scale로 나누고 zeroPoint를 더하는 식",
    "____ARD3____": "INT8 출력에서 zeroPoint를 빼고 scale을 곱하는 식",
    "____ARD4____": "큰 exp 값을 막도록 maxLogit을 뺀 안정적인 지수식",
    "____ARD5____": "현재 probabilities[i]를 total로 나누는 복합 대입 연산",
    "____ARD6____": "현재 확률이 지금까지 최고 확률보다 큰지 비교하는 조건",
    "____ARD7____": "bestProbability를 현재 probabilities[i]로 갱신하는 문장",
    "____ARD8____": "bestIndex를 현재 반복 위치 i로 갱신하는 문장",
}


def remaining_tokens(path: Path, hints: dict[str, str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [token for token in hints if token in text]


def report_remaining(path: Path, hints: dict[str, str]) -> bool:
    tokens = remaining_tokens(path, hints)
    if not tokens:
        return False
    print(f"\n아직 남은 빈칸: {path}")
    for token in tokens:
        print(f"- {token}: {hints[token]}")
    return True


def import_actual_training():
    spec = importlib.util.spec_from_file_location("actual_camera_training", PYTHON_TRAINING)
    if spec is None or spec.loader is None:
        raise RuntimeError("실제 Python 학습 파일을 불러올 수 없습니다.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def check_python_behavior() -> None:
    import numpy as np
    import tensorflow as tf

    training = import_actual_training()
    images = [
        np.zeros((28, 28), dtype=np.uint8),
        np.full((28, 28), 255, dtype=np.uint8),
    ]
    normalized = training.normalize_images(images)
    assert normalized.shape == (2, 28, 28, 1), "정규화 후 shape가 다릅니다."
    assert normalized.dtype == np.float32, "정규화 dtype은 float32여야 합니다."
    assert float(normalized.min()) == 0.0, "검은 픽셀은 0이어야 합니다."
    assert float(normalized.max()) == 1.0, "밝은 픽셀은 1이어야 합니다."
    print("[통과 1/5] 실제 이미지 정규화")

    model = training.build_model(4)
    assert model.output_shape == (None, 4), "마지막 출력 개수는 4여야 합니다."
    conv_count = sum(
        isinstance(layer, tf.keras.layers.Conv2D) for layer in model.layers
    )
    pool_count = sum(
        isinstance(layer, tf.keras.layers.MaxPooling2D) for layer in model.layers
    )
    assert conv_count == 2 and pool_count == 2, (
        "Conv2D와 MaxPooling2D가 각각 2개여야 합니다."
    )
    print("[통과 2/5] 실제 CNN 구조")

    model = training.compile_model(model)
    assert isinstance(model.optimizer, tf.keras.optimizers.Adam), (
        "optimizer는 Adam이어야 합니다."
    )
    assert getattr(model.loss, "from_logits", False) is True, (
        "loss의 from_logits는 True여야 합니다."
    )
    print("[통과 3/5] compile 설정")

    x_train = np.zeros((8, 28, 28, 1), dtype=np.float32)
    y_train = np.array([0, 1, 2, 3, 0, 1, 2, 3], dtype=np.int64)
    history = training.train_model(
        model,
        x_train,
        y_train,
        x_train[:4],
        y_train[:4],
        epochs=1,
    )
    assert "loss" in history.history, "fit()의 학습 기록에 loss가 없습니다."
    assert "val_loss" in history.history, (
        "fit()에 validation_data가 전달되지 않았습니다."
    )
    print("[통과 4/5] fit() 실제 1 epoch")

    assert training.select_best_index(np.array([0.1, 0.7, 0.2])) == 1
    print("[통과 5/5] argmax 예측")
    print("Python 핵심 빈칸 완료! 이제 실제 기본 학습 명령을 실행할 수 있습니다.")


def check_arduino_structure() -> None:
    text = ARDUINO_EXERCISE.read_text(encoding="utf-8")
    required = [
        "bool prepareInput()",
        "void sendPrediction(bool guiMode)",
        "inputTensor->data.int8[i]",
        "outputTensor->data.int8[i]",
        "interpreter->Invoke()",
    ]
    missing = [name for name in required if name not in text]
    if missing:
        raise AssertionError(
            "Arduino 실제 추론 흐름이 없습니다: " + ", ".join(missing)
        )
    print("Arduino 핵심 빈칸 완료! Arduino IDE의 컴파일 버튼으로 확인하세요.")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="실제 파이프라인 빈칸 검사")
    parser.add_argument(
        "--part", choices=["python", "arduino", "all"], default="all"
    )
    args = parser.parse_args()

    failed = False
    if args.part in {"python", "all"}:
        failed |= report_remaining(PYTHON_TRAINING, PYTHON_HINTS)
    if args.part in {"arduino", "all"}:
        failed |= report_remaining(ARDUINO_EXERCISE, ARDUINO_HINTS)
    if failed:
        print("\n위 힌트를 읽고 빈칸을 더 채운 뒤 다시 검사하세요.")
        return 1

    try:
        if args.part in {"python", "all"}:
            check_python_behavior()
        if args.part in {"arduino", "all"}:
            check_arduino_structure()
    except Exception as error:
        print(f"\n검사 실패: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
