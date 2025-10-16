// Camera functionality
class Camera {
  constructor() {
    this.video = document.getElementById("video");
    this.canvas = document.getElementById("canvas");
    this.ctx = this.canvas.getContext("2d");
    this.stream = null;
    this.currentFilter = "none";
    this.facingMode = "user"; // 'user' for front camera, 'environment' for back camera

    this.init();
  }

  init() {
    this.bindEvents();
    this.setupFilters();
  }

  bindEvents() {
    const startBtn = document.getElementById("start-camera");
    const captureBtn = document.getElementById("capture");
    const toggleBtn = document.getElementById("toggle-camera");
    const closeBtn = document.getElementById("close-camera");

    if (startBtn) startBtn.addEventListener("click", () => this.startCamera());
    if (captureBtn)
      captureBtn.addEventListener("click", () => this.capturePhoto());
    if (toggleBtn)
      toggleBtn.addEventListener("click", () => this.toggleCamera());
    if (closeBtn) closeBtn.addEventListener("click", () => this.closeCamera());

    // Filter buttons
    document.querySelectorAll(".filter-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        this.setFilter(e.target.dataset.filter);
        this.updateFilterButtons(e.target);
      });
    });
  }

  async startCamera() {
    try {
      const constraints = {
        video: {
          facingMode: this.facingMode,
          width: { ideal: 640 },
          height: { ideal: 480 },
        },
      };

      this.stream = await navigator.mediaDevices.getUserMedia(constraints);
      this.video.srcObject = this.stream;

      // Show camera section
      const cameraSection = document.getElementById("camera-section");
      if (cameraSection) {
        cameraSection.style.display = "block";
        cameraSection.scrollIntoView({ behavior: "smooth" });
      }

      // Hide hero buttons
      const heroButtons = document.querySelector(".hero-buttons");
      if (heroButtons) {
        heroButtons.style.display = "none";
      }

      // Update button text
      const startBtn = document.getElementById("start-camera");
      if (startBtn) {
        startBtn.innerHTML = '<div class="loading"></div> Đang khởi động...';
        startBtn.disabled = true;
      }

      this.video.onloadedmetadata = () => {
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;

        if (startBtn) {
          startBtn.innerHTML = '<i class="icon">📷</i> Bắt đầu chụp ảnh';
          startBtn.disabled = false;
        }
      };
    } catch (error) {
      console.error("Lỗi khi khởi động camera:", error);
      this.showError(
        "Không thể truy cập camera. Vui lòng kiểm tra quyền truy cập."
      );
    }
  }

  capturePhoto() {
    if (!this.video.videoWidth || !this.video.videoHeight) {
      this.showError("Camera chưa sẵn sàng. Vui lòng thử lại.");
      return;
    }

    // Draw video frame to canvas
    this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);

    // Apply current filter
    this.applyFilter(this.ctx);

    // Convert to blob and send to server
    this.canvas.toBlob(
      async (blob) => {
        try {
          await this.uploadPhoto(blob);
          this.showSuccess("Ảnh đã được chụp và lưu thành công!");
        } catch (error) {
          console.error("Lỗi khi upload ảnh:", error);
          this.showError("Lỗi khi lưu ảnh. Vui lòng thử lại.");
        }
      },
      "image/jpeg",
      0.9
    );
  }

  async uploadPhoto(blob) {
    const formData = new FormData();
    formData.append("photo", blob, "captured-photo.jpg");

    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Upload failed");
    }

    return await response.json();
  }

  toggleCamera() {
    this.facingMode = this.facingMode === "user" ? "environment" : "user";
    this.closeCamera();
    setTimeout(() => this.startCamera(), 100);
  }

  closeCamera() {
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }

    if (this.video) {
      this.video.srcObject = null;
    }

    // Hide camera section
    const cameraSection = document.getElementById("camera-section");
    if (cameraSection) {
      cameraSection.style.display = "none";
    }

    // Show hero buttons
    const heroButtons = document.querySelector(".hero-buttons");
    if (heroButtons) {
      heroButtons.style.display = "flex";
    }

    // Scroll to top
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  setupFilters() {
    this.filters = {
      none: () => {},
      sepia: (ctx) => {
        const imageData = ctx.getImageData(
          0,
          0,
          this.canvas.width,
          this.canvas.height
        );
        const data = imageData.data;

        for (let i = 0; i < data.length; i += 4) {
          const r = data[i];
          const g = data[i + 1];
          const b = data[i + 2];

          data[i] = Math.min(255, r * 0.393 + g * 0.769 + b * 0.189);
          data[i + 1] = Math.min(255, r * 0.349 + g * 0.686 + b * 0.168);
          data[i + 2] = Math.min(255, r * 0.272 + g * 0.534 + b * 0.131);
        }

        ctx.putImageData(imageData, 0, 0);
      },
      grayscale: (ctx) => {
        const imageData = ctx.getImageData(
          0,
          0,
          this.canvas.width,
          this.canvas.height
        );
        const data = imageData.data;

        for (let i = 0; i < data.length; i += 4) {
          const gray =
            data[i] * 0.299 + data[i + 1] * 0.587 + data[i + 2] * 0.114;
          data[i] = gray;
          data[i + 1] = gray;
          data[i + 2] = gray;
        }

        ctx.putImageData(imageData, 0, 0);
      },
      vintage: (ctx) => {
        ctx.filter = "contrast(1.1) brightness(0.9) saturate(0.8) sepia(0.3)";
        ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
        ctx.filter = "none";
      },
      bright: (ctx) => {
        ctx.filter = "brightness(1.2) contrast(1.1)";
        ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
        ctx.filter = "none";
      },
      contrast: (ctx) => {
        ctx.filter = "contrast(1.3) saturate(1.2)";
        ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
        ctx.filter = "none";
      },
    };
  }

  applyFilter(ctx) {
    if (this.filters[this.currentFilter]) {
      this.filters[this.currentFilter](ctx);
    }
  }

  setFilter(filterName) {
    this.currentFilter = filterName;
  }

  updateFilterButtons(activeBtn) {
    document.querySelectorAll(".filter-btn").forEach((btn) => {
      btn.classList.remove("active");
    });
    activeBtn.classList.add("active");
  }

  showError(message) {
    this.showNotification(message, "error");
  }

  showSuccess(message) {
    this.showNotification(message, "success");
  }

  showNotification(message, type = "info") {
    // Remove existing notifications
    const existing = document.querySelector(".notification");
    if (existing) existing.remove();

    const notification = document.createElement("div");
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${
                  type === "error" ? "❌" : type === "success" ? "✅" : "ℹ️"
                }</span>
                <span class="notification-message">${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;

    // Add styles
    notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${
              type === "error"
                ? "#ff4757"
                : type === "success"
                ? "#2ed573"
                : "#3742fa"
            };
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            z-index: 10000;
            max-width: 400px;
            animation: slideInRight 0.3s ease;
        `;

    document.body.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.style.animation = "slideOutRight 0.3s ease";
        setTimeout(() => notification.remove(), 300);
      }
    }, 5000);

    // Close button
    notification
      .querySelector(".notification-close")
      .addEventListener("click", () => {
        notification.style.animation = "slideOutRight 0.3s ease";
        setTimeout(() => notification.remove(), 300);
      });
  }
}

// Initialize camera when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("video")) {
    window.camera = new Camera();
  }
});

// Add CSS for notifications
const notificationStyles = `
@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes slideOutRight {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}

.notification-content {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.notification-close {
    background: none;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    margin-left: auto;
    opacity: 0.7;
    transition: opacity 0.3s ease;
}

.notification-close:hover {
    opacity: 1;
}
`;

const styleSheet = document.createElement("style");
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);
