// Client-side collage preview and export
// Requires SESSION_ID global variable provided by template

// Inject CSS animations for notifications
(function injectStyles() {
    if (document.getElementById('collage-export-styles')) return;
    const style = document.createElement('style');
    style.id = 'collage-export-styles';
    style.textContent = `
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOutRight {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
})();

document.addEventListener('DOMContentLoaded', () => {
    // read session data from JSON script inserted by template to avoid raw template tags in executable JS
    let sessionId = (typeof SESSION_ID !== 'undefined') ? SESSION_ID : null;
    let stickers = (typeof STICKERS !== 'undefined') ? STICKERS : null;
    const sessionDataEl = document.getElementById('session-data');
    if (sessionDataEl) {
        try {
            const sd = JSON.parse(sessionDataEl.textContent);
            sessionId = sessionId || sd.session_id;
            stickers = stickers || sd.stickers || [];
            // expose globals for backward compatibility
            window.SESSION_ID = sessionId;
            window.STICKERS = stickers;
        } catch (e) { console.warn('Failed to parse session-data', e); }
    }
    if (!sessionId) return;
    initCollageUI(sessionId);
});

async function initCollageUI(sessionId) {
    // Define two simple templates inline: 1x4 (vertical strip) and 2x2 (grid)
    const templatesMeta = {
        // 1x4 vertical strip: wider top/bottom margins and gaps between photos
        '1x4': {
            name: '1x4',
            size: [420, 1300],
            photo_size: [360, 260],
            positions: [
                [30, 60],
                [30, 360],
                [30, 660],
                [30, 960]
            ]
        },
        // 2x2 grid: larger margins and gaps to allow sticker placement
        '2x2': {
            name: '2x2',
            size: [900, 940],
            photo_size: [360, 360],
            positions: [
                [60, 60],
                [480, 60],
                [60, 460],
                [480, 460]
            ]
        }
    };

    const templatesListEl = document.getElementById('template-list');
    const iconsListEl = document.getElementById('icons-list');
    const svg = document.getElementById('collage-svg');
    const colorFrame = document.getElementById('color-frame');
    // optional color inputs that may not exist in template — provide safe fallbacks
    const colorBg = document.getElementById('color-bg') || { value: (colorFrame && colorFrame.value) || '#ffffff' };
    const colorAccent = document.getElementById('color-accent') || { value: '#000000' };
    const colorBorder = document.getElementById('color-border') || { value: '#000000' };
    const fillModeEl = document.getElementById('fill-mode') || { value: 'cover' };
    const filtersListEl = document.getElementById('filters-list');
    const applyPreviewBtn = document.getElementById('apply-preview-btn');
    const exportBtn = document.getElementById('export-collage-btn');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    // control tab buttons
    const btnTemplates = document.getElementById('btn-templates');
    const btnColors = document.getElementById('btn-colors');
    const btnIcons = document.getElementById('btn-icons');
    const sectionTemplates = document.getElementById('template-section');
    const sectionColors = document.getElementById('colors-section');
    const sectionIcons = document.getElementById('icons-section');

    // default template selection: first template in metadata
    let selectedTemplate = '1x4';

    // wire template choice buttons
    const tpl1 = document.getElementById('tpl-1x4');
    const tpl2 = document.getElementById('tpl-2x2');
    if (tpl1) tpl1.addEventListener('click', () => { selectedTemplate = '1x4'; tpl1.classList.add('active'); tpl2.classList.remove('active'); renderPreview(); });
    if (tpl2) tpl2.addEventListener('click', () => { selectedTemplate = '2x2'; tpl2.classList.add('active'); tpl1.classList.remove('active'); renderPreview(); });

    // highlight helper (guard if template list is not present)
    function highlightSelectedTemplate(name) {
        if (!templatesListEl) return;
        const thumbs = templatesListEl.querySelectorAll('.template-thumb');
        thumbs.forEach(t => t.style.outline = t.dataset.name === name ? '3px solid #3b82f6' : 'none');
    }

    // control tabs behavior
    function showSection(name) {
        sectionTemplates.style.display = name === 'templates' ? '' : 'none';
        sectionColors.style.display = name === 'colors' ? '' : 'none';
        sectionIcons.style.display = name === 'icons' ? '' : 'none';
        btnTemplates.classList.toggle('active', name === 'templates');
        btnColors.classList.toggle('active', name === 'colors');
        btnIcons.classList.toggle('active', name === 'icons');
    }
    if (btnTemplates && btnColors && btnIcons) {
        btnTemplates.addEventListener('click', () => showSection('templates'));
        btnColors.addEventListener('click', () => showSection('colors'));
        btnIcons.addEventListener('click', () => showSection('icons'));
        // default
        showSection('templates');
    }

    // Load session photos
    let photos = [];
    try {
        const resp = await fetch(`/api/sessions/${sessionId}/photos`);
        const data = await resp.json();
        if (data && data.photos) {
            // prefer slot preview -> thumbnail -> processed -> original
            photos = data.photos.map(p => p.slot_url || p.thumbnail_url || p.processed_url || p.original_url);
        }
    } catch (e) {
        console.warn('Failed to load session photos', e);
    }

    // load decorations list (from decorations.json) OR use STICKERS provided by template
    let decorationsCatalog = [];
    // runtime decorations state (persist position/scale for export)
    const decorationsState = [];
    try {
        decorationsCatalog = await fetch('/static/templates/decorations.json').then(r => r.json()).catch(() => []);
        // normalize decoration paths so they always point under /static/
        decorationsCatalog = (decorationsCatalog || []).map(p => String(p || '').replace(/^\//, '')).map(p => {
            if (!p) return p;
            if (p.startsWith('static/')) return p;
            if (p.startsWith('templates/')) return 'static/' + p;
            return p;
        }).filter(Boolean);
    } catch (e) {
        decorationsCatalog = [];
    }
    // if server passed STICKERS array, use those as additional icons
    if (typeof STICKERS !== 'undefined' && Array.isArray(STICKERS) && STICKERS.length) {
        // STICKERS contains full static URLs
        for (const s of STICKERS) {
            // convert "/static/..." or full URL to relative path for addDecoration
            // store as absolute path starting without leading slash
            const rel = s.replace(window.location.origin + '/', '').replace(/^\//, '');
            decorationsCatalog.push(rel);
        }
    }
    // exclude certain decoration filenames from rendering as toolbar buttons
    const excludedDecos = new Set(['heart.svg', 'star.svg', 'start.svg']);

    // populate icons list as clickable thumbnail buttons
    // helper: add a decoration element to svg (exposed to button handlers)
    function addDecorationToSvg(decoPath, x, y, scale = 1.0, fromState = false) {
        const deco = document.createElementNS('http://www.w3.org/2000/svg', 'image');
        // ensure URL is encoded to handle spaces / non-ASCII filenames
        const href = '/' + String(decoPath || '').replace(/^\//, '');
        try {
            deco.setAttributeNS('http://www.w3.org/1999/xlink', 'href', encodeURI(href));
        } catch (e) {
            deco.setAttributeNS('http://www.w3.org/1999/xlink', 'href', href);
        }
        deco.setAttribute('x', x);
        deco.setAttribute('y', y);
        deco.setAttribute('width', 80 * scale);
        deco.setAttribute('height', 80 * scale);
        deco.setAttribute('data-path', decoPath);
        deco.setAttribute('class', 'svg-deco');
        deco.style.cursor = 'move';
        svg.appendChild(deco);
        // if this decoration is newly created by user drop, register in state
        if (!fromState) {
            const decoId = `d${Date.now()}${Math.floor(Math.random()*1000)}`;
            deco.dataset.decoId = decoId;
            decorationsState.push({
                id: decoId,
                path: decoPath,
                x: parseFloat(x) || 0,
                y: parseFloat(y) || 0,
                scale: parseFloat(scale) || 1.0,
                color: null
            });
        }

        // make draggable inside svg (pointer events)
        let isDragging = false;
        let start = null;
        deco.addEventListener('pointerdown', (evt) => {
            evt.preventDefault();
            isDragging = true;
            start = { x: evt.clientX, y: evt.clientY, origX: parseFloat(deco.getAttribute('x')), origY: parseFloat(deco.getAttribute('y')) };
            deco.setPointerCapture(evt.pointerId);
        });
        window.addEventListener('pointermove', (evt) => {
            if (!isDragging) return;
            const dx = evt.clientX - start.x;
            const dy = evt.clientY - start.y;
            const newX = start.origX + dx;
            const newY = start.origY + dy;
            deco.setAttribute('x', newX);
            deco.setAttribute('y', newY);
            // update state entry if present
            const id = deco.dataset.decoId;
            const state = decorationsState.find(d => d.id === id);
            if (state) {
                state.x = newX;
                state.y = newY;
            }
        });
        deco.addEventListener('pointerup', (evt) => {
            isDragging = false;
            try { deco.releasePointerCapture(evt.pointerId); } catch (e) {}
        });
        // double-click to remove decoration
        deco.addEventListener('dblclick', () => {
            const id = deco.dataset.decoId;
            if (id) {
                const idx = decorationsState.findIndex(d => d.id === id);
                if (idx >= 0) decorationsState.splice(idx, 1);
            }
            deco.remove();
        });
        return deco;
    }

    for (const decoPath of decorationsCatalog) {
        const baseName = (decoPath || '').split('/').pop().toLowerCase();
        if (excludedDecos.has(baseName)) continue;
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'sticker-btn';
        btn.dataset.path = decoPath;
        btn.title = decoPath.split('/').pop();

        // Render the sticker as the button thumbnail using background-image.
        // Encode the URL (spaces / non-ASCII chars) to avoid load failures.
        const bgUrl = encodeURI('/' + decoPath);
        btn.style.backgroundImage = `url("${bgUrl}")`;
        btn.style.backgroundRepeat = 'no-repeat';
        btn.style.backgroundPosition = 'center';
        btn.style.backgroundSize = '44px 44px';
        // Ensure no fallback text or elements appear inside the button
        btn.innerHTML = '';
        // Accessibility: expose label
        btn.setAttribute('aria-label', btn.title);

        // clicking a sticker will place multiple copies automatically onto the photobooth template
        btn.addEventListener('click', () => {
            // toggle active visual state
            document.querySelectorAll('.sticker-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const tmpl = templatesMeta[selectedTemplate] || {};
            const width = (tmpl.size && tmpl.size[0]) || svg.clientWidth || 600;
            const height = (tmpl.size && tmpl.size[1]) || svg.clientHeight || 800;

            // compute photo slot rectangles to avoid overlapping them
            const slots = (tmpl.positions || []).map((p, i) => {
                const pw = (tmpl.photo_size && tmpl.photo_size[0]) || 360;
                const ph = (tmpl.photo_size && tmpl.photo_size[1]) || 360;
                return { x: p[0], y: p[1], w: pw, h: ph };
            });

            function overlapsAnySlot(x, y, w, h) {
                for (const s of slots) {
                    if (x + w < s.x || x > s.x + s.w || y + h < s.y || y > s.y + s.h) {
                        // no overlap with this slot
                    } else {
                        return true;
                    }
                }
                return false;
            }

            // decide number of decorations based on frame area (scaled) and clamp
            const areaScale = (width * height) / (900 * 940);
            const desiredBase = Math.round(8 * areaScale);
            const minDecos = 6;
            const maxDecos = 20;
            const numDecos = Math.max(minDecos, Math.min(maxDecos, desiredBase + Math.floor(Math.random() * 5)));

            // margin inside frame where decorations can be placed (avoid borders too close)
            const framePadding = Math.max(12, Math.round(Math.min(width, height) * 0.04));

            for (let iDeco = 0; iDeco < numDecos; iDeco++) {
                // preferred size depends on template photo size to keep proportions reasonable
                const minSize = Math.max(18, Math.round(Math.min(tmpl.photo_size ? tmpl.photo_size[0] : 360, tmpl.photo_size ? tmpl.photo_size[1] : 360) * 0.08));
                const maxSize = Math.max(minSize + 8, Math.round(Math.min(tmpl.photo_size ? tmpl.photo_size[0] : 360, tmpl.photo_size ? tmpl.photo_size[1] : 360) * 0.14));
                const decoWidth = minSize + Math.floor(Math.random() * (maxSize - minSize + 1));
                const scale = Math.round((decoWidth / 80) * 100) / 100;

                // attempt to find a placement not overlapping photo slots; bias to margins
                let placed = false;
                for (let attempt = 0; attempt < 60 && !placed; attempt++) {
                    // choose zone bias: 0=top,1=bottom,2=left,3=right,4=around-corners,5=random-inside
                    const zone = Math.floor(Math.random() * 6);
                    let x = framePadding + Math.floor(Math.random() * Math.max(1, width - framePadding * 2 - decoWidth));
                    let y = framePadding + Math.floor(Math.random() * Math.max(1, height - framePadding * 2 - decoWidth));
                    if (zone === 0) {
                        y = framePadding + Math.floor(Math.random() * Math.max(1, Math.round(height * 0.18)));
                    } else if (zone === 1) {
                        y = height - framePadding - decoWidth - Math.floor(Math.random() * Math.max(1, Math.round(height * 0.18)));
                    } else if (zone === 2) {
                        x = framePadding + Math.floor(Math.random() * Math.max(1, Math.round(width * 0.18)));
                    } else if (zone === 3) {
                        x = width - framePadding - decoWidth - Math.floor(Math.random() * Math.max(1, Math.round(width * 0.18)));
                    } else if (zone === 4) {
                        // place near a random corner
                        const corner = Math.floor(Math.random() * 4);
                        if (corner === 0) { x = framePadding + Math.floor(Math.random() * 40); y = framePadding + Math.floor(Math.random() * 40); }
                        if (corner === 1) { x = width - framePadding - decoWidth - Math.floor(Math.random() * 40); y = framePadding + Math.floor(Math.random() * 40); }
                        if (corner === 2) { x = framePadding + Math.floor(Math.random() * 40); y = height - framePadding - decoWidth - Math.floor(Math.random() * 40); }
                        if (corner === 3) { x = width - framePadding - decoWidth - Math.floor(Math.random() * 40); y = height - framePadding - decoWidth - Math.floor(Math.random() * 40); }
                    }

                    // ensure coordinates are within frame bounds
                    x = Math.max(framePadding, Math.min(x, width - framePadding - decoWidth));
                    y = Math.max(framePadding, Math.min(y, height - framePadding - decoWidth));

                    if (!overlapsAnySlot(x, y, decoWidth, decoWidth)) {
                        addDecorationToSvg(decoPath, x, y, scale, false);
                        placed = true;
                    }
                }
                // if not placed after attempts, skip this deco
            }
        });

        // dragstart support (if user drags)
        btn.addEventListener('dragstart', (ev) => {
            try { ev.dataTransfer.setData('text/plain', decoPath); } catch (e) {}
        });

        iconsListEl.appendChild(btn);
    }

    // render current preview using SVG by placing images at positions
    async function renderPreview() {
        if (!selectedTemplate) return;
        const meta = templatesMeta[selectedTemplate];
        if (!meta) return;

        // adjust svg size and wrapper width to match selected template
        const wrapper = document.getElementById('frame-wrapper');
        if (wrapper) {
            wrapper.style.width = (meta.size[0]) + 'px';
        }
        // use viewBox for responsive scaling but set explicit height to preserve aspect
        svg.setAttribute('viewBox', `0 0 ${meta.size[0]} ${meta.size[1]}`);
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', meta.size[1]);
        svg.style.background = colorFrame.value || meta.background || '#ffffff';
        // clear
        while (svg.firstChild) svg.removeChild(svg.firstChild);

        // add template background asset (if exists)
        // draw outer white frame rect (colored by colorFrame)
        const frameRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        frameRect.setAttribute('x', 0);
        frameRect.setAttribute('y', 0);
        frameRect.setAttribute('width', meta.size[0]);
        frameRect.setAttribute('height', meta.size[1]);
        frameRect.setAttribute('fill', colorFrame.value || '#ffffff');
        frameRect.setAttribute('rx', 8);
        frameRect.setAttribute('ry', 8);
        svg.appendChild(frameRect);

        // add photos into positions
        const slots = meta.positions || [];
        for (let i = 0; i < slots.length; i++) {
            const pos = slots[i];
            const imgUrl = photos[i] || photos[i % photos.length] || '/static/templates/placeholders/placeholder.png';
            const imgEl = document.createElementNS('http://www.w3.org/2000/svg', 'image');
            imgEl.setAttributeNS('http://www.w3.org/1999/xlink', 'href', imgUrl);
            imgEl.setAttribute('x', pos[0]);
            imgEl.setAttribute('y', pos[1]);
            imgEl.setAttribute('width', meta.photo_size[0]);
            imgEl.setAttribute('height', meta.photo_size[1]);
            imgEl.setAttribute('preserveAspectRatio', 'xMidYMid slice');
            svg.appendChild(imgEl);
        }

        // draw footer text centered and small copyright at bottom-right
        const footerText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        footerText.setAttribute('x', meta.size[0] / 2);
        footerText.setAttribute('y', meta.size[1] - 18);
        footerText.setAttribute('text-anchor', 'middle');
        footerText.setAttribute('font-size', '14');
        footerText.setAttribute('fill', '#222');
        footerText.setAttribute('font-family', 'Arial, sans-serif');
        footerText.textContent = 'BeautyPlus Photo Booth';
        svg.appendChild(footerText);

        const copyright = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        copyright.setAttribute('x', meta.size[0] - 8);
        copyright.setAttribute('y', meta.size[1] - 6);
        copyright.setAttribute('text-anchor', 'end');
        copyright.setAttribute('font-size', '12');
        copyright.setAttribute('fill', '#666');
        copyright.setAttribute('font-family', 'Arial, sans-serif');
        copyright.textContent = '© 2026 BP';
        svg.appendChild(copyright);

        // re-render existing decorations from state (so decorations survive re-renders)
        for (const s of decorationsState) {
            // call addDecorationToSvg in fromState mode and set id accordingly
            const elem = addDecorationToSvg(s.path, s.x, s.y, s.scale, true);
            if (elem) elem.dataset.decoId = s.id;
        }

        // enable drop for decorations onto the svg
        svg.addEventListener('dragover', (ev) => {
            ev.preventDefault();
        });
        svg.addEventListener('drop', (ev) => {
            ev.preventDefault();
            const decoPath = ev.dataTransfer.getData('text/plain');
            if (!decoPath) return;
            // compute SVG coordinates
            const pt = svg.createSVGPoint();
            pt.x = ev.clientX;
            pt.y = ev.clientY;
            const svgP = pt.matrixTransform(svg.getScreenCTM().inverse());
            addDecorationToSvg(decoPath, svgP.x, svgP.y, 1.0, false);
        });

        // decorations existing on svg will be managed via pointer events
        function addDecorationToSvg(decoPath, x, y, scale = 1.0, fromState = false) {
            const deco = document.createElementNS('http://www.w3.org/2000/svg', 'image');
            // ensure URL is encoded to handle spaces / non-ASCII filenames
            const href = '/' + String(decoPath || '').replace(/^\//, '');
            try {
                deco.setAttributeNS('http://www.w3.org/1999/xlink', 'href', encodeURI(href));
            } catch (e) {
                deco.setAttributeNS('http://www.w3.org/1999/xlink', 'href', href);
            }
            deco.setAttribute('x', x);
            deco.setAttribute('y', y);
            deco.setAttribute('width', 80 * scale);
            deco.setAttribute('height', 80 * scale);
            deco.setAttribute('data-path', decoPath);
            deco.setAttribute('class', 'svg-deco');
            deco.style.cursor = 'move';
            svg.appendChild(deco);
            // if this decoration is newly created by user drop, register in state
            if (!fromState) {
                const decoId = `d${Date.now()}${Math.floor(Math.random()*1000)}`;
                deco.dataset.decoId = decoId;
                decorationsState.push({
                    id: decoId,
                    path: decoPath,
                    x: parseFloat(x) || 0,
                    y: parseFloat(y) || 0,
                    scale: parseFloat(scale) || 1.0,
                    color: null
                });
            }

            // make draggable inside svg (pointer events)
            let isDragging = false;
            let start = null;
            deco.addEventListener('pointerdown', (evt) => {
                evt.preventDefault();
                isDragging = true;
                start = { x: evt.clientX, y: evt.clientY, origX: parseFloat(deco.getAttribute('x')), origY: parseFloat(deco.getAttribute('y')) };
                deco.setPointerCapture(evt.pointerId);
            });
            window.addEventListener('pointermove', (evt) => {
                if (!isDragging) return;
                const dx = evt.clientX - start.x;
                const dy = evt.clientY - start.y;
                // transform dx,dy to svg coords
                const pt = svg.createSVGPoint();
                pt.x = start.origX + dx;
                pt.y = start.origY + dy;
                // approximate: directly use pixel offsets
                const newX = start.origX + dx;
                const newY = start.origY + dy;
                deco.setAttribute('x', newX);
                deco.setAttribute('y', newY);
                // update state entry if present
                const id = deco.dataset.decoId;
                const state = decorationsState.find(d => d.id === id);
                if (state) {
                    state.x = newX;
                    state.y = newY;
                }
            });
            deco.addEventListener('pointerup', (evt) => {
                isDragging = false;
                try { deco.releasePointerCapture(evt.pointerId); } catch (e) {}
            });
            // double-click to remove decoration
            deco.addEventListener('dblclick', () => {
                const id = deco.dataset.decoId;
                if (id) {
                    const idx = decorationsState.findIndex(d => d.id === id);
                    if (idx >= 0) decorationsState.splice(idx, 1);
                }
                deco.remove();
            });
            return deco;
        }
        // optional accent/border overlay (draw border rect)
        const border = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        border.setAttribute('x', 0.5);
        border.setAttribute('y', 0.5);
        border.setAttribute('width', meta.size[0]-1);
        border.setAttribute('height', meta.size[1]-1);
        border.setAttribute('fill', 'none');
        border.setAttribute('stroke', colorBorder.value || '#000000');
        border.setAttribute('stroke-width', 2);
        svg.appendChild(border);
    }

    applyPreviewBtn.addEventListener('click', () => {
        renderPreview();
    });

    exportBtn.addEventListener('click', async () => {
        exportBtn.disabled = true;
        const originalBtnText = exportBtn.textContent;
        exportBtn.textContent = '⏳ Đang xuất...';
        if (loadingOverlay) {
            loadingText && (loadingText.textContent = 'Đang tạo ảnh collage...');
            loadingOverlay.style.display = 'flex';
        }
        try {
            // Build decorations payload from current decorationsState
            const decorationsPayload = decorationsState.map(d => ({
                path: d.path,
                x: Math.round(d.x),
                y: Math.round(d.y),
                scale: Number(d.scale) || 1.0,
                color: d.color || null
            }));

            // Lấy màu frame từ color picker
            const frameColor = colorFrame ? colorFrame.value : '#ffffff';

            const payload = {
                session_id: sessionId,
                template: selectedTemplate,
                colors: {
                    bg: frameColor,  // Sử dụng màu frame người dùng chọn
                    accent: colorAccent.value || frameColor,
                    border: colorBorder.value || '#000000'
                },
                decorations: decorationsPayload,
                fill_mode: fillModeEl.value || 'cover',
                use_processed: true  // Sử dụng ảnh đã áp dụng filter
            };

            const resp = await fetch('/api/collage', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!resp.ok) {
                const errorData = await resp.json().catch(() => ({}));
                throw new Error(errorData.error || `Server error: ${resp.status}`);
            }

            const data = await resp.json();
            if (data && data.collage_url) {
                try {
                    // fetch the generated image as blob and trigger download
                    const respImg = await fetch(data.collage_url);
                    if (!respImg.ok) {
                        throw new Error('Không thể tải ảnh collage');
                    }
                    const blob = await respImg.blob();
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;

                    // Tạo tên file đẹp với timestamp
                    const now = new Date();
                    const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '');
                    const timeStr = now.toTimeString().slice(0, 8).replace(/:/g, '');
                    const fname = `photobooth_${selectedTemplate}_${dateStr}_${timeStr}.png`;
                    a.download = fname;

                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    URL.revokeObjectURL(url);

                    // Hiển thị thông báo thành công
                    showExportNotification(`✅ Đã tải xuống: ${fname}`, 'success');
                } catch (e) {
                    console.error('Download error:', e);
                    // fallback: open in new tab
                    window.open(data.collage_url, '_blank');
                    showExportNotification('📥 Đã mở ảnh trong tab mới', 'info');
                }
            } else {
                throw new Error(data.error || 'Không thể tạo collage');
            }
        } catch (e) {
            console.error('Export error:', e);
            showExportNotification('❌ Lỗi: ' + e.message, 'error');
        } finally {
            exportBtn.disabled = false;
            exportBtn.textContent = originalBtnText;
            if (loadingOverlay) loadingOverlay.style.display = 'none';
        }
    });

    // Helper function để hiển thị thông báo export
    function showExportNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 24px;
            border-radius: 8px;
            background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
            color: white;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 10000;
            animation: slideInRight 0.3s ease;
            max-width: 350px;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }

    // initial actions
    highlightSelectedTemplate(selectedTemplate);
    renderPreview();

    // Load available filters and render simple buttons
    try {
        const resp = await fetch('/api/filters');
        if (resp.ok) {
            const data = await resp.json();
            const available = (data.filters || []).slice(0, 12); // show first 12
            for (const f of available) {
                const btn = document.createElement('button');
                btn.className = 'filter-btn';
                btn.textContent = f.display_name || f.name;
                btn.dataset.filter = f.name;
                btn.addEventListener('click', async () => {
                    // preview filter for session photos
                    try {
                        btn.disabled = true;
                        btn.textContent = 'Đang xử lý...';
                        const r = await fetch('/api/apply-filter', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ session_id: sessionId, filter_name: f.name, commit: false })
                        });
                        const dd = await r.json();
                        if (r.ok && dd.processed_images) {
                            // update photos array to processed images ordered by photo_number
                            const ordered = dd.processed_images.sort((a,b)=>a.photo_number-b.photo_number);
                            photos = ordered.map(p => p.processed_url || p.thumbnail_url || p.original_url);
                            renderPreview();
                        } else {
                            alert('Filter preview failed: ' + (dd.error || 'unknown'));
                        }
                    } catch (e) {
                        console.error('Filter preview error', e);
                        alert('Filter preview error');
                    } finally {
                        btn.disabled = false;
                        btn.textContent = f.display_name || f.name;
                    }
                });
                filtersListEl.appendChild(btn);
            }
        }
    } catch (e) {
        console.warn('Failed to load filters', e);
    }
    
    // selection toolbar for decorations
    const decoToolbar = createDecoToolbar();

    function createDecoToolbar() {
        const tb = document.createElement('div');
        tb.id = 'deco-toolbar';
        tb.style.position = 'absolute';
        tb.style.display = 'none';
        tb.style.gap = '6px';
        tb.style.padding = '6px';
        tb.style.background = 'rgba(255,255,255,0.95)';
        tb.style.border = '1px solid rgba(0,0,0,0.08)';
        tb.style.borderRadius = '8px';
        tb.style.boxShadow = '0 6px 18px rgba(0,0,0,0.08)';
        tb.style.zIndex = 9999;
        const btnSize = (label) => {
            const b = document.createElement('button');
            b.type = 'button';
            b.textContent = label;
            b.className = 'btn btn-secondary';
            b.style.padding = '6px 8px';
            b.style.fontSize = '0.85rem';
            return b;
        };
        const scaleUp = btnSize('+');
        const scaleDown = btnSize('−');
        const bringForward = btnSize('↑');
        const sendBack = btnSize('↓');
        const removeBtn = btnSize('✖');
        tb.appendChild(scaleUp);
        tb.appendChild(scaleDown);
        tb.appendChild(bringForward);
        tb.appendChild(sendBack);
        tb.appendChild(removeBtn);

        document.body.appendChild(tb);

        let currentDeco = null;

        scaleUp.addEventListener('click', () => {
            if (!currentDeco) return;
            changeDecoScale(currentDeco, 1.1);
        });
        scaleDown.addEventListener('click', () => {
            if (!currentDeco) return;
            changeDecoScale(currentDeco, 0.9);
        });
        bringForward.addEventListener('click', () => {
            if (!currentDeco) return;
            svg.appendChild(currentDeco);
        });
        sendBack.addEventListener('click', () => {
            if (!currentDeco) return;
            svg.insertBefore(currentDeco, svg.firstChild);
        });
        removeBtn.addEventListener('click', () => {
            if (!currentDeco) return;
            const id = currentDeco.dataset.decoId;
            const idx = decorationsState.findIndex(d => d.id === id);
            if (idx >= 0) decorationsState.splice(idx, 1);
            currentDeco.remove();
            hideToolbar();
        });

        function showToolbarFor(elem) {
            currentDeco = elem;
            const rect = elem.getBoundingClientRect();
            tb.style.left = `${rect.right + 8}px`;
            tb.style.top = `${rect.top}px`;
            tb.style.display = 'flex';
        }
        function hideToolbar() {
            currentDeco = null;
            tb.style.display = 'none';
        }

        // expose to outer scope
        return { showToolbarFor, hideToolbar, element: tb };
    }

    function selectDecorationElement(elem) {
        // deselect others visually
        document.querySelectorAll('.svg-deco').forEach(e => e.style.outline = 'none');
        elem.style.outline = '2px dashed rgba(0,0,0,0.2)';
        // position toolbar
        decoToolbar.showToolbarFor(elem);
    }

    function changeDecoScale(elem, factor) {
        const w = parseFloat(elem.getAttribute('width') || 80);
        const h = parseFloat(elem.getAttribute('height') || 80);
        const newW = Math.max(8, Math.round(w * factor));
        const newH = Math.max(8, Math.round(h * factor));
        elem.setAttribute('width', newW);
        elem.setAttribute('height', newH);
        // update state
        const id = elem.dataset.decoId;
        const state = decorationsState.find(d => d.id === id);
        if (state) state.scale = newW / 80;
    }
}


