"""실제 카메라 CNN 학습 코드의 핵심 문법을 채우는 학생용 파일입니다.

이 파일은 장난감 신경망이 아닙니다. TODO를 모두 채우면 실제 촬영 데이터 또는
저장소의 공개 예제 데이터를 학습하고, INT8 TFLite 모델과 Arduino의
model_data.h를 생성합니다.

진행 방법
1. 위에서 아래로 ``____PY...____`` 토큰 10개를 찾습니다.
2. 각 TODO 위의 '문법 미니 노트'와 '생각 질문'을 읽고 코드를 작성합니다.
3. check_actual_pipeline_exercise.py --part python으로 확인합니다.
4. 검사 통과 후 이 파일을 직접 실행해 실제 모델을 학습합니다.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np
import tensorflow as tf

# 이 파일은 python/learning 안에 있고, 실제 학습 도구는 바로 위 python 폴더에 있습니다.
PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PYTHON_DIR.parent
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

import train_camera_model as core  # noqa: E402


def normalize_images(images: list[np.ndarray]) -> np.ndarray:
    """uint8 이미지 목록을 CNN 입력인 float32 0~1 배열로 바꿉니다."""

    # TODO PY1: 데이터 정규화
    # 문법 미니 노트
    # - np.asarray(목록, dtype=자료형)은 목록을 NumPy 배열로 바꿉니다.
    # - [..., np.newaxis]는 맨 뒤에 채널 축 1개를 추가합니다.
    # - / 연산은 배열의 모든 값에 한꺼번에 적용됩니다.
    # 생각 질문: 카메라 픽셀의 최댓값을 어떤 실수로 나누면 0~1이 될까요?
    return np.asarray(images, dtype=np.float32)[..., np.newaxis] / ____PY1____


def load_student_dataset(
    root: Path, digits: list[int]
) -> tuple[np.ndarray, np.ndarray]:
    """실제 PGM 파일을 읽고 학생이 작성한 정규화를 적용합니다."""

    images: list[np.ndarray] = []
    labels: list[int] = []
    for class_index, digit in enumerate(digits):
        for path in sorted((root / str(digit)).glob("*.pgm")):
            images.append(core.read_pgm(path))
            labels.append(class_index)
    if not images:
        raise ValueError(f"학습 이미지가 없습니다: {root}")
    return normalize_images(images), np.asarray(labels, dtype=np.int64)


def build_student_model(class_count: int) -> tf.keras.Model:
    """실제 Arduino에 넣을 작은 CNN을 만듭니다."""

    # TODO PY2~PY4: CNN 구조
    # 문법 미니 노트
    # - 함수(위치인자, 이름=값)는 함수를 호출하는 기본 형태입니다.
    # - 문자열은 "따옴표"로 감쌉니다. 변수 이름에는 따옴표를 쓰지 않습니다.
    # - Sequential([층1, 층2, ...])은 층을 위에서 아래 순서로 연결합니다.
    # 생각 질문
    # - 음수를 0으로 만드는 활성화 함수 이름은 무엇일까요?
    # - 2x2 풀링의 크기는 어떤 정수 하나로 쓸 수 있을까요?
    # - 마지막 출력 개수는 고정 숫자일까요, 함수가 받은 class_count일까요?
    return tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(28, 28, 1)),
            tf.keras.layers.Conv2D(8, 3, activation=____PY2____),
            tf.keras.layers.MaxPooling2D(____PY3____),
            tf.keras.layers.Conv2D(16, 3, activation="relu"),
            tf.keras.layers.MaxPooling2D(2),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(32, activation="relu"),
            tf.keras.layers.Dense(____PY4____),
        ]
    )


def compile_student_model(model: tf.keras.Model) -> tf.keras.Model:
    """학습에 사용할 최적화 방법, 손실함수, 평가값을 지정합니다."""

    # TODO PY5~PY7: compile
    # 문법 미니 노트
    # - optimizer="이름"처럼 Keras가 아는 이름을 문자열로 전달할 수 있습니다.
    # - True와 False는 따옴표를 쓰지 않는 Python 불리언입니다.
    # - metrics는 여러 평가 기준을 담으므로 ["..."] 리스트 형태입니다.
    # 생각 질문
    # - 이 프로젝트가 사용하는 적응형 최적화 방법은 Adam입니다.
    # - 마지막 Dense에 Softmax가 없으므로 출력은 확률이 아닌 logits입니다.
    # - 학습 중 화면에서 보고 싶은 평가값은 정확도입니다.
    model.compile(
        optimizer=____PY5____,
        loss=tf.keras.losses.SparseCategoricalCrossentropy(
            from_logits=____PY6____
        ),
        metrics=[____PY7____],
    )
    return model


def train_student_model(
    model: tf.keras.Model,
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    epochs: int,
) -> tf.keras.callbacks.History:
    """TensorFlow가 순전파·손실·역전파·가중치 수정을 반복하게 합니다."""

    # TODO PY8~PY9: 실제 학습 시작
    # 문법 미니 노트
    # - 객체.메서드(...)는 객체가 가진 기능을 실행합니다.
    # - model의 학습 메서드는 f로 시작합니다.
    # - batch_size는 한 번의 가중치 수정에 함께 보는 이미지 수인 정수입니다.
    # 생각 질문: 현재 완성 코드에서는 32장씩 묶어 학습합니다.
    history = model.____PY8____(
        x_train,
        y_train,
        validation_data=(x_val, y_val),
        epochs=epochs,
        batch_size=____PY9____,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(
                monitor="val_loss", patience=12, restore_best_weights=True
            )
        ],
        verbose=2,
    )
    return history


def select_best_index(scores: np.ndarray) -> int:
    """가장 점수가 큰 클래스의 위치를 고릅니다."""

    # TODO PY10: argmax 추론
    # 문법 미니 노트
    # - np.함수이름(배열)은 NumPy 도구 상자의 함수를 호출한다는 뜻입니다.
    # - 가장 큰 값 자체가 아니라 '가장 큰 값의 위치'를 반환하는 함수를 찾습니다.
    # 생각 질문: [0.1, 0.7, 0.2]에서 필요한 답은 값 0.7일까요, 위치 1일까요?
    return int(np.____PY10____(scores))


def quantized_accuracy(
    model_bytes: bytes, x: np.ndarray, y: np.ndarray
) -> float:
    """학생이 만든 argmax를 사용해 실제 INT8 모델의 정확도를 계산합니다."""

    interpreter = tf.lite.Interpreter(model_content=model_bytes)
    interpreter.allocate_tensors()
    input_detail = interpreter.get_input_details()[0]
    output_detail = interpreter.get_output_details()[0]
    input_scale, input_zero = input_detail["quantization"]
    correct = 0
    for image, label in zip(x, y):
        value = np.clip(
            np.rint(image / input_scale + input_zero), -128, 127
        ).astype(np.int8)
        interpreter.set_tensor(input_detail["index"], value[np.newaxis])
        interpreter.invoke()
        scores = interpreter.get_tensor(output_detail["index"])[0]
        correct += int(select_best_index(scores) == label)
    return correct / len(y)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="학생이 완성하는 실제 OV7675 CNN 학습"
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=PROJECT_ROOT / "data" / "example_camera_digits",
    )
    parser.add_argument("--digits", default="0123")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "models" / "learning_actual",
    )
    parser.add_argument(
        "--header",
        type=Path,
        default=PROJECT_ROOT
        / "arduino"
        / "camera_03_inference"
        / "model_data.h",
    )
    parser.add_argument(
        "--exercise-header",
        type=Path,
        default=PROJECT_ROOT
        / "arduino"
        / "camera_03_inference_exercise"
        / "model_data.h",
        help="학생용 Arduino 스케치에 넣을 헤더 경로",
    )
    return parser.parse_args()


def run_pipeline(args: argparse.Namespace) -> None:
    """완성한 함수들을 실제 학습·INT8 변환·Arduino 헤더 생성에 연결합니다."""

    random.seed(args.seed)
    np.random.seed(args.seed)
    tf.random.set_seed(args.seed)

    digits = [int(char) for char in args.digits]
    if len(digits) < 2 or len(set(digits)) != len(digits):
        raise ValueError("--digits에는 서로 다른 숫자를 최소 2개 지정하세요.")

    x, y = load_student_dataset(args.data, digits)
    counts = np.bincount(y, minlength=len(digits))
    print(
        "숫자별 사진:",
        ", ".join(f"{digit}:{counts[i]}" for i, digit in enumerate(digits)),
    )
    x_train, y_train, x_val, y_val = core.stratified_split(
        x, y, digits, 0.2, args.seed
    )
    x_aug, y_aug = core.augment(x_train, y_train, args.seed)

    model = compile_student_model(build_student_model(len(digits)))
    history = train_student_model(
        model, x_aug, y_aug, x_val, y_val, args.epochs
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model.save(args.output_dir / "camera_digit_model.keras")
    model_bytes = core.convert_int8(model, x_train)
    (args.output_dir / "camera_digit_int8.tflite").write_bytes(model_bytes)
    accuracy = quantized_accuracy(model_bytes, x_val, y_val)

    generator = "python/learning/train_camera_model_exercise.py"
    core.write_header(args.header, model_bytes, digits, generator=generator)
    core.write_header(
        args.output_dir / "model_data.h", model_bytes, digits, generator=generator
    )
    exercise_header = args.exercise_header
    core.write_header(exercise_header, model_bytes, digits, generator=generator)

    metadata = {
        "exercise": "actual_camera_pipeline",
        "class_labels": digits,
        "sample_counts": {
            str(digit): int(counts[i]) for i, digit in enumerate(digits)
        },
        "best_float_validation_accuracy": float(
            max(history.history["val_accuracy"])
        ),
        "int8_validation_accuracy": float(accuracy),
        "model_bytes": len(model_bytes),
    }
    (args.output_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nINT8 검증 정확도: {accuracy * 100:.1f}%")
    print(f"모델 크기: {len(model_bytes) / 1024:.1f} KiB")
    print(f"Arduino 완성본 헤더: {args.header}")
    print(f"Arduino 학생용 헤더: {exercise_header}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    run_pipeline(parse_args())


if __name__ == "__main__":
    main()
