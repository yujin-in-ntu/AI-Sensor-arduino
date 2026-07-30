"""OV7675의 원본 160x120 영상을 확대해서 보여줍니다."""

from __future__ import annotations

import argparse
import sys
import tkinter as tk

import numpy as np
import serial

WIDTH = 160
HEIGHT = 120
ZOOM = 4
FRAME_BYTES = WIDTH * HEIGHT


def wait_for_board(board: serial.Serial) -> None:
    """PING을 반복해 Arduino가 준비됐는지 확인합니다."""
    import time
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        board.write(b"PING\n")
        board.flush()
        line = board.readline().decode("ascii", errors="ignore").strip()
        if line.startswith("HELLO,OV7675_FULL"):
            return
        time.sleep(0.2)
    raise TimeoutError("원본 미리보기 스케치의 응답을 받지 못했습니다.")


def read_frame(board: serial.Serial) -> np.ndarray:
    """헤더 다음의 19,200바이트를 정확히 읽습니다."""
    board.reset_input_buffer()
    board.write(b"FRAME\n")
    board.flush()

    header = board.readline().decode("ascii", errors="ignore").strip()
    if header != f"FRAME,{FRAME_BYTES}":
        raise RuntimeError(f"잘못된 프레임 헤더: {header!r}")

    data = board.read(FRAME_BYTES)
    if len(data) != FRAME_BYTES:
        raise RuntimeError(f"프레임 부족: {len(data)}/{FRAME_BYTES}바이트")
    board.readline()  # 바이너리 뒤 줄바꿈
    end = board.readline().decode("ascii", errors="ignore").strip()
    if end != "END_FRAME":
        raise RuntimeError(f"프레임 종료 표시 오류: {end!r}")
    return np.frombuffer(data, dtype=np.uint8).reshape(HEIGHT, WIDTH)


class App:
    def __init__(self, root: tk.Tk, board: serial.Serial):
        self.root = root
        self.board = board
        self.photo = None
        root.title("OV7675 원본 160x120 미리보기")
        root.protocol("WM_DELETE_WINDOW", self.close)

        tk.Label(
            root,
            text="빨간 사각형이 AI가 사용하는 중앙 120×120 영역입니다.",
            font=("Malgun Gothic", 11),
        ).pack(pady=(10, 4))

        self.canvas = tk.Canvas(
            root, width=WIDTH * ZOOM, height=HEIGHT * ZOOM, bg="black"
        )
        self.canvas.pack(padx=10, pady=5)
        self.status = tk.Label(root, text="촬영 버튼을 누르세요.")
        self.status.pack(pady=4)
        tk.Button(root, text="한 장 촬영", command=self.capture, width=16).pack(
            pady=(2, 10)
        )
        root.after(300, self.capture)

    def to_photo(self, frame: np.ndarray) -> tk.PhotoImage:
        image = tk.PhotoImage(width=WIDTH, height=HEIGHT)
        for y, row in enumerate(frame):
            colors = " ".join(
                f"#{int(v):02x}{int(v):02x}{int(v):02x}" for v in row
            )
            image.put("{" + colors + "}", to=(0, y))
        return image.zoom(ZOOM, ZOOM)

    def capture(self) -> None:
        self.status.config(text="촬영 중...")
        self.root.update_idletasks()
        try:
            frame = read_frame(self.board)
            self.photo = self.to_photo(frame)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
            # 160x120 중 x=20~139가 AI에 들어가는 정사각형 영역입니다.
            self.canvas.create_rectangle(
                20 * ZOOM,
                0,
                140 * ZOOM,
                120 * ZOOM,
                outline="red",
                width=3,
            )
            contrast = int(np.percentile(frame, 95) - np.percentile(frame, 5))
            self.status.config(
                text=f"명암 차이: {contrast}/255 — 숫자를 빨간 영역 중앙에 크게 놓으세요."
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
    parser = argparse.ArgumentParser(description="OV7675 원본 영상 확인")
    parser.add_argument("--port", required=True)
    args = parser.parse_args()

    board = serial.Serial(args.port, 921600, timeout=5)
    try:
        wait_for_board(board)
        root = tk.Tk()
        App(root, board)
        root.mainloop()
    finally:
        if board.is_open:
            board.close()


if __name__ == "__main__":
    main()
