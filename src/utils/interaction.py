from dataclasses import dataclass

import cv2
from screeninfo import get_monitors

from src.logger import logger
from src.utils.image import ImageUtils

monitor_window = get_monitors()[0]


@dataclass
class ImageMetrics:
    # TODO: Move TEXT_SIZE, etc here and find a better class name
    window_width, window_height = monitor_window.width, monitor_window.height
    # for positioning image windows
    window_x, window_y = 0, 0
    reset_pos = [0, 0]


class InteractionUtils:
    """Perform primary functions such as displaying images and reading responses"""

    image_metrics = ImageMetrics()

    @staticmethod
    def show(name, origin, pause=1, resize=False, reset_pos=None, config=None):
        image_metrics = InteractionUtils.image_metrics
        if origin is None:
            logger.info(f"'{name}' - NoneType image to show!")
            if pause:
                cv2.destroyAllWindows()
            return
        
        # Get original image dimensions
        original_h, original_w = origin.shape[:2]
        
        # Determine target display dimensions
        if resize and config:
            # Use config dimensions if provided
            target_width = config.dimensions.display_width
            target_height = config.dimensions.display_height
        else:
            # Use screen dimensions as fallback
            target_width = image_metrics.window_width
            target_height = image_metrics.window_height
        
        # Calculate scaling to fit image within screen bounds
        # Leave some margin for window decorations and taskbar
        max_width = int(image_metrics.window_width * 0.9)
        max_height = int(image_metrics.window_height * 0.8)
        
        # Calculate scale to fit image within screen bounds
        scale_x = max_width / original_w
        scale_y = max_height / original_h
        scale = min(scale_x, scale_y, 1.0)  # Don't scale up, only down
        
        # Resize image if needed
        if scale < 1.0:
            new_width = int(original_w * scale)
            new_height = int(original_h * scale)
            img = ImageUtils.resize_util(origin, new_width)
        else:
            img = origin
        
        # Get final image dimensions
        h, w = img.shape[:2]
        
        if not is_window_available(name):
            cv2.namedWindow(name, cv2.WINDOW_NORMAL)
        
        cv2.imshow(name, img)
        
        # Calculate window position to center it on screen
        if reset_pos:
            image_metrics.window_x = reset_pos[0]
            image_metrics.window_y = reset_pos[1]
        else:
            # Center the window on screen
            image_metrics.window_x = (image_metrics.window_width - w) // 2
            image_metrics.window_y = (image_metrics.window_height - h) // 2
        
        # Ensure window stays within screen bounds
        image_metrics.window_x = max(0, min(image_metrics.window_x, image_metrics.window_width - w))
        image_metrics.window_y = max(0, min(image_metrics.window_y, image_metrics.window_height - h))
        
        cv2.moveWindow(
            name,
            image_metrics.window_x,
            image_metrics.window_y,
        )
        
        # Set next window position for multiple windows
        margin = 25
        next_w = w + margin
        next_h = h + margin
        
        # Calculate next position (simplified grid layout)
        if image_metrics.window_x + next_w > image_metrics.window_width:
            image_metrics.window_x = 0
            if image_metrics.window_y + next_h > image_metrics.window_height:
                image_metrics.window_y = 0
            else:
                image_metrics.window_y += next_h
        else:
            image_metrics.window_x += next_w
        
        if pause:
            logger.info(
                f"Showing '{name}' (Size: {w}x{h})\n\t Press Q on image to continue. Press Ctrl + C in terminal to exit"
            )
            
            wait_q()
            InteractionUtils.image_metrics.window_x = 0
            InteractionUtils.image_metrics.window_y = 0


@dataclass
class Stats:
    # TODO Fill these for stats
    # Move qbox_vals here?
    # badThresholds = []
    # veryBadPoints = []
    files_moved = 0
    files_not_moved = 0


def wait_q():
    esc_key = 27
    while cv2.waitKey(1) & 0xFF not in [ord("q"), esc_key]:
        pass
    cv2.destroyAllWindows()


def is_window_available(name: str) -> bool:
    """Checks if a window is available"""
    try:
        cv2.getWindowProperty(name, cv2.WND_PROP_VISIBLE)
        return True
    except Exception as e:
        print(e)
        return False
