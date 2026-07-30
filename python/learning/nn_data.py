"""직접 구현 신경망 실습에서 공통으로 사용하는 데이터 입출력 코드입니다.

이 파일은 데이터를 읽고 0~1 범위로 바꾸는 일만 담당합니다.
신경망의 순전파, 역전파, 가중치 수정은 exercise/answer 파일에 있습니다.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

IMAGE_SIZE = 28
INPUT_SIZE = IMAGE_SIZE * IMAGE_SIZE
PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Dataset:
    """신경망에 넣을 학습·검증 데이터와 실제 숫자 라벨입니다."""

    x_train: np.ndarray
    y_train: np.ndarray
    x_val: np.ndarray
    y_val: np.ndarray
    digits: list[int]


def configure_console() -> None:
    """Windows PowerShell에서도 한국어 출력이 깨지지 않게 합니다."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def parse_digits(text: str) -> list[int]:
    digits = [int(char) for char in text]
    if len(digits) < 2 or len(set(digits)) != len(digits):
        raise ValueError("--digits에는 서로 다른 숫자를 최소 2개 지정하세요.")
    if any(digit < 0 or digit > 9 for digit in digits):
        raise ValueError("숫자는 0부터 9까지만 사용할 수 있습니다.")
    return digits


def read_pgm(path: Path) -> np.ndarray:
    """이 프로젝트가 저장한 28x28 P5 PGM 파일 하나를 읽습니다."""
    data = path.read_bytes()
    parts = data.split(b"\n", 3)
    if len(parts) != 4 or parts[0] != b"P5" or parts[1] != b"28 28":
        raise ValueError(f"지원하지 않는 PGM 파일: {path}")
    if parts[2] != b"255" or len(parts[3]) != INPUT_SIZE:
        raise ValueError(f"PGM 픽셀 데이터가 잘못되었습니다: {path}")
    return np.frombuffer(parts[3], dtype=np.uint8).reshape(IMAGE_SIZE, IMAGE_SIZE)


def _shuffle_pair(
    x: np.ndarray, y: np.ndarray, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    order = rng.permutation(len(y))
    return x[order], y[order]


def load_camera_dataset(root: Path, digits: list[int], seed: int) -> Dataset:
    """02 단계에서 촬영한 28x28 사진을 숫자별로 나누어 읽습니다."""
    rng = np.random.default_rng(seed)
    train_images: list[np.ndarray] = []
    train_labels: list[int] = []
    val_images: list[np.ndarray] = []
    val_labels: list[int] = []

    for class_index, digit in enumerate(digits):
        paths = sorted((root / str(digit)).glob("*.pgm"))
        if len(paths) < 5:
            raise ValueError(
                f"숫자 {digit} 사진이 {len(paths)}장입니다. 최소 5장, 권장 20장 이상입니다."
            )
        indices = rng.permutation(len(paths))
        val_count = max(1, int(round(len(paths) * 0.2)))
        val_set = set(indices[:val_count].tolist())
        for index, path in enumerate(paths):
            image = read_pgm(path)
            if index in val_set:
                val_images.append(image)
                val_labels.append(class_index)
            else:
                train_images.append(image)
                train_labels.append(class_index)

    x_train = np.asarray(train_images, dtype=np.float32).reshape(-1, INPUT_SIZE) / 255.0
    y_train = np.asarray(train_labels, dtype=np.int64)
    x_val = np.asarray(val_images, dtype=np.float32).reshape(-1, INPUT_SIZE) / 255.0
    y_val = np.asarray(val_labels, dtype=np.int64)
    x_train, y_train = _shuffle_pair(x_train, y_train, rng)
    x_val, y_val = _shuffle_pair(x_val, y_val, rng)
    return Dataset(x_train, y_train, x_val, y_val, digits)


def load_mnist_dataset(
    digits: list[int], per_digit: int, seed: int
) -> Dataset:
    """MNIST는 내려받기만 TensorFlow에 맡기고 학습 계산에는 사용하지 않습니다."""
    if per_digit < 10:
        raise ValueError("--per-digit은 10 이상으로 지정하세요.")

    import tensorflow as tf

    print("MNIST를 불러옵니다. 최초 실행 때만 약 11MB를 내려받습니다.")
    (train_images, train_labels), (test_images, test_labels) = (
        tf.keras.datasets.mnist.load_data()
    )
    rng = np.random.default_rng(seed)

    def select(
        images: np.ndarray, labels: np.ndarray, limit: int
    ) -> tuple[np.ndarray, np.ndarray]:
        selected_x: list[np.ndarray] = []
        selected_y: list[np.ndarray] = []
        for class_index, digit in enumerate(digits):
            indices = np.flatnonzero(labels == digit)
            rng.shuffle(indices)
            indices = indices[: min(limit, len(indices))]
            selected_x.append(images[indices])
            selected_y.append(np.full(len(indices), class_index, dtype=np.int64))
        x = np.concatenate(selected_x).astype(np.float32).reshape(-1, INPUT_SIZE) / 255.0
        y = np.concatenate(selected_y)
        return _shuffle_pair(x, y, rng)

    x_train, y_train = select(train_images, train_labels, per_digit)
    x_val, y_val = select(test_images, test_labels, max(100, per_digit // 4))
    return Dataset(x_train, y_train, x_val, y_val, digits)


def load_dataset(
    source: str,
    digits: list[int],
    data_root: Path,
    per_digit: int,
    seed: int,
) -> Dataset:
    if source == "camera":
        return load_camera_dataset(data_root, digits, seed)
    if source == "mnist":
        return load_mnist_dataset(digits, per_digit, seed)
    raise ValueError(f"알 수 없는 데이터 종류: {source}")


def save_parameters(path: Path, parameters: dict[str, np.ndarray], digits: list[int]) -> None:
    """직접 학습한 가중치와 라벨을 NumPy 파일로 보관합니다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, **parameters, digits=np.asarray(digits, dtype=np.int64))


def load_parameters(path: Path) -> tuple[dict[str, np.ndarray], list[int]]:
    """저장된 가중치를 불러와 새 사진 추론에 사용합니다."""
    with np.load(path) as data:
        parameters = {name: data[name] for name in ("w1", "b1", "w2", "b2")}
        digits = data["digits"].astype(int).tolist()
    return parameters, digits
