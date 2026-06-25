from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>🛒 Plans & Where to Buy</title>
    <style>
        /* ----- RESET & BASE ----- */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Roboto, system-ui, -apple-system, sans-serif;
            background: #0a0e1a;
            color: #eaeef2;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            background-image: radial-gradient(circle at 10% 30%, #1a1f35 0%, #0a0e1a 80%);
        }

        .container {
            max-width: 1200px;
            width: 100%;
            padding: 30px 20px;
        }

        /* ----- HEADER ----- */
        .header {
            text-align: center;
            margin-bottom: 50px;
        }

        .header h1 {
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #f7b733, #fc4a1a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: 1px;
            display: inline-block;
        }

        .header p {
            color: #8a9bb5;
            font-size: 1.2rem;
            margin-top: 10px;
            letter-spacing: 0.5px;
        }

        /* ----- GRID DE PLANES ----- */
        .plans-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 28px;
            margin-top: 20px;
        }

        .plan-card {
            background: rgba(22, 28, 50, 0.75);
            backdrop-filter: blur(8px);
            border-radius: 28px;
            padding: 28px 22px 30px;
            border: 1px solid rgba(255, 255, 255, 0.06);
            box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.6);
            transition: transform 0.25s ease, box-shadow 0.3s ease, border-color 0.2s;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .plan-card::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 50% 0%, rgba(247, 183, 51, 0.06), transparent 70%);
            pointer-events: none;
        }

        .plan-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 30px 60px -12px rgba(247, 183, 51, 0.2);
            border-color: rgba(247, 183, 51, 0.25);
        }

        .plan-icon {
            font-size: 3.2rem;
            margin-bottom: 12px;
        }

        .plan-card h2 {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 8px;
            color: #ffffff;
        }

        .plan-card .desc {
            font-size: 0.95rem;
            color: #b0c0d5;
            line-height: 1.5;
            margin-bottom: 18px;
            flex-grow: 1;
        }

        .plan-card .btn {
            background: linear-gradient(135deg, #f7b733, #fc4a1a);
            border: none;
            padding: 12px 30px;
            border-radius: 50px;
            font-weight: 600;
            font-size: 1rem;
            color: #0a0e1a;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 8px 20px -6px rgba(252, 74, 26, 0.3);
            text-decoration: none;
            display: inline-block;
        }

        .plan-card .btn:hover {
            transform: scale(1.03);
            box-shadow: 0 12px 28px -6px rgba(252, 74, 26, 0.5);
        }

        /* ----- MODAL / DETALLE ----- */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(6px);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            padding: 20px;
            animation: fadeIn 0.25s ease;
        }

        .modal-overlay.active {
            display: flex;
        }

        .modal {
            background: #151d30;
            border-radius: 32px;
            max-width: 480px;
            width: 100%;
            padding: 36px 30px 40px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 40px 80px -20px #000;
            position: relative;
            animation: slideUp 0.3s ease;
        }

        .modal h2 {
            font-size: 1.8rem;
            margin-bottom: 8px;
            color: #fff;
        }

        .modal .sub {
            color: #8a9bb5;
            margin-bottom: 24px;
            font-size: 1rem;
        }

        .modal .options {
            display: flex;
            flex-direction: column;
            gap: 14px;
        }

        .modal .option-btn {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 16px 20px;
            color: #eaeef2;
            font-size: 1.05rem;
            font-weight: 500;
            text-decoration: none;
            transition: background 0.2s, border-color 0.2s, transform 0.15s;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .modal .option-btn:hover {
            background: rgba(247, 183, 51, 0.12);
            border-color: rgba(247, 183, 51, 0.3);
            transform: scale(1.01);
        }

        .modal .option-btn .emoji {
            font-size: 1.6rem;
        }

        .modal .close-modal {
            position: absolute;
            top: 16px;
            right: 22px;
            font-size: 2rem;
            cursor: pointer;
            color: #5a6b85;
            transition: color 0.2s;
            background: none;
            border: none;
            line-height: 1;
        }

        .modal .close-modal:hover {
            color: #fc4a1a;
        }

        /* ----- ANIMACIONES ----- */
        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }

        @keyframes slideUp {
            0% { transform: translateY(30px); opacity: 0; }
            100% { transform: translateY(0); opacity: 1; }
        }

        /* ----- RESPONSIVE ----- */
        @media (max-width: 700px) {
            .header h1 {
                font-size: 2.2rem;
            }
            .plans-grid {
                grid-template-columns: 1fr;
                max-width: 400px;
                margin-left: auto;
                margin-right: auto;
            }
            .modal {
                padding: 28px 20px 32px;
            }
        }

        @media (max-width: 480px) {
            .header h1 {
                font-size: 1.8rem;
            }
            .plan-card {
                padding: 22px 16px 24px;
            }
            .plan-card h2 {
                font-size: 1.3rem;
            }
        }

        /* ----- SCROLLBAR ----- */
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #0a0e1a;
        }
        ::-webkit-scrollbar-thumb {
            background: #3a4a6a;
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #5a7aaa;
        }
    </style>
</head>
<body>

