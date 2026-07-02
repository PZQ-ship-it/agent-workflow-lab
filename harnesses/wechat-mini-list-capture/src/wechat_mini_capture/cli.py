from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


Point = Tuple[int, int]
Rect = Tuple[int, int, int, int]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def package_root() -> Path:
    return Path(__file__).resolve().parents[2]


def repo_root() -> Path:
    return package_root().parents[1]


def default_runtime_dir() -> Path:
    return repo_root() / "runtime" / "wechat-mini-list-capture"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def append_jsonl(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16]


def normalize_text(text: str) -> str:
    return " ".join(text.replace("\r", "\n").split())


def resolve_path(value: Optional[str], base: Path) -> Path:
    if not value:
        return default_runtime_dir()
    p = Path(value)
    if p.is_absolute():
        return p
    return (base / p).resolve()


def rect_from_config(value: Optional[Sequence[int]]) -> Optional[Rect]:
    if not value:
        return None
    if len(value) != 4:
        raise ValueError("rect must be [left, top, right, bottom]")
    left, top, right, bottom = [int(x) for x in value]
    if right <= left or bottom <= top:
        raise ValueError("rect right/bottom must be greater than left/top")
    return left, top, right, bottom


def parse_rect_arg(value: str) -> Rect:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        raise ValueError("rect argument must be left,top,right,bottom")
    return rect_from_config([int(part) for part in parts])  # type: ignore[return-value]


def point_from_config(value: Optional[Sequence[int]]) -> Optional[Point]:
    if not value:
        return None
    if len(value) != 2:
        raise ValueError("point must be [x, y]")
    return int(value[0]), int(value[1])


def crop_box(rect: Rect) -> Tuple[int, int, int, int]:
    return rect


def rect_center(rect: Sequence[int]) -> Point:
    return int((int(rect[0]) + int(rect[2])) / 2), int((int(rect[1]) + int(rect[3])) / 2)


def point_in_rect(point: Point, rect: Sequence[int]) -> bool:
    return int(rect[0]) <= point[0] <= int(rect[2]) and int(rect[1]) <= point[1] <= int(rect[3])


def filter_boxes_in_rect(boxes: Sequence["OCRBox"], rect: Sequence[int]) -> List["OCRBox"]:
    filtered = []
    for box in boxes:
        if point_in_rect(rect_center(box.box), rect):
            filtered.append(box)
    return filtered


def image_pixels(image):
    getter = getattr(image, "get_flattened_data", None)
    if callable(getter):
        return getter()
    return image.getdata()


@dataclass
class OCRBox:
    text: str
    score: float
    box: Rect


class DesktopDriver:
    def __init__(self) -> None:
        try:
            import pyautogui  # type: ignore
        except Exception as exc:
            raise RuntimeError("pyautogui is not installed in this Python env") from exc
        self.pg = pyautogui
        self.pg.PAUSE = 0.08

    def screen_size(self) -> Tuple[int, int]:
        size = self.pg.size()
        return int(size.width), int(size.height)

    def position(self) -> Point:
        pos = self.pg.position()
        return int(pos.x), int(pos.y)

    def screenshot(self):
        return self.pg.screenshot()

    def click(self, point: Point) -> None:
        self.pg.click(point[0], point[1])

    def scroll(self, clicks: int) -> None:
        self.pg.scroll(int(clicks))

    def hotkey(self, keys: Sequence[str]) -> None:
        self.pg.hotkey(*keys)


class AndroidAdbDriver:
    def __init__(self, adb_path: str = "adb", serial: Optional[str] = None) -> None:
        self.adb_path = adb_path
        self.serial = serial
        if shutil.which(adb_path) is None and not Path(adb_path).exists():
            raise RuntimeError("adb is not installed or not on PATH")
        self._check_device()

    def _base_cmd(self) -> List[str]:
        cmd = [self.adb_path]
        if self.serial:
            cmd += ["-s", self.serial]
        return cmd

    def _run(self, args: Sequence[str], binary: bool = False, timeout: int = 20):
        result = subprocess.run(
            self._base_cmd() + list(args),
            check=False,
            capture_output=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="ignore").strip()
            stdout = result.stdout.decode("utf-8", errors="ignore").strip()
            raise RuntimeError(stderr or stdout or f"adb command failed: {' '.join(args)}")
        return result.stdout if binary else result.stdout.decode("utf-8", errors="ignore")

    def _check_device(self) -> None:
        out = self._run(["devices"])
        devices = [line.split()[0] for line in out.splitlines()[1:] if "\tdevice" in line]
        if self.serial:
            if self.serial not in devices:
                raise RuntimeError(f"adb device not connected: {self.serial}")
        elif not devices:
            raise RuntimeError("no adb device connected")
        elif len(devices) > 1:
            raise RuntimeError(f"multiple adb devices connected; pass --adb-serial. Found: {', '.join(devices)}")
        else:
            self.serial = devices[0]

    def screen_size(self) -> Tuple[int, int]:
        out = self._run(["shell", "wm", "size"])
        # Example: Physical size: 1080x2400
        for part in out.replace("\r", "\n").split():
            if "x" in part and part.replace("x", "").isdigit():
                width, height = part.split("x", 1)
                return int(width), int(height)
        raise RuntimeError(f"could not parse adb wm size: {out}")

    def position(self) -> Point:
        return (0, 0)

    def screenshot(self):
        from PIL import Image

        data = self._run(["exec-out", "screencap", "-p"], binary=True, timeout=30)
        return Image.open(io.BytesIO(data)).convert("RGB")

    def click(self, point: Point) -> None:
        self._run(["shell", "input", "tap", str(int(point[0])), str(int(point[1]))])

    def scroll(self, clicks: int) -> None:
        width, height = self.screen_size()
        magnitude = min(max(abs(int(clicks)), 1), 12)
        start_y = int(height * (0.72 if clicks < 0 else 0.32))
        end_y = int(height * (0.28 if clicks < 0 else 0.72))
        duration = max(120, 360 - magnitude * 18)
        self.swipe((int(width * 0.5), start_y), (int(width * 0.5), end_y), duration_ms=duration)

    def swipe(self, start: Point, end: Point, duration_ms: int = 220) -> None:
        self._run(
            [
                "shell",
                "input",
                "swipe",
                str(int(start[0])),
                str(int(start[1])),
                str(int(end[0])),
                str(int(end[1])),
                str(int(duration_ms)),
            ]
        )

    def hotkey(self, keys: Sequence[str]) -> None:
        joined = ",".join(keys).lower()
        if "back" in joined or "alt,left" in joined:
            self._run(["shell", "input", "keyevent", "4"])
        elif "home" in joined:
            self._run(["shell", "input", "keyevent", "3"])
        else:
            raise RuntimeError(f"unsupported adb hotkey: {keys}")


