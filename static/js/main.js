// Global state
let originalImageData = null;
let currentImageData = null;
let selectedPreset = null;
let selectedOutfit = null;
let selectedOutfitCategory = 'jackets';

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const imageInput = document.getElementById('imageInput');
const previewSection = document.getElementById('previewSection');
const controlsSection = document.getElementById('controlsSection');
const originalImage = document.getElementById('originalImage');
const processedImage = document.getElementById('processedImage');
const loadingOverlay = document.getElementById('loadingOverlay');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    setupTabs();
    setupSliders();
    setupBackgroundControls();
    setupOutfitControls();
});

// Event Listeners Setup
function setupEventListeners() {
    // Upload area click
    uploadArea.addEventListener('click', () => imageInput.click());
    
    // File input change
    imageInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#667eea';
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = '#334155';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#334155';
        
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            handleFile(file);
        }
    });
    
    // Button clicks
    document.getElementById('removeBgBtn').addEventListener('click', removeBackground);
    document.getElementById('applyBgBtn').addEventListener('click', applyBackground);
    document.getElementById('applyOutfitBtn').addEventListener('click', applyOutfit);
    document.getElementById('applyEnhancementBtn').addEventListener('click', applyEnhancements);
    document.getElementById('resetBtn').addEventListener('click', resetImage);
    document.getElementById('processAllBtn').addEventListener('click', processAll);
    document.getElementById('downloadBtn').addEventListener('click', downloadImage);
}

// Tab Setup
function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            
            // Remove active class from all
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked
            btn.classList.add('active');
            document.getElementById(`${tabName}Tab`).classList.add('active');
        });
    });
}

// Slider Setup
function setupSliders() {
    const brightness = document.getElementById('brightness');
    const contrast = document.getElementById('contrast');
    const blurAmount = document.getElementById('blurAmount');
    
    brightness.addEventListener('input', (e) => {
        document.getElementById('brightnessValue').textContent = `${e.target.value}%`;
    });
    
    contrast.addEventListener('input', (e) => {
        document.getElementById('contrastValue').textContent = `${e.target.value}%`;
    });
    
    blurAmount.addEventListener('input', (e) => {
        document.getElementById('blurValue').textContent = e.target.value;
    });
}

// Background Controls Setup
function setupBackgroundControls() {
    const bgType = document.getElementById('bgType');
    const colorPickerGroup = document.getElementById('colorPickerGroup');
    const blurAmountGroup = document.getElementById('blurAmountGroup');
    const presetGroup = document.getElementById('presetGroup');
    const customBgGroup = document.getElementById('customBgGroup');
    
    bgType.addEventListener('change', (e) => {
        // Hide all groups
        colorPickerGroup.style.display = 'none';
        blurAmountGroup.style.display = 'none';
        presetGroup.style.display = 'none';
        customBgGroup.style.display = 'none';
        
        // Show relevant group
        switch(e.target.value) {
            case 'color':
                colorPickerGroup.style.display = 'block';
                break;
            case 'blur':
                blurAmountGroup.style.display = 'block';
                break;
            case 'preset':
                presetGroup.style.display = 'block';
                break;
            case 'image':
                customBgGroup.style.display = 'block';
                break;
        }
    });
    
    // Preset selection
    const presetItems = document.querySelectorAll('.preset-item');
    presetItems.forEach(item => {
        item.addEventListener('click', () => {
            presetItems.forEach(i => i.classList.remove('selected'));
            item.classList.add('selected');
            selectedPreset = item.dataset.preset;
        });
    });
}

