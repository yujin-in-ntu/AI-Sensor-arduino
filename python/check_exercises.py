"""실제로 실행되는 Arduino 추론 파일의 학생용 빈칸을 검사합니다."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ARDUINO_EXERCISE = (
    PROJECT_ROOT
    / "arduino"
    / "camera_03_inference_exercise"
    / "camera_03_inference_exercise.ino"
)

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

    parser = argparse.ArgumentParser(description="Arduino 실제 추론 빈칸 검사")
    parser.add_argument(
        "--part",
        choices=["arduino"],
        default="arduino",
        help="호환성을 위해 남겨 둔 옵션이며 현재는 arduino만 검사합니다.",
    )
    parser.parse_args()

    if report_remaining(ARDUINO_EXERCISE, ARDUINO_HINTS):
        print("\n위 힌트를 읽고 빈칸을 더 채운 뒤 다시 검사하세요.")
        return 1

    try:
        check_arduino_structure()
    except Exception as error:
        print(f"\n검사 실패: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