def create_driver(config: Dict[str, Any], args: Optional[argparse.Namespace] = None):
    driver_name = str(getattr(args, "driver", "") or config.get("driver", "desktop"))
    if driver_name in ("android_adb", "adb", "android"):
        adb_cfg = config.get("adb", {})
        adb_path = str(getattr(args, "adb_path", "") or adb_cfg.get("path", "adb"))
        serial = getattr(args, "adb_serial", None) or adb_cfg.get("serial")
        return AndroidAdbDriver(adb_path=adb_path, serial=serial)
    return DesktopDriver()


class OCRProvider:
    def __init__(self, engine: str = "auto") -> None:
        self.engine = engine
        self.impl = None
        self.name = "none"
        if engine in ("auto", "rapidocr"):
            try:
                from rapidocr_onnxruntime import RapidOCR  # type: ignore

                self.impl = RapidOCR()
                self.name = "rapidocr"
                return
            except Exception:
                if engine == "rapidocr":
                    raise
        if engine in ("auto", "tesseract"):
            try:
                import pytesseract  # type: ignore

                if shutil.which("tesseract"):
                    self.impl = pytesseract
                    self.name = "tesseract"
                    return
            except Exception:
                if engine == "tesseract":
                    raise
        self.impl = None
        self.name = "none"

    def available(self) -> bool:
        return self.name != "none"

    def read(self, image, offset: Point = (0, 0)) -> List[OCRBox]:
        if self.name == "rapidocr":
            import numpy as np  # type: ignore

            result, _ = self.impl(np.array(image))
            boxes: List[OCRBox] = []
            for item in result or []:
                raw_box, text, score = item[0], str(item[1]), float(item[2])
                xs = [int(p[0]) + offset[0] for p in raw_box]
                ys = [int(p[1]) + offset[1] for p in raw_box]
                boxes.append(OCRBox(text=text, score=score, box=(min(xs), min(ys), max(xs), max(ys))))
            return boxes
        if self.name == "tesseract":
            data = self.impl.image_to_data(image, output_type=self.impl.Output.DICT, lang="chi_sim+eng")
            boxes = []
            count = len(data.get("text", []))
            for i in range(count):
                text = str(data["text"][i]).strip()
                if not text:
                    continue
                try:
                    score = float(data["conf"][i]) / 100.0
                except Exception:
                    score = 0.0
                x, y = int(data["left"][i]), int(data["top"][i])
                w, h = int(data["width"][i]), int(data["height"][i])
                boxes.append(OCRBox(text=text, score=score, box=(x + offset[0], y + offset[1], x + w + offset[0], y + h + offset[1])))
            return boxes
        return []


def group_rows(boxes: List[OCRBox], min_score: float, min_chars: int) -> List[Dict[str, Any]]:
    filtered = [b for b in boxes if b.score >= min_score and len(normalize_text(b.text)) >= min_chars]
    filtered.sort(key=lambda b: (b.box[1], b.box[0]))
    rows: List[List[OCRBox]] = []
    for box in filtered:
        cy = (box.box[1] + box.box[3]) / 2
        placed = False
        for row in rows:
            rcy = sum((b.box[1] + b.box[3]) / 2 for b in row) / len(row)
            if abs(cy - rcy) <= 24:
                row.append(box)
                placed = True
                break
        if not placed:
            rows.append([box])

    candidates: List[Dict[str, Any]] = []
    for row in rows:
        row.sort(key=lambda b: b.box[0])
        text = normalize_text(" ".join(b.text for b in row))
        if len(text) < min_chars:
            continue
        left = min(b.box[0] for b in row)
        top = min(b.box[1] for b in row)
        right = max(b.box[2] for b in row)
        bottom = max(b.box[3] for b in row)
        candidates.append(
            {
                "text": text,
                "score": round(sum(b.score for b in row) / max(len(row), 1), 3),
                "box": [left, top, right, bottom],
                "center": [int((left + right) / 2), int((top + bottom) / 2)],
                "key": stable_hash(text),
            }
        )
    return candidates


def union_box(items: Sequence[Dict[str, Any]], pad: int, screen_size: Tuple[int, int]) -> Optional[List[int]]:
    if not items:
        return None
    left = max(0, min(int(item["box"][0]) for item in items) - pad)
    top = max(0, min(int(item["box"][1]) for item in items) - pad)
    right = min(screen_size[0], max(int(item["box"][2]) for item in items) + pad)
    bottom = min(screen_size[1], max(int(item["box"][3]) for item in items) + pad)
    if right <= left or bottom <= top:
        return None
    return [left, top, right, bottom]


