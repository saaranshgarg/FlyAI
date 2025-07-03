# Minimal web server for FlyAI using only standard library
import json
import os
import random
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from http import cookies

from flyai import load_data, save_data, MESSAGES


def format_html(body: str, lang: str = 'en') -> bytes:
    """Wrap body in basic HTML structure with simple styling and add language toggle."""
    style = "<style>body{font-family:sans-serif;font-size:1.5em;text-align:center;}#lang-toggle{position:fixed;top:10px;right:10px;font-size:1em;z-index:1000;}</style>"
    # Add a language toggle form always visible at top right
    toggle = f'''
    <form id="lang-toggle" method="post" action="/toggle-lang">
        <select name="lang" onchange="this.form.submit()">
            <option value="en"{' selected' if lang=='en' else ''}>English</option>
            <option value="hi"{' selected' if lang=='hi' else ''}>हिन्दी</option>
        </select>
    </form>'''
    html = (
        f"<!doctype html><html lang='{lang}'><meta charset='utf-8'>" +
        style + f"<body>{toggle}{body}</body></html>"
    )
    return html.encode('utf-8')


class FlyAIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve static files (e.g., JS)
        if self.path.startswith('/address_dropdown.js'):
            js_path = os.path.join(os.path.dirname(__file__), 'address_dropdown.js')
            if os.path.exists(js_path):
                self.send_response(200)
                self.send_header('Content-Type', 'application/javascript; charset=utf-8')
                self.end_headers()
                with open(js_path, 'rb') as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Not found')
                return
        if self.path.startswith('/register'):
            self.show_register()
        elif self.path.startswith('/book'):
            self.show_book()
        elif self.path.startswith('/history'):
            self.show_history()
        elif self.path.startswith('/help'):
            self.show_help()
        else:
            self.redirect('/register')

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode()
        params = parse_qs(body)
        if self.path == '/toggle-lang':
            # Handle global language toggle
            lang = params.get('lang', ['en'])[0]
            self.send_response(302)
            self.set_cookie('lang', lang)
            # Redirect back to Referer or home
            ref = self.headers.get('Referer', '/book')
            self.send_header('Location', ref)
            self.end_headers()
        elif self.path.startswith('/register'):
            self.handle_register(params)
        elif self.path.startswith('/book'):
            self.handle_book(params)
        else:
            self.redirect('/register')

    # Utility functions
    def get_cookies(self):
        if 'Cookie' in self.headers:
            c = cookies.SimpleCookie(self.headers['Cookie'])
            return {k: v.value for k, v in c.items()}
        return {}

    def set_cookie(self, key, value):
        c = cookies.SimpleCookie()
        c[key] = value
        self.send_header('Set-Cookie', c.output(header='').strip())

    def redirect(self, location):
        self.send_response(302)
        self.send_header('Location', location)
        self.end_headers()

    # Page handlers
    def show_register(self, error=None, otp=None, phone='', lang=None):
        cookies_in = self.get_cookies()
        if cookies_in.get('user'):
            return self.redirect('/book')
        if not lang:
            lang = cookies_in.get('lang', 'en')
        msg = MESSAGES[lang]
        body = f"<h1>{msg['register_title']}</h1>"
        if otp:
            text = 'Your OTP' if lang == 'en' else 'आपका OTP'
            body += f"<p>{text}: {otp}</p>"
        body += "<form method='post'>"
        body += f"<label>{msg['enter_phone']}<input name='phone' value='{phone}'></label><br>"
        if not otp:
            body += (
                f"<label>{msg['language_prompt']}<select name='lang'>"
                f"<option value='en'{' selected' if lang=='en' else ''}>English</option>"
                f"<option value='hi'{' selected' if lang=='hi' else ''}>हिन्दी</option>"
                "</select></label><br>"
            )
        else:
            body += f"<label>{msg['enter_otp']}<input name='otp'></label><br>"
            body += f"<input type='hidden' name='lang' value='{lang}'>"
        body += "<button type='submit'>Submit</button></form>"
        if error:
            body += f"<p style='color:red'>{error}</p>"
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(format_html(body, lang))

    def handle_register(self, params):
        phone = params.get('phone', [''])[0]
        otp_input = params.get('otp', [''])[0]
        lang = params.get('lang', ['en'])[0]
        if not otp_input:
            otp = str(random.randint(1000, 9999))
            self.server.pending = {'phone': phone, 'otp': otp, 'lang': lang}
            self.show_register(otp=otp, phone=phone, lang=lang)
        else:
            pending = getattr(self.server, 'pending', {})
            if phone == pending.get('phone') and otp_input == pending.get('otp'):
                lang = pending.get('lang', 'en')
                data = self.server.data
                data['user'] = {'phone': phone, 'language': lang}
                save_data(data)
                self.send_response(302)
                self.set_cookie('user', phone)
                self.set_cookie('lang', lang)
                self.send_header('Location', '/book')
                self.end_headers()
            else:
                self.show_register(error=MESSAGES[lang]['wrong_otp'], otp=pending.get('otp'), phone=phone, lang=lang)

    def show_book(self, error=None):
        cookies_in = self.get_cookies()
        if not cookies_in.get('user'):
            return self.redirect('/register')
        lang = cookies_in.get('lang', 'en')
        msg = MESSAGES[lang]
        body = f"<h1>{msg['new_booking']}</h1>"
        # Crop options localized
        if lang == 'hi':
            crop_options = [
                ('सेब', 'सेब'),
                ('टमाटर', 'टमाटर'),
                ('फूलगोभी', 'फूलगोभी'),
            ]
        else:
            crop_options = [
                ('Apple', 'Apple'),
                ('Tomato', 'Tomato'),
                ('Cauliflower', 'Cauliflower'),
            ]
        crop_select = f"<label>{msg['crop']}<select name='crop'>" + ''.join([
            f"<option value='{val}'>{disp}</option>" for val, disp in crop_options
        ]) + "</select></label><br>"
        # Field size unit options localized
        if lang == 'hi':
            unit_options = [
                ('बीघा', 'बीघा'),
                ('कनाल', 'कनाल'),
                ('एकड़', 'एकड़'),
            ]
        else:
            unit_options = [
                ('Bigha', 'Bigha'),
                ('Kanal', 'Kanal'),
                ('Acre', 'Acre'),
            ]
        unit_select = "<select name='field_unit'>" + ''.join([
            f"<option value='{val}'>{disp}</option>" for val, disp in unit_options
        ]) + "</select>"
        # Region options localized
        if lang == 'hi':
            region_options = [
                ('हिमाचल', 'हिमाचल'),
                ('उत्तर प्रदेश', 'उत्तर प्रदेश'),
                ('हरियाणा', 'हरियाणा'),
                ('उत्तराखंड', 'उत्तराखंड'),
            ]
        else:
            region_options = [
                ('Himachal', 'Himachal'),
                ('Uttar Pradesh', 'Uttar Pradesh'),
                ('Haryana', 'Haryana'),
                ('Uttarakhand', 'Uttarakhand'),
            ]
        village_data = {
            'en': {
                'Himachal': {
                    'Shimla': ['Mashobra', 'Rampur', 'Chopal'],
                    'Kangra': ['Dharamshala', 'Palampur', 'Nagrota'],
                    'Mandi': ['Sundernagar', 'Jogindernagar', 'Karsog'],
                },
                'Uttar Pradesh': {
                    'Lucknow': ['Gosainganj', 'Malihabad', 'Bakshi Ka Talab'],
                    'Kanpur': ['Bilhaur', 'Ghatampur', 'Sarsaul'],
                    'Varanasi': ['Cholapur', 'Araziline', 'Pindra'],
                },
                'Haryana': {
                    'Gurgaon': ['Sikanderpur', 'Badshahpur', 'Manesar'],
                    'Faridabad': ['Ballabgarh', 'Tigaon', 'Pali'],
                    'Panipat': ['Samalkha', 'Israna', 'Bapoli'],
                },
                'Uttarakhand': {
                    'Dehradun': ['Raipur', 'Vikasnagar', 'Doiwala'],
                    'Haridwar': ['Roorkee', 'Laksar', 'Bhagwanpur'],
                    'Nainital': ['Haldwani', 'Ramgarh', 'Betalghat'],
                },
            },
            'hi': {
                'हिमाचल': {
                    'शिमला': ['मशोबरा', 'रामपुर', 'चौपाल'],
                    'कांगड़ा': ['धर्मशाला', 'पालमपुर', 'नगरोटा'],
                    'मंडी': ['सुंदरनगर', 'जोगिंदरनगर', 'करसोग'],
                },
                'उत्तर प्रदेश': {
                    'लखनऊ': ['गोसाईगंज', 'मलिहाबाद', 'बक्शी का तालाब'],
                    'कानपुर': ['बिल्हौर', 'घाटमपुर', 'सरसौल'],
                    'वाराणसी': ['चोलापुर', 'अराजीलाइन', 'पिंडरा'],
                },
                'हरियाणा': {
                    'गुड़गांव': ['सिकंदरपुर', 'बादशाहपुर', 'मानेसर'],
                    'फरीदाबाद': ['बल्लभगढ़', 'टिगांव', 'पाली'],
                    'पानीपत': ['समालखा', 'इसराना', 'बापोली'],
                },
                'उत्तराखंड': {
                    'देहरादून': ['रायपुर', 'विकासनगर', 'डोईवाला'],
                    'हरिद्वार': ['रुड़की', 'लक्सर', 'भगवानपुर'],
                    'नैनीताल': ['हल्द्वानी', 'रामगढ़', 'बेतालघाट'],
                },
            }
        }
        region_select = f"<label>{msg['region']}<select id='state' name='region'>" + ''.join([
            f"<option value='{val}'>{disp}</option>" for val, disp in region_options
        ]) + "</select></label><br>"
        district_label = 'District' if lang == 'en' else 'जनपद'
        district_select = f"<label>{district_label}<select id='district' name='district'></select></label><br>"
        village_label = 'Village' if lang == 'en' else 'गांव'
        village_select = f"<label>{village_label}<select id='village' name='village'></select></label><br>"
        js_block = f"""
<script>
const VILLAGE_DATA = {json.dumps(village_data[lang], ensure_ascii=False)};
</script>
<script src='address_dropdown.js'></script>
"""
        body += (
            js_block +
            "<form method='post'>"
            f"{crop_select}"
            f"<label>{msg['field_size']}<select name='field_size' style='width:6em;'>"
            + ''.join([f"<option value='{i}'>{i}</option>" for i in range(1, 16)])
            + f"</select> {unit_select}</label><br>"
            f"{region_select}"
            f"{district_select}"
            f"{village_select}"
            f"<label>{msg['datetime']}<input name='datetime'></label><br>"
            "<button type='submit'>Submit</button></form>"
        )
        if error:
            body += f"<p style='color:red'>{error}</p>"
        body += (
            f"<p><a href='/history'>{msg['history']}</a> | <a href='/help'>{msg['menu_help']}</a></p>"
        )
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(format_html(body, lang))

    def handle_book(self, params):
        cookies_in = self.get_cookies()
        if not cookies_in.get('user'):
            return self.redirect('/register')
        lang = cookies_in.get('lang', 'en')
        try:
            dt = datetime.strptime(params.get('datetime', [''])[0], '%Y-%m-%d %H:%M')
        except ValueError:
            return self.show_book(error=MESSAGES[lang]['bad_date'])
        data = self.server.data
        booking = {
            'id': len(data['bookings']) + 1,
            'crop': params.get('crop', [''])[0],
            'field_size': params.get('field_size', [''])[0],
            'region': params.get('region', [''])[0],
            'datetime': dt.strftime('%Y-%m-%d %H:%M'),
            'status': 'Scheduled'
        }
        data['bookings'].append(booking)
        save_data(data)
        self.send_response(302)
        self.send_header('Location', '/history')
        self.end_headers()

    def show_history(self):
        cookies_in = self.get_cookies()
        if not cookies_in.get('user'):
            return self.redirect('/register')
        lang = cookies_in.get('lang', 'en')
        msg = MESSAGES[lang]
        data = self.server.data
        body = f"<h1>{msg['history']}</h1>"
        if not data['bookings']:
            body += f"<p>{msg['none']}</p>"
        else:
            body += '<ul>'
            for b in data['bookings']:
                item = f"#{b['id']} | {b['crop']} | {b['field_size']}ha | {b['region']} | {b['datetime']} | {b['status']}"
                body += f'<li>{item}</li>'
            body += '</ul>'
        body += f"<p><a href='/book'>{msg['menu_booking']}</a> | <a href='/help'>{msg['menu_help']}</a></p>"
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(format_html(body, lang))

    def show_help(self):
        cookies_in = self.get_cookies()
        lang = cookies_in.get('lang', 'en')
        msg = MESSAGES[lang]
        body = (
            f"<h1>{msg['menu_help']}</h1>"
            f"<p>{msg['phone']}</p>"
            f"<p>{msg['email'].strip()}</p>"
            f"<p><a href='/book'>{msg['menu_booking']}</a></p>"
        )
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(format_html(body, lang))


def run(port=8000):
    server = HTTPServer(('', port), FlyAIHandler)
    server.data = load_data()
    server.pending = {}
    print(f"Server running on http://localhost:{port}/register")
    server.serve_forever()


if __name__ == '__main__':
    run()
