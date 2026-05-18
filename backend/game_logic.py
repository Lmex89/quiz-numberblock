import os
import random
from loguru import logger
from config import get

COUNT_MIN = get("COUNT_MIN")
COUNT_MAX = get("COUNT_MAX")
SUM_MIN_ITEMS = get("SUM_MIN_ITEMS")
SUM_MAX_ITEMS = get("SUM_MAX_ITEMS")
SUM_MIN_VALUE = get("SUM_MIN_VALUE")
SUM_MAX_VALUE = get("SUM_MAX_VALUE")
SUM_TOTAL_MAX = get("SUM_TOTAL_MAX")
TOTAL_IMAGES = get("TOTAL_IMAGES")

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "images")


def _image_filename(num: int) -> str:
    for ext in (".jpg", ".jpeg"):
        if os.path.isfile(os.path.join(IMAGES_DIR, f"{num}{ext}")):
            return f"{num}{ext}"
    return f"{num}.jpg"


def _image_url(num: int) -> str:
    return f"/static/images/{_image_filename(num)}"


def pick_random_images(count: int, max_value: int = TOTAL_IMAGES) -> list[dict]:
    nums = [random.randint(1, max_value) for _ in range(count)]
    images = [
        {"filename": _image_filename(n), "value": n, "url": _image_url(n)}
        for n in nums
    ]
    logger.debug(f"Picked {len(images)} images with values: {[img['value'] for img in images]}")
    return images


def _generate_count_distractors(correct: int) -> list[int]:
    possible = [i for i in range(COUNT_MIN, COUNT_MAX + 1) if i != correct]
    if len(possible) <= 2:
        logger.debug(f"Count distractors (exhaustive): {possible}")
        return possible
    result = random.sample(possible, 2)
    logger.debug(f"Count distractors: {result}")
    return result


def _generate_sum_distractors(correct: int, min_val: int, max_val: int, count: int = 2) -> list[int]:
    distractors: set[int] = set()
    offsets = [1, -1, 2, -2, 3, -3, 5, -5, 4, -4]
    for offset in offsets:
        c = correct + offset
        if min_val <= c <= max_val and c != correct:
            distractors.add(c)
        if len(distractors) >= count:
            break
    while len(distractors) < count:
        c = random.randint(min_val, max_val)
        if c != correct and c not in distractors:
            distractors.add(c)
    result = list(distractors)[:count]
    logger.debug(f"Sum distractors for correct={correct}: {result}")
    return result


def generate_count_quiz() -> dict:
    quantity = random.randint(COUNT_MIN, COUNT_MAX)
    images = pick_random_images(quantity)

    correct_value = quantity
    distractors = _generate_count_distractors(correct_value)

    options = [correct_value] + distractors
    random.shuffle(options)

    quiz = {
        "game_type": "count",
        "quantity": quantity,
        "images": images,
        "options": options,
        "correct_answer": correct_value,
    }
    logger.info(f"Count quiz generated: quantity={quantity}, options={options}")
    return quiz



def generate_sum_quiz() -> dict:
    for _ in range(50):
        num_items = random.randint(SUM_MIN_ITEMS, SUM_MAX_ITEMS)
        images = pick_random_images(num_items, SUM_MAX_VALUE)
        total = sum(img["value"] for img in images)
        if total <= SUM_TOTAL_MAX:
            break

    sum_min = SUM_MIN_ITEMS * SUM_MIN_VALUE
    sum_max = SUM_TOTAL_MAX
    distractor_min = max(sum_min, total - 5)
    distractor_max = min(sum_max, total + 5)
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
    }
    logger.info(f"Sum quiz generated: total={total}, num_items={num_items}, options={options}")
    return quiz
