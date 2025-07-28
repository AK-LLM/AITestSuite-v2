import http.server
import socketserver
import threading
import random

PORT = random.randint(9000, 9999)
Handler = http.server.SimpleHTTPRequestHandler

def run_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"[+] Burner C2 server running at port {PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    input("[*] Press Enter to tear down C2...")
    print("[*] C2 teardown complete.")
