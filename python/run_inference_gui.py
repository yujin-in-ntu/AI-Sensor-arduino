"""Arduino에서 실행한 TinyML 추론 결과와 카메라 화면을 GUI로 표시합니다."""

from __future__ import annotations

import argparse
import sys
import time
import tkinter as tk

import numpy as np
import serial

from camera_preprocess import (
    check_frame_quality,
    find_digit_bounds,
    find_paper_bounds,
    make_digit_image,
)

WIDTH = 160
HEIGHT = 120
ZOOM = 4
FRAME_BYTES = WIDTH * HEIGHT
UNKNOWN_THRESHOLD = 0.55


def wait_for_board(board: serial.Serial) -> None:
    """Arduino 추론 스케치가 준비될 때까지 PING을 보냅니다."""
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        board.write(b"PING\n")
        board.flush()
        line = board.readline().decode("ascii", errors="ignore").strip()
        if line == "HELLO,INFERENCE,1":
            return
        if line == "HELLO,INFERENCE,0":
            raise RuntimeError("Arduino에서 모델을 시작하지 못했습니다.")
        time.sleep(0.2)
    raise TimeoutError("Arduino 추론 스케치의 응답을 받지 못했습니다.")


def predict(board: serial.Serial):
    """촬영 명령을 보내고 원본 프레임과 확률을 받습니다."""
    board.reset_input_buffer()
    board.write(b"PREDICT\n")
    board.flush()

    header = board.readline().decode("ascii", errors="ignore").strip()
    if header != f"FRAME,{FRAME_BYTES}":
        raise RuntimeError(f"잘못된 프레임 헤더: {header!r}")

    data = board.read(FRAME_BYTES)
    if len(data) != FRAME_BYTES:
        raise RuntimeError(f"프레임 부족: {len(data)}/{FRAME_BYTES}바이트")
    board.readline()  # 바이너리 뒤의 줄바꿈

    result = board.readline().decode("ascii", errors="ignore").strip()
    parts = result.split(",")
    if len(parts) < 4 or parts[0] != "RESULT":
        raise RuntimeError(f"잘못된 결과: {result!r}")

    best_label = int(parts[1])
    confidence = float(parts[2])
    class_count = int(parts[3])
    if len(parts) != 4 + class_count * 2:
        raise RuntimeError("클래스 확률 개수가 맞지 않습니다.")
    probabilities = {
        int(parts[4 + i * 2]): float(parts[5 + i * 2])
        for i in range(class_count)
    }
    frame = np.frombuffer(data, dtype=np.uint8).reshape(HEIGHT, WIDTH)
    return frame, best_label, confidence, probabilities


class InferenceApp:
    def __init__(self, root: tk.Tk, board: serial.Serial):
        self.root = root
        self.board = board
        self.photo = None
        self.digit_photo = None
        root.title("Nano 33 BLE Sense 숫자 인식")
        root.protocol("WM_DELETE_WINDOW", self.close)

        tk.Label(
            root,
            text="숫자를 빨간 영역 중앙에 놓고 ‘촬영 및 인식’을 누르세요.",
            font=("Malgun Gothic", 11),
        ).pack(pady=(10, 4))

        previews = tk.Frame(root)
        previews.pack(padx=10, pady=5)

        full_group = tk.Frame(previews)
        full_group.pack(side="left", padx=4)
        tk.Label(full_group, text="카메라 원본").pack()
        self.canvas = tk.Canvas(
            full_group, width=WIDTH * ZOOM, height=HEIGHT * ZOOM, bg="black"
        )
        self.canvas.pack()

        digit_group = tk.Frame(previews)
        digit_group.pack(side="left", padx=4)
        tk.Label(digit_group, text="AI 입력 28×28").pack()
        self.digit_canvas = tk.Canvas(
            digit_group, width=280, height=280, bg="black"
        )
        self.digit_canvas.pack()

        self.result_label = tk.Label(
            root, text="대기 중", font=("Malgun Gothic", 20, "bold")
        )
        self.result_label.pack(pady=(5, 2))

        self.probability_label = tk.Label(
            root, text="", font=("Consolas", 12), justify="left"
        )
        self.probability_label.pack(pady=3)

        self.status = tk.Label(root, text="Arduino 연결 완료")
        self.status.pack(pady=2)

        tk.Button(
            root,
            text="촬영 및 인식",
            command=self.capture,
            width=18,
            font=("Malgun Gothic", 11),
        ).pack(pady=(4, 10))

    def to_photo(self, frame: np.ndarray) -> tk.PhotoImage:
        image = tk.PhotoImage(width=WIDTH, height=HEIGHT)
        for y, row in enumerate(frame):
            colors = " ".join(
                f"#{int(value):02x}{int(value):02x}{int(value):02x}"
                for value in row
            )
            image.put("{" + colors + "}", to=(0, y))
        return image.zoom(ZOOM, ZOOM)

    def to_digit_photo(self, image_array: np.ndarray) -> tk.PhotoImage:
        image = tk.PhotoImage(width=28, height=28)
        for y, row in enumerate(image_array):
            colors = " ".join(
                f"#{int(value):02x}{int(value):02x}{int(value):02x}"
                for value in row
            )
            image.put("{" + colors + "}", to=(0, y))
        return image.zoom(10, 10)

    def capture(self) -> None:
        self.status.config(text="촬영하고 Arduino에서 추론하는 중...")
        self.root.update_idletasks()
        try:
            frame, label, confidence, probabilities = predict(self.board)
            self.photo = self.to_photo(frame)
            digit_image = make_digit_image(frame)
            self.digit_photo = self.to_digit_photo(digit_image)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
            left, right, top, bottom = find_paper_bounds(frame)
            self.canvas.create_rectangle(
                left * ZOOM,
                top * ZOOM,
                (right + 1) * ZOOM,
                (bottom + 1) * ZOOM,
                outline="red",
                width=3,
            )
            digit_bounds = find_digit_bounds(frame)
            if digit_bounds is not None:
                digit_left, digit_right, digit_top, digit_bottom = digit_bounds
                self.canvas.create_rectangle(
                    digit_left * ZOOM,
                    digit_top * ZOOM,
                    (digit_right + 1) * ZOOM,
                    (digit_bottom + 1) * ZOOM,
                    outline="lime",
                    width=3,
                )
            self.digit_canvas.delete("all")
            self.digit_canvas.create_image(
                0, 0, anchor="nw", image=self.digit_photo
            )

            frame_ok, frame_message = check_frame_quality(frame)
            if not frame_ok:
                result_text = "촬영 다시 하기"
            elif confidence < UNKNOWN_THRESHOLD:
                result_text = f"모르겠음 (최고 후보 {label})"
            else:
                result_text = f"예측 숫자: {label}"
            self.result_label.config(text=result_text)
            self.probability_label.config(
                text="   ".join(
                    f"{digit}: {probability * 100:5.1f}%"
                    for digit, probability in probabilities.items()
                )
            )
            self.status.config(
                text=(
                    f"신뢰도 {confidence * 100:.1f}%"
                    if frame_ok
                    else frame_message
                )
            )
        except Exception as error:
            self.status.config(text=f"오류: {error}")

    def close(self) -> None:
        self.board.close()
        self.root.destroy()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Arduino TinyML 추론 GUI")
    parser.add_argument("--port", required=True, help="예: COM5")
    args = parser.parse_args()

    board = serial.Serial(args.port, 115200, timeout=5)
    try:
        wait_for_board(board)
        root = tk.Tk()
        InferenceApp(root, board)
        root.mainloop()
    finally:
        if board.is_open:
            board.close()


if __name__ == "__main__":
    main()
