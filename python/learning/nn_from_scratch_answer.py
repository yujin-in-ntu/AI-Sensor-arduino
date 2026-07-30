"""NumPy만으로 만드는 28x28 숫자 신경망 실습의 정답 코드입니다.

신경망 구조: 784 입력 -> 64개 ReLU 은닉 뉴런 -> 숫자별 출력 점수
TensorFlow는 MNIST 다운로드에만 사용하며 학습과 추론 수식은 모두 아래에 있습니다.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from nn_data import (
    PROJECT_ROOT,
    configure_console,
    load_dataset,
    load_parameters,
    parse_digits,
    read_pgm,
    save_parameters,
)

Parameters = dict[str, np.ndarray]
Cache = dict[str, np.ndarray]


def initialize_parameters(
    input_size: int, hidden_size: int, class_count: int, seed: int
) -> Parameters:
    """학습할 가중치와 편향을 만듭니다. ReLU에 맞는 He 초기화를 사용합니다."""
    rng = np.random.default_rng(seed)
    return {
        "w1": (
            rng.standard_normal((input_size, hidden_size))
            * np.sqrt(2.0 / input_size)
        ).astype(np.float32),
        "b1": np.zeros(hidden_size, dtype=np.float32),
        "w2": (
            rng.standard_normal((hidden_size, class_count))
            * np.sqrt(2.0 / hidden_size)
        ).astype(np.float32),
        "b2": np.zeros(class_count, dtype=np.float32),
    }


def relu(z: np.ndarray) -> np.ndarray:
    """음수는 0으로 막고 양수는 그대로 통과시킵니다."""
    return np.maximum(0.0, z)


def softmax(logits: np.ndarray) -> np.ndarray:
    """숫자별 점수를 각 행의 합이 1인 확률로 바꿉니다."""
    shifted = logits - np.max(logits, axis=1, keepdims=True)
    exp_scores = np.exp(shifted)
    return exp_scores / np.sum(exp_scores, axis=1, keepdims=True)


def cross_entropy(probs: np.ndarray, y: np.ndarray) -> float:
    """정답 확률이 낮을수록 큰 벌점을 주는 평균 손실입니다."""
    correct_probs = probs[np.arange(len(y)), y]
    return float(-np.mean(np.log(correct_probs + 1e-12)))


def forward(parameters: Parameters, x: np.ndarray) -> Cache:
    """입력에서 출력 확률까지 왼쪽에서 오른쪽으로 계산합니다."""
    z1 = x @ parameters["w1"] + parameters["b1"]
    a1 = relu(z1)
    logits = a1 @ parameters["w2"] + parameters["b2"]
    probs = softmax(logits)
    return {"x": x, "z1": z1, "a1": a1, "logits": logits, "probs": probs}


def output_layer_gradients(
    parameters: Parameters, cache: Cache, y: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Softmax+교차엔트로피의 미분으로 출력층 기울기를 구합니다."""
    one_hot = np.zeros_like(cache["probs"])
    one_hot[np.arange(len(y)), y] = 1.0
    d_logits = (cache["probs"] - one_hot) / len(y)
    d_w2 = cache["a1"].T @ d_logits
    d_b2 = np.sum(d_logits, axis=0)
    d_a1 = d_logits @ parameters["w2"].T
    return d_a1, d_w2, d_b2


