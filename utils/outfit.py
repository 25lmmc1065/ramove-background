"""
Virtual dress/outfit changer functions
"""
import cv2
import numpy as np
from PIL import Image

def detect_upper_body(image):
    """
    Detect upper body region for outfit placement
    
    Args:
        image: numpy array (BGR image)
        
    Returns:
        (x, y, w, h) tuple for upper body region, or None if not detected
    """
    # Load upper body cascade
    upper_body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_upperbody.xml')
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bodies = upper_body_cascade.detectMultiScale(gray, 1.1, 3)
    
    if len(bodies) > 0:
        # Return the largest detected body
        return max(bodies, key=lambda x: x[2] * x[3])
    
    # Fallback: use face detection to estimate body position
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    if len(faces) > 0:
        fx, fy, fw, fh = faces[0]
        # Estimate body region below face
        body_w = int(fw * 2.5)
        body_h = int(fh * 3)
        body_x = max(0, fx - int(fw * 0.75))
        body_y = fy + fh
        
        return (body_x, body_y, body_w, body_h)
    
    return None

def apply_outfit(image, outfit_image_path, blend_mode='overlay', opacity=0.8):
    """
    Apply outfit/clothing overlay to image
    
    Args:
        image: numpy array (BGR image)
        outfit_image_path: Path to outfit image (should have transparency)
        blend_mode: Blending mode ('overlay', 'multiply', 'screen')
        opacity: Opacity of the outfit (0-1)
        
    Returns:
        Image with outfit applied
    """
    # Load outfit image
    outfit = cv2.imread(outfit_image_path, cv2.IMREAD_UNCHANGED)
    
    if outfit is None:
        return image
    
    # Detect upper body
    body_region = detect_upper_body(image)
    
    if body_region is None:
        # Fallback: center the outfit
        h, w = image.shape[:2]
        outfit_h, outfit_w = outfit.shape[:2]
        x = (w - outfit_w) // 2
        y = (h - outfit_h) // 2
        body_w, body_h = outfit_w, outfit_h
    else:
        x, y, body_w, body_h = body_region
    
    # Resize outfit to fit body region
    outfit_resized = cv2.resize(outfit, (body_w, body_h), interpolation=cv2.INTER_AREA)
    
    # Ensure the outfit fits within image bounds
    result = image.copy()
    
    # Handle alpha channel if present
    if outfit_resized.shape[2] == 4:
        # Extract alpha channel
        alpha = outfit_resized[:, :, 3] / 255.0 * opacity
        outfit_bgr = outfit_resized[:, :, :3]
    else:
        alpha = np.ones((body_h, body_w)) * opacity
        outfit_bgr = outfit_resized
    
    # Calculate actual overlay region (within bounds)
    y_start = max(0, y)
    y_end = min(result.shape[0], y + body_h)
    x_start = max(0, x)
    x_end = min(result.shape[1], x + body_w)
    
    outfit_y_start = max(0, -y)
    outfit_y_end = outfit_y_start + (y_end - y_start)
    outfit_x_start = max(0, -x)
    outfit_x_end = outfit_x_start + (x_end - x_start)
    
    # Extract regions
    roi = result[y_start:y_end, x_start:x_end]
    outfit_roi = outfit_bgr[outfit_y_start:outfit_y_end, outfit_x_start:outfit_x_end]
    alpha_roi = alpha[outfit_y_start:outfit_y_end, outfit_x_start:outfit_x_end]
    
    # Apply blending
    if blend_mode == 'overlay':
        # Standard alpha blending
        for c in range(3):
            roi[:, :, c] = (alpha_roi * outfit_roi[:, :, c] + 
                           (1 - alpha_roi) * roi[:, :, c])
    elif blend_mode == 'multiply':
        # Multiply blend
        blended = (roi.astype(float) * outfit_roi.astype(float) / 255.0).astype(np.uint8)
        for c in range(3):
            roi[:, :, c] = (alpha_roi * blended[:, :, c] + 
                           (1 - alpha_roi) * roi[:, :, c])
    else:  # screen
        # Screen blend
        blended = (255 - (255 - roi.astype(float)) * (255 - outfit_roi.astype(float)) / 255.0).astype(np.uint8)
        for c in range(3):
            roi[:, :, c] = (alpha_roi * blended[:, :, c] + 
                           (1 - alpha_roi) * roi[:, :, c])
    
    result[y_start:y_end, x_start:x_end] = roi
    
    return result

def apply_outfit_smart(image, outfit_image_path, adjust_color=True):
    """
    Apply outfit with smart color matching and positioning
    
    Args:
        image: numpy array (BGR image)
        outfit_image_path: Path to outfit image
        adjust_color: Whether to match outfit color to image lighting
        
    Returns:
        Image with outfit applied
    """
    result = apply_outfit(image, outfit_image_path, blend_mode='overlay', opacity=0.85)
    
    if adjust_color:
        # Slight color adjustment to match image tone (simplified)
        # This would ideally analyze the image's color temperature
        pass
    
    return result
