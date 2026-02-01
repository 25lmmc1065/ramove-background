# 🎨 AI-Powered Professional Portrait Enhancement

A complete web application for professional portrait enhancement using Python, Flask, OpenCV, and AI libraries. Transform your portraits with AI-powered background removal, virtual outfits, and professional image enhancements.

![Professional Portrait Enhancement](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-red.svg)

## ✨ Features

### 🖼️ Background Processing
- **Background Removal** - Automatically remove background from photos using AI (rembg)
- **Custom Background Color** - Pick any color as new background with color picker
- **Custom Background Image** - Upload your own background images
- **Cinematic Blurred Background** - Professional soft blurred backgrounds
- **Preset Backgrounds** - Choose from studio, office, nature, city, and gradient presets

### 👔 Virtual Dress/Outfit Changer
- **Jacket Overlay** - Add leather, denim, or blazer jackets
- **Formal Wear** - Business suits and dress shirts
- **Casual Wear** - T-shirts and hoodies
- **Traditional Wear** - Cultural outfits (kurta, etc.)
- **Custom Clothing Upload** - Apply your own clothing images
- Smart positioning based on body/shoulder detection

### ✨ Image Enhancement
- **Brightness Control** - Adjustable slider (50-200%)
- **Contrast Control** - Adjustable slider (50-200%)
- **Dynamic Range Enhancement** - HDR-like effect using CLAHE
- **Skin Tone Enhancement** - Natural skin smoothing with bilateral filtering
- **Soft Studio Lighting Effect** - Professional lighting simulation
- **Color Correction** - Auto white balance and color enhancement

### 🎯 Face Preservation & Smart Features
- **Face Detection** - Using OpenCV Haar cascades
- **Keep Face Realistic** - Face details preserved during transformations
- **Face-aware Processing** - Enhancements protect facial features
- **Multiple Format Support** - PNG, JPG, WebP
- **Before/After Preview** - Side-by-side comparison
- **Easy Download** - Download processed images with one click

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/25lmmc1065/ramove-background.git
cd ramove-background
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

4. **Open in browser**
Navigate to `http://localhost:5000` in your web browser.

## 📋 Tech Stack

### Backend
- **Python 3** - Core programming language
- **Flask** - Web framework
- **OpenCV** - Image processing
- **NumPy** - Numerical operations
- **Pillow (PIL)** - Image manipulation
- **rembg** - AI-powered background removal

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with modern animations
- **JavaScript** - Interactive functionality and AJAX

### AI/ML
- **OpenCV Haar Cascades** - Face and body detection
- **U2-Net (via rembg)** - Background segmentation

## 📁 Project Structure

```
├── app.py                 # Main Flask application with all routes
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── static/
│   ├── css/
│   │   └── style.css     # Modern styling with animations
│   ├── js/
│   │   └── main.js       # Frontend logic and AJAX calls
│   ├── backgrounds/      # Preset background images
│   │   ├── studio.jpg
│   │   ├── office.jpg
│   │   ├── nature.jpg
│   │   ├── city.jpg
│   │   └── gradient.jpg
│   ├── outfits/          # Preset clothing images
│   │   ├── jackets/
│   │   │   ├── leather.png
│   │   │   ├── denim.png
│   │   │   └── blazer.png
│   │   ├── formal/
│   │   │   ├── suit.png
│   │   │   └── dress_shirt.png
│   │   ├── casual/
│   │   │   ├── tshirt.png
│   │   │   └── hoodie.png
│   │   └── traditional/
│   │       └── kurta.png
│   └── uploads/          # User uploaded files
├── templates/
│   └── index.html        # Main web interface
└── utils/
    ├── __init__.py
    ├── background.py     # Background processing functions
    ├── enhancement.py    # Image enhancement functions
    ├── outfit.py         # Virtual dress changer functions
    └── face_detection.py # Face detection utilities
```

## 🎮 Usage Guide

### 1. Upload an Image
- Drag and drop an image onto the upload area, or
- Click to browse and select an image
- Supports PNG, JPG, JPEG, WebP (max 16MB)

### 2. Process Background
- Click **"Remove Background"** to remove the background
- Select a background type:
  - **Solid Color**: Pick any color using the color picker
  - **Gradient**: Apply a gradient background
  - **Blurred Background**: Create cinematic blurred effect
  - **Preset**: Choose from professional presets
  - **Custom Image**: Upload your own background
- Click **"Apply Background"** to apply changes

### 3. Add Virtual Outfit
- Switch to the **"Outfit"** tab
- Select a category (Jackets, Formal, Casual, Traditional)
- Click on an outfit to select it
- Or upload a custom outfit (PNG with transparency)
- Click **"Apply Outfit"** to add the clothing

### 4. Enhance Image
- Switch to the **"Enhancement"** tab
- Adjust brightness and contrast sliders
- Enable optional enhancements:
  - Dynamic Range Enhancement (HDR)
  - Skin Tone Enhancement
  - Soft Studio Lighting
  - Auto Color Correction
- Toggle **"Preserve Face Details"** to protect facial features
- Click **"Apply Enhancements"**

### 5. Download
- Click **"Download"** to save your enhanced portrait
- Use **"Reset"** to return to the original image
- Use **"Process All"** to apply multiple transformations at once

## 🔧 API Routes

- `GET /` - Main application page
- `POST /upload` - Upload image
- `POST /remove-background` - Remove background from image
- `POST /change-background` - Apply new background
- `POST /apply-outfit` - Apply clothing overlay
- `POST /enhance` - Apply image enhancements
- `POST /process-all` - Apply all selected transformations
- `GET /download/<filename>` - Download processed image

## 🛠️ Development

### Adding Custom Backgrounds
Place your background images in `static/backgrounds/` directory.

### Adding Custom Outfits
1. Create PNG images with transparency
2. Place in appropriate category folder under `static/outfits/`
3. Update the HTML gallery in `templates/index.html`

### Modifying Image Processing
- Background functions: `utils/background.py`
- Enhancement functions: `utils/enhancement.py`
- Outfit functions: `utils/outfit.py`
- Face detection: `utils/face_detection.py`

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📧 Contact

For questions or support, please open an issue on GitHub.

## 🙏 Acknowledgments

- **rembg** - AI background removal
- **OpenCV** - Computer vision library
- **Flask** - Web framework
- **U2-Net** - Deep learning model for salient object detection

---

**Made with ❤️ using Python, Flask, OpenCV, and AI**