def detect_item_candidates(
    boxes: List[OCRBox],
    min_score: float,
    min_chars: int,
    item_gap_px: int = 42,
    min_item_chars: int = 4,
) -> List[Dict[str, Any]]:
    rows = group_rows(boxes, min_score=min_score, min_chars=min_chars)
    rows.sort(key=lambda row: (row["box"][1], row["box"][0]))
    clusters: List[List[Dict[str, Any]]] = []
    for row in rows:
        text = normalize_text(row.get("text", ""))
        if len(text) < min_chars:
            continue
        top = int(row["box"][1])
        bottom = int(row["box"][3])
        if top < 40:
            continue
        if not clusters:
            clusters.append([row])
            continue
        prev_bottom = max(int(prev["box"][3]) for prev in clusters[-1])
        if top - prev_bottom <= item_gap_px:
            clusters[-1].append(row)
        else:
            clusters.append([row])

    candidates: List[Dict[str, Any]] = []
    for cluster in clusters:
        text = normalize_text(" ".join(str(row.get("text", "")) for row in cluster))
        if len(text) < min_item_chars:
            continue
        left = min(int(row["box"][0]) for row in cluster)
        top = min(int(row["box"][1]) for row in cluster)
        right = max(int(row["box"][2]) for row in cluster)
        bottom = max(int(row["box"][3]) for row in cluster)
        candidates.append(
            {
                "text": text,
                "score": round(sum(float(row.get("score", 0.0)) for row in cluster) / max(len(cluster), 1), 3),
                "box": [left, top, right, bottom],
                "center": [int((left + right) / 2), int((top + bottom) / 2)],
                "key": stable_hash(text),
                "row_count": len(cluster),
            }
        )
    return candidates


def configured_row_slots(row_slots: Sequence[Sequence[int]]) -> List[Dict[str, Any]]:
    rows = []
    for idx, raw in enumerate(row_slots):
        rect = rect_from_config(raw)
        assert rect is not None
        left, top, right, bottom = rect
        text = f"configured-row-{idx + 1}"
        rows.append(
            {
                "text": text,
                "score": 0.1,
                "box": [left, top, right, bottom],
                "center": [int((left + right) / 2), int((top + bottom) / 2)],
                "key": stable_hash(text),
            }
        )
    return rows


def candidates_from_row_slots(boxes: Sequence[OCRBox], row_slots: Sequence[Sequence[int]], min_score: float, min_chars: int) -> List[Dict[str, Any]]:
    rows = []
    for idx, raw in enumerate(row_slots):
        rect = rect_from_config(raw)
        assert rect is not None
        inside = [box for box in boxes if box.score >= min_score and point_in_rect(rect_center(box.box), rect)]
        inside.sort(key=lambda box: (box.box[1], box.box[0]))
        text = normalize_text(" ".join(box.text for box in inside))
        if len(text) < min_chars:
            text = f"configured-row-{idx + 1}"
        left, top, right, bottom = rect
        rows.append(
            {
                "text": text,
                "score": round(sum(box.score for box in inside) / max(len(inside), 1), 3) if inside else 0.1,
                "box": [left, top, right, bottom],
                "center": [int((left + right) / 2), int((top + bottom) / 2)],
                "key": stable_hash(text),
                "row_count": len(inside),
                "source": "row-slot",
            }
        )
    return rows


def _connected_components(mask: bytearray, width: int, height: int) -> List[Dict[str, int]]:
    visited = bytearray(width * height)
    components: List[Dict[str, int]] = []
    for start, value in enumerate(mask):
        if not value or visited[start]:
            continue
        stack = [start]
        visited[start] = 1
        area = 0
        left = right = start % width
        top = bottom = start // width
        while stack:
            idx = stack.pop()
            x = idx % width
            y = idx // width
            area += 1
            left = min(left, x)
            right = max(right, x)
            top = min(top, y)
            bottom = max(bottom, y)
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if nx < 0 or ny < 0 or nx >= width or ny >= height:
                    continue
                nidx = ny * width + nx
                if mask[nidx] and not visited[nidx]:
                    visited[nidx] = 1
                    stack.append(nidx)
        components.append({"left": left, "top": top, "right": right, "bottom": bottom, "area": area})
    return components


def detect_blue_app_region(image) -> Optional[List[int]]:
    rgb = image.convert("RGB")
    original_width, original_height = rgb.size
    scale = max(original_width / 720.0, 1.0)
    if scale > 1.0:
        small = rgb.resize((max(1, int(original_width / scale)), max(1, int(original_height / scale))))
    else:
        small = rgb
    width, height = small.size
    mask = bytearray(width * height)
    for idx, (red, green, blue) in enumerate(image_pixels(small)):
        if blue >= 145 and 20 <= red <= 115 and 20 <= green <= 125 and blue - red >= 45 and blue - green >= 35:
            mask[idx] = 1
    components = _connected_components(mask, width, height)
    viable = []
    for comp in components:
        comp_width = comp["right"] - comp["left"] + 1
        comp_height = comp["bottom"] - comp["top"] + 1
        if comp["area"] >= 1800 and comp_width >= 90 and comp_height >= 45:
            viable.append(comp)
    if not viable:
        return None
    comp = max(viable, key=lambda item: item["area"])
    left = max(0, int(comp["left"] * scale) - 3)
    top = max(0, int(comp["top"] * scale) - 3)
    right = min(original_width, int((comp["right"] + 1) * scale) + 3)
    header_bottom = min(original_height, int((comp["bottom"] + 1) * scale) + 3)
    app_width = right - left
    app_height = max(int(app_width * 1.88), int((header_bottom - top) * 2.65))
    bottom = min(original_height, top + app_height)
    if app_width < 260 or bottom - top < 450:
        return None
    return [left, top, right, bottom]


