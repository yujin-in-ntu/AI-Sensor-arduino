"""저장된 160x120 원본에서 새 전처리로 28x28 학습 이미지를 다시 만듭니다."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from camera_preprocess import check_digit_quality, check_frame_quality, make_digit_image

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_pgm(path: Path) -> np.ndarray:
    parts = path.read_bytes().split(b"\n", 3)
    dimensions = parts[1].split()
    width, height = int(dimensions[0]), int(dimensions[1])
    return np.frombuffer(parts[3], dtype=np.uint8).reshape(height, width)


def save_pgm(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"P5\n28 28\n255\n" + image.tobytes())


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="원본 카메라 사진 재전처리")
    parser.add_argument("--digits", default="0123")
    parser.add_argument(
        "--input", type=Path, default=PROJECT_ROOT / "data" / "camera_full"
    )
    parser.add_argument(
        "--output", type=Path, default=PROJECT_ROOT / "data" / "camera_digits_clean"
    )
    args = parser.parse_args()

    for digit in [int(char) for char in args.digits]:
        accepted = rejected = 0
        for source in sorted((args.input / str(digit)).glob("*.pgm")):
            frame = read_pgm(source)
            image = make_digit_image(frame)
            frame_passed, _ = check_frame_quality(frame)
            image_passed, _ = check_digit_quality(image)
            if frame_passed and image_passed:
                save_pgm(args.output / str(digit) / source.name, image)
                accepted += 1
            else:
                rejected += 1
        print(f"숫자 {digit}: 사용 {accepted}장, 제외 {rejected}장")


if __name__ == "__main__":
    main()
