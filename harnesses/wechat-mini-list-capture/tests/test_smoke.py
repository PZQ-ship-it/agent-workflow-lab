import json
from pathlib import Path

from PIL import Image, ImageDraw

from wechat_mini_capture.cli import (
    OCRBox,
    annotation_items_to_candidates,
    build_parser,
    candidates_from_card_regions,
    candidates_from_row_slots,
    detect_blue_app_region,
    detect_item_candidates,
    detect_light_card_regions,
    group_rows,
    stable_hash,
)


def test_parser_builds():
    parser = build_parser()
    args = parser.parse_args(["doctor"])
    assert args.command == "doctor"


def test_hash_is_stable():
    assert stable_hash("abc") == stable_hash("abc")
    assert stable_hash("abc") != stable_hash("abcd")


def test_group_rows_merges_same_line():
    boxes = [
        OCRBox(text="Tencent", score=0.9, box=(10, 10, 80, 30)),
        OCRBox(text="AI", score=0.9, box=(90, 12, 120, 32)),
        OCRBox(text="Next", score=0.9, box=(10, 80, 80, 100)),
    ]
    rows = group_rows(boxes, min_score=0.3, min_chars=1)
    assert len(rows) == 2
    assert rows[0]["text"] == "Tencent AI"


def test_detect_item_candidates_clusters_close_rows():
    boxes = [
        OCRBox(text="Company", score=0.9, box=(10, 100, 90, 120)),
        OCRBox(text="Role", score=0.9, box=(10, 130, 70, 150)),
        OCRBox(text="Next", score=0.9, box=(10, 230, 80, 250)),
    ]
    items = detect_item_candidates(boxes, min_score=0.3, min_chars=1, item_gap_px=45)
    assert len(items) == 2
    assert items[0]["text"] == "Company Role"


def test_detect_blue_app_region_from_synthetic_header():
    image = Image.new("RGB", (900, 900), (30, 30, 30))
    draw = ImageDraw.Draw(image)
    draw.rectangle((300, 80, 620, 300), fill=(55, 58, 210))
    region = detect_blue_app_region(image)
    assert region is not None
    assert region[0] <= 305
    assert region[1] <= 85
    assert region[2] >= 615


def test_card_candidates_from_synthetic_list():
    image = Image.new("RGB", (360, 520), (240, 245, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 30, 340, 150), fill=(255, 255, 255))
    draw.rectangle((20, 180, 340, 300), fill=(255, 255, 255))
    cards = detect_light_card_regions(image)
    boxes = [
        OCRBox(text="First", score=0.9, box=(40, 55, 120, 75)),
        OCRBox(text="Second", score=0.9, box=(40, 205, 140, 225)),
    ]
    items = candidates_from_card_regions(boxes, cards, min_score=0.3, min_chars=1)
    assert len(items) == 2
    assert items[0]["text"] == "First"


def test_row_slot_candidates_use_ocr_text_for_key():
    boxes = [
        OCRBox(text="Title", score=0.9, box=(20, 20, 80, 40)),
        OCRBox(text="Outside", score=0.9, box=(20, 120, 100, 140)),
    ]
    items = candidates_from_row_slots(boxes, [(10, 10, 120, 80)], min_score=0.3, min_chars=1)
    assert len(items) == 1
    assert items[0]["text"] == "Title"
    assert items[0]["source"] == "row-slot"


def test_annotation_items_to_candidates():
    items = annotation_items_to_candidates([{"label": "card-1", "box": [1, 2, 11, 22], "confidence": 0.8}])
    assert len(items) == 1
    assert items[0]["center"] == [6, 12]
    assert items[0]["source"] == "codex-annotation"