// Outfit Controls Setup
function setupOutfitControls() {
    const outfitCategory = document.getElementById('outfitCategory');
    const outfitCategories = document.querySelectorAll('.outfit-category');
    
    outfitCategory.addEventListener('change', (e) => {
        selectedOutfitCategory = e.target.value;
        
        // Hide all categories
        outfitCategories.forEach(cat => cat.style.display = 'none');
        
        // Show selected category
        document.querySelector(`[data-category="${selectedOutfitCategory}"]`).style.display = 'grid';
        
        // Clear selection
        document.querySelectorAll('.outfit-item').forEach(item => item.classList.remove('selected'));
        selectedOutfit = null;
    });
    
    // Outfit selection
    const outfitItems = document.querySelectorAll('.outfit-item');
    outfitItems.forEach(item => {
        item.addEventListener('click', () => {
            outfitItems.forEach(i => i.classList.remove('selected'));
            item.classList.add('selected');
            selectedOutfit = item.dataset.outfit;
        });
    });
}

// File Handling
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        showError('Please select an image file');
        return;
    }
    
    if (file.size > 16 * 1024 * 1024) {
        showError('File size must be less than 16MB');
        return;
    }
    
    // Read and display image
    const reader = new FileReader();
    reader.onload = (e) => {
        originalImageData = e.target.result;
        currentImageData = e.target.result;
        
        originalImage.src = originalImageData;
        processedImage.src = currentImageData;
        
        // Show preview and controls
        previewSection.style.display = 'block';
        controlsSection.style.display = 'block';
        uploadArea.style.display = 'none';
    };
    reader.readAsDataURL(file);
}