def detect_light_card_regions(image, offset: Point = (0, 0)) -> List[List[int]]:
    rgb = image.convert("RGB")
    width, height = rgb.size
    mask = bytearray(width * height)
    for idx, (red, green, blue) in enumerate(image_pixels(rgb)):
        if red >= 248 and green >= 248 and blue >= 248:
            mask[idx] = 1
    components = _connected_components(mask, width, height)
    min_width = max(120, int(width * 0.52))
    min_height = 58
    cards: List[List[int]] = []
    for comp in components:
        comp_width = comp["right"] - comp["left"] + 1
        comp_height = comp["bottom"] - comp["top"] + 1
        if comp_width < min_width or comp_height < min_height:
            continue
        if comp["area"] < int(comp_width * comp_height * 0.45):
            continue
        cards.append(
            [
                comp["left"] + offset[0],
                comp["top"] + offset[1],
                comp["right"] + 1 + offset[0],
                comp["bottom"] + 1 + offset[1],
            ]
        )
    cards.sort(key=lambda rect: (rect[1], rect[0]))
    return cards


def candidates_from_card_regions(
    boxes: Sequence[OCRBox],
    card_regions: Sequence[Sequence[int]],
    min_score: float,
    min_chars: int,
) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    for rect in card_regions:
        inside = [box for box in boxes if box.score >= min_score and point_in_rect(rect_center(box.box), rect)]
        inside.sort(key=lambda box: (box.box[1], box.box[0]))
        text = normalize_text(" ".join(box.text for box in inside))
        if len(text) < max(min_chars, 4):
            continue
        left, top, right, bottom = [int(x) for x in rect]
        candidates.append(
            {
                "text": text,
                "score": round(sum(box.score for box in inside) / max(len(inside), 1), 3),
                "box": [left, top, right, bottom],
                "center": [int((left + right) / 2), int((top + bottom) / 2)],
                "key": stable_hash(text),
                "row_count": len(inside),
                "source": "visual-card",
            }
        )
    return candidates


