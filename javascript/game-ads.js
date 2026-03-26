(function () {
    var INTERSTITIAL_OVERLAY_ENABLED = false; // SET TO false TO COMPLY WITH GOOGLE ADSENSE POLICY
                                              // The full-screen overlay violates AdSense policy on
                                              // ads that obscure content / non-standard placements.
    var AD_DURATION = 5; // seconds shown before "Continue" button pulses

    var styles = `
        #gameAdOverlay {
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.93);
            z-index: 99999;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        #gameAdBox {
            background: #18182a;
            border: 1px solid #2d2d45;
            border-radius: 12px;
            padding: 28px 24px 20px;
            max-width: 480px;
            width: 92%;
            text-align: center;
            color: #e2d9f3;
            box-shadow: 0 8px 32px rgba(0,0,0,0.6);
        }
        #gameAdLabel {
            font-size: 0.7rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 12px;
            font-family: sans-serif;
        }
        #gameAdSlot {
            min-height: 180px;
            background: #0d0d14;
            border-radius: 8px;
            margin: 0 0 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #444;
            font-size: 0.85rem;
            font-family: sans-serif;
            overflow: hidden;
        }
        #gameAdTimer {
            font-size: 0.88rem;
            color: #888;
            margin-bottom: 14px;
            font-family: sans-serif;
        }
        #gameAdTimer span {
            color: #a78bfa;
            font-weight: 600;
        }
        #gameAdContinue {
            background: #7c3aed;
            color: white;
            border: none;
            padding: 10px 28px;
            border-radius: 6px;
            font-size: 0.95rem;
            cursor: pointer;
            font-family: sans-serif;
            transition: background 0.2s, transform 0.1s;
        }
        #gameAdContinue:hover {
            background: #6d28d9;
        }
        #gameAdContinue.ad-ready {
            animation: adReadyPulse 0.4s ease;
        }
        @keyframes adReadyPulse {
            0%   { transform: scale(1); }
            50%  { transform: scale(1.06); }
            100% { transform: scale(1); }
        }
    `;

    function injectStyles() {
        var el = document.createElement('style');
        el.textContent = styles;
        document.head.appendChild(el);
    }

    function buildOverlay() {
        var overlay = document.createElement('div');
        overlay.id = 'gameAdOverlay';
        overlay.innerHTML =
            '<div id="gameAdBox">' +
                '<div id="gameAdLabel">Advertisement</div>' +
                '<div id="gameAdSlot"></div>' +
                '<div id="gameAdTimer">Game starts in <span id="gameAdCount">' + AD_DURATION + '</span>s</div>' +
                '<button id="gameAdContinue">Continue ▶</button>' +
            '</div>';
        return overlay;
    }

    function showAd(onClose) {
        if (!INTERSTITIAL_OVERLAY_ENABLED) {
            if (typeof onClose === 'function') onClose();
            return;
        }

        var existing = document.getElementById('gameAdOverlay');
        if (existing) existing.remove();

        var overlay = buildOverlay();
        document.body.appendChild(overlay);

        // Try to push a display ad into the slot (Auto Ads may populate it)
        var slot = document.getElementById('gameAdSlot');
        var ins = document.createElement('ins');
        ins.className = 'adsbygoogle';
        ins.style.cssText = 'display:block;width:100%;min-height:100px;';
        ins.setAttribute('data-ad-client', 'ca-pub-3633320799834823');
        ins.setAttribute('data-ad-format', 'auto');
        ins.setAttribute('data-full-width-responsive', 'true');
        slot.appendChild(ins);
        try { (adsbygoogle = window.adsbygoogle || []).push({}); } catch (e) {}

        var count = AD_DURATION;
        var countEl = document.getElementById('gameAdCount');
        var timerEl = document.getElementById('gameAdTimer');
        var btn = document.getElementById('gameAdContinue');

        var interval = setInterval(function () {
            count--;
            if (count <= 0) {
                clearInterval(interval);
                timerEl.innerHTML = 'Ad complete — enjoy the game!';
                btn.classList.add('ad-ready');
            } else {
                if (countEl) countEl.textContent = count;
            }
        }, 1000);

        btn.addEventListener('click', function () {
            clearInterval(interval);
            overlay.remove();
            if (typeof onClose === 'function') onClose();
        });
    }

    // Play Again — reloads the iframe after showing an ad
    window.playAgain = function () {
        showAd(function () {
            var frame = document.getElementById('gameFrame');
            if (frame) {
                var src = frame.src;
                frame.src = '';
                setTimeout(function () { frame.src = src; }, 50);
            }
        });
    };

    // Show on first page load
    function init() {
        injectStyles();
        showAd(null); // null = just close the overlay, game already loading behind it
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
