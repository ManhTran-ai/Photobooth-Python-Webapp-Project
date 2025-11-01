/**
 * Minimal JavaScript for camera access
 * All image processing (flipping, filters) is handled by Python backend
 */

// Minimal camera handler - only handles browser camera API
document.addEventListener("DOMContentLoaded", () => {
  if (!document.getElementById("video")) return;

  const video = document.getElementById("video");
  const canvas = document.getElementById("canvas");
  const ctx = canvas.getContext("2d");
  let stream = null;
  let facingMode = "user"; // 'user' for front camera, 'environment' for back camera

  // Get buttons
  const startBtn = document.getElementById("start-camera");
  const captureBtn = document.getElementById("capture");
  const toggleBtn = document.getElementById("toggle-camera");
  const closeBtn = document.getElementById("close-camera");

  // Start camera
  async function startCamera() {
    try {
      const constraints = {
        video: {
          facingMode: facingMode,
          width: { ideal: 640 },
          height: { ideal: 480 },
        },
      };

      stream = await navigator.mediaDevices.getUserMedia(constraints);
      video.srcObject = stream;

      // Show camera section
      const cameraSection = document.getElementById("camera-section");
      if (cameraSection) {
        cameraSection.style.display = "block";
        cameraSection.scrollIntoView({ behavior: "smooth" });
      }

      // Hide hero buttons
      const heroButtons = document.querySelector(".hero-buttons");
      if (heroButtons) heroButtons.style.display = "none";

      // Update start button
      if (startBtn) {
        startBtn.innerHTML = '<div class="loading"></div> Đang khởi động...';
        startBtn.disabled = true;
      }

      video.onloadedmetadata = () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Fix mirroring: Flip video preview for front camera (CSS only)
        if (facingMode === "user") {
          video.style.transform = "scaleX(-1)";
        } else {
          video.style.transform = "scaleX(1)";
        }

        if (startBtn) {
          startBtn.innerHTML = '<i class="icon">📷</i> Bắt đầu chụp ảnh';
          startBtn.disabled = false;
        }
      };
    } catch (error) {
      console.error("Camera error:", error);
      showNotification("Không thể truy cập camera. Vui lòng kiểm tra quyền truy cập.", "error");
    }
  }

  // Capture photo - send to Python backend for processing
  function capturePhoto() {
    if (!video.videoWidth || !video.videoHeight) {
      showNotification("Camera chưa sẵn sàng. Vui lòng thử lại.", "error");
      return;
    }

    // Draw video frame to canvas (no flipping - Python will handle it)
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Get selected filter
    const activeFilter = document.querySelector(".filter-btn.active");
    const filterName = activeFilter ? activeFilter.dataset.filter : "none";

    // Convert to blob and send to Python backend
    canvas.toBlob(
      async (blob) => {
        try {
          const formData = new FormData();
          formData.append("photo", blob, "captured-photo.jpg");
          formData.append("filter", filterName);
          formData.append("flip", facingMode === "user" ? "true" : "false"); // Tell Python to flip if front camera

          const response = await fetch("/api/upload", {
            method: "POST",
            body: formData,
          });

          if (!response.ok) {
            throw new Error("Upload failed");
          }

          const result = await response.json();
          showNotification("Ảnh đã được chụp và lưu thành công!", "success");
          
          // Optionally reload gallery or redirect
          setTimeout(() => {
            window.location.href = "/gallery";
          }, 2000);
        } catch (error) {
          console.error("Upload error:", error);
          showNotification("Lỗi khi lưu ảnh. Vui lòng thử lại.", "error");
        }
      },
      "image/jpeg",
      0.9
    );
  }

  // Toggle between front and back camera
  function toggleCamera() {
    facingMode = facingMode === "user" ? "environment" : "user";
    closeCamera();
    setTimeout(() => startCamera(), 100);
  }

  // Close camera
  function closeCamera() {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      stream = null;
    }

    if (video) {
      video.srcObject = null;
    }

    const cameraSection = document.getElementById("camera-section");
    if (cameraSection) cameraSection.style.display = "none";

    const heroButtons = document.querySelector(".hero-buttons");
    if (heroButtons) heroButtons.style.display = "flex";

    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // Filter button handlers
  document.querySelectorAll(".filter-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
      e.target.classList.add("active");
    });
  });

  // Bind events
  if (startBtn) startBtn.addEventListener("click", startCamera);
  if (captureBtn) captureBtn.addEventListener("click", capturePhoto);
  if (toggleBtn) toggleBtn.addEventListener("click", toggleCamera);
  if (closeBtn) closeBtn.addEventListener("click", closeCamera);

  // Notification function (simple version)
  function showNotification(message, type = "info") {
    const existing = document.querySelector(".notification");
    if (existing) existing.remove();

    const notification = document.createElement("div");
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <div class="notification-content">
        <span class="notification-icon">${type === "error" ? "❌" : type === "success" ? "✅" : "ℹ️"}</span>
        <span class="notification-message">${message}</span>
        <button class="notification-close">&times;</button>
      </div>
    `;

    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: ${type === "error" ? "#ff4757" : type === "success" ? "#2ed573" : "#3742fa"};
      color: white;
      padding: 1rem 1.5rem;
      border-radius: 10px;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
      z-index: 10000;
      max-width: 400px;
      animation: slideInRight 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
      if (notification.parentNode) {
        notification.style.animation = "slideOutRight 0.3s ease";
        setTimeout(() => notification.remove(), 300);
      }
    }, 5000);

    notification.querySelector(".notification-close").addEventListener("click", () => {
      notification.style.animation = "slideOutRight 0.3s ease";
      setTimeout(() => notification.remove(), 300);
    });
  }
});

// Add CSS for notifications (injected via JavaScript to keep it simple)
const style = document.createElement("style");
style.textContent = `
  @keyframes slideInRight {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  @keyframes slideOutRight {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
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
document.head.appendChild(style);