def save_screenshot(image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(str(path))


def load_config(args: argparse.Namespace) -> Tuple[Dict[str, Any], Path]:
    base = package_root()
    config_path = Path(args.config) if args.config else base / "config.example.json"
    config_path = config_path.resolve()
    config = load_json(config_path)
    return config, config_path


def runtime_for(config: Dict[str, Any], config_path: Path, run_id: Optional[str] = None) -> Path:
    runtime = resolve_path(config.get("runtime_dir"), config_path.parent)
    if run_id:
        runtime = runtime / "runs" / run_id
    return runtime


def command_doctor(args: argparse.Namespace) -> int:
    config, config_path = load_config(args)
    runtime = runtime_for(config, config_path)
    checks: List[Tuple[str, bool, str]] = []
    checks.append(("python", True, sys.version.split()[0]))
    checks.append(("config", config_path.exists(), str(config_path)))
    checks.append(("runtime_parent", True, str(runtime)))
    driver_name = str(getattr(args, "driver", "") or config.get("driver", "desktop"))
    try:
        driver = create_driver(config, args)
        checks.append(("driver", True, driver_name))
        try:
            checks.append(("screen", True, f"{driver.screen_size()[0]}x{driver.screen_size()[1]}"))
        except Exception as exc:
            checks.append(("screen", False, repr(exc)))
        if args.screenshot:
            img = driver.screenshot()
            checks.append(("screenshot", True, f"{img.size[0]}x{img.size[1]}"))
    except Exception as exc:
        checks.append(("driver", False, repr(exc)))
    ocr = OCRProvider(config.get("ocr", {}).get("engine", "auto"))
    checks.append(("ocr", ocr.available(), ocr.name))
    adb_cfg = config.get("adb", {})
    adb_probe = str(getattr(args, "adb_path", "") or adb_cfg.get("path", "adb"))
    adb_found = shutil.which(adb_probe) or (str(Path(adb_probe)) if Path(adb_probe).exists() else None)
    checks.append(("adb", adb_found is not None, adb_found or "not found"))
    checks.append(("tesseract", shutil.which("tesseract") is not None, shutil.which("tesseract") or "not found"))
    for name, ok, note in checks:
        print(f"[{'OK' if ok else 'MISS'}] {name}: {note}")
    return 0 if all(ok for name, ok, note in checks if name in ("python", "config", "driver")) else 2


def command_init_run(args: argparse.Namespace) -> int:
    config, config_path = load_config(args)
    run_id = args.run_id or now_stamp()
    runtime = runtime_for(config, config_path, run_id)
    runtime.mkdir(parents=True, exist_ok=True)
    save_json(runtime / "run-meta.json", {"run_id": run_id, "created_at": datetime.now().isoformat(), "config": str(config_path)})
    print(runtime)
    return 0


def wait_prompt(message: str) -> None:
    input(message + " Press Enter...")


def capture_point(driver: DesktopDriver, label: str) -> Point:
    wait_prompt(f"Move mouse to {label}.")
    return driver.position()


def capture_rect(driver: DesktopDriver, label: str) -> Rect:
    p1 = capture_point(driver, f"{label} top-left")
    p2 = capture_point(driver, f"{label} bottom-right")
    return min(p1[0], p2[0]), min(p1[1], p2[1]), max(p1[0], p2[0]), max(p1[1], p2[1])


def command_calibrate(args: argparse.Namespace) -> int:
    config, config_path = load_config(args)
    driver = DesktopDriver()
    runtime = resolve_path(config.get("runtime_dir"), config_path.parent)
    runtime.mkdir(parents=True, exist_ok=True)
    img = driver.screenshot()
    save_screenshot(img, runtime / "calibration-screen.png")
    print(f"Saved calibration screenshot: {runtime / 'calibration-screen.png'}")
    print("Calibrating two lists. Skip an entry point by pressing Enter without moving if the current list is already open.")
    for item in config.get("lists", []):
        print(f"\nList: {item.get('id')}")
        answer = input("Record a tab/entry click point for this list? [y/N] ").strip().lower()
        if answer == "y":
            item["entry_point"] = list(capture_point(driver, f"{item.get('id')} entry/tab center"))
        item["list_region"] = list(capture_rect(driver, f"{item.get('id')} visible list region"))
        answer = input("Use the same region for detail OCR? [Y/n] ").strip().lower()
        if answer == "n":
            item["detail_region"] = list(capture_rect(driver, f"{item.get('id')} detail content region"))
        else:
            item["detail_region"] = item["list_region"]
        answer = input("Add fixed row slots if OCR is unavailable? [y/N] ").strip().lower()
        slots: List[List[int]] = []
        if answer == "y":
            while True:
                more = input("Add one visible row slot? [y/N] ").strip().lower()
                if more != "y":
                    break
                slots.append(list(capture_rect(driver, f"{item.get('id')} row slot {len(slots)+1}")))
        item["row_slots"] = slots
    local_config = runtime / "config.local.json"
    save_json(local_config, config)
    print(f"Saved local config: {local_config}")
    return 0


def annotate_candidates(
    image,
    candidates: Sequence[Dict[str, Any]],
    output: Path,
    extra_rects: Optional[Sequence[Tuple[str, Sequence[int], str]]] = None,
) -> None:
    from PIL import ImageDraw, ImageFont

    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except Exception:
        font = ImageFont.load_default()
    colors = ["red", "orange", "deepskyblue", "lime", "magenta", "yellow"]
    for label, rect, color in extra_rects or []:
        left, top, right, bottom = [int(x) for x in rect]
        draw.rectangle((left, top, right, bottom), outline=color, width=4)
        label_width = max(70, min(240, 16 + 11 * len(label)))
        draw.rectangle((left, max(0, top - 28), left + label_width, top), fill=color)
        draw.text((left + 4, max(0, top - 26)), label, fill="black", font=font)
    for idx, candidate in enumerate(candidates, start=1):
        left, top, right, bottom = [int(x) for x in candidate["box"]]
        color = colors[(idx - 1) % len(colors)]
        draw.rectangle((left, top, right, bottom), outline=color, width=4)
        label = f"#{idx}"
        draw.rectangle((left, max(0, top - 28), left + 58, top), fill=color)
        draw.text((left + 4, max(0, top - 26)), label, fill="black", font=font)
    save_screenshot(annotated, output)


def annotation_items_to_candidates(items: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    candidates = []
    for idx, item in enumerate(items, start=1):
        rect = rect_from_config(item.get("box"))
        if rect is None:
            continue
        left, top, right, bottom = rect
        label = str(item.get("label") or item.get("id") or f"item-{idx}")
        candidates.append(
            {
                "text": label,
                "score": float(item.get("confidence", 1.0)),
                "box": [left, top, right, bottom],
                "center": [int((left + right) / 2), int((top + bottom) / 2)],
                "key": stable_hash(label),
                "source": "codex-annotation",
            }
        )
    return candidates


def command_apply_annotation(args: argparse.Namespace) -> int:
    config, config_path = load_config(args)
    annotation_path = Path(args.annotation).resolve()
    annotation = load_json(annotation_path)
    list_id = str(args.list_id or annotation.get("list_id") or "list_a")
    screen_path = Path(args.screen_image or annotation.get("screen_image") or annotation.get("source_image") or "")
    if not screen_path:
        raise ValueError("Annotation must provide screen_image/source_image, or pass --screen-image.")
    screen_path = screen_path.resolve()
    if not screen_path.exists():
        raise FileNotFoundError(str(screen_path))
    from PIL import Image

    img = Image.open(screen_path).convert("RGB")
    runtime = resolve_path(config.get("runtime_dir"), config_path.parent)
    runtime.mkdir(parents=True, exist_ok=True)

    app_region = rect_from_config(annotation.get("app_region"))
    list_region = rect_from_config(annotation.get("list_region"))
    if app_region is None:
        raise ValueError("Annotation must include app_region.")
    if list_region is None:
        raise ValueError("Annotation must include list_region.")
    items = list(annotation.get("items") or [])
    if not items:
        raise ValueError("Annotation must include at least one item in items[].")
    row_slots = []
    for item in items:
        rect = rect_from_config(item.get("box"))
        if rect:
            row_slots.append([rect[0], rect[1], rect[2], rect[3]])
    candidates = annotation_items_to_candidates(items)
    review_path = runtime / f"codex-annotation-{list_id}-review.png"
    annotate_candidates(
        img,
        candidates,
        review_path,
        extra_rects=[
            ("app", app_region, "cyan"),
            ("list", list_region, "gold"),
        ],
    )

    lists = config.setdefault("lists", [])
    target = None
    for item in lists:
        if item.get("id") == list_id:
            target = item
            break
    if target is None:
        target = {"id": list_id, "name": list_id}
        lists.append(target)
    target["app_region"] = [app_region[0], app_region[1], app_region[2], app_region[3]]
    target["list_region"] = [list_region[0], list_region[1], list_region[2], list_region[3]]
    target["detail_region"] = [app_region[0], app_region[1], app_region[2], app_region[3]]
    target["candidate_mode"] = "row_slots"
    target["row_slots"] = row_slots
    target.setdefault("entry_point", None)
    target["calibration"] = {
        "mode": "codex-annotation",
        "annotation": str(annotation_path),
        "review_image": str(review_path),
        "source_image": str(screen_path),
        "item_count": len(row_slots),
        "updated_at": datetime.now().isoformat(),
        "updated_by": "apply-annotation",
    }
    local_config = runtime / "config.local.json"
    save_json(local_config, config)
    save_json(
        runtime / f"codex-annotation-{list_id}-applied.json",
        {
            "list_id": list_id,
            "annotation": str(annotation_path),
            "review_image": str(review_path),
            "config": str(local_config),
            "row_slots": row_slots,
            "applied_at": datetime.now().isoformat(),
        },
    )
    print(f"Saved review image: {review_path}")
    print(f"Saved local config: {local_config}")
    print(f"Applied {len(row_slots)} Codex item boxes for {list_id}.")
    return 0


def command_calibrate_visual(args: argparse.Namespace) -> int:
    config, config_path = load_config(args)
    ocr = OCRProvider(config.get("ocr", {}).get("engine", "auto"))
    if not ocr.available():
        raise RuntimeError("No OCR provider available. Run doctor.ps1 and install requirements-ocr.txt.")

    runtime = resolve_path(config.get("runtime_dir"), config_path.parent)
    runtime.mkdir(parents=True, exist_ok=True)
    if args.screen_image:
        from PIL import Image

        img = Image.open(args.screen_image).convert("RGB")
    else:
        driver = create_driver(config, args)
        img = driver.screenshot().convert("RGB")
    screen = (int(img.size[0]), int(img.size[1]))
    raw_path = runtime / f"calibration-{args.list_id}-screen.png"
    save_screenshot(img, raw_path)

    if str(args.app_region).lower() == "auto":
        app_region = detect_blue_app_region(img)
        if not app_region:
            raise RuntimeError(
                "Could not detect the mini-program blue header. Put the mini program in the middle of the screen, "
                "or pass --app-region left,top,right,bottom."
            )
    elif str(args.app_region).lower() == "full":
        app_region = [0, 0, screen[0], screen[1]]
    else:
        app_region = list(parse_rect_arg(str(args.app_region)))

    app_rect = rect_from_config(app_region)
    assert app_rect is not None
    app_img = img.crop(crop_box(app_rect))
    boxes = ocr.read(app_img, offset=(app_rect[0], app_rect[1]))

    min_score = float(config.get("ocr", {}).get("min_score", 0.35))
    min_chars = int(config.get("ocr", {}).get("min_row_chars", 3))
    item_gap_px = int(config.get("ocr", {}).get("item_gap_px", 42))
    app_width = app_rect[2] - app_rect[0]
    list_top = min(app_rect[3] - 80, app_rect[1] + int(app_width * float(args.list_top_ratio)))
    list_region = [app_rect[0], max(app_rect[1], list_top), app_rect[2], app_rect[3]]
    list_rect = rect_from_config(list_region)
    assert list_rect is not None
    list_boxes = filter_boxes_in_rect(boxes, list_region)
    card_regions = detect_light_card_regions(img.crop(crop_box(list_rect)), offset=(list_rect[0], list_rect[1]))
    candidates = candidates_from_card_regions(
        list_boxes,
        card_regions,
        min_score=min_score,
        min_chars=min_chars,
    )
    if not candidates:
        candidates = detect_item_candidates(
            list_boxes,
            min_score=min_score,
            min_chars=min_chars,
            item_gap_px=item_gap_px,
            min_item_chars=max(min_chars, 4),
        )
    candidates = candidates[: int(args.max_candidates)]
    annotated_path = runtime / f"calibration-{args.list_id}-annotated.png"
    annotate_candidates(
        img,
        candidates,
        annotated_path,
        extra_rects=[
            ("app", app_region, "cyan"),
            ("list", list_region, "gold"),
        ],
    )
    save_json(
        runtime / f"calibration-{args.list_id}-candidates.json",
        {
            "list_id": args.list_id,
            "created_at": datetime.now().isoformat(),
            "app_region": app_region,
            "list_region": list_region,
            "card_regions": card_regions,
            "candidates": candidates,
        },
    )

    region = list_region
    if not candidates:
        inferred = union_box(candidates, pad=int(args.pad), screen_size=screen)
        if inferred:
            region = inferred

    lists = config.setdefault("lists", [])
    target = None
    for item in lists:
        if item.get("id") == args.list_id:
            target = item
            break
    if target is None:
        target = {"id": args.list_id, "name": args.list_id}
        lists.append(target)

    target["list_region"] = region
    target["detail_region"] = app_region
    target["app_region"] = app_region
    target.setdefault("entry_point", None)
    target["row_slots"] = []
    target["calibration"] = {
        "mode": "visual-ocr",
        "candidate_count": len(candidates),
        "card_count": len(card_regions),
        "annotated_image": str(annotated_path),
        "raw_screenshot": str(raw_path),
        "updated_at": datetime.now().isoformat(),
    }

    local_config = runtime / "config.local.json"
    save_json(local_config, config)
    print(f"Saved raw screenshot: {raw_path}")
    print(f"Saved annotated image: {annotated_path}")
    print(f"Saved local config: {local_config}")
    print(f"Inferred {len(candidates)} item candidates for {args.list_id}.")
    for idx, candidate in enumerate(candidates[:12], start=1):
        excerpt = normalize_text(str(candidate.get("text", "")))[:90]
        print(f"  #{idx} {candidate.get('box')} {excerpt}")
    return 0


def parse_slots_arg(values: Sequence[str]) -> List[List[int]]:
    slots = []
    for value in values:
        rect = parse_rect_arg(value)
        slots.append([int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3])])
    return slots


