"""
Background removal and replacement functions
"""
import cv2
import numpy as np
from PIL import Image
from rembg import remove
import io

def remove_background(image_data):
    """
    Remove background from image using rembg
    
    Args:
        image_data: Image as numpy array (BGR) or PIL Image
        
    Returns:
        Image with transparent background (RGBA)
    """
    # Convert to PIL if needed
    if isinstance(image_data, np.ndarray):
        image_rgb = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
    else:
        pil_image = image_data
    
    # Remove background
    output = remove(pil_image)
    
    return output

def apply_solid_color_background(image_rgba, color):
    """
    Apply solid color background to image with transparent background
    
    Args:
        image_rgba: PIL Image with alpha channel
        color: Tuple (R, G, B) for background color
        
    Returns:
        PIL Image with solid color background
    """
    # Create background with specified color
    background = Image.new('RGB', image_rgba.size, color)
    
    # Composite the image on the background
    background.paste(image_rgba, (0, 0), image_rgba)
    
    return background

def apply_image_background(image_rgba, background_image):
    """
    Apply custom image as background
    
    Args:
        image_rgba: PIL Image with alpha channel
        background_image: PIL Image for background
        
    Returns:
        PIL Image with custom background
    """
    # Resize background to match foreground
    background_resized = background_image.resize(image_rgba.size, Image.LANCZOS)
    
    # Convert to RGB if needed
    if background_resized.mode != 'RGB':
        background_resized = background_resized.convert('RGB')
    
    # Composite
    background_resized.paste(image_rgba, (0, 0), image_rgba)
    
    return background_resized

def apply_blurred_background(image_data, blur_amount=25):
    """
    Apply cinematic blurred background effect
    
    Args:
        image_data: numpy array (BGR image)
        blur_amount: Amount of blur (odd number)
        
    Returns:
        numpy array with blurred background
    """
    # Remove background to get RGBA
    image_rgb = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    foreground_rgba = remove(pil_image)
    
    # Convert back to numpy
    foreground_np = np.array(foreground_rgba)
    
    # Create mask from alpha channel
    alpha = foreground_np[:, :, 3]
    
    # Blur the original image
    blur_amount = blur_amount if blur_amount % 2 == 1 else blur_amount + 1
    blurred = cv2.GaussianBlur(image_data, (blur_amount, blur_amount), 0)
    
    # Convert foreground RGBA to BGR
    foreground_bgr = cv2.cvtColor(foreground_np[:, :, :3], cv2.COLOR_RGB2BGR)
    
    # Blend foreground with blurred background
    alpha_normalized = alpha.astype(float) / 255.0
    alpha_3d = np.stack([alpha_normalized] * 3, axis=2)
    
    result = (foreground_bgr * alpha_3d + blurred * (1 - alpha_3d)).astype(np.uint8)
    
    return result

def create_gradient_background(width, height, color1=(100, 50, 150), color2=(200, 100, 50)):
    """
    Create gradient background
    
    Args:
        width: Width of image
        height: Height of image
        color1: Starting color (R, G, B)
        color2: Ending color (R, G, B)
        
    Returns:
        PIL Image with gradient
    """
    gradient = np.zeros((height, width, 3), dtype=np.uint8)
    
    for i in range(height):
        ratio = i / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        gradient[i, :] = [r, g, b]
    
    return Image.fromarray(gradient, 'RGB')
