import cv2
import numpy as np

def run_model(img):
    """
    Extremely simple, bare-minimum color detection for Currency.
    No complex AI, no SIFT, no hanging. Looks purely at the dominant color.
    """
    # Resize very small
    small_img = cv2.resize(img, (200, int(200 * img.shape[0] / img.shape[1])))
    
    # img from app.py is in RGB format! We must use RGB2HSV
    hsv = cv2.cvtColor(small_img, cv2.COLOR_RGB2HSV)
    
    # Center crop 60% of the image to ignore the background table/wall
    h, w = hsv.shape[:2]
    cx1, cx2 = int(w * 0.2), int(w * 0.8)
    cy1, cy2 = int(h * 0.2), int(h * 0.8)
    center_hsv = hsv[cy1:cy2, cx1:cx2]

    # Massively forgiving color boundaries for phones with bad lighting
    color_ranges = {
        # 50 Rupee: Fluorescent Blue / Cyan / Light Blue
        "50Rupees": ([70, 40, 40], [130, 255, 255]), 
        
        # 100 Rupee: Lavender / Purple / Violet
        "100Rupees": ([130, 20, 40], [170, 200, 255]), 
        
        # 20 Rupee: Greenish Yellow / Pale Lime
        "20Rupees": ([35, 40, 40], [70, 255, 255]), 
        
        # 200 Rupee: Bright Orange / Strong Yellow
        "200Rupees": ([10, 100, 80], [35, 255, 255]), 
        
        # 10 Rupee: Chocolate Brown / Muddy Red / Dark Orange
        "10Rupees": ([0, 40, 40], [20, 200, 200]), 
        
        # 500 Rupee: Stone Grey (Low Saturation, any Hue)
        "500Rupees": ([0, 0, 30], [180, 50, 180]), 
    }

    max_pixels = 0
    best_color_match = None
    total_center_pixels = center_hsv.shape[0] * center_hsv.shape[1]

    for label, (lower, upper) in color_ranges.items():
        lower_np = np.array(lower, dtype=np.uint8)
        upper_np = np.array(upper, dtype=np.uint8)
        mask = cv2.inRange(center_hsv, lower_np, upper_np)
        
        pixel_count = cv2.countNonZero(mask)
        if pixel_count > max_pixels:
            max_pixels = pixel_count
            best_color_match = label

    # If the dominant color takes up just 5% of the center frame, declare it!
    # This makes it aggressively responsive.
    if max_pixels > total_center_pixels * 0.05 and best_color_match is not None:
        cv2.putText(img, best_color_match, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return img, f"Image contains One {best_color_match} Note"
        
    return img, "Image contains"
