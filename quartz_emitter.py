from Quartz import (
    CGEventCreateScrollWheelEvent,
    CGEventPost,
    kCGScrollEventUnitPixel,
    kCGHIDEventTap,
)
import config


def post_scroll(pixels: int) -> None:
    if pixels == 0:
        return
    if config.INVERT_SCROLL:
        pixels = -pixels
    event = CGEventCreateScrollWheelEvent(
        None,
        kCGScrollEventUnitPixel,
        1,
        int(pixels),
    )
    CGEventPost(kCGHIDEventTap, event)
