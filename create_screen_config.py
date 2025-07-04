#!/usr/bin/env python3
"""
Utility script to create a config.json file optimized for your screen size.
This will help the template layout windows fit properly on your display.
"""

import json
import sys
from pathlib import Path

try:
    from screeninfo import get_monitors
except ImportError:
    print("Error: screeninfo package not found. Please install it with:")
    print("pip install screeninfo")
    sys.exit(1)


def get_screen_info():
    """Get information about the primary monitor"""
    try:
        monitors = get_monitors()
        if not monitors:
            print("Error: No monitors detected")
            return None
        
        primary_monitor = monitors[0]
        print(f"Detected primary monitor: {primary_monitor.width}x{primary_monitor.height}")
        return primary_monitor
    except Exception as e:
        print(f"Error detecting screen: {e}")
        return None


def calculate_optimal_dimensions(monitor):
    """Calculate optimal display dimensions for the monitor"""
    # Use 80% of screen width and 70% of screen height to leave room for window decorations
    display_width = int(monitor.width * 0.8)
    display_height = int(monitor.height * 0.7)
    
    # Ensure minimum usable size
    display_width = max(display_width, 800)
    display_height = max(display_height, 600)
    
    return display_width, display_height


def create_config(display_width, display_height, output_path="config.json"):
    """Create a config.json file with optimal dimensions"""
    config = {
        "dimensions": {
            "display_width": display_width,
            "display_height": display_height,
            "processing_height": 820,
            "processing_width": 666,
        },
        "threshold_params": {
            "GAMMA_LOW": 0.7,
            "MIN_GAP": 30,
            "MIN_JUMP": 25,
            "CONFIDENT_SURPLUS": 5,
            "JUMP_DELTA": 30,
            "PAGE_TYPE_FOR_THRESHOLD": "white",
        },
        "alignment_params": {
            "auto_align": False,
            "match_col": 5,
            "max_steps": 20,
            "stride": 1,
            "thickness": 3,
        },
        "outputs": {
            "show_image_level": 5,  # Enable template layout display
            "save_image_level": 0,
            "save_detections": True,
            "filter_out_multimarked_files": False,
        },
    }
    
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config


def main():
    print("OMRChecker Screen Configuration Generator")
    print("=" * 40)
    
    # Get screen information
    monitor = get_screen_info()
    if not monitor:
        sys.exit(1)
    
    # Calculate optimal dimensions
    display_width, display_height = calculate_optimal_dimensions(monitor)
    
    print(f"\nRecommended display dimensions for your screen:")
    print(f"  Width:  {display_width}px")
    print(f"  Height: {display_height}px")
    
    # Ask user for confirmation
    response = input(f"\nCreate config.json with these dimensions? (y/n): ").lower().strip()
    if response not in ['y', 'yes']:
        print("Configuration cancelled.")
        return
    
    # Create the config file
    config_path = Path("config.json")
    if config_path.exists():
        overwrite = input("config.json already exists. Overwrite? (y/n): ").lower().strip()
        if overwrite not in ['y', 'yes']:
            print("Configuration cancelled.")
            return
    
    try:
        config = create_config(display_width, display_height)
        print(f"\n✅ Created config.json with optimal dimensions for your screen!")
        print(f"📁 File location: {config_path.absolute()}")
        print(f"\nTo use this configuration:")
        print(f"1. Place this config.json in your OMR image directory")
        print(f"2. Run OMRChecker with: python main.py --setLayout")
        print(f"\nThe template layout windows should now fit properly on your screen.")
        
    except Exception as e:
        print(f"Error creating config file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

