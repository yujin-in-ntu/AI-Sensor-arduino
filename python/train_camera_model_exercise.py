"""학생이 실제 CNN 구조를 작성하는 카메라 모델 학습 실습 파일입니다.

PY1~PY5는 숫자를 채우고, PY6~PY8은 조건을 읽어 Keras 층을 직접 작성합니다.
완성하면 촬영 데이터 학습부터 INT8 변환과 Arduino 헤더 생성까지 실제로 실행됩니다.
막힐 때는 빈칸이 없는 train_camera_model.py와 비교할 수 있습니다.
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

    # uint8 0~255를 float32 0~1로 바꾸고 흑백 채널 축 1개를 추가합니다.
    return np.asarray(images, dtype=np.float32)[..., np.newaxis] / 255.0


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

    return tf.keras.Sequential(
        [
            tf.keras.layers.Input(
                shape=(____PY1A____, ____PY1B____, ____PY1C____)
            ),

            # valid는 바깥 여백을 추가하지 않으므로 28×28×1 → 26×26×8입니다.
            # relu는 음수 결과를 0으로 바꿉니다.
            tf.keras.layers.Conv2D(
                filters=____PY2____,
                kernel_size=(____PY3A____, ____PY3B____),
                strides=(____PY4A____, ____PY4B____),
                padding="valid",
                activation="relu",
            ),

            tf.keras.layers.MaxPooling2D(
                pool_size=(____PY5A____, ____PY5B____)
            ),

            # PY6
            # 조건
            # - 특징 지도 16개를 만듭니다.
            # - 필터는 세로 5칸, 가로 5칸입니다.
            # - 필터는 아래와 오른쪽으로 각각 2칸씩 이동합니다.
            # - 이미지 바깥에 여백을 추가하지 않습니다.
            # - 음수 결과는 0으로 바꿉니다.

            # PY7
            # 조건
            # - 세로 2칸, 가로 2칸 영역마다 가장 큰 값 하나만 남깁니다.

            # PY8
            # 조건
            # - 2×2×16 형태의 특징 지도를 Dense 층이 받을 수 있게 한 줄로 펼칩니다.
            # - 펼친 뒤 배열의 길이는 64가 되어야 합니다.
            # Flatten() 함수를 사용합니다.


            # 특징 64개를 조합하여 숫자를 판단할 중간 특징 32개를 만듭니다.
            tf.keras.layers.Dense(units=32, activation="relu"),

            # 분류할 숫자가 0~3이면 class_count는 4이고 점수(logit)도 4개입니다.
            # Softmax는 Arduino에서 직접 계산하므로 여기에는 activation을 넣지 않습니다.
            tf.keras.layers.Dense(units=class_count),
        ]
    )


def compile_model(model: tf.keras.Model) -> tf.keras.Model:
    """완성된 학습 설정을 모델에 연결합니다."""

    # 마지막 Dense는 확률이 아닌 logits를 출력하므로 from_logits=True입니다.
    # 이 손실함수 안에서 Softmax와 Cross Entropy가 안정적인 방식으로 계산됩니다.
    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
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

    # model.fit()은 각 batch마다 TensorFlow 내부에서 개념적으로 다음을 수행합니다.
    # 1. GradientTape 안에서 model 입력 → logits → 위 Cross Entropy 손실을 계산합니다.
    # 2. tape.gradient(loss, model.trainable_variables)로 역전파 기울기를 구합니다.
    # 3. Adam.apply_gradients(...)로 필터와 Dense 가중치를 수정합니다.
    history = model.fit(
        x_train,
        y_train,
        validation_data=(x_val, y_val),
        epochs=epochs,
        batch_size=32,
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

    # argmax는 가장 큰 점수 자체가 아니라 그 점수의 위치를 반환합니다.
    return int(np.argmax(scores))


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
    generator: str = "python/train_camera_model_exercise.py",
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

    # 위에서 읽은 CNN, 손실함수, fit 흐름으로 실제 모델을 학습합니다.
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
