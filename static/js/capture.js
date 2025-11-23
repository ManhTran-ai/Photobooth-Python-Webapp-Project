/**
 * Capture interface for 4-photo sequence
 */
class PhotoCapture {
    constructor() {
        this.video = document.getElementById('video');
        this.canvas = document.getElementById('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.stream = null;
        this.sessionId = null;
        this.currentPhoto = 0;
        this.totalPhotos = 4;
        this.capturedPhotos = [];
        this.isCapturing = false;
        
        this.initializeElements();
        this.initializeEventListeners();
        this.startCamera();
    }

    initializeElements() {
        this.startBtn = document.getElementById('start-session-btn');
        this.captureBtn = document.getElementById('capture-btn');
        this.backBtn = document.getElementById('back-btn');
        this.countdownOverlay = document.getElementById('countdown-overlay');
        this.countdownNumber = document.getElementById('countdown-number');
        this.countdownLabel = document.getElementById('countdown-label');
        this.flashEffect = document.getElementById('flash-effect');
        this.previewModal = document.getElementById('preview-modal');
        this.previewImage = document.getElementById('preview-image');
        this.previewTitle = document.getElementById('preview-title');
        this.confirmBtn = document.getElementById('confirm-btn');
        this.retakeBtn = document.getElementById('retake-btn');
        this.progressFill = document.getElementById('progress-fill');
        this.progressText = document.getElementById('progress-text');
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.loadingText = document.getElementById('loading-text');
        this.errorMessage = document.getElementById('error-message');
        this.errorText = document.getElementById('error-text');
        this.errorClose = document.getElementById('error-close');
    }

    initializeEventListeners() {
        this.startBtn.addEventListener('click', () => this.startSession());
        this.captureBtn.addEventListener('click', () => this.capturePhoto());
        this.backBtn.addEventListener('click', () => window.location.href = '/');
        this.confirmBtn.addEventListener('click', () => this.confirmPhoto());
        this.retakeBtn.addEventListener('click', () => this.retakePhoto());
        this.errorClose.addEventListener('click', () => this.hideError());
    }

    async startCamera() {
        try {
            const constraints = {
                video: {
                    facingMode: 'user',
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            };

            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = this.stream;

            this.video.onloadedmetadata = () => {
                this.canvas.width = this.video.videoWidth;
                this.canvas.height = this.video.videoHeight;
                // Mirror video for front camera
                this.video.style.transform = 'scaleX(-1)';
                
                // Adjust video wrapper aspect ratio to match video stream
                this.adjustVideoWrapperAspectRatio();
            };
        } catch (error) {
            console.error('Camera error:', error);
            this.showError('Could not access camera. Please check permissions and try again.');
        }
    }

    async startSession() {
        // Create new session
        try {
            const response = await fetch('/api/sessions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Failed to create session');

            const data = await response.json();
            this.sessionId = data.session_id;
            this.currentPhoto = 0;
            this.capturedPhotos = [];
            this.isCapturing = true;

            // Hide start button, show capture button
            this.startBtn.style.display = 'none';
            this.captureBtn.style.display = 'block';

            // Start first photo capture
            this.captureNextPhoto();
        } catch (error) {
            console.error('Session creation error:', error);
            this.showError('Failed to start session. Please try again.');
        }
    }

    captureNextPhoto() {
        if (this.currentPhoto >= this.totalPhotos) {
            // All photos captured, redirect to filter selection
            this.redirectToFilters();
            return;
        }

        this.currentPhoto++;
        this.updateProgress();
        this.showCountdown();
    }

    updateProgress() {
        const progress = (this.currentPhoto / this.totalPhotos) * 100;
        this.progressFill.style.width = `${progress}%`;
        this.progressText.textContent = `Photo ${this.currentPhoto}/${this.totalPhotos}`;
    }

    showCountdown() {
        this.countdownOverlay.style.display = 'flex';
        this.countdownLabel.textContent = `Photo ${this.currentPhoto}/${this.totalPhotos}`;
        
        let count = 3;
        this.countdownNumber.textContent = count;

        const countdownInterval = setInterval(() => {
            count--;
            if (count > 0) {
                this.countdownNumber.textContent = count;
            } else {
                this.countdownNumber.textContent = '📸';
                clearInterval(countdownInterval);
                
                setTimeout(() => {
                    this.countdownOverlay.style.display = 'none';
                    this.triggerCapture();
                }, 500);
            }
        }, 1000);
    }

    triggerCapture() {
        // Draw video frame to canvas (mirror will be handled by backend)
        this.ctx.save();
        this.ctx.scale(-1, 1);
        this.ctx.drawImage(this.video, -this.canvas.width, 0, this.canvas.width, this.canvas.height);
        this.ctx.restore();

        // Flash effect
        this.flashEffect.style.display = 'block';
        setTimeout(() => {
            this.flashEffect.style.display = 'none';
        }, 300);

        // Convert to base64 and send to backend
        const imageData = this.canvas.toDataURL('image/jpeg', 0.9);
        this.sendPhotoToBackend(imageData);
    }

    async sendPhotoToBackend(imageData) {
        this.showLoading('Saving photo...');

        try {
            // Convert base64 to blob
            const base64Data = imageData.split(',')[1];
            const byteCharacters = atob(base64Data);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: 'image/jpeg' });

            const formData = new FormData();
            formData.append('image', blob, 'photo.jpg');
            formData.append('session_id', this.sessionId);
            formData.append('photo_number', this.currentPhoto);

            const response = await fetch('/api/capture', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to save photo');
            }

            const data = await response.json();
            this.capturedPhotos.push(data);
            this.hideLoading();
            this.showPreview(data);

        } catch (error) {
            console.error('Upload error:', error);
            this.hideLoading();
            this.showError(`Failed to save photo: ${error.message}`);
        }
    }

