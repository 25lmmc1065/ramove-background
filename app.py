"""
Flask application for professional portrait enhancement
"""
from flask import Flask, render_template, request, send_file, jsonify
import os
import cv2
import numpy as np
from PIL import Image
import io
from werkzeug.utils import secure_filename
import base64

from utils.background import (
    remove_background, apply_solid_color_background, 
    apply_image_background, apply_blurred_background,
    create_gradient_background
)
from utils.enhancement import apply_all_enhancements
from utils.outfit import apply_outfit, apply_outfit_smart
from utils.face_detection import FaceDetector

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp'}

# Initialize face detector
face_detector = FaceDetector()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def load_image_from_request(file_key='image'):
    """Load image from request"""
    if file_key not in request.files:
        return None, "No file provided"
    
    file = request.files[file_key]
    
    if file.filename == '':
        return None, "No file selected"
    
    if not allowed_file(file.filename):
        return None, "File type not allowed"
    
    # Read image
    file_bytes = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    if image is None:
        return None, "Failed to load image"
    
    return image, None

def encode_image_to_base64(image, format='png'):
    """Encode image to base64 string"""
    if isinstance(image, np.ndarray):
        # OpenCV image
        _, buffer = cv2.imencode(f'.{format}', image)
        img_str = base64.b64encode(buffer).decode()
    else:
        # PIL Image
        buffered = io.BytesIO()
        image.save(buffered, format=format.upper())
        img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/{format};base64,{img_str}"

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    """Upload and store image"""
    image, error = load_image_from_request('image')
    
    if error:
        return jsonify({'error': error}), 400
    
    # Save original image
    filename = secure_filename('uploaded_image.jpg')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    cv2.imwrite(filepath, image)
    
    # Return base64 encoded image for preview
    img_base64 = encode_image_to_base64(image, 'jpeg')
    
    return jsonify({
        'success': True,
        'filename': filename,
        'preview': img_base64
    })

