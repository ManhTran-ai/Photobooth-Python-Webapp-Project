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
        // Attempt to start camera immediately; if it fails we'll show a retry button
        this.startCamera().catch((err) => {
            // startCamera handles showing a helpful message; swallow here
            console.warn('Initial camera start failed:', err);
        });
    }

    initializeElements() {
        this.startBtn = document.getElementById('start-session-btn');
        this.captureBtn = document.getElementById('capture-btn');
        this.proceedBtn = document.getElementById('proceed-btn');
        this.backBtn = document.getElementById('back-btn');
        this.countdownOverlay = document.getElementById('countdown-overlay');
        this.countdownNumber = document.getElementById('countdown-number');
        this.countdownLabel = document.getElementById('countdown-label');
        this.delaySelect = document.getElementById('delay-select');
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
        this.enableCameraBtn = document.getElementById('enable-camera-btn');
        this.thumbList = document.getElementById('thumb-list');
    }

    initializeEventListeners() {
        if (this.startBtn) {
            this.startBtn.addEventListener('click', () => this.startSession());
        }

        if (this.captureBtn) {
            this.captureBtn.addEventListener('click', () => this.capturePhoto());
        }

        if (this.backBtn) {
            this.backBtn.addEventListener('click', () => window.location.href = '/');
        }

        if (this.confirmBtn) {
            this.confirmBtn.addEventListener('click', () => this.confirmPhoto());
        }

        if (this.retakeBtn) {
            this.retakeBtn.addEventListener('click', () => this.retakePhoto());
        }

        if (this.errorClose) {
            this.errorClose.addEventListener('click', () => this.hideError());
        }

        if (this.enableCameraBtn) {
            this.enableCameraBtn.addEventListener('click', () => {
                // user gesture to retry camera access
                this.startCamera().catch((err) => {
                    console.warn('Retry camera failed:', err);
                });
            });
        }
        if (this.proceedBtn) {
            this.proceedBtn.addEventListener('click', () => {
                // proceed to next page (session filters) only if session created
                if (this.sessionId) {
                    window.location.href = `/session/${this.sessionId}`;
                } else {
                    this.showError('Chưa có session. Vui lòng chụp ảnh trước.');
                }
            });
        }
    }

    async startCamera() {
        // Check support and secure context
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.handleCameraError(new Error('Camera API not supported on this browser.'));
            throw new Error('Camera API not supported');
        }

        if (!window.isSecureContext) {
            // getUserMedia is blocked on insecure origins; inform the user
            this.handleCameraError(new Error('Insecure context'));
            throw new Error('Insecure context for camera');
        }

        try {
            const constraints = {
                video: {
                    facingMode: 'user',
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                },
                audio: false
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

            // Hide any previous camera error
            this.hideError();
            return;
        } catch (error) {
            this.handleCameraError(error);
            throw error;
        }
    }

    handleCameraError(error) {
        console.error('Camera error handler:', error);
        // Friendly messages for common cases
        const name = error && error.name ? error.name : '';
        if (error.message && error.message.includes('Insecure context')) {
            this.showError('Trình duyệt chặn truy cập camera vì trang không an toàn. Vui lòng dùng HTTPS hoặc truy cập từ `localhost`.');
            this.showEnableCameraButton(true);
            return;
        }

        switch (name) {
            case 'NotAllowedError':
            case 'PermissionDeniedError':
                this.showError('Quyền truy cập camera bị từ chối. Vui lòng cho phép camera trong trình duyệt và thử lại.');
                break;
            case 'NotFoundError':
            case 'DevicesNotFoundError':
                this.showError('Không tìm thấy camera trên thiết bị này.');
                break;
            case 'NotReadableError':
            case 'TrackStartError':
                this.showError('Không thể mở camera — có thể đang được sử dụng bởi ứng dụng khác.');
                break;
            default:
                this.showError('Không thể truy cập camera. Vui lòng kiểm tra quyền/thiết bị và thử lại.');
                break;
        }

        // Show retry button so user can trigger a gesture to re-request permission
        this.showEnableCameraButton(true);
    }

    showEnableCameraButton(visible = true) {
        if (!this.enableCameraBtn) {
            // try to create a small retry button near controls
            const controlsRow = document.querySelector('.controls-row') || document.querySelector('.top-controls');
            if (controlsRow) {
                const btn = document.createElement('button');
                btn.id = 'enable-camera-btn';
                btn.className = 'btn btn-outline';
                btn.textContent = 'Bật camera';
                btn.style.marginLeft = '8px';
                controlsRow.appendChild(btn);
                this.enableCameraBtn = btn;
                this.enableCameraBtn.addEventListener('click', () => {
                    this.startCamera().catch((err) => {
                        console.warn('Retry camera failed:', err);
                    });
                });
            }
        } else {
            this.enableCameraBtn.style.display = visible ? 'inline-flex' : 'none';
        }
    }

    async startSession() {
        // Create new session
        try {
            console.log('Creating session...');
            const response = await fetch('/api/sessions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            let data = null;
            try {
                data = await response.json();
            } catch (parseErr) {
                console.warn('Failed to parse session response as JSON', parseErr);
            }

            if (!response.ok) {
                const serverMessage = (data && (data.error || data.message)) ? (data.error || data.message) : `HTTP ${response.status}`;
                throw new Error(`Failed to create session: ${serverMessage}`);
            }

            console.log('Session created', data);
            this.sessionId = data.session_id;
            this.currentPhoto = 0;
            this.capturedPhotos = [];
            this.isCapturing = true;

            // Hide start button, show capture button (if present)
            if (this.startBtn) this.startBtn.style.display = 'none';
            if (this.captureBtn) this.captureBtn.style.display = 'block';

            // Start first photo capture
            this.captureNextPhoto();
        } catch (error) {
            console.error('Session creation error:', error);
            // Show more helpful message if available
            const message = error && error.message ? error.message : 'Failed to start session. Please try again.';
            this.showError(message);
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
        // Determine delay from select (0,3,5). Default to 3 if missing.
        let delay = 3;
        try {
            if (this.delaySelect && this.delaySelect.value !== undefined) {
                delay = parseInt(this.delaySelect.value, 10) || 0;
            }
        } catch (e) { /* ignore */ }

        if (delay === 0) {
            // immediate capture
            this.triggerCapture();
        } else {
            this.showCountdown(delay);
        }
    }

    updateProgress() {
        const progress = (this.currentPhoto / this.totalPhotos) * 100;
        if (this.progressFill) {
            this.progressFill.style.width = `${progress}%`;
        }
        if (this.progressText) {
            this.progressText.textContent = `Photo ${this.currentPhoto}/${this.totalPhotos}`;
        }
    }

    showCountdown(seconds = 3) {
        if (!this.countdownOverlay || !this.countdownNumber) {
            // Fallback: trigger immediate capture if countdown elements missing
            this.triggerCapture();
            return;
        }

        // Clear any previous countdown
        if (this._countdownInterval) {
            clearInterval(this._countdownInterval);
            this._countdownInterval = null;
        }

        this.countdownOverlay.style.display = 'flex';
        if (this.countdownLabel) this.countdownLabel.textContent = `Photo ${this.currentPhoto}/${this.totalPhotos}`;
        
        let count = parseInt(seconds, 10) || 3;
        this.countdownNumber.textContent = count;

        this._countdownInterval = setInterval(() => {
            count--;
            if (count > 0) {
                this.countdownNumber.textContent = count;
            } else {
                this.countdownNumber.textContent = '📸';
                clearInterval(this._countdownInterval);
                this._countdownInterval = null;
                
                setTimeout(() => {
                    if (this.countdownOverlay) this.countdownOverlay.style.display = 'none';
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
            // Add thumbnail into right panel
            this.addThumbnailToPanel(data);
            // Show preview modal for user to confirm or retake
            this.showPreview(data);
            // If we've captured all photos, enable proceed button
            if (this.capturedPhotos.length >= this.totalPhotos) {
                if (this.proceedBtn) this.proceedBtn.style.display = 'inline-flex';
            }

        } catch (error) {
            console.error('Upload error:', error);
            this.hideLoading();
            this.showError(`Failed to save photo: ${error.message}`);
        }
    }

    addThumbnailToPanel(photoData) {
        if (!this.thumbList) return;
        // Find first empty thumb
        const emptyThumb = this.thumbList.querySelector('.thumb.empty');
        if (!emptyThumb) {
            // If none empty, append at end
            const thumb = document.createElement('div');
            thumb.className = 'thumb';
            const img = document.createElement('img');
            img.src = photoData.thumbnail_url || photoData.processed_url || photoData.original_url || '';
            thumb.appendChild(img);
            this.thumbList.appendChild(thumb);
            return;
        }
        emptyThumb.classList.remove('empty');
        // replace content with image
        emptyThumb.innerHTML = '';
        const img = document.createElement('img');
        img.src = photoData.thumbnail_url || photoData.processed_url || photoData.original_url || '';
        emptyThumb.appendChild(img);
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

