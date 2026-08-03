"""카메라 숫자 사진을 CNN으로 학습하고 Arduino용 INT8 모델을 만듭니다.

이 파일은 README의 기본 학습 명령이 실제로 실행하는 코드입니다. 학생은 별도의
연습용 신경망이 아니라 이 파일의 ``____PY...____`` 7곳을 직접 완성합니다.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np
import tensorflow as tf

IMAGE_SIZE = 28
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_pgm(path: Path) -> np.ndarray:
    """이 프로젝트가 저장한 28x28 P5 PGM 파일을 읽습니다."""
    data = path.read_bytes()
    parts = data.split(b"\n", 3)
    if len(parts) != 4 or parts[0] != b"P5" or parts[1] != b"28 28":
        raise ValueError(f"지원하지 않는 PGM 파일: {path}")
    if parts[2] != b"255" or len(parts[3]) != IMAGE_SIZE * IMAGE_SIZE:
        raise ValueError(f"PGM 픽셀 데이터가 잘못됨: {path}")
    return np.frombuffer(parts[3], dtype=np.uint8).reshape(IMAGE_SIZE, IMAGE_SIZE)


def normalize_images(images: list[np.ndarray]) -> np.ndarray:
    """uint8 이미지 목록을 CNN 입력인 float32 0~1 배열로 바꿉니다."""

    # TODO PY1: 데이터 정규화
    # 문법 미니 노트
    # - np.asarray(목록, dtype=자료형)은 목록을 NumPy 배열로 바꿉니다.
    # - [..., np.newaxis]는 맨 뒤에 채널 축 1개를 추가합니다.
    # - / 연산은 배열의 모든 값에 한꺼번에 적용됩니다.
    # 생각 질문: 카메라 픽셀의 최댓값을 어떤 실수로 나누면 0~1이 될까요?
    return np.asarray(images, dtype=np.float32)[..., np.newaxis] / ____PY1____


def load_dataset(root: Path, digits: list[int]) -> tuple[np.ndarray, np.ndarray]:
    images: list[np.ndarray] = []
    labels: list[int] = []
    # 모델 내부 정답은 0, 1, 2...의 연속 번호를 사용하고,
    # 실제 숫자 값은 생성되는 헤더의 g_class_labels에 저장합니다.
    for class_index, digit in enumerate(digits):
        for path in sorted((root / str(digit)).glob("*.pgm")):
            images.append(read_pgm(path))
            labels.append(class_index)
    if not images:
        raise ValueError("카메라 학습 이미지가 없습니다.")
    # 위에서 학생이 완성한 정규화 함수가 실제 학습 데이터에 적용됩니다.
    x = normalize_images(images)
    y = np.asarray(labels, dtype=np.int64)
    return x, y


def stratified_split(x, y, digits: list[int], ratio: float, seed: int):
    rng = np.random.default_rng(seed)
    train_idx, val_idx = [], []
    for class_index, digit in enumerate(digits):
        indices = np.flatnonzero(y == class_index)
        if len(indices) < 10:
            raise ValueError(
                f"숫자 {digit} 사진이 {len(indices)}장입니다. 최소 10장, 권장 30장입니다."
            )
        rng.shuffle(indices)
        count = max(2, int(round(len(indices) * ratio)))
        val_idx.extend(indices[:count])
        train_idx.extend(indices[count:])
    rng.shuffle(train_idx)
    rng.shuffle(val_idx)
    return x[train_idx], y[train_idx], x[val_idx], y[val_idx]


def translate(image: np.ndarray, dx: int, dy: int) -> np.ndarray:
    """검은색으로 빈 공간을 채우며 이미지를 이동합니다."""
    result = np.zeros_like(image)
    src_x0, src_x1 = max(0, -dx), min(IMAGE_SIZE, IMAGE_SIZE - dx)
    src_y0, src_y1 = max(0, -dy), min(IMAGE_SIZE, IMAGE_SIZE - dy)
    dst_x0, dst_x1 = max(0, dx), min(IMAGE_SIZE, IMAGE_SIZE + dx)
    dst_y0, dst_y1 = max(0, dy), min(IMAGE_SIZE, IMAGE_SIZE + dy)
    result[dst_y0:dst_y1, dst_x0:dst_x1] = image[src_y0:src_y1, src_x0:src_x1]
    return result


def augment(x: np.ndarray, y: np.ndarray, seed: int, copies: int = 5):
    """작은 위치·밝기 차이를 만들어 적은 사진의 과적합을 줄입니다."""
    rng = np.random.default_rng(seed)
    out_x, out_y = [x], [y]
    for _ in range(copies):
        batch = np.empty_like(x)
        for i, image in enumerate(x):
            shifted = translate(
                image,
                int(rng.integers(-2, 3)),
                int(rng.integers(-2, 3)),
            )
            gain = float(rng.uniform(0.85, 1.15))
            noise = rng.normal(0, 0.025, shifted.shape)
            batch[i] = np.clip(shifted * gain + noise, 0, 1)
        out_x.append(batch)
        out_y.append(y)
    joined_x = np.concatenate(out_x)
    joined_y = np.concatenate(out_y)
    order = rng.permutation(len(joined_y))
    return joined_x[order], joined_y[order]


def build_model(class_count: int) -> tf.keras.Model:
    """실제 Arduino에 넣을 작은 CNN을 만듭니다."""

    # CNN 구조는 처음 배우는 학생이 API 인자 순서를 추측하지 않도록 완성해 둡니다.
    # Sequential은 아래 목록의 층을 위에서 아래 순서로 연결합니다.
    return tf.keras.Sequential(
        [
            # 입력: 28×28 흑백 이미지입니다. 마지막 1은 흑백 채널 1개를 뜻합니다.
            tf.keras.layers.Input(shape=(28, 28, 1)),

            # 3×3 필터 8개가 선·모서리 같은 특징을 찾습니다.
            # valid는 바깥 여백을 추가하지 않으므로 28×28×1 → 26×26×8입니다.
            # relu는 음수 결과를 0으로 바꿉니다.
            tf.keras.layers.Conv2D(
                filters=8,
                kernel_size=(3, 3),
                strides=(1, 1),
                padding="valid",
                activation="relu",
            ),

            # 각 2×2 영역의 최댓값만 남겨 26×26×8 → 13×13×8로 줄입니다.
            tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

            # 앞에서 찾은 선들을 조합해 곡선·숫자 일부 같은 특징 16종류를 찾습니다.
            # 3×3 valid 합성곱이므로 13×13×8 → 11×11×16입니다.
            tf.keras.layers.Conv2D(
                filters=16,
                kernel_size=(3, 3),
                strides=(1, 1),
                padding="valid",
                activation="relu",
            ),

            # 다시 2×2 최댓값만 남겨 11×11×16 → 5×5×16으로 줄입니다.
            tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

            # 5×5×16개의 특징을 Dense 층이 받을 수 있는 길이 400의 배열로 펼칩니다.
            tf.keras.layers.Flatten(),

            # 특징 400개를 조합하여 숫자를 판단할 중간 특징 32개를 만듭니다.
            tf.keras.layers.Dense(units=32, activation="relu"),

            # 분류할 숫자가 0~3이면 class_count는 4이고 점수(logit)도 4개입니다.
            # Softmax는 Arduino에서 직접 계산하므로 여기에는 activation을 넣지 않습니다.
            tf.keras.layers.Dense(units=class_count),
        ]
    )


def compile_model(model: tf.keras.Model) -> tf.keras.Model:
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


def train_model(
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


def convert_int8(model: tf.keras.Model, representative: np.ndarray) -> bytes:
    def samples():
        for i in range(min(len(representative), 300)):
            yield [representative[i : i + 1].astype(np.float32)]

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = samples
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8
    return converter.convert()


def quantized_accuracy(model_bytes: bytes, x: np.ndarray, y: np.ndarray) -> float:
    interpreter = tf.lite.Interpreter(model_content=model_bytes)
    interpreter.allocate_tensors()
    inp = interpreter.get_input_details()[0]
    out = interpreter.get_output_details()[0]
    in_scale, in_zero = inp["quantization"]
    correct = 0
    for image, label in zip(x, y):
        value = np.clip(np.rint(image / in_scale + in_zero), -128, 127).astype(np.int8)
        interpreter.set_tensor(inp["index"], value[np.newaxis])
        interpreter.invoke()
        scores = interpreter.get_tensor(out["index"])[0]
        correct += int(select_best_index(scores) == label)
    return correct / len(y)


def write_header(
    path: Path,
    model_bytes: bytes,
    digits: list[int],
    generator: str = "python/train_camera_model.py",
) -> None:
    values = [f"0x{byte:02x}" for byte in model_bytes]
    lines = [", ".join(values[i : i + 12]) for i in range(0, len(values), 12)]
    text = (
        "#pragma once\n"
        f"// {generator}가 자동 생성했습니다.\n"
        "#define MODEL_DATA_GENERATED 1\n"
        "alignas(16) const unsigned char g_model[] = {\n  "
        + ",\n  ".join(lines)
        + "\n};\n"
        + f"const unsigned int g_model_len = {len(model_bytes)};\n"
        + f"const unsigned int g_class_count = {len(digits)};\n"
        + "const int g_class_labels[] = {"
        + ", ".join(str(digit) for digit in digits)
        + "};\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description="OV7675 숫자 CNN을 학습합니다.")
    parser.add_argument(
        "--data", type=Path, default=PROJECT_ROOT / "data" / "camera_digits"
    )
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--digits",
        default="0123456789",
        help="학습할 숫자 목록. 처음 실습은 0123처럼 지정합니다.",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=PROJECT_ROOT / "models" / "camera"
    )
    parser.add_argument(
        "--header",
        type=Path,
        default=PROJECT_ROOT / "arduino" / "camera_03_inference" / "model_data.h",
    )
    return parser.parse_args()


def main() -> None:
    # Windows PowerShell의 출력 인코딩이 cp1252로 잡혀 있어도
    # 한국어 진행 메시지를 출력하다가 학습이 중단되지 않게 합니다.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    args = parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)
    tf.random.set_seed(args.seed)

    digits = [int(char) for char in args.digits]
    if len(digits) < 2 or len(set(digits)) != len(digits):
        raise ValueError("--digits에는 서로 다른 숫자를 최소 2개 지정하세요.")

    x, y = load_dataset(args.data, digits)
    counts = np.bincount(y, minlength=len(digits))
    print(
        "숫자별 사진:",
        ", ".join(f"{digit}:{counts[i]}" for i, digit in enumerate(digits)),
    )
    x_train, y_train, x_val, y_val = stratified_split(
        x, y, digits, 0.2, args.seed
    )
    x_aug, y_aug = augment(x_train, y_train, args.seed)

    # 학생이 위에서 완성한 CNN·compile·fit 함수가 실제 모델 학습에 사용됩니다.
    model = compile_model(build_model(len(digits)))
    history = train_model(
        model, x_aug, y_aug, x_val, y_val, args.epochs
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model.save(args.output_dir / "camera_digit_model.keras")
    model_bytes = convert_int8(model, x_train)
    (args.output_dir / "camera_digit_int8.tflite").write_bytes(model_bytes)
    accuracy = quantized_accuracy(model_bytes, x_val, y_val)
    # Arduino가 바로 사용할 헤더와, 나중에 모델을 비교할 보관용 헤더를 함께 만듭니다.
    write_header(args.header, model_bytes, digits)
    write_header(args.output_dir / "model_data.h", model_bytes, digits)

    metadata = {
        "image_size": [28, 28, 1],
        "class_labels": digits,
        "sample_counts": {
            str(digit): int(counts[i]) for i, digit in enumerate(digits)
        },
        "best_float_validation_accuracy": float(max(history.history["val_accuracy"])),
        "int8_validation_accuracy": float(accuracy),
        "model_bytes": len(model_bytes),
    }
    (args.output_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nINT8 검증 정확도: {accuracy * 100:.1f}%")
    print(f"모델 크기: {len(model_bytes) / 1024:.1f} KiB")
    print(f"Arduino 헤더 생성: {args.header}")


if __name__ == "__main__":
    main()
