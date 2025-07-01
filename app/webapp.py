# Minimal web server for FlyAI using only standard library
import os
import random
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from http import cookies

from .flyai import load_data, save_data


def format_html(body: str) -> bytes:
    """Wrap body in basic HTML structure and encode to bytes."""
    html = (
        "<!doctype html><html lang='hi'><meta charset='utf-8'>"
        f"<body>{body}</body></html>"
    )
    return html.encode('utf-8')


class FlyAIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
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
        if self.path.startswith('/register'):
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
    def show_register(self, error=None, otp=None, phone=''):
        cookies_in = self.get_cookies()
        if cookies_in.get('user'):
            return self.redirect('/book')
        body = '<h1>उपयोगकर्ता पंजीकरण</h1>'
        if otp:
            body += f'<p>आपका OTP: {otp}</p>'
        body += (
            "<form method='post'>"
            f"<label>मोबाइल नंबर: <input name='phone' value='{phone}'></label><br>"
        )
        if otp:
            body += "<label>OTP: <input name='otp'></label><br>"
        body += "<button type='submit'>जमा करें</button></form>"
        if error:
            body += f"<p style='color:red'>{error}</p>"
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(format_html(body))

    def handle_register(self, params):
        phone = params.get('phone', [''])[0]
        otp_input = params.get('otp', [''])[0]
        if not otp_input:
            otp = str(random.randint(1000, 9999))
            self.server.pending = {'phone': phone, 'otp': otp}
            self.show_register(otp=otp, phone=phone)
        else:
            pending = getattr(self.server, 'pending', {})
            if phone == pending.get('phone') and otp_input == pending.get('otp'):
                data = self.server.data
                data['user'] = {'phone': phone, 'language': 'hi'}
                save_data(data)
                self.send_response(302)
                self.set_cookie('user', phone)
                self.send_header('Location', '/book')
                self.end_headers()
            else:
                self.show_register(error='गलत OTP', otp=pending.get('otp'), phone=phone)

    def show_book(self, error=None):
        cookies_in = self.get_cookies()
        if not cookies_in.get('user'):
            return self.redirect('/register')
        body = '<h1>नई स्प्रे बुकिंग</h1>'
        body += (
            "<form method='post'>"
            "<label>फ़सल का प्रकार: <input name='crop'></label><br>"
            "<label>क्षेत्रफल (हेक्टेयर): <input name='field_size'></label><br>"
            "<label>क्षेत्र: <input name='region'></label><br>"
            "<label>तारीख/समय (YYYY-MM-DD HH:MM): <input name='datetime'></label><br>"
            "<button type='submit'>बुक करें</button></form>"
        )
        if error:
            body += f"<p style='color:red'>{error}</p>"
        body += "<p><a href='/history'>इतिहास देखें</a> | <a href='/help'>सहायता</a></p>"
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(format_html(body))

    def handle_book(self, params):
        cookies_in = self.get_cookies()
        if not cookies_in.get('user'):
            return self.redirect('/register')
        try:
            dt = datetime.strptime(params.get('datetime', [''])[0], '%Y-%m-%d %H:%M')
        except ValueError:
            return self.show_book(error='गलत तारीख प्रारूप')
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
        data = self.server.data
        body = '<h1>बुकिंग इतिहास</h1>'
        if not data['bookings']:
            body += '<p>कोई बुकिंग नहीं।</p>'
        else:
            body += '<ul>'
            for b in data['bookings']:
                item = f"#{b['id']} | {b['crop']} | {b['field_size']}ha | {b['region']} | {b['datetime']} | {b['status']}"
                body += f'<li>{item}</li>'
            body += '</ul>'
        body += "<p><a href='/book'>नई बुकिंग</a> | <a href='/help'>सहायता</a></p>"
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(format_html(body))

    def show_help(self):
        body = (
            '<h1>सहायता</h1>'
            '<p>फोन: 1800-000-000</p>'
            '<p>ईमेल: support@flyai.example.com</p>'
            "<p><a href='/book'>पीछे जाएं</a></p>"
        )
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(format_html(body))


def run(port=8000):
    server = HTTPServer(('', port), FlyAIHandler)
    server.data = load_data()
    server.pending = {}
    print(f"Server running on http://localhost:{port}/register")
    server.serve_forever()


if __name__ == '__main__':
    run()
