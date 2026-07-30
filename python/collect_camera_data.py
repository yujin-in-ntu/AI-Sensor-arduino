"""160x120 Full View를 보며 숫자 데이터를 수집하고 28x28 학습본을 만듭니다."""

from __future__ import annotations

import argparse
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path

import numpy as np
import serial

from camera_preprocess import (
    check_digit_quality,
    check_frame_quality,
    find_digit_bounds,
    find_paper_bounds,
    make_digit_image,
)
from preview_camera import HEIGHT, WIDTH, ZOOM, read_frame, wait_for_board

IMAGE_SIZE = 28
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def save_pgm(path: Path, image: np.ndarray) -> None:
    """uint8 흑백 배열을 PGM으로 저장합니다."""
    height, width = image.shape
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(f"P5\n{width} {height}\n255\n".encode("ascii") + image.tobytes())


def count_saved(root: Path, digit: int) -> int:
    return len(list((root / str(digit)).glob("*.pgm")))


class CollectorApp:
    def __init__(
        self,
        root: tk.Tk,
        board: serial.Serial,
        digits: list[int],
        per_digit: int,
        digit_root: Path,
        full_root: Path,
    ):
        self.root = root
        self.board = board
        self.digits = digits
        self.per_digit = per_digit
        self.digit_root = digit_root
        self.full_root = full_root
        self.current_digit_index = 0
        self.frame: np.ndarray | None = None
        self.digit_image: np.ndarray | None = None
        self.photo = None
        self.digit_photo = None

        root.title("TinyML Full View 숫자 데이터 수집")
        root.protocol("WM_DELETE_WINDOW", self.close)

        self.title = tk.Label(root, font=("Malgun Gothic", 13, "bold"))
        self.title.pack(pady=(10, 3))
        tk.Label(
            root,
            text="줄 있는 흰 종이도 가능하며, 검은 책상과 종이 바깥은 자동으로 제외됩니다.",
            font=("Malgun Gothic", 10),
        ).pack()

        previews = tk.Frame(root)
        previews.pack(padx=10, pady=6)

        full_group = tk.Frame(previews)
        full_group.pack(side="left", padx=4)
        tk.Label(full_group, text="카메라 원본 160×120").pack()
        self.canvas = tk.Canvas(
            full_group, width=WIDTH * ZOOM, height=HEIGHT * ZOOM, bg="black"
        )
        self.canvas.pack()

        digit_group = tk.Frame(previews)
        digit_group.pack(side="left", padx=4)
        tk.Label(digit_group, text="AI가 실제로 보는 28×28").pack()
        self.digit_canvas = tk.Canvas(
            digit_group, width=28 * 10, height=28 * 10, bg="black"
        )
        self.digit_canvas.pack()

        self.status = tk.Label(
            root, text="촬영 버튼을 누르세요.", font=("Malgun Gothic", 10)
        )
        self.status.pack(pady=3)

        buttons = tk.Frame(root)
        buttons.pack(pady=(3, 10))
        tk.Button(buttons, text="촬영", command=self.capture, width=12).pack(
            side="left", padx=4
        )
        self.save_button = tk.Button(
            buttons, text="이 사진 저장", command=self.save, width=12, state="disabled"
        )
        self.save_button.pack(side="left", padx=4)
        tk.Button(buttons, text="종료", command=self.close, width=10).pack(
            side="left", padx=4
        )

        self.advance_if_complete()
        self.update_title()
        root.after(300, self.capture)

    @property
    def digit(self) -> int:
        return self.digits[self.current_digit_index]

    def advance_if_complete(self) -> None:
        while (
            self.current_digit_index < len(self.digits)
            and count_saved(self.digit_root, self.digits[self.current_digit_index])
            >= self.per_digit
        ):
            self.current_digit_index += 1
        if self.current_digit_index >= len(self.digits):
            self.status.config(text="목표한 모든 숫자 촬영을 완료했습니다!")
            self.save_button.config(state="disabled")

    def update_title(self) -> None:
        if self.current_digit_index >= len(self.digits):
            self.title.config(text="수집 완료")
            return
        count = count_saved(self.digit_root, self.digit)
        self.title.config(
            text=f"현재 숫자: {self.digit}   {count + 1}/{self.per_digit}"
        )

    def to_photo(self, frame: np.ndarray) -> tk.PhotoImage:
        image = tk.PhotoImage(width=WIDTH, height=HEIGHT)
        for y, row in enumerate(frame):
            colors = " ".join(
                f"#{int(v):02x}{int(v):02x}{int(v):02x}" for v in row
            )
            image.put("{" + colors + "}", to=(0, y))
        return image.zoom(ZOOM, ZOOM)

    def to_digit_photo(self, image_array: np.ndarray) -> tk.PhotoImage:
        image = tk.PhotoImage(width=28, height=28)
        for y, row in enumerate(image_array):
            colors = " ".join(
                f"#{int(v):02x}{int(v):02x}{int(v):02x}" for v in row
            )
            image.put("{" + colors + "}", to=(0, y))
        return image.zoom(10, 10)

    def capture(self) -> None:
        if self.current_digit_index >= len(self.digits):
            return
        self.status.config(text="촬영 중...")
        self.root.update_idletasks()
        try:
            self.frame = read_frame(self.board)
            self.digit_image = make_digit_image(self.frame)
            self.photo = self.to_photo(self.frame)
            self.digit_photo = self.to_digit_photo(self.digit_image)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
            left, right, top, bottom = find_paper_bounds(self.frame)
            self.canvas.create_rectangle(
                left * ZOOM,
                top * ZOOM,
                (right + 1) * ZOOM,
                (bottom + 1) * ZOOM,
                outline="red",
                width=3,
            )
            digit_bounds = find_digit_bounds(self.frame)
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
            frame_passed, frame_message = check_frame_quality(self.frame)
            image_passed, image_message = check_digit_quality(self.digit_image)
            passed = frame_passed and image_passed
            message = frame_message if not frame_passed else image_message
            self.status.config(
                text=(
                    "품질 검사 통과 — 오른쪽 AI 입력이 숫자로 보이면 저장하세요."
                    if passed
                    else f"저장 불가: {message}"
                )
            )
            self.save_button.config(state="normal" if passed else "disabled")
        except Exception as error:
            self.status.config(text=f"촬영 오류: {error}")
            self.save_button.config(state="disabled")

    def save(self) -> None:
        if (
            self.frame is None
            or self.digit_image is None
            or self.current_digit_index >= len(self.digits)
        ):
            return
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        digit = self.digit

        # 원본을 보존하면 나중에 다른 자르기/축소 방식도 시험할 수 있습니다.
        save_pgm(self.full_root / str(digit) / f"{stamp}.pgm", self.frame)
        save_pgm(self.digit_root / str(digit) / f"{stamp}.pgm", self.digit_image)

        self.frame = None
        self.digit_image = None
        self.save_button.config(state="disabled")
        self.advance_if_complete()
        self.update_title()
        if self.current_digit_index < len(self.digits):
            self.status.config(text="저장 완료. 다음 숫자를 놓고 촬영하세요.")

    def close(self) -> None:
        self.board.close()
        self.root.destroy()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Full View 숫자 데이터 수집")
    parser.add_argument("--port", required=True, help="예: COM5")
    parser.add_argument("--digits", default="0123456789")
    parser.add_argument("--per-digit", type=int, default=30)
    parser.add_argument(
        "--digit-output",
        type=Path,
        default=PROJECT_ROOT / "data" / "camera_digits",
    )
    parser.add_argument(
        "--full-output",
        type=Path,
        default=PROJECT_ROOT / "data" / "camera_full",
    )
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    digits = [int(char) for char in args.digits]
    board = serial.Serial(args.port, 921600, timeout=5)
    try:
        wait_for_board(board)
        root = tk.Tk()
        CollectorApp(
            root,
            board,
            digits,
            args.per_digit,
            args.digit_output,
            args.full_output,
        )
        root.mainloop()
    finally:
        if board.is_open:
            board.close()


if __name__ == "__main__":
    main()
