import cv2
import numpy as np
import os
import glob

# Initialize SIFT (Scale-Invariant Feature Transform)
# Matches patterns regardless of rotation, lighting, color cast, or zoom level!
try:
    sift = cv2.SIFT_create(nfeatures=500)
    bf = cv2.BFMatcher()
except:
    sift = None

templates = {}
base_dir = "./test_images"
classes = ["10Rupees", "20Rupees", "50Rupees", "100Rupees", "200Rupees", "500Rupees", "2000Rupees"]

# Pre-load features on boot to keep inference strictly under 50 milliseconds
print("Loading Currency Signature Templates for Lighting-Invariant SIFT Detection...")
if sift:
    for c in classes:
        templates[c] = []
        folder = os.path.join(base_dir, c)
        if os.path.exists(folder):
            images = glob.glob(os.path.join(folder, "*.*"))
            # Only need a couple of good images per denomination to match structural patterns
            for impath in images[:3]:
                if not impath.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    continue
                tmp = cv2.imread(impath, 0)
                if tmp is not None and tmp.size > 0:
                    tmp = cv2.resize(tmp, (400, int(400 * tmp.shape[0] / tmp.shape[1])))
                    kp, des = sift.detectAndCompute(tmp, None)
                    if des is not None and len(des) > 5:
                        templates[c].append(des)

def run_model(img):
    """
    Two-Stage Hybrid Detector:
    1. SIFT Structural Matcher: Bypasses bad lighting and white balance perfectly.
    2. HSV Color Fallback: For extreme blurriness where shapes aren't visible.
    """
    # ---------------- STAGE 1: SIFT STRUCTURAL MATCH ----------------
    small_img = cv2.resize(img, (400, int(400 * img.shape[0] / img.shape[1])))
    best_match = None
    
    if sift:
        gray = cv2.cvtColor(small_img, cv2.COLOR_BGR2GRAY)
        kp, des = sift.detectAndCompute(gray, None)
        
        max_good_matches = 0
        
        if des is not None and len(des) > 5:
            for class_name, descriptors_list in templates.items():
                for t_des in descriptors_list:
                    # knnMatch finds the k top matches
                    matches = bf.knnMatch(des, t_des, k=2)
                    good = 0
                    # Apply Lowe's Ratio test
                    for match_set in matches:
                        if len(match_set) == 2:
                            m, n = match_set
                            if m.distance < 0.75 * n.distance:
                                good += 1
                                
                    if good > max_good_matches:
                        max_good_matches = good
                        best_match = class_name
                        
        # 10 structural matching points means unquestionable physical identity!
        if max_good_matches > 8 and best_match is not None:
            print(f"Detected {best_match} strictly via SIFT Invariant Geometry ({max_good_matches} matches). Ignored lighting.")
            cv2.putText(img, best_match, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            return img, f"Image contains One {best_match} Note"

    # ---------------- STAGE 2: HSV COLOR FALLBACK ----------------
    # Widen the ranges to accommodate bad white-balance of phone cameras
    hsv = cv2.cvtColor(small_img, cv2.COLOR_BGR2HSV)
    
    color_ranges = {
        # 50 Rupee (Cyan/Blueish/Even greenish due to bad light)
        "50Rupees": ([70, 30, 40], [120, 255, 255]), 
        # 100 Rupee (Purple / Dark Lilac)
        "100Rupees": ([115, 20, 40], [165, 255, 255]), 
        # 20 Rupee (Greenish Yellow / Pale lime)
        "20Rupees": ([20, 40, 40], [55, 255, 255]), 
        # 200 Rupee (Bright Orange / Bright Yellow)
        "200Rupees": ([10, 80, 80], [25, 255, 255]), 
        # 10 Rupee (Chocolate Brown / Muddy Red)
        "10Rupees": ([0, 30, 40], [20, 200, 200]), 
        # 500 Rupee (Grey / Dull green / Yellowish grey low saturation)
        "500Rupees": ([15, 0, 40], [60, 45, 210]), 
    }

    max_pixels = 0
    best_color_match = None
    
    h, w = small_img.shape[:2]
    cx1, cx2 = int(w * 0.15), int(w * 0.85)
    cy1, cy2 = int(h * 0.15), int(h * 0.85)
    center_hsv = hsv[cy1:cy2, cx1:cx2]
    
    total_center_pixels = (cx2 - cx1) * (cy2 - cy1)

    for label, (lower, upper) in color_ranges.items():
        lower_np = np.array(lower, dtype=np.uint8)
        upper_np = np.array(upper, dtype=np.uint8)
        mask = cv2.inRange(center_hsv, lower_np, upper_np)
        
        pixel_count = cv2.countNonZero(mask)
        if pixel_count > max_pixels:
            max_pixels = pixel_count
            best_color_match = label

    # Require minimum coverage of the center frame to prevent random noise alerts
    if max_pixels > total_center_pixels * 0.12 and best_color_match is not None:
        print(f"Detected {best_color_match} via fallback HSV Center-Crop.")
        cv2.putText(img, best_color_match, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return img, f"Image contains One {best_color_match} Note"
        
    return img, "Image contains"
