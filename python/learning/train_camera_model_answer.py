"""실제 카메라 학습 빈칸 실습의 교사용 정답 실행 파일입니다.

학생용 파일과 같은 데이터, 증강, INT8 변환, Arduino 헤더 생성 경로를 사용합니다.
먼저 exercise 파일을 충분히 고민한 뒤 비교하세요.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import tensorflow as tf

LEARNING_DIR = Path(__file__).resolve().parent
if str(LEARNING_DIR) not in sys.path:
    sys.path.insert(0, str(LEARNING_DIR))

import train_camera_model_exercise as exercise  # noqa: E402


def normalize_images(images: list[np.ndarray]) -> np.ndarray:
    return np.asarray(images, dtype=np.float32)[..., np.newaxis] / 255.0


def build_student_model(class_count: int) -> tf.keras.Model:
    return tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(28, 28, 1)),
            tf.keras.layers.Conv2D(8, 3, activation="relu"),
            tf.keras.layers.MaxPooling2D(2),
            tf.keras.layers.Conv2D(16, 3, activation="relu"),
            tf.keras.layers.MaxPooling2D(2),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(32, activation="relu"),
            tf.keras.layers.Dense(class_count),
        ]
    )


def compile_student_model(model: tf.keras.Model) -> tf.keras.Model:
    model.compile(
        optimizer="adam",
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
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
    return model.fit(
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


def select_best_index(scores: np.ndarray) -> int:
    return int(np.argmax(scores))


def main() -> None:
    # 실행 흐름은 학생용과 완전히 같고, 핵심 함수만 정답 구현으로 교체합니다.
    exercise.normalize_images = normalize_images
    exercise.build_student_model = build_student_model
    exercise.compile_student_model = compile_student_model
    exercise.train_student_model = train_student_model
    exercise.select_best_index = select_best_index
    exercise.main()


if __name__ == "__main__":
    main()
