"""01 카메라 확인 스케치의 28×28 문자 영상을 터미널에 표시합니다."""

from __future__ import annotations

import argparse
import sys
import time

import serial

IMAGE_SIZE = 28
READY_RESPONSE = "HELLO,CAMERA_CHECK"
BEGIN_MARKER = f"BEGIN_ASCII,{IMAGE_SIZE},{IMAGE_SIZE}"
END_MARKER = "END_ASCII"


def read_line(board: serial.Serial) -> str:
    """줄 끝만 제거하고 문자 그림 왼쪽의 공백은 보존합니다."""

    return board.readline().decode("ascii", errors="replace").rstrip("\r\n")


def wait_for_board(board: serial.Serial) -> None:
    """보드가 재시작할 시간을 주면서 01 스케치의 준비 응답을 기다립니다."""

    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        board.write(b"PING\n")
        board.flush()
        if read_line(board) == READY_RESPONSE:
            return
        time.sleep(0.2)
    raise TimeoutError(
        "01 카메라 확인 스케치의 응답을 받지 못했습니다. "
        "camera_01_check.ino 업로드와 포트를 확인하세요."
    )


def capture_ascii(board: serial.Serial) -> list[str]:
    """한 장을 요청하고 정확히 28줄의 문자 영상을 받습니다."""

    board.reset_input_buffer()
    board.write(b"CAPTURE\n")
    board.flush()

    if read_line(board) != BEGIN_MARKER:
        raise RuntimeError("카메라 영상 시작 표시를 받지 못했습니다.")

    rows = [read_line(board) for _ in range(IMAGE_SIZE)]
    if any(len(row) != IMAGE_SIZE for row in rows):
        lengths = [len(row) for row in rows]
        raise RuntimeError(f"28×28 문자 영상의 줄 길이가 올바르지 않습니다: {lengths}")
    if read_line(board) != END_MARKER:
        raise RuntimeError("카메라 영상 종료 표시를 받지 못했습니다.")
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="OV7675 카메라 응답과 28×28 문자 영상을 터미널에서 확인합니다."
    )
    parser.add_argument("--port", required=True, help="예: COM5 또는 /dev/ttyACM0")
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    args = parse_args()
    try:
        with serial.Serial(args.port, 115200, timeout=3) as board:
            wait_for_board(board)
            rows = capture_ascii(board)
    except (serial.SerialException, TimeoutError, RuntimeError) as error:
        print(f"카메라 확인 실패: {error}")
        print("Arduino IDE 시리얼 모니터를 닫고 포트 번호를 다시 확인하세요.")
        return 1

    print("카메라 응답 정상: 28×28 문자 미리보기")
    print("+" + "-" * IMAGE_SIZE + "+")
    for row in rows:
        print("|" + row + "|")
    print("+" + "-" * IMAGE_SIZE + "+")
    print("문자 그림이 거칠어도 카메라가 응답했다면 02 Full View로 이동하세요.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
