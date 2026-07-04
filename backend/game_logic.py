import os
import random
from loguru import logger
from config import get

SUM_MIN_ITEMS = get("SUM_MIN_ITEMS")
SUM_MAX_ITEMS = get("SUM_MAX_ITEMS")
SUM_MIN_VALUE = get("SUM_MIN_VALUE")
SUM_MAX_VALUE = get("SUM_MAX_VALUE")
SUM_TOTAL_MAX = get("SUM_TOTAL_MAX")
SUM_BIG_THRESHOLD = get("SUM_BIG_THRESHOLD")
SUM_SMALL_MIN = get("SUM_SMALL_MIN")
SUM_SMALL_MAX = get("SUM_SMALL_MAX")
TOTAL_IMAGES = get("TOTAL_IMAGES")

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "images")


def _image_filename(num: int) -> str:
    for ext in (".jpg", ".jpeg"):
        path = os.path.join(IMAGES_DIR, f"{num}{ext}")
        if os.path.isfile(path):
            logger.debug(f"Found image file: {path}")
            return f"{num}{ext}"
    logger.warning(f"Image file not found for value {num} in {IMAGES_DIR}, falling back to {num}.jpg")
    return f"{num}.jpg"


def _image_url(num: int) -> str:
    return f"/static/images/{_image_filename(num)}"


def _image_exists(num: int) -> bool:
    for ext in (".jpg", ".jpeg"):
        if os.path.isfile(os.path.join(IMAGES_DIR, f"{num}{ext}")):
            return True
    return False


def generate_gallery_page(page: int = 1, per_page: int = 50) -> dict:
    continuous_max = get("GALLERY_CONTINUOUS_MAX")
    extras = get("GALLERY_EXTRAS")

    numbers = set(range(1, continuous_max + 1))
    for num in extras:
        if _image_exists(num):
            numbers.add(num)

    sorted_numbers = sorted(numbers)
    total = len(sorted_numbers)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total)
    page_numbers = sorted_numbers[start_idx:end_idx]

    images = []
    for v in page_numbers:
        images.append({
            "value": v,
            "filename": _image_filename(v),
            "url": _image_url(v),
        })

    return {
        "images": images,
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }


def pick_random_images(count: int, max_value: int = TOTAL_IMAGES) -> list[dict]:
    nums = [random.randint(1, max_value) for _ in range(count)]
    images = [
        {"filename": _image_filename(n), "value": n, "url": _image_url(n)}
        for n in nums
    ]
    logger.debug(f"Picked {len(images)} images with values: {[img['value'] for img in images]}")
    return images


def _generate_sum_distractors(correct: int, min_val: int, max_val: int, count: int = 2) -> list[int]:
    distractors: set[int] = set()
    offsets = [1, -1, 2, -2, 3, -3, 5, -5, 4, -4]
    logger.debug(f"Generating sum distractors: correct={correct}, range=[{min_val},{max_val}], count={count}")
    for offset in offsets:
        c = correct + offset
        if min_val <= c <= max_val and c != correct:
            distractors.add(c)
            logger.debug(f"  distractor candidate +{offset}: {c} (accepted)")
        else:
            logger.debug(f"  distractor candidate +{offset}: {c} (out of range [{min_val},{max_val}] or equals correct)")
        if len(distractors) >= count:
            break
    before_fill = len(distractors)
    while len(distractors) < count:
        c = random.randint(min_val, max_val)
        if c != correct and c not in distractors:
            distractors.add(c)
            logger.debug(f"  random fill distractor: {c}")
    if before_fill < count:
        logger.debug(f"  filled {count - before_fill} distractors with random values")
    result = list(distractors)[:count]
    logger.debug(f"Sum distractors for correct={correct}: {result}")
    return result


