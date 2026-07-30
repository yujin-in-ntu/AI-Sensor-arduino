"""PC 수집/미리보기에서 공통으로 사용하는 카메라 숫자 전처리입니다."""

from __future__ import annotations

import numpy as np

IMAGE_SIZE = 28
PAPER_THRESHOLD = 100
INK_THRESHOLD = 50
MNIST_DIGIT_SIZE = 20
CURVED_DIGIT_RATIO = 0.16
CURVED_DIGIT_MIN_WIDTH = 16


def _longest_run(mask: np.ndarray) -> tuple[int, int] | None:
    """True가 가장 길게 이어지는 시작/끝 인덱스를 찾습니다."""
    best_start = best_end = -1
    start = -1
    for index, value in enumerate(np.append(mask, False)):
        if value and start < 0:
            start = index
        elif not value and start >= 0:
            if index - start > best_end - best_start + 1:
                best_start, best_end = start, index - 1
            start = -1
    if best_start < 0:
        return None
    return best_start, best_end


def _bridge_small_gaps(mask: np.ndarray, max_gap: int = 12) -> np.ndarray:
    """숫자 획 때문에 종이 영역에 생긴 짧은 False 구간을 이어 붙입니다."""
    result = mask.copy()
    index = 0
    while index < len(result):
        if result[index]:
            index += 1
            continue
        start = index
        while index < len(result) and not result[index]:
            index += 1
        # 양쪽이 종이이고 틈이 짧을 때만 메웁니다.
        if start > 0 and index < len(result) and index - start <= max_gap:
            result[start:index] = True
    return result


def find_paper_bounds(frame: np.ndarray) -> tuple[int, int, int, int]:
    """밝은 종이로 보이는 가장 큰 직사각형 영역을 찾습니다."""
    height, width = frame.shape
    bright = frame > PAPER_THRESHOLD

    column_mask = bright.sum(axis=0) >= int(height * 0.35)
    column_mask = _bridge_small_gaps(column_mask)
    column_run = _longest_run(column_mask)
    if column_run is None or column_run[1] - column_run[0] + 1 < 20:
        return 20, 139, 0, 119
    left, right = column_run

    paper_width = right - left + 1
    row_mask = bright[:, left : right + 1].sum(axis=1) >= int(paper_width * 0.35)
    row_mask = _bridge_small_gaps(row_mask)
    row_run = _longest_run(row_mask)
    if row_run is None or row_run[1] - row_run[0] + 1 < 20:
        top, bottom = 0, height - 1
    else:
        top, bottom = row_run
    return left, right, top, bottom


def _paper_level(frame: np.ndarray, bounds: tuple[int, int, int, int]) -> int:
    """자동 노출이 달라져도 쓸 수 있도록 현재 종이의 대표 밝기를 구합니다."""
    left, right, top, bottom = bounds
    paper = frame[top : bottom + 1, left : right + 1]
    bright_pixels = paper[paper > PAPER_THRESHOLD]
    return int(bright_pixels.mean()) if bright_pixels.size else 200


def find_digit_bounds(frame: np.ndarray) -> tuple[int, int, int, int] | None:
    """종이 가장자리와 줄을 제외하고 실제 숫자 획의 범위를 찾습니다."""
    paper_bounds = find_paper_bounds(frame)
    left, right, top, bottom = paper_bounds
    paper_level = _paper_level(frame, paper_bounds)

    # 종이 테두리, 검은 책상, 스프링이 숫자로 잡히지 않도록 안쪽만 검사합니다.
    margin_x = max(3, int((right - left + 1) * 0.08))
    margin_y = max(3, int((bottom - top + 1) * 0.08))
    inner_left = left + margin_x
    inner_right = right - margin_x
    inner_top = top + margin_y
    inner_bottom = bottom - margin_y
    if inner_left >= inner_right or inner_top >= inner_bottom:
        return None

    region = frame[inner_top : inner_bottom + 1, inner_left : inner_right + 1]
    ink = paper_level - region.astype(np.int16) > INK_THRESHOLD

    # 공책의 가로줄처럼 화면을 길게 가로지르는 얇은 선은 제거합니다.
    long_rows = ink.sum(axis=1) >= int(region.shape[1] * 0.55)
    ink[long_rows, :] = False

    # 숫자는 같은 열에 최소 두 픽셀 이상 이어집니다. 작은 점 노이즈는 무시합니다.
    column_mask = ink.sum(axis=0) >= 2
    column_mask = _bridge_small_gaps(column_mask, max_gap=3)
    column_run = _longest_run(column_mask)
    if column_run is None:
        return None
    x0, x1 = column_run

    row_mask = ink[:, x0 : x1 + 1].sum(axis=1) >= 1
    row_mask = _bridge_small_gaps(row_mask, max_gap=3)
    row_run = _longest_run(row_mask)
    if row_run is None:
        return None
    y0, y1 = row_run
    return inner_left + x0, inner_left + x1, inner_top + y0, inner_top + y1


