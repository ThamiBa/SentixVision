"""
MJPEG Streaming Server
Serves live video frames as an MJPEG stream on port 5002.
Dynamic host detection included for network/multi-device access.
"""
import cv2
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import socketserver
import numpy as np

_MJPEG_PORT = 5002
_server_started = False
_server_lock = threading.Lock()
_manager_ref = None

class _MJPEGHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass 

    def do_GET(self):
        if self.path.startswith('/stream'):
            print(f"[MJPEG] Client connected: {self.client_address}")
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=--frame')
            self.send_header('Cache-Control', 'no-cache, private, max-age=0, no-store, must-revalidate')
            self.send_header('Access-Control-Allow-Origin', '*') 
            self.end_headers()
            try:
                while True:
                    frame = _manager_ref.latest_frame if _manager_ref else None
                    
                    if frame is None:
                        # Send a standard black placeholder to keep connection alive
                        frame = np.zeros((480, 640, 3), dtype=np.uint8)
                        cv2.putText(frame, "WAITING FOR CAMERA...", (160, 240), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    
                    _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    blob = buf.tobytes()
                    
                    self.wfile.write(b'--frame\r\n')
                    self.wfile.write(b'Content-Type: image/jpeg\r\n')
                    self.wfile.write(f'Content-Length: {len(blob)}\r\n\r\n'.encode())
                    self.wfile.write(blob)
                    self.wfile.write(b'\r\n')
                    time.sleep(0.05) # ~20 FPS
            except Exception as e:
                print(f"[MJPEG] Client disconnected ({self.client_address}): {e}")
                pass
        else:
            self.send_response(404)
            self.end_headers()

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

def start_mjpeg_server(manager):
    global _server_started, _manager_ref
    with _server_lock:
        _manager_ref = manager
        if _server_started:
            return
        _server_started = True

    def _run():
        try:
            server = ThreadedHTTPServer(('0.0.0.0', _MJPEG_PORT), _MJPEGHandler)
            server.serve_forever()
        except Exception as e:
            print(f"[MJPEG] Error: {e}")

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    print(f"[MJPEG] Stream available on port {_MJPEG_PORT}")

def get_lan_ip():
    """Detects the LAN IP of this machine to help clients find the MJPEG server."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def get_stream_html():
    """Returns HTML with JS to detect the server's IP automatically."""
    return f"""
    <div id="container" style="width:100%; height:100%; background:#000; display:flex; align-items:center; justify-content:center; border-radius:12px;">
        <img id="stream-img" style="max-width:100%; max-height:100%; object-fit:contain;" src="" />
        <div id="error-msg" style="display:none; color:#D4AF37; font-family:sans-serif; text-align:center;">
            Connection Lost<br><small>Retrying live feed...</small>
        </div>
    </div>
    <script>
        // Use the same hostname as the Streamlit app
        const host = window.location.hostname;
        const img = document.getElementById('stream-img');
        const err = document.getElementById('error-msg');
        
        function loadStream() {{
            img.src = "http://" + host + ":{_MJPEG_PORT}/stream?t=" + Date.now();
            img.style.display = 'block';
            err.style.display = 'none';
        }}

        img.onerror = () => {{
            img.style.display = 'none';
            err.style.display = 'block';
            setTimeout(loadStream, 2000);
        }};

        loadStream();
    </script>
    """