// Image Processing Functions
async function removeBackground() {
    if (!currentImageData) return;
    
    showLoading(true);
    
    try {
        const formData = new FormData();
        const blob = await fetch(currentImageData).then(r => r.blob());
        formData.append('image', blob, 'image.jpg');
        
        const response = await fetch('/remove-background', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentImageData = data.image;
            processedImage.src = currentImageData;
            showSuccess('Background removed successfully!');
        } else {
            showError(data.error || 'Failed to remove background');
        }
    } catch (error) {
        showError('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

async function applyBackground() {
    if (!currentImageData) return;
    
    const bgType = document.getElementById('bgType').value;
    showLoading(true);
    
    try {
        const formData = new FormData();
        const blob = await fetch(currentImageData).then(r => r.blob());
        formData.append('image', blob, 'image.jpg');
        formData.append('bg_type', bgType);
        
        if (bgType === 'color') {
            formData.append('color', document.getElementById('bgColor').value);
        } else if (bgType === 'blur') {
            formData.append('blur_amount', document.getElementById('blurAmount').value);
        } else if (bgType === 'preset') {
            if (!selectedPreset) {
                showError('Please select a preset background');
                showLoading(false);
                return;
            }
            formData.append('preset', selectedPreset);
        } else if (bgType === 'image') {
            const customBg = document.getElementById('customBgInput').files[0];
            if (!customBg) {
                showError('Please select a background image');
                showLoading(false);
                return;
            }
            formData.append('bg_image', customBg);
        }
        
        const response = await fetch('/change-background', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentImageData = data.image;
            processedImage.src = currentImageData;
            showSuccess('Background applied successfully!');
        } else {
            showError(data.error || 'Failed to apply background');
        }
    } catch (error) {
        showError('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

async function applyOutfit() {
    if (!currentImageData) return;
    
    showLoading(true);
    
    try {
        const formData = new FormData();
        const blob = await fetch(currentImageData).then(r => r.blob());
        formData.append('image', blob, 'image.jpg');
        
        const customOutfit = document.getElementById('customOutfitInput').files[0];
        
        if (customOutfit) {
            formData.append('outfit_type', 'custom');
            formData.append('outfit_image', customOutfit);
        } else if (selectedOutfit) {
            formData.append('outfit_type', 'preset');
            formData.append('category', selectedOutfitCategory);
            formData.append('outfit', selectedOutfit);
        } else {
            showError('Please select an outfit');
            showLoading(false);
            return;
        }
        
        const response = await fetch('/apply-outfit', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentImageData = data.image;
            processedImage.src = currentImageData;
            showSuccess('Outfit applied successfully!');
        } else {
            showError(data.error || 'Failed to apply outfit');
        }
    } catch (error) {
        showError('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

async function applyEnhancements() {
    if (!currentImageData) return;
    
    showLoading(true);
    
    try {
        const formData = new FormData();
        const blob = await fetch(currentImageData).then(r => r.blob());
        formData.append('image', blob, 'image.jpg');
        
        const brightness = document.getElementById('brightness').value / 100;
        const contrast = document.getElementById('contrast').value / 100;
        
        formData.append('brightness', brightness);
        formData.append('contrast', contrast);
        formData.append('hdr', document.getElementById('hdrEnhancement').checked);
        formData.append('skin', document.getElementById('skinTone').checked);
        formData.append('lighting', document.getElementById('studioLighting').checked);
        formData.append('color', document.getElementById('colorCorrection').checked);
        formData.append('preserve_face', document.getElementById('preserveFace').checked);
        
        const response = await fetch('/enhance', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentImageData = data.image;
            processedImage.src = currentImageData;
            showSuccess('Enhancements applied successfully!');
        } else {
            showError(data.error || 'Failed to apply enhancements');
        }
    } catch (error) {
        showError('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

async function processAll() {
    if (!currentImageData) return;
    
    showLoading(true);
    
    try {
        const formData = new FormData();
        const blob = await fetch(originalImageData).then(r => r.blob());
        formData.append('image', blob, 'image.jpg');
        
        // Background settings
        const changeBg = confirm('Apply background changes?');
        formData.append('change_bg', changeBg);
        if (changeBg) {
            const bgType = document.getElementById('bgType').value;
            formData.append('bg_type', bgType);
            if (bgType === 'color') {
                formData.append('color', document.getElementById('bgColor').value);
            } else if (bgType === 'blur') {
                formData.append('blur_amount', document.getElementById('blurAmount').value);
            }
        }
        
        // Outfit settings
        const applyOutfitFlag = confirm('Apply outfit?');
        formData.append('apply_outfit', applyOutfitFlag);
        if (applyOutfitFlag && selectedOutfit) {
            formData.append('outfit_category', selectedOutfitCategory);
            formData.append('outfit_name', selectedOutfit);
        }
        
        // Enhancement settings
        const applyEnhancements = confirm('Apply enhancements?');
        formData.append('apply_enhancements', applyEnhancements);
        if (applyEnhancements) {
            formData.append('brightness', document.getElementById('brightness').value / 100);
            formData.append('contrast', document.getElementById('contrast').value / 100);
            formData.append('hdr', document.getElementById('hdrEnhancement').checked);
            formData.append('skin', document.getElementById('skinTone').checked);
            formData.append('lighting', document.getElementById('studioLighting').checked);
            formData.append('color', document.getElementById('colorCorrection').checked);
            formData.append('preserve_face', document.getElementById('preserveFace').checked);
        }
        
        const response = await fetch('/process-all', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentImageData = data.image;
            processedImage.src = currentImageData;
            showSuccess('All processing completed successfully!');
        } else {
            showError(data.error || 'Failed to process image');
        }
    } catch (error) {
        showError('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function resetImage() {
    if (originalImageData) {
        currentImageData = originalImageData;
        processedImage.src = currentImageData;
        showSuccess('Image reset to original');
    }
}

function downloadImage() {
    if (!currentImageData) return;
    
    const link = document.createElement('a');
    link.href = currentImageData;
    link.download = 'enhanced_portrait_' + Date.now() + '.png';
    link.click();
    
    showSuccess('Image downloaded!');
}

// Utility Functions
function showLoading(show) {
    if (show) {
        loadingOverlay.classList.add('active');
    } else {
        loadingOverlay.classList.remove('active');
    }
}

function showError(message) {
    alert('❌ ' + message);
}

function showSuccess(message) {
    // Simple success notification (could be enhanced with a toast notification)
    console.log('✅ ' + message);
}