    showPreview(photoData) {
        this.previewImage.src = photoData.thumbnail_url || photoData.original_url;
        this.previewTitle.textContent = `Photo ${this.currentPhoto}/${this.totalPhotos} Preview`;
        this.previewModal.style.display = 'flex';
    }

    confirmPhoto() {
        this.previewModal.style.display = 'none';
        
        if (this.currentPhoto < this.totalPhotos) {
            // Continue to next photo
            setTimeout(() => {
                this.captureNextPhoto();
            }, 500);
        } else {
            // All photos captured
            this.redirectToFilters();
        }
    }

    retakePhoto() {
        this.previewModal.style.display = 'none';
        // Retake current photo (same photo number)
        setTimeout(() => {
            this.showCountdown();
        }, 500);
    }

    redirectToFilters() {
        window.location.href = `/session/${this.sessionId}`;
    }

    showLoading(text = 'Processing...') {
        this.loadingText.textContent = text;
        this.loadingOverlay.style.display = 'flex';
    }

    hideLoading() {
        this.loadingOverlay.style.display = 'none';
    }

    showError(message) {
        this.errorText.textContent = message;
        this.errorMessage.style.display = 'block';
    }

    hideError() {
        this.errorMessage.style.display = 'none';
    }

    adjustVideoWrapperAspectRatio() {
        if (!this.video.videoWidth || !this.video.videoHeight) return;
        
        const videoWrapper = document.querySelector('.video-wrapper');
        if (!videoWrapper) return;
        
        // Calculate aspect ratio from video stream
        const videoAspectRatio = this.video.videoWidth / this.video.videoHeight;
        
        // Set the aspect ratio dynamically to match the video stream
        // This ensures the container matches the video's native aspect ratio
        videoWrapper.style.aspectRatio = `${this.video.videoWidth} / ${this.video.videoHeight}`;
        
        // Ensure video fills the container properly and is centered
        this.video.style.width = '100%';
        this.video.style.height = '100%';
        this.video.style.objectFit = 'cover';
        this.video.style.objectPosition = 'center';
        
        console.log(`Video aspect ratio adjusted: ${this.video.videoWidth}x${this.video.videoHeight} (${videoAspectRatio.toFixed(2)})`);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('video')) {
        new PhotoCapture();
    }
});