@app.route('/remove-background', methods=['POST'])
def remove_bg():
    """Remove background from image"""
    try:
        image, error = load_image_from_request('image')
        
        if error:
            return jsonify({'error': error}), 400
        
        # Remove background
        result_rgba = remove_background(image)
        
        # Convert to base64
        img_base64 = encode_image_to_base64(result_rgba, 'png')
        
        return jsonify({
            'success': True,
            'image': img_base64
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/change-background', methods=['POST'])
def change_background():
    """Apply new background to image"""
    try:
        image, error = load_image_from_request('image')
        
        if error:
            return jsonify({'error': error}), 400
        
        bg_type = request.form.get('bg_type', 'color')
        
        # Remove background first
        image_rgba = remove_background(image)
        
        if bg_type == 'color':
            # Solid color background
            color_hex = request.form.get('color', '#FFFFFF')
            # Convert hex to RGB
            color_hex = color_hex.lstrip('#')
            color = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
            
            result = apply_solid_color_background(image_rgba, color)
            
        elif bg_type == 'image':
            # Custom image background
            if 'bg_image' in request.files:
                bg_file = request.files['bg_image']
                bg_bytes = np.frombuffer(bg_file.read(), np.uint8)
                bg_cv = cv2.imdecode(bg_bytes, cv2.IMREAD_COLOR)
                bg_rgb = cv2.cvtColor(bg_cv, cv2.COLOR_BGR2RGB)
                bg_pil = Image.fromarray(bg_rgb)
            else:
                return jsonify({'error': 'No background image provided'}), 400
            
            result = apply_image_background(image_rgba, bg_pil)
            
        elif bg_type == 'preset':
            # Preset background
            preset_name = request.form.get('preset', 'studio')
            preset_path = os.path.join('static', 'backgrounds', f'{preset_name}.jpg')
            
            if os.path.exists(preset_path):
                bg_pil = Image.open(preset_path)
                result = apply_image_background(image_rgba, bg_pil)
            else:
                return jsonify({'error': 'Preset background not found'}), 404
                
        elif bg_type == 'blur':
            # Blurred background
            blur_amount = int(request.form.get('blur_amount', 25))
            result_cv = apply_blurred_background(image, blur_amount)
            result = Image.fromarray(cv2.cvtColor(result_cv, cv2.COLOR_BGR2RGB))
            
        elif bg_type == 'gradient':
            # Gradient background
            result = apply_image_background(
                image_rgba,
                create_gradient_background(image_rgba.size[0], image_rgba.size[1])
            )
        else:
            return jsonify({'error': 'Invalid background type'}), 400
        
        # Convert to base64
        img_base64 = encode_image_to_base64(result, 'jpeg')
        
        return jsonify({
            'success': True,
            'image': img_base64
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/apply-outfit', methods=['POST'])
def apply_outfit_route():
    """Apply clothing overlay to image"""
    try:
        image, error = load_image_from_request('image')
        
        if error:
            return jsonify({'error': error}), 400
        
        outfit_type = request.form.get('outfit_type', 'preset')
        
        if outfit_type == 'preset':
            # Preset outfit
            category = request.form.get('category', 'jackets')
            outfit_name = request.form.get('outfit', 'blazer')
            outfit_path = os.path.join('static', 'outfits', category, f'{outfit_name}.png')
            
            if not os.path.exists(outfit_path):
                return jsonify({'error': 'Outfit not found'}), 404
                
        elif outfit_type == 'custom':
            # Custom outfit upload
            if 'outfit_image' not in request.files:
                return jsonify({'error': 'No outfit image provided'}), 400
            
            outfit_file = request.files['outfit_image']
            outfit_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_outfit.png')
            outfit_file.save(outfit_path)
        else:
            return jsonify({'error': 'Invalid outfit type'}), 400
        
        # Apply outfit
        result = apply_outfit_smart(image, outfit_path)
        
        # Convert to base64
        img_base64 = encode_image_to_base64(result, 'jpeg')
        
        return jsonify({
            'success': True,
            'image': img_base64
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/enhance', methods=['POST'])
def enhance_image():
    """Apply image enhancements"""
    try:
        image, error = load_image_from_request('image')
        
        if error:
            return jsonify({'error': error}), 400
        
        # Get enhancement parameters
        brightness = float(request.form.get('brightness', 1.0))
        contrast = float(request.form.get('contrast', 1.0))
        enable_hdr = request.form.get('hdr', 'false').lower() == 'true'
        enable_skin = request.form.get('skin', 'false').lower() == 'true'
        enable_lighting = request.form.get('lighting', 'false').lower() == 'true'
        enable_color = request.form.get('color', 'false').lower() == 'true'
        
        # Apply enhancements
        result = apply_all_enhancements(
            image, 
            brightness=brightness,
            contrast=contrast,
            enable_hdr=enable_hdr,
            enable_skin=enable_skin,
            enable_lighting=enable_lighting,
            enable_color=enable_color
        )
        
        # Preserve face details if needed
        preserve_face = request.form.get('preserve_face', 'true').lower() == 'true'
        if preserve_face and (enable_skin or enable_hdr or enable_lighting):
            result = face_detector.preserve_face_details(image, result, blend_factor=0.2)
        
        # Convert to base64
        img_base64 = encode_image_to_base64(result, 'jpeg')
        
        return jsonify({
            'success': True,
            'image': img_base64
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process-all', methods=['POST'])
def process_all():
    """Apply all selected transformations"""
    try:
        image, error = load_image_from_request('image')
        
        if error:
            return jsonify({'error': error}), 400
        
        result = image.copy()
        
        # 1. Background processing (if requested)
        if request.form.get('change_bg', 'false').lower() == 'true':
            bg_type = request.form.get('bg_type', 'color')
            
            if bg_type == 'blur':
                blur_amount = int(request.form.get('blur_amount', 25))
                result = apply_blurred_background(result, blur_amount)
            else:
                # Remove background for other types
                image_rgba = remove_background(result)
                
                if bg_type == 'color':
                    color_hex = request.form.get('color', '#FFFFFF')
                    color_hex = color_hex.lstrip('#')
                    color = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
                    result_pil = apply_solid_color_background(image_rgba, color)
                    result = cv2.cvtColor(np.array(result_pil), cv2.COLOR_RGB2BGR)
                elif bg_type == 'gradient':
                    result_pil = apply_image_background(
                        image_rgba,
                        create_gradient_background(image_rgba.size[0], image_rgba.size[1])
                    )
                    result = cv2.cvtColor(np.array(result_pil), cv2.COLOR_RGB2BGR)
        
        # 2. Outfit application (if requested)
        if request.form.get('apply_outfit', 'false').lower() == 'true':
            category = request.form.get('outfit_category', 'jackets')
            outfit_name = request.form.get('outfit_name', 'blazer')
            outfit_path = os.path.join('static', 'outfits', category, f'{outfit_name}.png')
            
            if os.path.exists(outfit_path):
                result = apply_outfit_smart(result, outfit_path)
        
        # 3. Enhancements (if requested)
        if request.form.get('apply_enhancements', 'false').lower() == 'true':
            brightness = float(request.form.get('brightness', 1.0))
            contrast = float(request.form.get('contrast', 1.0))
            enable_hdr = request.form.get('hdr', 'false').lower() == 'true'
            enable_skin = request.form.get('skin', 'false').lower() == 'true'
            enable_lighting = request.form.get('lighting', 'false').lower() == 'true'
            enable_color = request.form.get('color', 'false').lower() == 'true'
            
            result = apply_all_enhancements(
                result,
                brightness=brightness,
                contrast=contrast,
                enable_hdr=enable_hdr,
                enable_skin=enable_skin,
                enable_lighting=enable_lighting,
                enable_color=enable_color
            )
            
            preserve_face = request.form.get('preserve_face', 'true').lower() == 'true'
            if preserve_face:
                result = face_detector.preserve_face_details(image, result, blend_factor=0.2)
        
        # Convert to base64
        img_base64 = encode_image_to_base64(result, 'jpeg')
        
        return jsonify({
            'success': True,
            'image': img_base64
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download processed image"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(filepath, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Run app
    # Note: Set debug=False in production for security
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
