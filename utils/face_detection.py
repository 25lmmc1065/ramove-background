"""
Face detection and preservation utilities
"""
import cv2
import numpy as np

class FaceDetector:
    def __init__(self):
        # Load Haar cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def detect_faces(self, image):
        """
        Detect faces in an image
        
        Args:
            image: numpy array (BGR image)
            
        Returns:
            List of (x, y, w, h) tuples for detected faces
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        return faces
    
    def create_face_mask(self, image, faces, expansion=1.5):
        """
        Create a mask for face regions with expansion
        
        Args:
            image: numpy array (BGR image)
            faces: List of (x, y, w, h) tuples
            expansion: Factor to expand face regions
            
        Returns:
            Binary mask where face regions are white
        """
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        
        for (x, y, w, h) in faces:
            # Expand face region
            expand_w = int(w * expansion)
            expand_h = int(h * expansion)
            expand_x = max(0, x - (expand_w - w) // 2)
            expand_y = max(0, y - (expand_h - h) // 2)
            
            # Ensure within bounds
            expand_x = min(expand_x, image.shape[1] - expand_w)
            expand_y = min(expand_y, image.shape[0] - expand_h)
            
            cv2.ellipse(mask, 
                       (expand_x + expand_w // 2, expand_y + expand_h // 2),
                       (expand_w // 2, expand_h // 2),
                       0, 0, 360, 255, -1)
        
        return mask
    
    def preserve_face_details(self, original, processed, blend_factor=0.3):
        """
        Blend processed image with original to preserve face details
        
        Args:
            original: Original image (BGR)
            processed: Processed image (BGR)
            blend_factor: How much of original to keep (0-1)
            
        Returns:
            Blended image with preserved face details
        """
        faces = self.detect_faces(original)
        
        if len(faces) == 0:
            return processed
        
        face_mask = self.create_face_mask(original, faces, expansion=1.2)
        face_mask_blur = cv2.GaussianBlur(face_mask, (21, 21), 0)
        face_mask_normalized = face_mask_blur.astype(float) / 255.0
        
        # Blend original and processed in face regions
        result = processed.copy()
        for i in range(3):
            result[:, :, i] = (
                processed[:, :, i] * (1 - face_mask_normalized * blend_factor) +
                original[:, :, i] * (face_mask_normalized * blend_factor)
            ).astype(np.uint8)
        
        return result
