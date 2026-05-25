const REMINDER_ASSETS = [
    { name: "WOS", url: "https://cdn.discordapp.com/attachments/1435569370389807144/1507347649408532520/new-icon.png?ex=6a14de24&is=6a138ca4&hm=9af7a0382eeb6ef837b479ea36c4f0a54121c542c24ab221c515039cfd5521a5" },
    { name: "Crazy Joe", url: "https://cdn.discordapp.com/attachments/1435569370389807144/1465697260829671687/images__7_-removebg-preview.png?ex=6a14f4b2&is=6a13a332&hm=ebe8ca159dd9a120fa5ff6b8a1095019e968155ec0523ad03790f1d6f93740cf" },
    { name: "Arena", url: "https://cdn.discordapp.com/attachments/1435569370389807144/1438668192372490331/95eab350caae2ac1.png?ex=6a14d7aa&is=6a13862a&hm=267c2b44c7d5d4fe6ce35d8851253b625a07680fb533f9fa92bd790390ebe582" },
    { name: "Sunfire Castle", url: "https://cdn.discordapp.com/attachments/1435569370389807144/1441753704867827954/e6e3d1fb5943666f.png?ex=6a14dc85&is=6a138b05&hm=8ba4980891151b8fb09702259b4adb2d625f480763f9e424e56c32a64c03467d" },
    { name: "Bear Trap", url: "https://cdn.discordapp.com/attachments/1435569370389807144/1441474311834832956/0f4d6593f84ba519bd095f077527f9ec-8.gif?ex=6a1529d1&is=6a13d851&hm=fda361585a06804f9fe9da6461b362a11a6042aed90f532aac2d89dd0aece5d9" }
];

let currentAssetTargetId = null;

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
            input.value = url;
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