def command_configure_list(args: argparse.Namespace) -> int:
    config, config_path = load_config(args)
    runtime = resolve_path(config.get("runtime_dir"), config_path.parent)
    lists = config.setdefault("lists", [])
    target = None
    for item in lists:
        if item.get("id") == args.list_id:
            target = item
            break
    if target is None:
        target = {"id": args.list_id, "name": args.list_id}
        lists.append(target)

    if args.app_region:
        target["app_region"] = list(parse_rect_arg(args.app_region))
    if args.list_region:
        target["list_region"] = list(parse_rect_arg(args.list_region))
    if args.detail_region:
        target["detail_region"] = list(parse_rect_arg(args.detail_region))
    elif args.app_region:
        target["detail_region"] = list(parse_rect_arg(args.app_region))
    if args.entry_point:
        parts = [part.strip() for part in str(args.entry_point).split(",")]
        if len(parts) != 2:
            raise ValueError("--entry-point must be x,y")
        target["entry_point"] = [int(parts[0]), int(parts[1])]
    if args.candidate_mode:
        target["candidate_mode"] = args.candidate_mode
    if args.row_slot:
        target["row_slots"] = parse_slots_arg(args.row_slot)
        if not args.candidate_mode:
            target["candidate_mode"] = "row_slots"
    target.setdefault("row_slots", [])
    target["calibration"] = {
        **target.get("calibration", {}),
        "mode": target.get("candidate_mode", "manual-config"),
        "updated_at": datetime.now().isoformat(),
        "updated_by": "configure-list",
    }

    local_config = runtime / "config.local.json"
    save_json(local_config, config)
    print(f"Saved local config: {local_config}")
    print(json.dumps(target, ensure_ascii=False, indent=2))
    return 0


