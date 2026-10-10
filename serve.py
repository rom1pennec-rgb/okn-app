import http.server
import socketserver
import json
import os
import socket

PORT = 8000
STORE = {}

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/state/'):
            code = self.path.split('/api/state/')[1].split('?')[0]
            data = STORE.get(code)
            body = json.dumps(data).encode('utf-8') if data is not None else b'null'
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith('/api/info'):
            body = json.dumps({'ip': get_local_ip(), 'port': PORT}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def do_PUT(self):
        if self.path.startswith('/api/state/'):
            code = self.path.split('/api/state/')[1].split('?')[0]
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                STORE[code] = json.loads(body)
            except Exception:
                pass
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,PUT,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        pass  # console silencieuse

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    ip = get_local_ip()
    print("")
    print("=========================================================")
    print(" Serveur de reeducation optocinetique demarre !")
    print("=========================================================")
    print(f" Sur cet ordinateur (therapeute) : http://localhost:{PORT}")
    print(f" Sur le casque / telephone (meme Wi-Fi) : http://{ip}:{PORT}")
    print("")
    print(" Laissez cette fenetre ouverte pendant toute la seance.")
    print(" Fermez-la (ou Ctrl+C) pour arreter le serveur.")
    print("=========================================================")
    print("")
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        httpd.serve_forever()