<div class="container">

    <!-- HEADER -->
    <header class="header">
        <h1>🛒 Plans &amp; where to buy them</h1>
        <p>Choose your plan and get it now</p>
    </header>

    <!-- GRID DE PLANES -->
    <div class="plans-grid">

        <!-- 1. YeiksVPN -->
        <div class="plan-card" data-plan="yeiksvpn">
            <div class="plan-icon">🔒</div>
            <h2>YeiksVPN</h2>
            <div class="desc">Premium VPN with 50+ countries, no logs, high speed. 1 week free trial available.</div>
            <button class="btn" data-plan="yeiksvpn">Buy now</button>
        </div>

        <!-- 2. Autododge + Aimbot -->
        <div class="plan-card" data-plan="autododge">
            <div class="plan-icon">🎯</div>
            <h2>Autododge + Aimbot</h2>
            <div class="desc">Ultimate combat hack: auto-dodge, perfect aim, kill aura. Works until next game update.</div>
            <button class="btn" data-plan="autododge">Buy now</button>
        </div>

        <!-- 3. Autogoal -->
        <div class="plan-card" data-plan="autogoal">
            <div class="plan-icon">⚽</div>
            <h2>Autogoal</h2>
            <div class="desc">Own goal trainer – score on yourself automatically. Perfect for trolling and fun.</div>
            <button class="btn" data-plan="autogoal">Buy now</button>
        </div>

        <!-- 4. New accs bots p3 -->
        <div class="plan-card" data-plan="newaccs">
            <div class="plan-icon">🤖</div>
            <h2>New accs bots p3</h2>
            <div class="desc">Fresh Telegram accounts with built‑in bots, ready for automation or farming.</div>
            <button class="btn" data-plan="newaccs">Buy now</button>
        </div>

        <!-- 5. Boost -->
        <div class="plan-card" data-plan="boost">
            <div class="plan-icon">🚀</div>
            <h2>Boost</h2>
            <div class="desc">Increase your rank or trophies with our professional boosting service.</div>
            <button class="btn" data-plan="boost">Buy now</button>
        </div>

    </div>

    <!-- PIE -->
    <footer style="margin-top: 50px; text-align: center; color: #4a5a75; font-size: 0.9rem; border-top: 1px solid rgba(255,255,255,0.04); padding-top: 24px;">
        All plans are delivered instantly via Telegram · 24/7 support · Secure payment
    </footer>
</div>

<!-- ===== MODAL ===== -->
<div class="modal-overlay" id="modalOverlay">
    <div class="modal" id="modalContent">
        <button class="close-modal" id="closeModalBtn">&times;</button>
        <h2 id="modalTitle">Plan</h2>
        <p class="sub" id="modalSub">Choose one option</p>
        <div class="options" id="modalOptions">
            <!-- Se llena con JS -->
        </div>
    </div>
</div>

<script>
    (function() {
        const plans = {
            yeiksvpn: {
                title: 'YeiksVPN',
                subtitle: 'Choose how to get it:',
                options: [
                    { label: '🌐 Web',          url: 'https://subhere.net/be615e78-6f6b-4f49-b244-a5387b7bb11e' },
                    { label: '👤 Admin',        url: 'https://t.me/yeikson' }
                ]
            },
            autododge: {
                title: 'Autododge + Aimbot',
                subtitle: 'Contact @yeikson to buy:',
                options: [
                    { label: '💬 Chat with Admin', url: 'https://t.me/yeikson' }
                ]
            },
            autogoal: {
                title: 'Autogoal',
                subtitle: 'Contact @yeikson to buy:',
                options: [
                    { label: '💬 Chat with Admin', url: 'https://t.me/yeikson' }
                ]
            },
            newaccs: {
                title: 'New accs bots p3',
                subtitle: 'Contact @yeikson to buy:',
                options: [
                    { label: '💬 Chat with Admin', url: 'https://t.me/yeikson' }
                ]
            },
            boost: {
                title: 'Boost',
                subtitle: 'Choose your boost type:',
                options: [
                    { label: '🏆 Ranked Boost',  url: 'https://t.me/yeikson' },
                    { label: '⭐ Trophies Boost', url: 'https://t.me/yeikson' }
                ]
            }
        };

        const overlay = document.getElementById('modalOverlay');
        const modalTitle = document.getElementById('modalTitle');
        const modalSub = document.getElementById('modalSub');
        const modalOptions = document.getElementById('modalOptions');
        const closeBtn = document.getElementById('closeModalBtn');

        function openModal(planKey) {
            const plan = plans[planKey];
            if (!plan) return;

            modalTitle.textContent = plan.title;
            modalSub.textContent = plan.subtitle;

            modalOptions.innerHTML = '';
            plan.options.forEach(opt => {
                const a = document.createElement('a');
                a.className = 'option-btn';
                a.href = opt.url;
                a.target = '_blank';
                a.rel = 'noopener noreferrer';
                a.innerHTML = `<span class="emoji">${opt.label.split(' ')[0]}</span> ${opt.label}`;
                modalOptions.appendChild(a);
            });

            overlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        }

        function closeModal() {
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }

        document.querySelectorAll('.plan-card .btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const planKey = this.dataset.plan;
                if (planKey) openModal(planKey);
            });
        });

        document.querySelectorAll('.plan-card').forEach(card => {
            card.addEventListener('click', function(e) {
                if (e.target.closest('.btn')) return;
                const planKey = this.dataset.plan;
                if (planKey) openModal(planKey);
            });
        });

        closeBtn.addEventListener('click', closeModal);

        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) closeModal();
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && overlay.classList.contains('active')) {
                closeModal();
            }
        });
    })();
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