def read_seen(path: Path) -> set:
    if not path.exists():
        return set()
    data = load_json(path)
    return set(data.get("seen", []))


def save_seen(path: Path, seen: set) -> None:
    save_json(path, {"seen": sorted(seen)})


def ocr_region_capture(driver: DesktopDriver, ocr: OCRProvider, region: Optional[Rect], shot_path: Path):
    img = driver.screenshot()
    offset = (0, 0)
    crop = img
    if region:
        crop = img.crop(crop_box(region))
        offset = (region[0], region[1])
    save_screenshot(crop, shot_path)
    boxes = ocr.read(crop, offset=offset)
    text = normalize_text("\n".join(b.text for b in boxes))
    return text, boxes, crop


def ocr_region(driver: DesktopDriver, ocr: OCRProvider, region: Optional[Rect], shot_path: Path) -> Tuple[str, List[OCRBox]]:
    text, boxes, _crop = ocr_region_capture(driver, ocr, region, shot_path)
    return text, boxes


def perform_back(driver: DesktopDriver, method: str) -> None:
    if method.startswith("hotkey:"):
        keys = [k.strip() for k in method.split(":", 1)[1].split(",") if k.strip()]
        driver.hotkey(keys)
    elif method.startswith("click:"):
        parts = method.split(":", 1)[1].split(",")
        driver.click((int(parts[0]), int(parts[1])))
    else:
        driver.hotkey(["alt", "left"])


def collect_detail(
    driver: DesktopDriver,
    ocr: OCRProvider,
    config: Dict[str, Any],
    list_id: str,
    item_key: str,
    detail_region: Optional[Rect],
    item_runtime: Path,
) -> Dict[str, Any]:
    automation = config.get("automation", {})
    max_rounds = int(automation.get("detail_max_scroll_rounds", 18))
    no_new_limit = int(automation.get("no_new_detail_rounds", 2))
    scroll_clicks = int(automation.get("detail_scroll_clicks", -5))
    settle = int(automation.get("settle_ms", 900)) / 1000.0
    no_new = 0
    texts: List[str] = []
    text_hashes: set = set()
    for round_idx in range(max_rounds):
        time.sleep(settle)
        text, _boxes = ocr_region(driver, ocr, detail_region, item_runtime / f"detail-{round_idx:03d}.png")
        h = stable_hash(text)
        if text and h not in text_hashes:
            text_hashes.add(h)
            texts.append(text)
            no_new = 0
        else:
            no_new += 1
        if no_new >= no_new_limit:
            break
        driver.scroll(scroll_clicks)
    raw_text = normalize_text("\n".join(texts))
    return {
        "list_id": list_id,
        "item_key": item_key,
        "captured_at": datetime.now().isoformat(),
        "ocr_engine": ocr.name,
        "raw_text": raw_text,
        "raw_text_hash": stable_hash(raw_text),
        "confidence": "low" if not ocr.available() else "candidate",
        "evidence_dir": str(item_runtime),
    }


def command_run(args: argparse.Namespace) -> int:
    config, config_path = load_config(args)
    run_id = args.run_id or now_stamp()
    runtime = runtime_for(config, config_path, run_id)
    runtime.mkdir(parents=True, exist_ok=True)
    save_json(runtime / "run-meta.json", {"run_id": run_id, "started_at": datetime.now().isoformat(), "config": str(config_path)})
    driver = create_driver(config, args)
    ocr = OCRProvider(config.get("ocr", {}).get("engine", "auto"))
    automation = config.get("automation", {})
    settle = int(automation.get("settle_ms", 900)) / 1000.0
    no_new_item_rounds = int(automation.get("no_new_item_rounds", 3))
    list_scroll = int(automation.get("list_scroll_clicks", -5))
    back_method = str(automation.get("back_method", "hotkey:alt,left"))
    max_items = automation.get("max_items_per_list")
    if args.max_items is not None:
        max_items = args.max_items
    min_score = float(config.get("ocr", {}).get("min_score", 0.35))
    min_chars = int(config.get("ocr", {}).get("min_row_chars", 3))
    seen_path = runtime / "checkpoint-seen.json"
    seen = read_seen(seen_path)
    total = 0
    for list_cfg in config.get("lists", []):
        list_id = list_cfg.get("id", "list")
        if args.list_id and list_id != args.list_id:
            continue
        if not list_cfg.get("list_region") and not list_cfg.get("entry_point"):
            print(f"Skipping uncalibrated list: {list_id}")
            continue
        entry = point_from_config(list_cfg.get("entry_point"))
        if entry:
            driver.click(entry)
            time.sleep(settle)
        list_region = rect_from_config(list_cfg.get("list_region"))
        detail_region = rect_from_config(list_cfg.get("detail_region")) or list_region
        no_new_rounds = 0
        processed_this_list = 0
        for list_round in range(int(args.max_rounds)):
            text, boxes, list_image = ocr_region_capture(driver, ocr, list_region, runtime / "screens" / f"{list_id}-list-{list_round:03d}.png")
            region_offset = (list_region[0], list_region[1]) if list_region else (0, 0)
            card_regions = detect_light_card_regions(list_image, offset=region_offset)
            candidate_mode = str(list_cfg.get("candidate_mode", "auto"))
            if candidate_mode == "row_slots" and list_cfg.get("row_slots"):
                candidates = candidates_from_row_slots(
                    boxes,
                    list_cfg.get("row_slots", []),
                    min_score=min_score,
                    min_chars=max(min_chars, 4),
                )
            else:
                candidates = candidates_from_card_regions(
                    boxes,
                    card_regions,
                    min_score=min_score,
                    min_chars=min_chars,
                )
                if not candidates:
                    candidates = detect_item_candidates(
                        boxes,
                        min_score=min_score,
                        min_chars=min_chars,
                        item_gap_px=int(config.get("ocr", {}).get("item_gap_px", 42)),
                        min_item_chars=max(min_chars, 4),
                    )
                if not candidates and list_cfg.get("row_slots"):
                    candidates = candidates_from_row_slots(
                        boxes,
                        list_cfg.get("row_slots", []),
                        min_score=min_score,
                        min_chars=max(min_chars, 4),
                    )
            new_candidates = [c for c in candidates if f"{list_id}:{c['key']}" not in seen]
            append_jsonl(
                runtime / "captures.jsonl",
                {
                    "list_id": list_id,
                    "round": list_round,
                    "card_count": len(card_regions),
                    "candidate_count": len(candidates),
                    "new_count": len(new_candidates),
                    "text_hash": stable_hash(text),
                },
            )
            if not new_candidates:
                no_new_rounds += 1
            else:
                no_new_rounds = 0
            for candidate in new_candidates:
                compound_key = f"{list_id}:{candidate['key']}"
                driver.click((int(candidate["center"][0]), int(candidate["center"][1])))
                item_runtime = runtime / "items" / list_id / candidate["key"]
                detail = collect_detail(driver, ocr, config, list_id, candidate["key"], detail_region, item_runtime)
                detail["list_candidate"] = candidate
                append_jsonl(runtime / "details.jsonl", detail)
                seen.add(compound_key)
                save_seen(seen_path, seen)
                processed_this_list += 1
                total += 1
                perform_back(driver, back_method)
                time.sleep(settle)
                if max_items is not None and processed_this_list >= int(max_items):
                    break
            if max_items is not None and processed_this_list >= int(max_items):
                break
            if no_new_rounds >= no_new_item_rounds:
                break
            driver.scroll(list_scroll)
            time.sleep(settle)
    print(f"Run saved: {runtime}")
    print(f"New details captured: {total}")
    return 0


