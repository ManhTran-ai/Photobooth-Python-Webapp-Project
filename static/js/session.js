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
});

