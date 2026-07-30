"""MNIST 숫자를 내려받아 학습하고 Arduino용 INT8 모델을 만듭니다."""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np
import tensorflow as tf

from train_camera_model import (
    build_model,
    convert_int8,
    quantized_accuracy,
    write_header,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def add_narrow_digit_variations(
    images: np.ndarray, labels: np.ndarray, seed: int
) -> tuple[np.ndarray, np.ndarray]:
    """카메라에서 가늘게 보이는 숫자도 배우도록 가로폭을 여러 단계로 줄입니다."""
    batches = [images]
    label_batches = [labels]
    for scale in (0.35, 0.50, 0.70, 0.85):
        target_width = max(1, round(28 * scale))
        resized = tf.image.resize(
            images, (28, target_width), method="bilinear"
        ).numpy()
        canvas = np.zeros_like(images)
        offset = (28 - target_width) // 2
        canvas[:, :, offset : offset + target_width, :] = resized
        batches.append(canvas)
        label_batches.append(labels)

    joined_x = np.concatenate(batches)
    joined_y = np.concatenate(label_batches)
    order = np.random.default_rng(seed).permutation(len(joined_y))
    return joined_x[order], joined_y[order]


def configure_console() -> None:
    """Windows PowerShell에서도 한국어 안내가 깨지거나 오류 나지 않게 합니다."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MNIST를 학습해 Nano 33 BLE Sense용 INT8 모델을 만듭니다."
    )
    parser.add_argument(
        "--digits",
        default="0123",
        help="학습할 숫자 목록입니다. 첫 실습은 0123을 권장합니다.",
    )
    parser.add_argument(
        "--per-digit",
        type=int,
        default=2000,
        help="숫자마다 사용할 MNIST 학습 이미지 수입니다. 기본값은 2000장입니다.",
    )
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "models" / "mnist",
    )
    parser.add_argument(
        "--header",
        type=Path,
        default=PROJECT_ROOT
        / "arduino"
        / "camera_03_inference"
        / "model_data.h",
    )
    return parser.parse_args()


def select_digits(
    images: np.ndarray,
    labels: np.ndarray,
    digits: list[int],
    per_digit: int | None,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, dict[str, int]]:
    """원하는 숫자만 고르고 모델 내부 라벨을 0, 1, 2...로 다시 매깁니다."""
    rng = np.random.default_rng(seed)
    selected_images: list[np.ndarray] = []
    selected_labels: list[np.ndarray] = []
    counts: dict[str, int] = {}

    for class_index, digit in enumerate(digits):
        indices = np.flatnonzero(labels == digit)
        rng.shuffle(indices)
        if per_digit is not None:
            indices = indices[: min(per_digit, len(indices))]
        selected_images.append(images[indices])
        selected_labels.append(
            np.full(len(indices), class_index, dtype=np.int64)
        )
        counts[str(digit)] = int(len(indices))

    x = np.concatenate(selected_images).astype(np.float32)[..., np.newaxis] / 255.0
    y = np.concatenate(selected_labels)
    order = rng.permutation(len(y))
    return x[order], y[order], counts


def main() -> None:
    configure_console()
    args = parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)
    tf.random.set_seed(args.seed)

    digits = [int(char) for char in args.digits]
    if len(digits) < 2 or len(set(digits)) != len(digits):
        raise ValueError("--digits에는 서로 다른 숫자를 최소 2개 지정하세요.")
    if any(digit < 0 or digit > 9 for digit in digits):
        raise ValueError("MNIST 숫자는 0부터 9까지만 사용할 수 있습니다.")
    if args.per_digit < 10:
        raise ValueError("--per-digit은 10 이상으로 지정하세요.")

    print("MNIST를 불러옵니다. 처음 실행할 때만 약 11MB를 다운로드합니다.")
    (train_images, train_labels), (test_images, test_labels) = (
        tf.keras.datasets.mnist.load_data()
    )

    x_train, y_train, train_counts = select_digits(
        train_images, train_labels, digits, args.per_digit, args.seed
    )
    # 검증은 MNIST가 제공하는 별도의 시험 데이터를 모두 사용합니다.
    x_test, y_test, test_counts = select_digits(
        test_images, test_labels, digits, None, args.seed + 1
    )
    print(
        "MNIST 학습 이미지:",
        ", ".join(f"{digit}:{train_counts[str(digit)]}" for digit in digits),
    )
    print(
        "MNIST 검증 이미지:",
        ", ".join(f"{digit}:{test_counts[str(digit)]}" for digit in digits),
    )

    # OV7675에서는 긴 숫자가 가로 5~10픽셀로 보일 수 있습니다.
    # 정상 폭과 여러 단계로 가로가 눌린 MNIST를 함께 보여 주어 1과 2를 구별합니다.
    x_augmented, y_augmented = add_narrow_digit_variations(
        x_train, y_train, args.seed
    )

    model = build_model(len(digits))
    model.compile(
        optimizer="adam",
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )
    history = model.fit(
        x_augmented,
        y_augmented,
        validation_data=(x_test, y_test),
        epochs=args.epochs,
        batch_size=64,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(
                monitor="val_loss", patience=4, restore_best_weights=True
            )
        ],
        verbose=2,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model.save(args.output_dir / "mnist_digit_model.keras")
    model_bytes = convert_int8(model, x_train)
    (args.output_dir / "mnist_digit_int8.tflite").write_bytes(model_bytes)
    accuracy = quantized_accuracy(model_bytes, x_test, y_test)

    # 보관용 헤더와 Arduino에서 바로 사용하는 헤더를 모두 생성합니다.
    generator = "python/train_mnist_model.py"
    write_header(
        args.output_dir / "model_data.h", model_bytes, digits, generator
    )
    write_header(args.header, model_bytes, digits, generator)

    metadata = {
        "source": "MNIST",
        "image_size": [28, 28, 1],
        "class_labels": digits,
        "train_sample_counts": train_counts,
        "test_sample_counts": test_counts,
        "horizontal_training_scales": [1.0, 0.35, 0.50, 0.70, 0.85],
        "best_float_validation_accuracy": float(
            max(history.history["val_accuracy"])
        ),
        "int8_validation_accuracy": float(accuracy),
        "model_bytes": len(model_bytes),
    }
    (args.output_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"\nMNIST INT8 검증 정확도: {accuracy * 100:.1f}%")
    print(f"모델 크기: {len(model_bytes) / 1024:.1f} KiB")
    print(f"MNIST 모델 보관: {args.output_dir}")
    print(f"Arduino 헤더 생성: {args.header}")
    print("이제 camera_03_inference.ino를 다시 업로드하세요.")


if __name__ == "__main__":
    main()