def title_guess(text: str) -> str:
    for part in text.split():
        if len(part) >= 4:
            return part[:80]
    return normalize_text(text)[:80]


def command_export_review(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    details = list(read_jsonl(run_dir / "details.jsonl"))
    output = Path(args.output).resolve() if args.output else run_dir / "review.csv"
    excerpt_chars = int(args.excerpt_chars)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "selected",
                "run_id",
                "list_id",
                "item_key",
                "title_guess",
                "confidence",
                "missing_fields",
                "human_note",
                "evidence_dir",
                "raw_text_excerpt",
            ],
        )
        writer.writeheader()
        for row in details:
            raw = normalize_text(row.get("raw_text", ""))
            writer.writerow(
                {
                    "selected": "",
                    "run_id": run_dir.name,
                    "list_id": row.get("list_id", ""),
                    "item_key": row.get("item_key", ""),
                    "title_guess": title_guess(raw),
                    "confidence": row.get("confidence", "candidate"),
                    "missing_fields": "",
                    "human_note": "",
                    "evidence_dir": row.get("evidence_dir", ""),
                    "raw_text_excerpt": raw[:excerpt_chars],
                }
            )
    print(output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wechat-mini-list-capture")
    parser.add_argument("--config", help="Config JSON path. Defaults to config.example.json.")
    parser.add_argument("--driver", choices=["desktop", "android_adb"], help="Override config driver.")
    parser.add_argument("--adb-path", default="adb", help="adb executable path for android_adb driver.")
    parser.add_argument("--adb-serial", help="ADB device serial. Required when multiple devices are connected.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("doctor")
    p.add_argument("--screenshot", action="store_true", help="Also test screenshot capture.")
    p.set_defaults(func=command_doctor)

    p = sub.add_parser("init-run")
    p.add_argument("--run-id")
    p.set_defaults(func=command_init_run)

    p = sub.add_parser("calibrate-desktop")
    p.set_defaults(func=command_calibrate)

    p = sub.add_parser("calibrate-visible-list")
    p.add_argument("--list-id", default="list_a")
    p.add_argument("--max-candidates", type=int, default=12)
    p.add_argument("--pad", type=int, default=28)
    p.add_argument("--app-region", default="auto", help="auto, full, or left,top,right,bottom.")
    p.add_argument("--list-top-ratio", type=float, default=0.84, help="List area starts at app_top + app_width * ratio.")
    p.add_argument("--screen-image", help="Use an existing screenshot instead of taking a new one.")
    p.set_defaults(func=command_calibrate_visual)

    p = sub.add_parser("configure-list")
    p.add_argument("--list-id", required=True)
    p.add_argument("--app-region")
    p.add_argument("--list-region")
    p.add_argument("--detail-region")
    p.add_argument("--entry-point")
    p.add_argument("--candidate-mode", choices=["auto", "row_slots"])
    p.add_argument("--row-slot", action="append", default=[])
    p.set_defaults(func=command_configure_list)

    p = sub.add_parser("apply-annotation")
    p.add_argument("--annotation", required=True)
    p.add_argument("--list-id")
    p.add_argument("--screen-image")
    p.set_defaults(func=command_apply_annotation)

    p = sub.add_parser("run-desktop")
    p.add_argument("--run-id")
    p.add_argument("--list-id")
    p.add_argument("--max-items", type=int)
    p.add_argument("--max-rounds", type=int, default=200)
    p.set_defaults(func=command_run)

    p = sub.add_parser("export-review")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--output")
    p.add_argument("--excerpt-chars", type=int, default=600)
    p.set_defaults(func=command_export_review)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        print("[ERROR] interrupted by user", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
