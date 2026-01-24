class FilterSelectionPage {
    constructor() {
        this.sessionId = typeof SESSION_ID !== 'undefined' ? SESSION_ID : null;
        if (!this.sessionId) {
            return;
        }

        this.photos = [];
        this.filters = [];
        this.filterCache = new Map();
        this.activeCategory = 'all';
        this.selectedFilter = null;
        this.selectedFilterMeta = null;
        this.comparisonEnabled = false;
        this.comparePercent = 50;
        this.isApplying = false;

        this.elements = {
            photosGrid: document.getElementById('photos-grid'),
            filtersList: document.getElementById('filters-list'),
            categoryTabs: document.querySelectorAll('.category-tab'),
            toggleComparison: document.getElementById('toggle-comparison'),
            comparisonSlider: document.getElementById('comparison-slider'),
            comparisonSliderWrapper: document.getElementById('comparison-slider-wrapper'),
            comparisonValue: document.getElementById('comparison-value'),
            comparisonHint: document.getElementById('comparison-hint'),
            loadingOverlay: document.getElementById('loading-overlay'),
            loadingText: document.getElementById('loading-text'),
            applyButton: document.getElementById('apply-filter-btn')
        };

        this.initialize();
    }

    async initialize() {
        try {
            await Promise.all([this.loadPhotos(), this.loadFilters()]);
            this.filterCache.set('none', this.photos);
            this.renderPhotos(this.photos);
            this.renderFilterCards();
            this.bindEvents();
            this.updateApplyButton();
        } catch (error) {
            console.error('Failed to initialize filter page', error);
            alert('Unable to load session data. Please refresh the page.');
        }
    }

    bindEvents() {
        this.elements.categoryTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                this.elements.categoryTabs.forEach(btn => btn.classList.remove('active'));
                tab.classList.add('active');
                this.activeCategory = tab.dataset.category;
                this.renderFilterCards();
            });
        });

        if (this.elements.toggleComparison) {
            this.elements.toggleComparison.addEventListener('click', () => this.toggleComparison());
        }

        if (this.elements.comparisonSlider) {
            this.elements.comparisonSlider.addEventListener('input', (event) => {
                this.updateComparisonPercent(event.target.value);
            });
        }

        if (this.elements.applyButton) {
            this.elements.applyButton.addEventListener('click', () => this.confirmFilterSelection());
        }
    }

    async loadPhotos() {
        const response = await fetch(`/api/sessions/${this.sessionId}/photos`);
        if (!response.ok) {
            throw new Error('Could not load session photos');
        }
        const data = await response.json();
        this.photos = (data.photos || []).map(photo => ({
            ...photo,
            photo_number: photo.photo_number || 0
        }));
        this.photoIds = this.photos.map(photo => photo.id);
    }

    async loadFilters() {
        const response = await fetch('/api/filters');
        if (!response.ok) {
            throw new Error('Could not load filter list');
        }
        const data = await response.json();
        this.filters = data.filters || [];
    }

    renderFilterCards() {
        if (!this.elements.filtersList) return;
        this.elements.filtersList.innerHTML = '';

        const filtersToShow = this.activeCategory === 'all'
            ? this.filters
            : this.filters.filter(filter => filter.category === this.activeCategory);

        filtersToShow.forEach(filter => {
            const card = document.createElement('div');
            card.className = 'filter-card';
            card.tabIndex = 0;
            card.dataset.filter = filter.name;

            if (filter.name === this.selectedFilter) {
                card.classList.add('active');
            }

            card.innerHTML = `
                <div class="filter-preview">
                    ${filter.example_thumbnail
                        ? `<img src="${filter.example_thumbnail}" alt="${filter.display_name} preview">`
                        : `<span>${filter.display_name}</span>`}
                </div>
                <div class="filter-name">${filter.display_name}</div>
                <div class="filter-description">${filter.description || ''}</div>
            `;

            card.addEventListener('click', () => this.handleFilterSelection(filter));
            card.addEventListener('keypress', (event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    this.handleFilterSelection(filter);
                }
            });

            this.elements.filtersList.appendChild(card);
        });
    }

    renderPhotos(photoSet) {
        if (!this.elements.photosGrid) return;
        const photos = photoSet || this.photos;
        this.elements.photosGrid.innerHTML = '';
        const orderedPhotos = [...photos].sort((a, b) => a.photo_number - b.photo_number);

        orderedPhotos.forEach(photo => {
            const card = document.createElement('div');
            card.className = 'photo-card';
            if (this.comparisonEnabled) {
                card.classList.add('comparison-enabled');
            }
            card.style.setProperty('--comparison-percent', `${this.comparePercent}%`);

            const filteredUrl = photo.processed_url || photo.original_url;

            card.innerHTML = `
                <div class="photo-layer photo-original">
                    <img src="${photo.original_url}" alt="Original photo ${photo.photo_number}">
                </div>
                <div class="photo-filtered">
                    <img src="${filteredUrl}" alt="Filtered photo ${photo.photo_number}">
                </div>
                <div class="photo-label">Photo ${photo.photo_number}</div>
            `;

            this.elements.photosGrid.appendChild(card);
        });
    }

    handleFilterSelection(filter) {
        if (this.isApplying) return;
        this.selectedFilter = filter.name;
        this.selectedFilterMeta = filter;
        this.setActiveFilterCard(filter.name);
        this.updateApplyButton();

        if (filter.name === 'none') {
            this.renderPhotos(this.photos);
            return;
        }

        this.previewFilter(filter.name);
    }

    setActiveFilterCard(filterName) {
        document.querySelectorAll('.filter-card').forEach(card => {
            card.classList.toggle('active', card.dataset.filter === filterName);
        });
    }

    async previewFilter(filterName) {
        if (this.filterCache.has(filterName)) {
            const cached = this.filterCache.get(filterName);
            this.renderPhotos(cached);
            return;
        }
        await this.applyFilterRequest(filterName, false);
    }

    async confirmFilterSelection() {
        if (!this.selectedFilter || this.isApplying) return;
        await this.applyFilterRequest(this.selectedFilter, true);
    }

    async applyFilterRequest(filterName, commit) {
        if (!this.photoIds || this.photoIds.length === 0) return;

        this.isApplying = true;
        this.updateApplyButton();
        const humanName = this.getFilterDisplayName(filterName);
        this.showLoading(`Applying ${humanName} filter to ${this.photoIds.length} photos${commit ? '...' : ' for preview...'}`);

        try {
            const response = await fetch('/api/apply-filter', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    filter_name: filterName,
                    photo_ids: this.photoIds,
                    commit
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || 'Filter processing failed');
            }

            const data = await response.json();
            const ordered = (data.processed_images || []).sort((a, b) => a.photo_number - b.photo_number);
            this.filterCache.set(filterName, ordered);
            this.renderPhotos(filterName === 'none' ? this.photos : ordered);

            if (commit) {
                this.showLoading('Filter applied! Redirecting to gallery...');
                setTimeout(() => window.location.assign('/gallery'), 1200);
            } else {
                this.hideLoading();
            }
        } catch (error) {
            console.error('Filter apply failed', error);
            this.hideLoading();
            alert(error.message || 'Something went wrong while applying the filter.');
        } finally {
            this.isApplying = false;
            this.updateApplyButton();
        }
    }

    toggleComparison() {
        this.comparisonEnabled = !this.comparisonEnabled;
        if (this.elements.comparisonSliderWrapper) {
            this.elements.comparisonSliderWrapper.classList.toggle('active', this.comparisonEnabled);
        }
        if (this.elements.comparisonHint) {
            this.elements.comparisonHint.style.display = this.comparisonEnabled ? 'block' : 'none';
        }
        this.updateComparisonPercent(this.comparePercent);
        document.querySelectorAll('.photo-card').forEach(card => {
            card.classList.toggle('comparison-enabled', this.comparisonEnabled);
        });
    }

    updateComparisonPercent(value) {
        this.comparePercent = value;
        if (this.elements.comparisonValue) {
            this.elements.comparisonValue.textContent = `${value}%`;
        }
        document.querySelectorAll('.photo-card').forEach(card => {
            card.style.setProperty('--comparison-percent', `${value}%`);
        });
    }

    updateApplyButton() {
        if (!this.elements.applyButton) return;
        const shouldEnable = Boolean(this.selectedFilter) && !this.isApplying;
        this.elements.applyButton.disabled = !shouldEnable;
    }

    getFilterDisplayName(filterName) {
        const filter = this.filters.find(item => item.name === filterName);
        return filter ? filter.display_name : filterName;
    }

    showLoading(message) {
        if (!this.elements.loadingOverlay) return;
        this.elements.loadingText.textContent = message;
        this.elements.loadingOverlay.style.display = 'flex';
    }

    hideLoading() {
        if (!this.elements.loadingOverlay) return;
        this.elements.loadingOverlay.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('photos-grid')) {
        new FilterSelectionPage();
    }

    // AI Beauty Buttons
    initAIBeautyButtons();

    // Auto Sticker Buttons
    initAutoStickerButtons();
});

