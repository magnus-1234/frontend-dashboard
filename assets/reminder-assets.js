const REMINDER_ASSETS = [
    { name: "WOS", url: "/assets/presets/wos.png" },
    { name: "Crazy Joe", url: "/assets/presets/crazy-joe.png" },
    { name: "Arena", url: "/assets/presets/arena.png" },
    { name: "Sunfire Castle", url: "/assets/presets/sunfire-castle.png" },
    { name: "Bear Trap", url: "/assets/presets/bear-trap.gif" }
];

let currentAssetTargetId = null;

function reminderAssetUrl(url) {
    if (!url) return "";
    try {
        return new URL(url, window.location.origin).href;
    } catch (e) {
        return url;
    }
}

function initAssetLibrary() {
    // Inject styles
    const style = document.createElement('style');
    style.textContent = `
        .asset-library-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(8px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        .asset-library-overlay.show {
            display: flex;
            opacity: 1;
        }
        .asset-library-modal {
            background: #16191f;
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 16px;
            width: 90%;
            max-width: 700px;
            max-height: 80vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
            transform: scale(0.95);
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .asset-library-overlay.show .asset-library-modal {
            transform: scale(1);
        }
        .asset-library-header {
            padding: 20px 24px;
            border-bottom: 1px solid rgba(139, 92, 246, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .asset-library-header h3 {
            margin: 0;
            font-family: 'Outfit', sans-serif;
            font-size: 1.25rem;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .asset-library-header h3 i {
            color: #a78bfa;
        }
        .asset-library-close {
            background: none;
            border: none;
            color: var(--text-muted, #9ca3af);
            cursor: pointer;
            padding: 4px;
            border-radius: 6px;
            transition: all 0.2s;
        }
        .asset-library-close:hover {
            color: #fff;
            background: rgba(255,255,255,0.1);
        }
        .asset-library-body {
            padding: 24px;
            overflow-y: auto;
            flex: 1;
        }
        .asset-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 16px;
        }
        .asset-card {
            background: #1e2229;
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 12px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            flex-direction: column;
        }
        .asset-card:hover {
            border-color: #8b5cf6;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.15);
        }
        .asset-img-wrap {
            height: 100px;
            background: #111317;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 12px;
            position: relative;
        }
        .asset-img-wrap img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }
        .asset-card-label {
            padding: 10px;
            text-align: center;
            font-size: 0.85rem;
            color: #e5e7eb;
            font-weight: 500;
            border-top: 1px solid rgba(255,255,255,0.05);
        }
    `;
    document.head.appendChild(style);

    // Inject modal HTML
    const overlay = document.createElement('div');
    overlay.className = 'asset-library-overlay';
    overlay.id = 'asset-library-overlay';
    
    overlay.innerHTML = `
        <div class="asset-library-modal">
            <div class="asset-library-header">
                <h3><i data-lucide="images"></i> Media Library</h3>
                <button class="asset-library-close" onclick="closeAssetLibrary()">
                    <i data-lucide="x"></i>
                </button>
            </div>
            <div class="asset-library-body">
                <div class="asset-grid" id="asset-library-grid"></div>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Close on clicking outside
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            closeAssetLibrary();
        }
    });

    renderAssets();
    
    // Re-initialize lucide icons for new content if function exists
    if (typeof lucide !== 'undefined' && lucide.createIcons) {
        lucide.createIcons({
            root: overlay
        });
    }
}

function renderAssets() {
    const grid = document.getElementById('asset-library-grid');
    if (!grid) return;
    
    grid.innerHTML = '';
    
    REMINDER_ASSETS.forEach(asset => {
        const card = document.createElement('div');
        card.className = 'asset-card';
        card.onclick = () => selectAsset(asset.url);
        
        card.innerHTML = `
            <div class="asset-img-wrap">
                <img src="${asset.url}" alt="${asset.name}">
            </div>
            <div class="asset-card-label">${asset.name}</div>
        `;
        
        grid.appendChild(card);
    });
}

function openAssetLibrary(targetId) {
    currentAssetTargetId = targetId;
    const overlay = document.getElementById('asset-library-overlay');
    if (overlay) {
        overlay.classList.add('show');
    } else {
        initAssetLibrary();
        setTimeout(() => {
            document.getElementById('asset-library-overlay').classList.add('show');
        }, 10);
    }
}

function closeAssetLibrary() {
    const overlay = document.getElementById('asset-library-overlay');
    if (overlay) {
        overlay.classList.remove('show');
        setTimeout(() => {
            currentAssetTargetId = null;
        }, 300); // Wait for transition
    }
}

function selectAsset(url) {
    if (currentAssetTargetId) {
        const input = document.getElementById(currentAssetTargetId);
        if (input) {
            input.value = reminderAssetUrl(url);
            // Dispatch input event so any listeners (like updateReminderPreview) catch it
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
    closeAssetLibrary();
}

// Ensure init is called if DOM is already loaded, else wait
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAssetLibrary);
} else {
    initAssetLibrary();
}
