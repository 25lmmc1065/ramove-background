"""
Image enhancement functions
"""
import cv2
import numpy as np

def adjust_brightness(image, factor=1.0):
    """
    Adjust image brightness
    
    Args:
        image: numpy array (BGR image)
        factor: Brightness factor (0.5 = darker, 1.0 = normal, 2.0 = brighter)
        
    Returns:
        Adjusted image
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * factor, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

def adjust_contrast(image, factor=1.0):
    """
    Adjust image contrast
    
    Args:
        image: numpy array (BGR image)
        factor: Contrast factor (0.5 = less contrast, 1.0 = normal, 2.0 = more contrast)
        
    Returns:
        Adjusted image
    """
    # Convert to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)
    
    # Adjust L channel
    l_channel = lab[:, :, 0]
    mean = np.mean(l_channel)
    lab[:, :, 0] = np.clip((l_channel - mean) * factor + mean, 0, 255)
    
    return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)

def enhance_dynamic_range(image, clip_limit=2.0):
    """
    Apply HDR-like dynamic range enhancement using CLAHE
    
    Args:
        image: numpy array (BGR image)
        clip_limit: Contrast limit for CLAHE
        
    Returns:
        Enhanced image
    """
    # Convert to LAB
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    
    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
    lab[:, :, 0] = clahe.apply(lab[:, :, 0])
    
    # Convert back to BGR
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

def enhance_skin_tone(image, smoothing=15):
    """
    Enhance skin tones with natural smoothing
    
    Args:
        image: numpy array (BGR image)
        smoothing: Smoothing strength (higher = more smoothing)
        
    Returns:
        Enhanced image
    """
    # Create bilateral filter for smoothing while preserving edges
    smoothed = cv2.bilateralFilter(image, smoothing, 75, 75)
    
    # Blend original and smoothed
    result = cv2.addWeighted(image, 0.5, smoothed, 0.5, 0)
    
    # Slight warm tone adjustment
    result = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
    result[:, :, 0] = np.clip(result[:, :, 0] - 5, 0, 180)  # Shift hue slightly to warm
    result[:, :, 1] = np.clip(result[:, :, 1] * 1.1, 0, 255)  # Increase saturation slightly
    
    return cv2.cvtColor(result.astype(np.uint8), cv2.COLOR_HSV2BGR)

def apply_studio_lighting(image):
    """
    Apply soft studio lighting effect
    
    Args:
        image: numpy array (BGR image)
        
    Returns:
        Image with studio lighting effect
    """
    # Create a soft light overlay
    height, width = image.shape[:2]
    
    # Create radial gradient from center
    y, x = np.ogrid[:height, :width]
    center_y, center_x = height // 2, width // 2
    
    # Distance from center
    dist_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
    max_dist = np.sqrt(center_x**2 + center_y**2)
    
    # Create vignette (inverse - brighter in center)
    vignette = 1 - (dist_from_center / max_dist) * 0.3
    vignette = np.clip(vignette, 0.7, 1.0)
    
    # Apply vignette
    result = image.astype(np.float32)
    for i in range(3):
        result[:, :, i] = np.clip(result[:, :, i] * vignette, 0, 255)
    
    # Add slight brightness boost
    result = cv2.convertScaleAbs(result, alpha=1.1, beta=10)
    
    return result

def auto_color_correct(image):
    """
    Apply automatic color correction and white balance
    
    Args:
        image: numpy array (BGR image)
        
    Returns:
        Color corrected image
    """
    # Simple white balance using gray world assumption
    result = image.astype(np.float32)
    
    for i in range(3):
        channel = result[:, :, i]
        avg = np.mean(channel)
        result[:, :, i] = np.clip(channel * (128 / avg), 0, 255)
    
    # Slight saturation boost
    hsv = cv2.cvtColor(result.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.2, 0, 255)
    
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

def apply_all_enhancements(image, brightness=1.0, contrast=1.0, enable_hdr=False, 
                          enable_skin=False, enable_lighting=False, enable_color=False):
    """
    Apply multiple enhancements to an image
    
    Args:
        image: numpy array (BGR image)
        brightness: Brightness factor
        contrast: Contrast factor
        enable_hdr: Apply HDR enhancement
        enable_skin: Apply skin tone enhancement
        enable_lighting: Apply studio lighting
        enable_color: Apply color correction
        
    Returns:
        Enhanced image
    """
    result = image.copy()
    
    # Apply in optimal order
    if enable_color:
        result = auto_color_correct(result)
    
    if brightness != 1.0:
        result = adjust_brightness(result, brightness)
    
    if contrast != 1.0:
        result = adjust_contrast(result, contrast)
    
    if enable_hdr:
        result = enhance_dynamic_range(result)
    
    if enable_skin:
        result = enhance_skin_tone(result)
    
    if enable_lighting:
        result = apply_studio_lighting(result)
    
    return result