def generate_sum_quiz(streak: int = 0) -> dict:
    for attempt in range(50):
        num_items = random.randint(SUM_MIN_ITEMS, SUM_MAX_ITEMS)
        images = pick_random_images(num_items, SUM_MAX_VALUE)
        total = sum(img["value"] for img in images)
        logger.debug(f"Sum quiz attempt {attempt + 1}: num_items={num_items}, values={[img['value'] for img in images]}, total={total}, max={SUM_TOTAL_MAX}")
        if total <= SUM_TOTAL_MAX:
            logger.debug(f"Found valid total in attempt {attempt + 1}")
            break
    else:
        logger.error(f"Failed to find valid total after 50 attempts, using last values: {[img['value'] for img in images]}, total={total}")

    if num_items == 2:
        v0, v1 = images[0]["value"], images[1]["value"]
        if streak > 20:
            small_max = min(10 + 2 * ((streak - 10) // 10) + 1, SUM_MAX_VALUE)
        else:
            small_max = SUM_SMALL_MAX
        logger.debug(f"Checking big/small logic: v0={v0}, v1={v1}, threshold={SUM_BIG_THRESHOLD}, small_range=[{SUM_SMALL_MIN},{small_max}] (streak={streak})")
        if v0 > SUM_BIG_THRESHOLD and not (SUM_SMALL_MIN <= v1 <= small_max):
            logger.info(f"v0={v0} is big and v1={v1} is not small, replacing v1")
            images[1] = pick_random_images(1, small_max)[0]
            total = images[0]["value"] + images[1]["value"]
            logger.debug(f"After replacement: values=[{images[0]['value']}, {images[1]['value']}], total={total}")
        elif v1 > SUM_BIG_THRESHOLD and not (SUM_SMALL_MIN <= v0 <= small_max):
            logger.info(f"v1={v1} is big and v0={v0} is not small, replacing v0")
            images[0] = pick_random_images(1, small_max)[0]
            total = images[0]["value"] + images[1]["value"]
            logger.debug(f"After replacement: values=[{images[0]['value']}, {images[1]['value']}], total={total}")
        else:
            logger.debug(f"No replacement needed: big/small pairing already valid")

    sum_min = SUM_MIN_ITEMS * SUM_MIN_VALUE
    sum_max = SUM_TOTAL_MAX
    distractor_min = max(sum_min, total - 5)
    distractor_max = min(sum_max, total + 5)
    logger.debug(f"Distractor range: sum_min={sum_min}, sum_max={sum_max}, distractor_min={distractor_min}, distractor_max={distractor_max}")
    distractors = _generate_sum_distractors(total, distractor_min, distractor_max)

    options = [total] + distractors
    random.shuffle(options)
    logger.debug(f"Options before shuffle: {[total] + distractors}, after shuffle: {options}")

    correct_url = _image_url(total)
    logger.debug(f"Correct image URL for total={total}: {correct_url}")

    quiz = {
        "game_type": "sum",
        "images": images,
        "total_sum": total,
        "options": options,
        "correct_answer": total,
        "correct_image_url": correct_url,
    }
    logger.info(f"Sum quiz generated: total={total}, num_items={num_items}, options={options}, values={[img['value'] for img in images]}")
    return quiz


def generate_repeated_sum_quiz() -> dict:
    base = random.randint(1, 10)
    repeats = random.randint(2, 8)
    total = base * repeats
    logger.debug(f"Generating repeated sum quiz: base={base}, repeats={repeats}, total={total}")

    images = [
        {"filename": _image_filename(base), "value": base, "url": _image_url(base)}
        for _ in range(repeats)
    ]

    sum_min = repeats * 1
    sum_max = min(10 * 8, SUM_TOTAL_MAX)
    distractor_min = max(sum_min, total - 10)
    distractor_max = min(sum_max, total + 10)
    logger.debug(f"Repeated sum distractor range: min={distractor_min}, max={distractor_max}")
    distractors = _generate_sum_distractors(total, distractor_min, distractor_max)

    options = [total] + distractors
    random.shuffle(options)

    quiz = {
        "game_type": "sum",
        "images": images,
        "total_sum": total,
        "options": options,
        "correct_answer": total,
        "correct_image_url": _image_url(total),
        "boss_active": True,
        "base_value": base,
        "repeats": repeats,
    }
    logger.info(f"Repeated sum quiz generated: {base} x {repeats} = {total}, options={options}")
    return quiz
