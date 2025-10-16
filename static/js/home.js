// Home page functionality
class HomePage {
  constructor() {
    this.init();
  }

  init() {
    this.loadRecentPhotos();
    this.setupScrollAnimations();
    this.setupIntersectionObserver();
  }

  async loadRecentPhotos() {
    try {
      const response = await fetch("/api/recent-photos");
      if (response.ok) {
        const photos = await response.json();
        this.displayRecentPhotos(photos);
      } else {
        console.log("Không thể tải ảnh gần đây");
      }
    } catch (error) {
      console.error("Lỗi khi tải ảnh gần đây:", error);
    }
  }

  displayRecentPhotos(photos) {
    const container = document.getElementById("recent-photos");
    if (!container) return;

    if (photos.length === 0) {
      container.innerHTML = `
                <div class="no-photos">
                    <div class="no-photos-icon">📷</div>
                    <p>Chưa có ảnh nào. Hãy chụp ảnh đầu tiên của bạn!</p>
                </div>
            `;
      return;
    }

    const photosHTML = photos
      .slice(0, 6)
      .map(
        (photo) => `
            <div class="photo-item" onclick="this.viewPhoto('${photo.id}')">
                <img src="${photo.thumbnail_url || photo.url}" 
                     alt="Ảnh gần đây" 
                     loading="lazy"
                     onerror="this.src='/static/images/placeholder.jpg'">
                <div class="photo-overlay">
                    <span class="photo-date">${this.formatDate(
                      photo.created_at
                    )}</span>
                </div>
            </div>
        `
      )
      .join("");

    container.innerHTML = photosHTML;

    // Add fade-in animation
    container.querySelectorAll(".photo-item").forEach((item, index) => {
      item.style.animationDelay = `${index * 0.1}s`;
      item.classList.add("fade-in");
    });
  }

  viewPhoto(photoId) {
    // Open photo in modal or navigate to gallery
    window.open(`/gallery?photo=${photoId}`, "_blank");
  }

  formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return "Hôm qua";
    if (diffDays < 7) return `${diffDays} ngày trước`;
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} tuần trước`;

    return date.toLocaleDateString("vi-VN");
  }

  setupScrollAnimations() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener("click", function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute("href"));
        if (target) {
          target.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
        }
      });
    });
  }

  setupIntersectionObserver() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: "0px 0px -50px 0px",
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("animate-in");
        }
      });
    }, observerOptions);

    // Observe feature cards
    document.querySelectorAll(".feature-card").forEach((card) => {
      observer.observe(card);
    });

    // Observe section headings
    document.querySelectorAll("section h2").forEach((heading) => {
      observer.observe(heading);
    });
  }

  // Utility method for showing loading states
  showLoading(element, text = "Đang tải...") {
    if (element) {
      const originalContent = element.innerHTML;
      element.innerHTML = `<div class="loading"></div> ${text}`;
      element.disabled = true;

      return () => {
        element.innerHTML = originalContent;
        element.disabled = false;
      };
    }
  }

  // Handle responsive navigation
  setupMobileNavigation() {
    const nav = document.querySelector("nav");
    if (!nav) return;

    // Add mobile menu toggle if screen is small
    if (window.innerWidth <= 768) {
      const menuToggle = document.createElement("button");
      menuToggle.className = "mobile-menu-toggle";
      menuToggle.innerHTML = "☰";
      menuToggle.style.cssText = `
                display: none;
                background: none;
                border: none;
                font-size: 1.5rem;
                color: #667eea;
                cursor: pointer;
            `;

      const navContainer = nav.querySelector(".container");
      if (navContainer) {
        navContainer.appendChild(menuToggle);

        menuToggle.addEventListener("click", () => {
          const navList = nav.querySelector("ul");
          if (navList) {
            navList.classList.toggle("mobile-open");
          }
        });
      }
    }
  }
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.homePage = new HomePage();
});

// Handle window resize
window.addEventListener("resize", () => {
  if (window.homePage) {
    window.homePage.setupMobileNavigation();
  }
});

// Add CSS for animations and mobile styles
const homeStyles = `
.animate-in {
    animation: fadeInUp 0.6s ease forwards;
}

.no-photos {
    grid-column: 1 / -1;
    text-align: center;
    padding: 3rem;
    color: #666;
}

.no-photos-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.5;
}

.photo-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
    color: white;
    padding: 1rem;
    transform: translateY(100%);
    transition: transform 0.3s ease;
}

.photo-item {
    position: relative;
    overflow: hidden;
    cursor: pointer;
}

.photo-item:hover .photo-overlay {
    transform: translateY(0);
}

.photo-date {
    font-size: 0.9rem;
    opacity: 0.9;
}

@media (max-width: 768px) {
    nav ul.mobile-open {
        display: flex !important;
        flex-direction: column;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    nav ul {
        display: none;
    }
    
    .mobile-menu-toggle {
        display: block !important;
    }
}

/* Additional animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Parallax effect for hero section */
.hero {
    background-attachment: fixed;
    background-position: center;
    background-repeat: no-repeat;
    background-size: cover;
}

/* Hover effects for buttons */
.btn {
    position: relative;
    overflow: hidden;
}

.btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s;
}

.btn:hover::before {
    left: 100%;
}

/* Loading spinner */
.loading {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}
`;

const homeStyleSheet = document.createElement("style");
homeStyleSheet.textContent = homeStyles;
document.head.appendChild(homeStyleSheet);