def hidden_layer_gradients(
    cache: Cache, d_a1: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """연쇄법칙으로 은닉층을 지나 첫 번째 가중치까지 역전파합니다."""
    d_z1 = d_a1 * (cache["z1"] > 0)
    d_w1 = cache["x"].T @ d_z1
    d_b1 = np.sum(d_z1, axis=0)
    return d_w1, d_b1


def update_parameters(
    parameters: Parameters, gradients: Parameters, learning_rate: float
) -> None:
    """손실이 작아지는 방향인 기울기의 반대 방향으로 한 걸음 이동합니다."""
    for name in ("w1", "b1", "w2", "b2"):
        parameters[name] -= learning_rate * gradients[name]


def predict(parameters: Parameters, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """학습 때와 같은 순전파 후 가장 확률이 큰 클래스 번호를 고릅니다."""
    probs = forward(parameters, x)["probs"]
    class_indices = np.argmax(probs, axis=1)
    return class_indices, probs


def accuracy(parameters: Parameters, x: np.ndarray, y: np.ndarray) -> float:
    predicted, _ = predict(parameters, x)
    return float(np.mean(predicted == y))


def train(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    class_count: int,
    hidden_size: int,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    seed: int,
) -> Parameters:
    """순전파 -> 손실 -> 역전파 -> 가중치 수정 과정을 반복합니다."""
    parameters = initialize_parameters(x_train.shape[1], hidden_size, class_count, seed)
    rng = np.random.default_rng(seed)

    for epoch in range(1, epochs + 1):
        order = rng.permutation(len(y_train))
        for start in range(0, len(order), batch_size):
            indices = order[start : start + batch_size]
            x_batch, y_batch = x_train[indices], y_train[indices]

            # 1. 현재 가중치로 답과 확률을 계산합니다.
            cache = forward(parameters, x_batch)

            # 2. 출력에서 시작해 손실에 대한 각 가중치의 기울기를 계산합니다.
            d_a1, d_w2, d_b2 = output_layer_gradients(parameters, cache, y_batch)
            d_w1, d_b1 = hidden_layer_gradients(cache, d_a1)
            gradients = {"w1": d_w1, "b1": d_b1, "w2": d_w2, "b2": d_b2}

            # 3. 같은 미니배치에서 계산한 기울기로 가중치를 한 번 수정합니다.
            update_parameters(parameters, gradients, learning_rate)

        train_cache = forward(parameters, x_train)
        train_loss = cross_entropy(train_cache["probs"], y_train)
        train_acc = accuracy(parameters, x_train, y_train)
        val_acc = accuracy(parameters, x_val, y_val)
        print(
            f"epoch {epoch:3d}/{epochs} | loss {train_loss:.4f} | "
            f"학습 {train_acc * 100:5.1f}% | 검증 {val_acc * 100:5.1f}%"
        )

    return parameters


def print_single_prediction(
    parameters: Parameters, digits: list[int], image_path: Path
) -> None:
    image = read_pgm(image_path).astype(np.float32).reshape(1, -1) / 255.0
    class_indices, probs = predict(parameters, image)
    print(f"\n입력 파일: {image_path}")
    print(f"예측 숫자: {digits[int(class_indices[0])]}")
    print(
        "확률:",
        ", ".join(
            f"{digit}={probs[0, index] * 100:.1f}%"
            for index, digit in enumerate(digits)
        ),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="NumPy로 순전파와 역전파를 직접 구현한 숫자 신경망 정답 코드"
    )
    parser.add_argument("--source", choices=("mnist", "camera"), default="mnist")
    parser.add_argument("--digits", default="0123")
    parser.add_argument("--data", type=Path, default=PROJECT_ROOT / "data" / "camera_digits")
    parser.add_argument("--per-digit", type=int, default=500)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--hidden-size", type=int, default=64)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--model-output",
        type=Path,
        default=PROJECT_ROOT / "models" / "learning" / "manual_mlp.npz",
    )
    parser.add_argument("--load-model", type=Path)
    parser.add_argument("--predict", type=Path, help="학습 후 추론할 28x28 PGM 파일")
    return parser.parse_args()


def main() -> None:
    configure_console()
    args = parse_args()

    if args.load_model:
        parameters, digits = load_parameters(args.load_model)
        print(f"저장된 가중치를 불러왔습니다: {args.load_model}")
    else:
        digits = parse_digits(args.digits)
        dataset = load_dataset(args.source, digits, args.data, args.per_digit, args.seed)
        print(
            f"데이터: 학습 {len(dataset.y_train)}장, 검증 {len(dataset.y_val)}장 | "
            f"입력 {dataset.x_train.shape[1]}개, 출력 {len(digits)}개"
        )
        parameters = train(
            dataset.x_train,
            dataset.y_train,
            dataset.x_val,
            dataset.y_val,
            len(digits),
            args.hidden_size,
            args.epochs,
            args.batch_size,
            args.learning_rate,
            args.seed,
        )
        save_parameters(args.model_output, parameters, digits)
        print(f"가중치 저장: {args.model_output}")

    if args.predict:
        print_single_prediction(parameters, digits, args.predict)
    elif args.load_model:
        print("추론할 사진을 --predict 경로로 지정하세요.")


if __name__ == "__main__":
    main()