/**
 * Initialize AI Beauty filter buttons
 */
function initAIBeautyButtons() {
    const aiButtons = {
        'ai-smart-beauty': 'smart_beauty',
        'ai-face-glow': 'face_glow',
        'ai-portrait-pro': 'portrait_pro'
    };

    Object.entries(aiButtons).forEach(([buttonId, filterName]) => {
        const btn = document.getElementById(buttonId);
        if (btn) {
            btn.addEventListener('click', async () => {
                await applyAIFilter(filterName, btn);
            });
        }
    });
}

/**
 * Apply AI filter to session photos
 */
async function applyAIFilter(filterName, button) {
    const sessionId = getSessionId();
    if (!sessionId) {
        showNotification('Session không hợp lệ', 'error');
        return;
    }

    // Visual feedback
    const originalText = button.innerHTML;
    button.innerHTML = '⏳ Đang xử lý...';
    button.disabled = true;

    try {
        // Call API to apply filter
        const response = await fetch(`/api/apply-filter`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                filter_name: filterName,
                commit: false  // Preview mode
            })
        });

        // Check if response is OK before parsing JSON
        if (!response.ok) {
            const errorText = await response.text();
            console.error('API Error Response:', errorText);
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            // Refresh the preview
            if (typeof refreshCollagePreview === 'function') {
                refreshCollagePreview();
            }

            // Show success message
            showNotification(`✨ Đã áp dụng filter ${getFilterDisplayName(filterName)}`, 'success');
        } else {
            throw new Error(data.error || 'Failed to apply filter');
        }
    } catch (error) {
        console.error('AI Filter error:', error);
        showNotification('❌ Lỗi khi áp dụng filter: ' + error.message, 'error');
    } finally {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

/**
 * Initialize Auto Sticker buttons
 * Click: Gắn phụ kiện trực tiếp vào ảnh
 */
function initAutoStickerButtons() {
    const stickerButtons = document.querySelectorAll('.btn-auto-sticker');

    stickerButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const stickerType = btn.dataset.type;
            // Always bake into image (true) for simpler UX
            await autoPlaceSticker(stickerType, btn, true);
        });

        // Add hover effect
        btn.addEventListener('mouseenter', () => {
            btn.style.transform = 'scale(1.05)';
            btn.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
        });
        btn.addEventListener('mouseleave', () => {
            btn.style.transform = 'scale(1)';
            btn.style.boxShadow = 'none';
        });
    });
}