def make_digit_image(frame: np.ndarray) -> np.ndarray:
    """숫자만 잘라 비율을 유지하고 MNIST와 같은 28x28 중앙에 놓습니다."""
    paper_bounds = find_paper_bounds(frame)
    digit_bounds = find_digit_bounds(frame)
    result = np.zeros((IMAGE_SIZE, IMAGE_SIZE), dtype=np.uint8)
    if digit_bounds is None:
        return result

    left, right, top, bottom = digit_bounds
    source_width = right - left + 1
    source_height = bottom - top + 1
    if source_width >= source_height:
        target_width = MNIST_DIGIT_SIZE
        target_height = max(1, round(source_height * MNIST_DIGIT_SIZE / source_width))
    else:
        target_height = MNIST_DIGIT_SIZE
        target_width = max(1, round(source_width * MNIST_DIGIT_SIZE / source_height))
    widen_after_cleanup = (
        source_width / source_height >= CURVED_DIGIT_RATIO
        and target_width < CURVED_DIGIT_MIN_WIDTH
    )

    offset_x = (IMAGE_SIZE - target_width) // 2
    offset_y = (IMAGE_SIZE - target_height) // 2
    paper_level = _paper_level(frame, paper_bounds)

    # 각 축소 칸에서 가장 어두운 점을 사용해 가는 펜 획도 보존합니다.
    for y in range(target_height):
        y0 = top + (y * source_height) // target_height
        y1 = max(y0 + 1, top + ((y + 1) * source_height) // target_height)
        for x in range(target_width):
            x0 = left + (x * source_width) // target_width
            x1 = max(x0 + 1, left + ((x + 1) * source_width) // target_width)
            gray = int(frame[y0:y1, x0:x1].min())
            darkness = paper_level - gray
            value = 0 if darkness <= INK_THRESHOLD else (darkness - INK_THRESHOLD) * 255 // 150
            result[offset_y + y, offset_x + x] = np.clip(value, 0, 255)

    # 회색 원본을 먼저 넓히면 획 사이가 붙을 수 있습니다. 검은 배경/밝은 획으로
    # 정리된 결과만 가로 보간하여 3의 위·아래 굴곡을 보존합니다.
    if widen_after_cleanup:
        source = result[
            offset_y : offset_y + target_height,
            offset_x : offset_x + target_width,
        ].astype(np.float32)
        widened = np.empty(
            (target_height, CURVED_DIGIT_MIN_WIDTH), dtype=np.uint8
        )
        for x in range(CURVED_DIGIT_MIN_WIDTH):
            position = (
                x * (target_width - 1) / (CURVED_DIGIT_MIN_WIDTH - 1)
                if target_width > 1
                else 0
            )
            x0 = int(position)
            x1 = min(x0 + 1, target_width - 1)
            weight = position - x0
            widened[:, x] = np.clip(
                source[:, x0] * (1.0 - weight) + source[:, x1] * weight,
                0,
                255,
            ).astype(np.uint8)
        result.fill(0)
        wide_offset_x = (IMAGE_SIZE - CURVED_DIGIT_MIN_WIDTH) // 2
        result[
            offset_y : offset_y + target_height,
            wide_offset_x : wide_offset_x + CURVED_DIGIT_MIN_WIDTH,
        ] = widened
    return result


def check_frame_quality(frame: np.ndarray) -> tuple[bool, str]:
    """숫자가 잘리지 않고 종이 안쪽에서 온전히 발견됐는지 검사합니다."""
    left, right, top, bottom = find_paper_bounds(frame)
    bounds = find_digit_bounds(frame)
    if bounds is None:
        return False, "검은 숫자 획을 찾지 못했습니다."

    margin_x = max(3, int((right - left + 1) * 0.08))
    margin_y = max(3, int((bottom - top + 1) * 0.08))
    safe_left = left + margin_x
    safe_right = right - margin_x
    safe_top = top + margin_y
    safe_bottom = bottom - margin_y
    digit_left, digit_right, digit_top, digit_bottom = bounds
    touches_both_sides = (
        digit_left <= safe_left + 1 and digit_right >= safe_right - 1
    )
    touches_top_and_bottom = (
        digit_top <= safe_top + 1 and digit_bottom >= safe_bottom - 1
    )
    if touches_both_sides or touches_top_and_bottom:
        return False, "숫자가 화면 밖으로 잘렸습니다. 숫자를 더 작게 쓰거나 카메라에서 멀리 놓으세요."
    return True, "숫자 전체 감지 완료"


def check_digit_quality(image: np.ndarray) -> tuple[bool, str]:
    """전처리된 28x28 이미지가 학습에 쓸 만한지 검사합니다."""
    border = np.concatenate(
        [
            image[:2, :].ravel(),
            image[-2:, :].ravel(),
            image[:, :2].ravel(),
            image[:, -2:].ravel(),
        ]
    )
    border_mean = float(border.mean())
    foreground_ratio = float((image > 100).mean())
    if border_mean > 80:
        return False, "종이 자동 탐지가 불안정합니다."
    if foreground_ratio < 0.01:
        return False, "숫자가 너무 얇거나 작습니다."
    if foreground_ratio > 0.35:
        return False, "숫자 이외의 어두운 영역이 너무 큽니다."
    return True, "품질 검사 통과"
