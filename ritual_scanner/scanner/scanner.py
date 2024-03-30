import math
import time

import cv2
import numpy as np
import pyperclip
import pytesseract
from loguru import logger
from PIL import Image, ImageGrab, ImageOps
from pydantic import BaseModel
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Key
from pynput.mouse import Button, Controller

from ritual_scanner.constants import TEMPLATES_DIR
from ritual_scanner.scanner import items, utils

STEP = 53
START = (1920 + 335, 295)
START_CLICK = (START[0], START[1] - 50)
WAIT_AFTER_KEY = 0.150  # Sleep this much after moving or pressing keys
WAIT_AFTER_COPY = 0.250  # Sleep this much after copying the item data
WAIT_AFTER_SCREENSHOT = 0.150
THRESHOLD_CONTROL = 0.26


class Item(BaseModel):
    """"""

    pos: tuple[int, int]
    data: str
    price: int


class Scanner:
    def __init__(self) -> None:
        self.mouse = Controller()
        self.keyboard = KeyboardController()
        self.items: list[Item] = []
        self.control_pos = self.mouse.position

    def is_slot_empty(self, slot: np.ndarray) -> bool:
        averages = slot.mean(axis=0).mean(axis=0)[:3]

        return all(averages < 12)

    def get_item_matrix(self, screenshot):
        ritual_part = screenshot.crop((306, 264, 940, 794))
        ritual_np = cv2.cvtColor(np.array(ritual_part), cv2.COLOR_BGR2RGB)

        mask = np.full((10, 12), False)

        for col in range(12):
            for row in range(10):
                slot = ritual_np[row * STEP : (row + 1) * STEP, col * STEP : (col + 1) * STEP]
                mask[row, col] = not self.is_slot_empty(slot)

        return mask

    def get_item_at_pos(self, row, col):
        self.mouse.position = (START[0] + col * STEP, START[1] + row * STEP)
        time.sleep(WAIT_AFTER_KEY)
        self.control_pos = self.mouse.position

        self.keyboard.press(Key.ctrl)
        time.sleep(WAIT_AFTER_KEY)
        self.keyboard.press("c")
        time.sleep(WAIT_AFTER_KEY)
        self.keyboard.release("c")
        time.sleep(WAIT_AFTER_KEY)
        self.keyboard.release(Key.ctrl)
        time.sleep(WAIT_AFTER_KEY)

        item_data = pyperclip.paste()

        time.sleep(WAIT_AFTER_COPY)

        return item_data

    def init_movement(self) -> None:
        logger.debug("Moving to testing position")
        self.mouse.position = START_CLICK

        logger.debug("Clicking to get window focus (hopefully)")
        self.mouse.click(Button.left)

    def scan(self):
        self.init_movement()

        for i in range(5, -1, -1):
            time.sleep(1)
            logger.info("Countdown: {}", i)

        tribute = Image.open(TEMPLATES_DIR / "tribute.png")
        screenshot = ImageGrab.grab((1920, 0, 1920 + 1920, 1080))

        item_mask = self.get_item_matrix(screenshot)
        logger.info("Found {} slots with items", item_mask.sum())

        processed_slots = 0

        for col in range(12):
            for row in range(10):
                if not item_mask[row, col]:
                    logger.debug("Skipping slot [{}, {}] (empty)", row, col)
                    continue

                item_data = self.get_item_at_pos(row, col)
                time.sleep(WAIT_AFTER_SCREENSHOT)
                screen = ImageGrab.grab()
                time.sleep(WAIT_AFTER_SCREENSHOT)
                processed_slots += 1

                if math.dist(self.mouse.position, self.control_pos) > 3:
                    logger.debug("Mouse: {}", self.mouse.position)
                    logger.debug("Control: {}", self.control_pos)
                    logger.debug("Distance: {}", math.dist(self.mouse.position, self.control_pos))
                    logger.warning("Interrupting, because mouse moved during scanning")
                    return

                result = cv2.matchTemplate(
                    utils.image_to_cv(screen),
                    utils.image_to_cv(tribute),
                    cv2.TM_SQDIFF_NORMED,
                )
                min_val, _, min_loc, _ = cv2.minMaxLoc(result)

                if min_val > THRESHOLD_CONTROL:
                    logger.error("Cannot find tribute price on screen, min_val={}", min_val)
                    continue

                price_img = screen.crop(
                    (
                        min_loc[0] - 64,
                        min_loc[1],
                        min_loc[0],
                        min_loc[1] + 25,
                    ),
                )
                price_img = ImageOps.expand(price_img, border=1, fill="white")

                text = pytesseract.image_to_string(price_img)

                try:
                    price = int("".join([x for x in text if x.isnumeric()]))
                except:
                    logger.error("Cannot get price from text: '{}'", text)
                    continue

                logger.success("Found price: {}", price)
                logger.info("Item: {}", item_data)

                self.items.append(
                    Item(
                        pos=(row, col),
                        data=item_data,
                        price=price,
                    ),
                )

                item_class = items.get_item_class(item_data)
                dimensions = items.get_item_dimensions(item_class)

                if dimensions != (1, 1):
                    skip_cols, skip_rows = dimensions

                    for s_col in range(skip_cols):
                        for s_row in range(skip_rows):
                            item_mask[row + s_row, col + s_col] = False

                logger.info(
                    "Processed slots: {}/{}",
                    processed_slots,
                    item_mask.sum(),
                )
