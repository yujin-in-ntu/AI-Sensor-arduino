"""학생용: NumPy로 숫자 신경망의 학습과 추론을 직접 완성합니다.

검색할 표시: TODO 1부터 TODO 8까지
막히면 check_nn_exercise.py로 현재 빈칸을 확인하고, 마지막에는
nn_from_scratch_answer.py와 한 줄씩 비교하세요.
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
    """가중치는 작은 난수, 편향은 0으로 시작합니다."""
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
    """TODO 1: 음수는 0, 양수는 그대로 반환하세요."""
    # 힌트: np.maximum을 사용할 수 있습니다.
    raise NotImplementedError("TODO 1: ReLU를 구현하세요.")


def softmax(logits: np.ndarray) -> np.ndarray:
    """TODO 2: 숫자별 점수를 각 행의 합이 1인 확률로 바꾸세요."""
    # 1) overflow 방지를 위해 각 행의 최댓값을 먼저 뺍니다.
    # 2) np.exp로 양수 점수를 만듭니다.
    # 3) 각 행의 합으로 나눕니다. axis=1, keepdims=True가 중요합니다.
    raise NotImplementedError("TODO 2: 안정적인 Softmax를 구현하세요.")


def cross_entropy(probs: np.ndarray, y: np.ndarray) -> float:
    """TODO 3: 정답 클래스 확률에 -log를 적용한 평균을 반환하세요."""
    # probs[np.arange(len(y)), y]로 각 샘플의 정답 확률만 고를 수 있습니다.
    # log(0)을 피하기 위해 확률에 1e-12를 더하세요.
    raise NotImplementedError("TODO 3: 교차엔트로피 손실을 구현하세요.")


def forward(parameters: Parameters, x: np.ndarray) -> Cache:
    """TODO 4: 입력 -> 은닉층 -> 출력 확률의 순전파를 구현하세요."""
    # 아래 네 줄의 ???를 실제 NumPy 식으로 바꾸고 raise를 지우세요.
    # z1 = x @ w1 + b1
    # a1 = relu(z1)
    # logits = a1 @ w2 + b2
    # probs = softmax(logits)
    # return {"x": x, "z1": z1, "a1": a1, "logits": logits, "probs": probs}
    raise NotImplementedError("TODO 4: 순전파를 구현하세요.")


def output_layer_gradients(
    parameters: Parameters, cache: Cache, y: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """TODO 5: 출력층에서 역전파를 시작하세요."""
    # one_hot은 probs와 같은 모양의 0 배열이며 정답 위치만 1입니다.
    # Softmax+교차엔트로피 미분: d_logits = (probs - one_hot) / 배치크기
    # d_w2 = a1.T @ d_logits
    # d_b2 = d_logits을 샘플 방향(axis=0)으로 합한 값
    # d_a1 = d_logits @ w2.T
    raise NotImplementedError("TODO 5: 출력층 기울기를 구현하세요.")


def hidden_layer_gradients(
    cache: Cache, d_a1: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """TODO 6: ReLU를 지나 입력층 방향으로 역전파하세요."""
    # ReLU의 미분은 z1 > 0일 때 1, 나머지는 0입니다.
    # d_z1 = d_a1 * ReLU의 미분
    # d_w1 = x.T @ d_z1
    # d_b1 = d_z1을 샘플 방향(axis=0)으로 합한 값
    raise NotImplementedError("TODO 6: 은닉층 기울기를 구현하세요.")


def update_parameters(
    parameters: Parameters, gradients: Parameters, learning_rate: float
) -> None:
    """TODO 7: SGD로 w1, b1, w2, b2를 제자리에서 수정하세요."""
    # 새 값 = 기존 값 - 학습률 * 기울기
    raise NotImplementedError("TODO 7: SGD 가중치 수정을 구현하세요.")


def predict(parameters: Parameters, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """TODO 8: 순전파 후 가장 확률이 높은 클래스 번호를 반환하세요."""
    # forward로 probs를 얻고 np.argmax(..., axis=1)를 사용하세요.
    # 반환값은 (class_indices, probs) 두 개입니다.
    raise NotImplementedError("TODO 8: 추론을 구현하세요.")


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
    """학생이 채운 함수들을 실제 학습 순서로 연결합니다."""
    parameters = initialize_parameters(x_train.shape[1], hidden_size, class_count, seed)
    rng = np.random.default_rng(seed)

    for epoch in range(1, epochs + 1):
        order = rng.permutation(len(y_train))
        for start in range(0, len(order), batch_size):
            indices = order[start : start + batch_size]
            x_batch, y_batch = x_train[indices], y_train[indices]

            # 학습 한 번의 전체 흐름입니다.
            cache = forward(parameters, x_batch)                         # 순전파
            d_a1, d_w2, d_b2 = output_layer_gradients(                  # 역전파 1
                parameters, cache, y_batch
            )
            d_w1, d_b1 = hidden_layer_gradients(cache, d_a1)            # 역전파 2
            gradients = {"w1": d_w1, "b1": d_b1, "w2": d_w2, "b2": d_b2}
            update_parameters(parameters, gradients, learning_rate)     # 학습

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
        description="학생이 NumPy로 순전파와 역전파를 채우는 숫자 신경망"
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