/**
 * Auto place sticker based on face detection
 * @param {string} stickerType - Type of sticker: 'hat', 'glasses', 'ears', 'mustache', 'noel_hat', 'bow'
 * @param {HTMLElement} button - Button element for visual feedback
 * @param {boolean} bakeIntoImage - If true, apply sticker directly to image files
 */
async function autoPlaceSticker(stickerType, button, bakeIntoImage = true) {
    const sessionId = getSessionId();
    if (!sessionId) {
        showNotification('Session không hợp lệ', 'error');
        return;
    }

    // Visual feedback
    const originalText = button.innerHTML;
    button.innerHTML = '⏳ Đang xử lý...';
    button.disabled = true;

    try {
        if (bakeIntoImage) {
            // Apply sticker directly to session photos using new API
            const response = await fetch('/api/apply-sticker-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    sticker_type: stickerType,
                    save: true
                })
            });

            const data = await response.json();

            if (data.success) {
                // Refresh the collage preview
                if (typeof refreshCollagePreview === 'function') {
                    refreshCollagePreview();
                }
                const displayName = STICKER_NAMES[stickerType] || stickerType;
                showNotification(`🎭 Đã gắn ${displayName} vào ${data.photos_with_faces} ảnh có khuôn mặt!`, 'success');
            } else {
                throw new Error(data.error || 'Failed to apply sticker');
            }
        } else {
            // Overlay mode - just show stickers on preview (existing behavior)
            const photosResponse = await fetch(`/api/sessions/${sessionId}/photos`);

            if (!photosResponse.ok) {
                throw new Error(`Server error: ${photosResponse.status}`);
            }

            const photosData = await photosResponse.json();

            if (!photosData.photos || photosData.photos.length === 0) {
                throw new Error('Không có ảnh trong session');
            }

            // Clear existing sticker overlays
            document.querySelectorAll('.auto-sticker-overlay').forEach(el => el.remove());

            // For each photo, detect face and get sticker positions
            for (const photo of photosData.photos) {
                const filename = photo.processed_filename || photo.original_filename;

                const response = await fetch(`/api/sticker-positions?sticker_type=${stickerType}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        filename: filename
                    })
                });

                const data = await response.json();

                if (data.success && data.positions && data.positions.length > 0) {
                    // Add stickers to collage preview at detected positions
                    data.positions.forEach(pos => {
                        addStickerToCollage(stickerType, pos.x, pos.y, pos.scale, filename);
                    });
                }
            }

            const displayName = STICKER_NAMES[stickerType] || stickerType;
            showNotification(`🎭 Đã thêm ${displayName} (preview)`, 'success');
        }

    } catch (error) {
        console.error('Auto sticker error:', error);
        showNotification('❌ Lỗi: ' + error.message, 'error');
    } finally {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// Mapping from sticker types to filenames in static/templates/
const STICKER_FILES = {
    'hat': 'hat-2.png',
    'glasses': 'glasses.png',
    'ears': 'rabbit_ears.png',
    'mustache': 'mustache.png',
    'noel_hat': 'noel-hat.png',
    'bow': 'No.png'
};

// Display names for sticker types
const STICKER_NAMES = {
    'hat': 'Mũ',
    'glasses': 'Kính',
    'ears': 'Tai thỏ',
    'mustache': 'Râu',
    'noel_hat': 'Nón Noel',
    'bow': 'Nơ'
};

/**
 * Add sticker overlay to the collage preview for a specific photo filename.
 * This function requests a processed (transparent) sticker from the server
 * and positions an absolutely positioned <img> over the matching photo preview.
 */
async function addStickerToCollage(stickerType, x, y, scale = 1.0, filename = null) {
    try {
        const stickerName = STICKER_FILES[stickerType] || STICKER_FILES['hat'];

        // Request processed sticker (transparent background) from server
        let stickerUrl = `/static/templates/${stickerName}`;
        try {
            const resp = await fetch(`/api/stickers/processed?name=${encodeURIComponent(stickerName)}`);
            if (resp.ok) {
                const j = await resp.json();
                if (j.processed_url) stickerUrl = j.processed_url;
            }
        } catch (e) {
            console.warn('Failed to fetch processed sticker, using original:', e);
        }

        // Try to find the target SVG <image> element inside the collage first
        let svgImage = null;
        if (filename) {
            const svgImgs = Array.from(document.querySelectorAll('#collage-svg image'));
            for (const si of svgImgs) {
                try {
                    const href = si.getAttribute('href') || si.getAttributeNS('http://www.w3.org/1999/xlink', 'href') || '';
                    if (href && href.endsWith(filename)) {
                        svgImage = si;
                        break;
                    }
                } catch (e) { /* ignore */ }
            }
        }

        let left, top, rect, ratio;
        if (svgImage) {
            // Use SVG image bounding box and its intrinsic width (attribute) to map coordinates
            rect = svgImage.getBoundingClientRect();
            const intrinsicW = parseFloat(svgImage.getAttribute('width')) || rect.width;
            ratio = rect.width / intrinsicW;
            left = rect.left + window.scrollX + x * ratio;
            top = rect.top + window.scrollY + y * ratio;
        } else {
            // Fallback: try to find an HTML <img> matching filename
            let targetImg = null;
            if (filename) {
                const imgs = Array.from(document.querySelectorAll('img'));
                for (const im of imgs) {
                    try {
                        const src = im.getAttribute('src') || '';
                        if (src && src.endsWith(filename)) {
                            targetImg = im;
                            break;
                        }
                    } catch (e) { /* ignore */ }
                }
            }
            if (!targetImg) {
                // fallback: use first photo image in DOM
                targetImg = document.querySelector('#photos-grid img') || document.querySelector('.photo-card img') || null;
            }
            if (!targetImg) return;
            rect = targetImg.getBoundingClientRect();
            const naturalW = targetImg.naturalWidth || rect.width;
            ratio = rect.width / naturalW;
            left = rect.left + window.scrollX + x * ratio;
            top = rect.top + window.scrollY + y * ratio;
        }

        // Create overlay image
        const img = document.createElement('img');
        img.src = stickerUrl;
        img.alt = stickerType;
        img.className = 'auto-sticker-overlay';
        img.style.position = 'absolute';
        img.style.left = `${left}px`;
        img.style.top = `${top}px`;
        img.style.transform = 'translate(-50%, -50%)';
        img.style.pointerEvents = 'none';
        img.style.zIndex = 9999;

        // Determine width based on scale and face bbox heuristics (scale is relative)
        const baseline = Math.max(60, Math.round(100 * scale));
        img.style.width = `${Math.round(baseline * ratio)}px`;
        img.style.height = 'auto';

        document.body.appendChild(img);

        // Auto-remove after some time (optional) or keep until next refresh
        setTimeout(() => {
            // keep overlays persistent; do not auto-remove by default
        }, 3000);

    } catch (e) {
        console.error('addStickerToCollage failed:', e);
    }
}

/**
 * Get display name for filter
 */
function getFilterDisplayName(filterName) {
    const names = {
        'smart_beauty': 'Smart Beauty',
        'face_glow': 'Face Glow',
        'portrait_pro': 'Portrait Pro'
    };
    return names[filterName] || filterName;
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 24px;
        border-radius: 8px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    .effect-item {
        width: 80px;
        height: 80px;
        border-radius: 8px;
        cursor: pointer;
        border: 2px solid transparent;
        transition: all 0.2s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        position: relative;
        overflow: hidden;
        background: #fff;
    }
    .effect-item:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .effect-item.selected {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3);
    }
    .effect-item img {
        width: 100%;
        height: 60px;
        object-fit: cover;
        border-radius: 6px 6px 0 0;
    }
    .effect-item .effect-name {
        font-size: 10px;
        padding: 4px 2px;
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        width: 100%;
        color: #333;
    }
    .effect-cat-tab.active {
        background: #667eea !important;
        color: #fff !important;
        border-color: #667eea !important;
    }
`;
document.head.appendChild(style);


// ============== EFFECT FILTERS MODULE (Using FilterEngine) ==============

let availableEffects = [];
let selectedEffect = 'none';
let activeEffectCategory = 'all';

/**
 * Get SESSION_ID from script data tag or global variable
 */
function getSessionId() {
    // Try global variable first
    if (typeof SESSION_ID !== 'undefined' && SESSION_ID) {
        return SESSION_ID;
    }

    // Try reading from script data tag
    const dataElement = document.getElementById('session-data');
    if (dataElement) {
        try {
            const data = JSON.parse(dataElement.textContent);
            return data.session_id;
        } catch (e) {
            console.error('Failed to parse session data:', e);
        }
    }

    return null;
}

/**
 * Initialize Effect Filters selection
 * Load filters từ API /api/filters (sử dụng FilterEngine có sẵn)
 */
async function initEffectFilters() {
    try {
        // Load filters from API - sử dụng FilterEngine
        const response = await fetch('/api/filters');

        // Check if response is OK
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.filters) {
            availableEffects = data.filters;
            renderEffectOptions();
            bindEffectEvents();
        }
    } catch (error) {
        console.error('Failed to load effect filters:', error);
    }
}

/**
 * Render effect options in the grid
 * Hiển thị các filter có sẵn từ FilterEngine với preview thumbnails
 */
function renderEffectOptions() {
    const container = document.getElementById('effects-list');
    if (!container) return;

    container.innerHTML = '';

    // Filter by category
    let effects = availableEffects;
    if (activeEffectCategory !== 'all') {
        effects = availableEffects.filter(ef => ef.category === activeEffectCategory);
    }

    effects.forEach(effect => {
        const item = document.createElement('div');
        item.className = `effect-item ${selectedEffect === effect.name ? 'selected' : ''}`;
        item.dataset.effect = effect.name;
        item.title = effect.description;

        // Sử dụng preview thumbnail từ FilterEngine
        const previewUrl = `/static/filter_previews/${effect.name}.jpg`;

        item.innerHTML = `
            <img src="${previewUrl}" alt="${effect.display_name}" onerror="this.src='/static/filter_previews/none.jpg'">
            <span class="effect-name">${effect.display_name}</span>
        `;

        container.appendChild(item);
    });
}

/**
 * Bind events for effect selection
 */
function bindEffectEvents() {
    // Category tabs
    document.querySelectorAll('.effect-cat-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.effect-cat-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            activeEffectCategory = tab.dataset.category;
            renderEffectOptions();
        });
    });

    // Effect items (use event delegation)
    const container = document.getElementById('effects-list');
    if (container) {
        container.addEventListener('click', async (e) => {
            const item = e.target.closest('.effect-item');
            if (item) {
                const effectName = item.dataset.effect;
                await applyEffectToSession(effectName);

                // Update selection UI
                document.querySelectorAll('.effect-item').forEach(i => i.classList.remove('selected'));
                item.classList.add('selected');
                selectedEffect = effectName;
            }
        });
    }
}

