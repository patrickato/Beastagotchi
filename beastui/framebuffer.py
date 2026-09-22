from __future__ import annotations

import os
from pathlib import Path


class FrameBuffer:
    """480x320 RGB565 framebuffer writer with dirty-row updates.

    The physical ILI9486/fbtft target accepts ordinary seek/write operations on
    /dev/fb*.  Rewriting all 307,200 bytes for a frame whose footer or one graph
    changed is needless work.  Beast therefore keeps the previous RGB565 frame,
    finds changed rows, merges nearby rows into spans, and writes only those
    spans.  A heavily animated frame automatically falls back to a single full
    write, which is faster than hundreds of tiny writes.

    ``last_*`` fields are deliberately public telemetry: the UI/runtime monitor
    can report whether a theme is cheap or expensive on the *actual* display.
    """

    def __init__(self, device: str = "/dev/fb1", width: int = 480, height: int = 320,
                 output: str | None = None, *, full_write_threshold: float = 0.72,
                 merge_gap_rows: int = 1) -> None:
        self.device = device
        self.width = width
        self.height = height
        self.output = output
        self._fd: int | None = None
        self._previous: bytes | None = None
        self.full_write_threshold = max(0.05, min(1.0, float(full_write_threshold)))
        self.merge_gap_rows = max(0, int(merge_gap_rows))
        self.last_changed_rows = height
        self.last_bytes_written = width * height * 2
        self.last_full_write = True
        self.last_spans: list[tuple[int, int]] = [(0, height - 1)]
        self.total_frames = 0
        self.total_bytes_written = 0
        self.total_full_writes = 0
        self.total_saved_bytes = 0

    @staticmethod
    def _rgb565_bytes(image) -> bytes:
        try:
            import numpy as np
            a = np.asarray(image.convert("RGB"), dtype=np.uint16)
            rgb565 = (((a[:, :, 0] >> 3) << 11) | ((a[:, :, 1] >> 2) << 5) | (a[:, :, 2] >> 3)).astype("<u2")
            return rgb565.tobytes()
        except Exception:
            raw = image.convert("RGB").tobytes()
            out = bytearray((len(raw) // 3) * 2)
            j = 0
            for i in range(0, len(raw), 3):
                r, g, b = raw[i], raw[i + 1], raw[i + 2]
                v = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
                out[j] = v & 0xff
                out[j + 1] = (v >> 8) & 0xff
                j += 2
            return bytes(out)

    def _dirty_spans(self, payload: bytes) -> tuple[list[tuple[int, int]], int]:
        if self._previous is None or len(self._previous) != len(payload):
            return [(0, self.height - 1)], self.height
        row_bytes = self.width * 2
        changed: list[int] = []
        previous = self._previous
        for row in range(self.height):
            start = row * row_bytes
            end = start + row_bytes
            if payload[start:end] != previous[start:end]:
                changed.append(row)
        if not changed:
            return [], 0
        spans: list[tuple[int, int]] = []
        start = prev = changed[0]
        for row in changed[1:]:
            if row - prev <= self.merge_gap_rows + 1:
                prev = row
                continue
            spans.append((start, prev))
            start = prev = row
        spans.append((start, prev))
        return spans, len(changed)

    @staticmethod
    def _write_all(fd: int, view: memoryview) -> int:
        total = 0
        while total < len(view):
            n = os.write(fd, view[total:])
            if n <= 0:
                raise OSError("framebuffer write returned no progress")
            total += n
        return total

    def write(self, image) -> None:
        if image.size != (self.width, self.height):
            raise ValueError(f"expected {self.width}x{self.height}, got {image.size}")
        if self.output:
            Path(self.output).parent.mkdir(parents=True, exist_ok=True)
            image.save(self.output)
            # Off-screen output still reports a full image write because PNG
            # emission is not comparable to the physical framebuffer path.
            self.last_changed_rows = self.height
            self.last_bytes_written = self.width * self.height * 2
            self.last_full_write = True
            self.last_spans = [(0, self.height - 1)]
            self.total_frames += 1
            self.total_bytes_written += self.last_bytes_written
            self.total_full_writes += 1
            return

        payload = self._rgb565_bytes(image)
        if self._fd is None:
            self._fd = os.open(self.device, os.O_WRONLY)

        spans, changed_rows = self._dirty_spans(payload)
        self.last_changed_rows = changed_rows
        if not spans:
            self.last_bytes_written = 0
            self.last_full_write = False
            self.last_spans = []
            self._previous = payload
            self.total_frames += 1
            self.total_saved_bytes += self.width * self.height * 2
            return

        # If most rows changed, one sequential write is cheaper than seeking and
        # issuing a large number of partial writes.
        if changed_rows / max(1, self.height) >= self.full_write_threshold:
            os.lseek(self._fd, 0, os.SEEK_SET)
            written = self._write_all(self._fd, memoryview(payload))
            self.last_bytes_written = written
            self.last_full_write = True
            self.last_spans = [(0, self.height - 1)]
        else:
            row_bytes = self.width * 2
            total = 0
            for first, last in spans:
                offset = first * row_bytes
                end = (last + 1) * row_bytes
                os.lseek(self._fd, offset, os.SEEK_SET)
                total += self._write_all(self._fd, memoryview(payload)[offset:end])
            self.last_bytes_written = total
            self.last_full_write = False
            self.last_spans = spans

        self._previous = payload
        total_frame = self.width * self.height * 2
        self.total_frames += 1
        self.total_bytes_written += int(self.last_bytes_written)
        self.total_full_writes += 1 if self.last_full_write else 0
        self.total_saved_bytes += max(0, total_frame - int(self.last_bytes_written))

    def reset_diff(self) -> None:
        """Force the next physical write to refresh the complete framebuffer."""
        self._previous = None

    def telemetry(self) -> dict[str, int | bool]:
        total = self.width * self.height * 2
        return {
            "changed_rows": int(self.last_changed_rows),
            "bytes_written": int(self.last_bytes_written),
            "full_write": bool(self.last_full_write),
            "span_count": len(self.last_spans),
            "frame_bytes": total,
            "saved_bytes": max(0, total - int(self.last_bytes_written)),
            "totals": {
                "frames": int(self.total_frames),
                "bytes_written": int(self.total_bytes_written),
                "full_writes": int(self.total_full_writes),
                "saved_bytes": int(self.total_saved_bytes),
            },
        }

    def close(self) -> None:
        if self._fd is not None:
            try:
                os.close(self._fd)
            finally:
                self._fd = None

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass
