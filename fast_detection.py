import cv2
import numpy as np

def run_model(img):
    """
    Ultra-fast color-based Indian Currency Detection.
    Bypasses Heavy PyTorch models for instant millisecond inference.
    """
    # Resize very small for lightning speed operations
    small_img = cv2.resize(img, (400, int(400 * img.shape[0] / img.shape[1])))
    hsv = cv2.cvtColor(small_img, cv2.COLOR_BGR2HSV)
    
    # Precise HSV color bounds for Indian Currency
    color_ranges = {
        # 50 Rupee: Fluorescent Blue / Cyan 
        "50Rupees": ([80, 50, 50], [110, 255, 255]), 
        
        # 100 Rupee: Lavender / Light Purple
        "100Rupees": ([115, 30, 50], [160, 200, 255]), 
        
        # 20 Rupee: Greenish Yellow
        "20Rupees": ([30, 50, 50], [50, 255, 255]), 
        
        # 200 Rupee: Bright Orange / Yellow
        "200Rupees": ([10, 100, 100], [25, 255, 255]), 
        
        # 10 Rupee: Chocolate Brown / Dark Orange
        "10Rupees": ([5, 50, 50], [15, 200, 200]), 
        
        # 500 Rupee: Stone Grey (Very Low Saturation, Green/Yellow hue)
        "500Rupees": ([20, 5, 50], [90, 45, 200]), 
    }

    best_match = None
    max_pixels = 0
    
    # Focus only on the center 60% of the image to ignore background walls/furniture
    h, w = small_img.shape[:2]
    cx1, cx2 = int(w * 0.2), int(w * 0.8)
    cy1, cy2 = int(h * 0.2), int(h * 0.8)
    center_hsv = hsv[cy1:cy2, cx1:cx2]
    
    total_center_pixels = (cx2 - cx1) * (cy2 - cy1)

    for label, (lower, upper) in color_ranges.items():
        lower_np = np.array(lower, dtype=np.uint8)
        upper_np = np.array(upper, dtype=np.uint8)
        mask = cv2.inRange(center_hsv, lower_np, upper_np)
        
        pixel_count = cv2.countNonZero(mask)
        if pixel_count > max_pixels:
            max_pixels = pixel_count
            best_match = label

    # Require the dominant matched color to fill at least 10% of the center view
    if max_pixels > total_center_pixels * 0.10:
        cv2.putText(img, best_match, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return img, f"Image contains One {best_match} Note"
        
    return img, "Image contains"