/**
 * Apply effect filter to all photos in session
 * Sử dụng API /api/sessions/{id}/apply-filter với FilterEngine
 */
async function applyEffectToSession(effectName) {
    const sessionId = getSessionId();
    if (!sessionId) {
        showNotification('Session không hợp lệ', 'error');
        return;
    }

    // Get display name for notification
    const effect = availableEffects.find(e => e.name === effectName);
    const displayName = effect ? effect.display_name : effectName;

    // Show loading
    showNotification(`🎨 Đang áp dụng hiệu ứng "${displayName}"...`, 'info');

    try {
        // Sử dụng API apply-filter có sẵn với FilterEngine
        const response = await fetch(`/api/apply-filter`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                filter_name: effectName,
                commit: false  // Preview mode - không lưu vĩnh viễn
            })
        });

        // Check if response is OK before parsing JSON
        if (!response.ok) {
            const errorText = await response.text();
            console.error('API Error Response:', errorText);
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            // Refresh the collage preview
            if (typeof refreshCollagePreview === 'function') {
                refreshCollagePreview();
            }

            // Update thumbnails if available
            if (data.processed_images && data.processed_images.length > 0) {
                updateEffectThumbnails(data.processed_images);
            }

            showNotification(`✅ Đã áp dụng hiệu ứng "${displayName}"`, 'success');
        } else {
            throw new Error(data.error || 'Failed to apply effect');
        }
    } catch (error) {
        console.error('Effect apply error:', error);
        showNotification('❌ Lỗi: ' + error.message, 'error');
    }
}

/**
 * Update photo thumbnails with new URLs after applying effect
 */
function updateEffectThumbnails(processedImages) {
    processedImages.forEach(img => {
        // Try to update any thumbnail elements
        const thumbElements = document.querySelectorAll(`[data-photo-number="${img.photo_number}"] img`);
        thumbElements.forEach(el => {
            el.src = img.thumbnail_url + '?t=' + Date.now(); // Cache bust
        });

        // Also update processed URL elements
        const processedElements = document.querySelectorAll(`[data-photo-id="${img.photo_id}"] img`);
        processedElements.forEach(el => {
            el.src = img.processed_url + '?t=' + Date.now();
        });
    });
}

// Effect filters module disabled here (duplicates with 'Bộ lọc' UI)


