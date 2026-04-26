#!/usr/bin/env python3
# Author: Sean Pesce

# The following project was used as a reference implementation for the HTTP-based MPJEG stream:
# https://github.com/damiencorpataux/pymjpeg

# Use the following shell command to create a self-signed TLS certificate and private key:
#    openssl req -new -newkey rsa:4096 -x509 -sha256 -days 365 -nodes -out cert.crt -keyout private.key


import html
import http.server
import queue
import socket
import ssl
import sys
import threading
import time

from io import BytesIO

import suear_struct
from suear_util import ping


class HttpHandler(http.server.BaseHTTPRequestHandler):
    BOUNDARY = b'--SP-LaputanMachine--'
    SUEAR_CLIENT = None
    RENDER_RATE = 0  # One frame is rendered locally (with MatPlotLib) for every RENDER_RATE frames sent to the HTTP client (Set to <1 to never render locally)
    PROTOCOL = 'http'
    PORT = 45100
    
    
    @classmethod
    def HEADERS_BASE(cls):
        headers = {
            'Cache-Control': 'no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0',
            'Content-Type': f'multipart/x-mixed-replace;boundary={cls.BOUNDARY.decode("ascii")}',
            #'Connection': 'close',
            'Pragma': 'no-cache',
            'Access-Control-Allow-Origin': '*',  # CORS
        }
        return headers
    
    
    @classmethod
    def HEADERS_IMAGE(cls, length):
        headers = {
            'X-Timestamp': time.time(),
            'Content-Length': str(int(length)),
            'Content-Type': 'image/jpeg',
        }
        return headers
    
    
    def do_GET(self):
        print(self.headers['Host'])
        suear_client = self.__class__.SUEAR_CLIENT
        
        if self.path == '/favicon.ico':
            self.send_response(204)  # No Content
            self.send_header('Connection', 'close')
            self.end_headers()
            return
        
        if self.path not in ('/', '/stream', '/battery', '/model', '/vendor', '/version', '/ssid', '/capacity', '/charging', '/serial', '/status', '/viewers'):
            self.send_response(404)
            self.send_header('Connection', 'close')
            self.end_headers()
            return
        
        if suear_client is None:
            self.send_response(503)  # Service Unavailable
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(b'Error: Suear client unavailable')
            return
            
        
        self.send_response(200)
        self.send_header('Connection', 'close')
        
        # Status endpoint to check if device is connected
        if self.path == '/status':
            try:
                # Try to get device info to check connection
                battery = suear_client.battery_level
                data = b'{"connected": true}'
            except:
                data = b'{"connected": false}'
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(data))
            self.end_headers()
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                pass
            return
        
        if self.path == '/viewers':
            viewer_count = suear_client.stream_clients
            data = str(viewer_count).encode('ascii')
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(data))
            self.end_headers()
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                pass
            return
        
        # For other endpoints, try to get battery level but don't fail
        try:
            self.send_header('X-Battery', str(suear_client.battery_level))
        except:
            pass
        
        if self.path == '/battery':
            try:
                data = html.escape(str(suear_client.battery_level)).encode('ascii')
            except:
                data = b'0'
            self.send_header('Content-Length', len(data))
            self.end_headers()
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                pass
            return
        
        elif self.path == '/model':
            try:
                data = html.escape(str(suear_client.model)).encode('ascii')
            except:
                data = b'N/A'
            self.send_header('Content-Length', len(data))
            self.end_headers()
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                pass
            return
        
        elif self.path == '/serial':
            try:
                data = html.escape(str(suear_client.serial_num)).encode('ascii')
            except:
                data = b'N/A'
            self.send_header('Content-Length', len(data))
            self.end_headers()
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                pass
            return
        
        elif self.path == '/vendor':
            try:
                data = html.escape(str(suear_client.vendor)).encode('ascii')
            except:
                data = b'N/A'
            self.send_header('Content-Length', len(data))
            self.end_headers()
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                pass
            return
        
        elif self.path == '/version':
            try:
                data = html.escape(str(suear_client.version)).encode('ascii')
            except:
                data = b'N/A'
            self.send_header('Content-Length', len(data))
            self.end_headers()
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                pass
            return
        
        elif self.path == '/ssid':
            try:
                data = html.escape(str(suear_client.ssid)).encode('ascii')
            except:
                data = b'N/A'
            self.send_header('Content-Length', len(data))
            self.end_headers()
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                pass
            return
        
        elif self.path == '/capacity':
            try:
                data = html.escape(str(suear_client.capacity)).encode('ascii')
            except:
                data = b'0'
            self.send_header('Content-Length', len(data))
            self.end_headers()
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                pass
            return
        
        elif self.path == '/charging':
            try:
                data = html.escape(str(int(suear_client.is_charging))).encode('ascii')
            except:
                data = b'0'
            self.send_header('Content-Length', len(data))
            self.end_headers()
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                pass
            return
        
        elif self.path == '/':
            # Try to get device info, but use defaults if not connected
            try:
                vendor = html.escape(suear_client.vendor)
                model = html.escape(suear_client.model)
                version = html.escape(suear_client.version)
                serial = html.escape(suear_client.serial_num)
                ssid = html.escape(suear_client.ssid)
                battery_level = suear_client.battery_level
                capacity = html.escape(str(suear_client.capacity))
                is_charging = suear_client.is_charging
            except:
                vendor = "N/A"
                model = "N/A"
                version = "N/A"
                serial = "N/A"
                ssid = "N/A"
                battery_level = 0
                capacity = "0"
                is_charging = False
            
            # Generate stream URL
            stream_url = f"{self.__class__.PROTOCOL.lower()}://{html.escape(self.headers['Host'])}/stream"
            charging_text = "⚡ Charging" if is_charging else "🔌 Not Charging"
            
            html_data = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <title>Suear Video Stream - Advanced Control Panel</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            min-height: 100vh;
            padding: 10px;
            overflow-x: hidden;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 20px;
            animation: fadeInDown 0.8s ease;
        }}
        
        .header h1 {{
            font-size: clamp(1.5rem, 5vw, 2.5rem);
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            margin-bottom: 5px;
        }}
        
        .header p {{
            font-size: clamp(0.9rem, 3vw, 1rem);
        }}
        
        .connection-banner {{
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(255, 107, 107, 0.5);
            display: none;
            animation: shake 0.5s ease;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }}
        
        .connection-banner.show {{
            display: block;
        }}
        
        .connection-banner h3 {{
            margin-bottom: 12px;
            font-size: clamp(1.1rem, 4vw, 1.3rem);
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .connection-banner p {{
            font-size: clamp(0.9rem, 3vw, 1rem);
            line-height: 1.6;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }}
        
        .main-content {{
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 15px;
            animation: fadeIn 1s ease;
        }}
        
        .video-section {{
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }}
        
        .video-section h3 {{
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        
        .video-container {{
            position: relative;
            background: #000;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            margin-bottom: 15px;
            touch-action: pan-x pan-y;
        }}
        
        .video-container:fullscreen {{
            border-radius: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .video-container:-webkit-full-screen {{
            border-radius: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .video-container:-moz-full-screen {{
            border-radius: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .video-container:fullscreen #video-stream {{
            max-width: 100vw;
            max-height: 100vh;
            width: auto;
            height: auto;
        }}
        
        /* iOS fullscreen fallback */
        .ios-fullscreen {{
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            z-index: 9999 !important;
            background: #000 !important;
            border-radius: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}
        
        .ios-fullscreen #video-stream {{
            max-width: 100vw;
            max-height: 100vh;
            width: auto;
            height: auto;
            object-fit: contain;
        }}
        
        .ios-fullscreen-body {{
            overflow: hidden !important;
        }}
        
        #video-stream {{
            width: 100%;
            height: auto;
            display: block;
            transition: transform 0.3s ease;
        }}
        
        .video-overlay {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0,0,0,0.85);
            padding: 6px 12px;
            border-radius: 15px;
            font-size: clamp(0.75rem, 2.5vw, 0.9rem);
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 10;
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .status-indicator {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00ff00;
            animation: pulse 2s infinite;
        }}
        
        .status-indicator.disconnected {{
            background: #ff6b6b;
            animation: none;
        }}
        
        .controls-panel {{
            background: rgba(255, 255, 255, 0.95);
            color: #333;
            border-radius: 15px;
            padding: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }}
        
        .control-section {{
            margin-bottom: 20px;
        }}
        
        .control-section:last-child {{
            margin-bottom: 0;
        }}
        
        .control-section h3 {{
            font-size: clamp(1rem, 4vw, 1.2rem);
            margin-bottom: 12px;
            color: #667eea;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .video-section .control-section h3 {{
            color: white;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        
        .battery-display {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 15px;
            color: white;
            margin-bottom: 12px;
        }}
        
        .battery-level {{
            font-size: clamp(2rem, 8vw, 2.5rem);
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        }}
        
        .battery-bar-container {{
            background: rgba(255,255,255,0.3);
            height: 35px;
            border-radius: 20px;
            overflow: hidden;
            position: relative;
            margin-bottom: 10px;
        }}
        
        .battery-bar {{
            height: 100%;
            background: linear-gradient(90deg, #00ff87 0%, #60efff 100%);
            border-radius: 20px;
            transition: width 0.5s ease, background 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #000;
            box-shadow: 0 0 20px rgba(96, 239, 255, 0.5);
            min-width: 2%;
        }}
        
        .battery-bar.low {{
            background: linear-gradient(90deg, #ff6b6b 0%, #ee5a6f 100%);
        }}
        
        .battery-bar.charging {{
            animation: charging 2s infinite;
        }}
        
        .charging-status {{
            text-align: center;
            font-size: clamp(0.8rem, 3vw, 0.9rem);
            opacity: 0.9;
        }}
        
        .device-info {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 12px;
        }}
        
        .info-row {{
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px solid #e0e0e0;
            font-size: clamp(0.85rem, 3vw, 0.95rem);
        }}
        
        .info-row:last-child {{
            border-bottom: none;
        }}
        
        .info-label {{
            font-weight: 600;
            color: #666;
        }}
        
        .info-value {{
            color: #333;
            text-align: right;
            word-break: break-all;
            max-width: 60%;
        }}
        
        .button-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
            margin-top: 12px;
        }}
        
        .control-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 15px;
            border-radius: 10px;
            font-size: clamp(0.85rem, 3vw, 1rem);
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            -webkit-user-select: none;
            user-select: none;
        }}
        
        .control-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }}
        
        .control-btn:active {{
            transform: translateY(0);
        }}
        
        .control-btn.active {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        
        .reconnect-btn {{
            width: 100%;
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            font-weight: bold;
            font-size: clamp(0.95rem, 4vw, 1.1rem);
            padding: 15px;
        }}
        
        .reset-btn {{
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-top: 8px;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        @keyframes charging {{
            0% {{ box-shadow: 0 0 20px rgba(96, 239, 255, 0.5); }}
            50% {{ box-shadow: 0 0 40px rgba(96, 239, 255, 1); }}
            100% {{ box-shadow: 0 0 20px rgba(96, 239, 255, 0.5); }}
        }}
        
        @keyframes shake {{
            0%, 100% {{ transform: translateX(0); }}
            25% {{ transform: translateX(-10px); }}
            75% {{ transform: translateX(10px); }}
        }}
        
        @media (max-width: 1024px) {{
            .main-content {{
                grid-template-columns: 1fr;
            }}
            
            .controls-panel {{
                order: -1;
            }}
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 5px;
            }}
            
            .video-section, .controls-panel {{
                padding: 10px;
            }}
            
            .button-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .notification {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 12px 20px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            display: none;
            z-index: 1000;
            animation: slideInRight 0.3s ease;
            font-size: clamp(0.85rem, 3vw, 0.95rem);
            max-width: 90%;
        }}
        
        @keyframes slideInRight {{
            from {{
                transform: translateX(400px);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎥 Suear Video Stream Viewer</h1>
            <p>Advanced Control Panel</p>
        </div>
        
        <div class="connection-banner" id="connection-banner">
            <h3>⚠️ Camera Not Connected</h3>
            <p>
                Please connect to your camera's WiFi network (usually starts with "Suear" or similar).<br>
                After connecting, refresh this page or click the Reconnect Stream button below.
            </p>
        </div>
        
        <div class="main-content">
            <div class="video-section">
                <div class="video-container">
                    <div class="video-overlay">
                        <div class="status-indicator" id="status-indicator"></div>
                        <span id="status-text">LIVE</span>
                        <span id="viewer-count" style="margin-left: 10px; font-size: 14px;">👁️ 0</span>
                    </div>
                    <div class="video-overlay" style="top: auto; bottom: 10px; left: 10px; display: none;" id="zoom-indicator">
                        🔍 <span id="zoom-level">100</span>%
                    </div>
                    <img id="video-stream" src="{stream_url}" alt="Video Stream">
                </div>
                
                <div class="control-section">
                    <h3>🎮 Camera Controls</h3>
                    <div class="button-grid">
                        <button class="control-btn" onclick="toggleFlipH()">
                            ↔️ Flip Horizontal
                        </button>
                        <button class="control-btn" onclick="toggleFlipV()">
                            ↕️ Flip Vertical
                        </button>
                        <button class="control-btn" onclick="rotateLeft()">
                            ↺ Rotate Left
                        </button>
                        <button class="control-btn" onclick="rotateRight()">
                            ↻ Rotate Right
                        </button>
                        <button class="control-btn" onclick="toggleFullscreen()">
                            ⛶ Fullscreen
                        </button>
                        <button class="control-btn" onclick="takeScreenshot()">
                            📸 Screenshot
                        </button>
                        <button class="control-btn" onclick="zoomIn()">
                            🔍+ Zoom In
                        </button>
                        <button class="control-btn" onclick="zoomOut()">
                            🔍- Zoom Out
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="controls-panel">
                <div class="control-section">
                    <h3>🔋 Battery Status</h3>
                    <div class="battery-display">
                        <div class="battery-level">
                            <span id="battery_lvl">{battery_level}</span>%
                        </div>
                        <div class="battery-bar-container">
                            <div class="battery-bar" id="battery-bar" style="width: {battery_level}%">
                            </div>
                        </div>
                        <div class="charging-status">
                            <span id="is_charging">{charging_text}</span>
                        </div>
                    </div>
                </div>
                
                <div class="control-section">
                    <h3>📱 Device Information</h3>
                    <div class="device-info">
                        <div class="info-row">
                            <span class="info-label">Vendor</span>
                            <span class="info-value" id="vendor">{vendor}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Model</span>
                            <span class="info-value" id="model">{model}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Version</span>
                            <span class="info-value" id="version">{version}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Serial</span>
                            <span class="info-value" id="serial">{serial}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">SSID</span>
                            <span class="info-value" id="ssid">{ssid}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Capacity</span>
                            <span class="info-value" id="capacity">{capacity} mAh</span>
                        </div>
                    </div>
                </div>
                
                <div class="control-section">
                    <h3>⚙️ Connection</h3>
                    <button class="control-btn reconnect-btn" onclick="reconnect()">
                        🔄 Reconnect Stream
                    </button>
                    <button class="control-btn reset-btn" onclick="resetTransforms()">
                        ♻️ Reset View
                    </button>
                </div>
                
                <div class="control-section" style="background: #f8f9fa; border-radius: 10px; padding: 12px; font-size: 0.85rem; color: #666;">
                    <h3 style="color: #667eea;">⌨️ Keyboard Shortcuts</h3>
                    <div style="line-height: 1.8;">
                        <b>F</b> - Fullscreen<br>
                        <b>S</b> - Screenshot<br>
                        <b>R</b> - Reconnect<br>
                        <b>+/-</b> - Zoom In/Out<br>
                        <b>0</b> - Reset View<br>
                        <i>💡 Pinch to zoom on mobile</i>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="notification" id="notification"></div>
    
            <script>
        // Transform state
        let flipH = false;
        let flipV = false;
        let rotation = 0;
        let zoomLevel = 1;
        let isConnected = false;
        
        // Utility function to escape HTML
        function escapeHtml(unsafe) {{
                return unsafe
                    .replace(/&/g, "&amp;")
                    .replace(/</g, "&lt;")
                    .replace(/>/g, "&gt;")
                    .replace(/"/g, "&quot;")
                    .replace(/'/g, "&#039;");
        }}
        
        // Show notification
        function showNotification(message) {{
            const notif = document.getElementById('notification');
            notif.textContent = message;
            notif.style.display = 'block';
            setTimeout(function() {{
                notif.style.display = 'none';
            }}, 3000);
        }}
        
        // Apply transforms to video
        function applyTransforms() {{
            const video = document.getElementById('video-stream');
            let transform = '';
            
            if (flipH) transform += 'scaleX(-1) ';
            if (flipV) transform += 'scaleY(-1) ';
            transform += 'rotate(' + rotation + 'deg) scale(' + zoomLevel + ')';
            
            video.style.transform = transform;
        }}
        
        // Camera control functions
        function toggleFlipH() {{
            flipH = !flipH;
            applyTransforms();
            showNotification(flipH ? 'Horizontal flip enabled' : 'Horizontal flip disabled');
        }}
        
        function toggleFlipV() {{
            flipV = !flipV;
            applyTransforms();
            showNotification(flipV ? 'Vertical flip enabled' : 'Vertical flip disabled');
        }}
        
        function rotateLeft() {{
            rotation -= 90;
            if (rotation <= -360) rotation = 0;
            applyTransforms();
            showNotification('Rotated left to ' + rotation + '°');
        }}
        
        function rotateRight() {{
            rotation += 90;
            if (rotation >= 360) rotation = 0;
            applyTransforms();
            showNotification('Rotated right to ' + rotation + '°');
        }}
        
        function updateZoomIndicator() {{
            const zoomIndicator = document.getElementById('zoom-indicator');
            const zoomLevelText = document.getElementById('zoom-level');
            zoomLevelText.textContent = Math.round(zoomLevel * 100);
            
            if (zoomLevel !== 1) {{
                zoomIndicator.style.display = 'flex';
            }} else {{
                zoomIndicator.style.display = 'none';
            }}
        }}
        
        function zoomIn() {{
            if (zoomLevel < 3) {{
                zoomLevel += 0.25;
                applyTransforms();
                updateZoomIndicator();
                showNotification('Zoom: ' + Math.round(zoomLevel * 100) + '%');
            }} else {{
                showNotification('Maximum zoom reached');
            }}
        }}
        
        function zoomOut() {{
            if (zoomLevel > 0.5) {{
                zoomLevel -= 0.25;
                applyTransforms();
                updateZoomIndicator();
                showNotification('Zoom: ' + Math.round(zoomLevel * 100) + '%');
            }} else {{
                showNotification('Minimum zoom reached');
            }}
        }}
        
        function resetTransforms() {{
            flipH = false;
            flipV = false;
            rotation = 0;
            zoomLevel = 1;
            applyTransforms();
            updateZoomIndicator();
            showNotification('View reset to default');
        }}
        
        function toggleFullscreen() {{
            const container = document.querySelector('.video-container');
            const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
            
            // Check if already in fullscreen (either native or iOS fallback)
            const inFullscreen = document.fullscreenElement || document.webkitFullscreenElement || 
                                document.mozFullScreenElement || container.classList.contains('ios-fullscreen');
            
            if (!inFullscreen) {{
                // Enter fullscreen
                if (isIOS) {{
                    // iOS fallback - use CSS to simulate fullscreen
                    container.classList.add('ios-fullscreen');
                    document.body.classList.add('ios-fullscreen-body');
                    showNotification('Entered fullscreen mode');
                }} else if (container.requestFullscreen) {{
                    container.requestFullscreen();
                    showNotification('Entered fullscreen mode');
                }} else if (container.webkitRequestFullscreen) {{
                    container.webkitRequestFullscreen();
                    showNotification('Entered fullscreen mode');
                }} else if (container.mozRequestFullScreen) {{
                    container.mozRequestFullScreen();
                    showNotification('Entered fullscreen mode');
                }} else if (container.msRequestFullscreen) {{
                    container.msRequestFullscreen();
                    showNotification('Entered fullscreen mode');
                }} else {{
                    // Fallback for browsers without fullscreen support
                    container.classList.add('ios-fullscreen');
                    document.body.classList.add('ios-fullscreen-body');
                    showNotification('Entered fullscreen mode');
                }}
            }} else {{
                // Exit fullscreen
                if (container.classList.contains('ios-fullscreen')) {{
                    // iOS fallback exit
                    container.classList.remove('ios-fullscreen');
                    document.body.classList.remove('ios-fullscreen-body');
                    showNotification('Exited fullscreen mode');
                }} else if (document.exitFullscreen) {{
                    document.exitFullscreen();
                    showNotification('Exited fullscreen mode');
                }} else if (document.webkitExitFullscreen) {{
                    document.webkitExitFullscreen();
                    showNotification('Exited fullscreen mode');
                }} else if (document.mozCancelFullScreen) {{
                    document.mozCancelFullScreen();
                    showNotification('Exited fullscreen mode');
                }} else if (document.msExitFullscreen) {{
                    document.msExitFullscreen();
                    showNotification('Exited fullscreen mode');
                }}
            }}
        }}
        
        function takeScreenshot() {{
            const video = document.getElementById('video-stream');
            const canvas = document.createElement('canvas');
            
            // Set canvas dimensions to match image
            canvas.width = video.naturalWidth || video.width;
            canvas.height = video.naturalHeight || video.height;
            
            const ctx = canvas.getContext('2d');
            
            // Apply same transforms to canvas
            ctx.save();
            ctx.translate(canvas.width / 2, canvas.height / 2);
            
            if (flipH) ctx.scale(-1, 1);
            if (flipV) ctx.scale(1, -1);
            ctx.rotate(rotation * Math.PI / 180);
            ctx.scale(zoomLevel, zoomLevel);
            
            ctx.translate(-canvas.width / 2, -canvas.height / 2);
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            ctx.restore();
            
            // Download the screenshot
            canvas.toBlob(function(blob) {{
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
                a.href = url;
                a.download = 'suear-screenshot-' + timestamp + '.png';
                a.click();
                URL.revokeObjectURL(url);
                showNotification('Screenshot saved!');
            }}, 'image/png');
        }}
        
        function reconnect() {{
            // Check if video is already loading/playing
            const video = document.getElementById('video-stream');
            if (video.complete && video.naturalWidth > 0) {{
                showNotification('Stream is already active!');
                return;
            }}
            
            showNotification('Reconnecting stream...');
            const src = video.src;
            video.src = '';
            setTimeout(function() {{
                video.src = src;
                checkConnectionStatus();
                updateViewerCount();
            }}, 500);
        }}
        
        function updateViewerCount() {{
            fetch('/viewers')
                .then(function(response) {{ return response.text(); }})
                .then(function(count) {{
                    const viewerElement = document.getElementById('viewer-count');
                    if (viewerElement) {{
                        viewerElement.textContent = '👁️ ' + count;
                    }}
                }})
                .catch(function() {{
                    // Silently fail if we can't get viewer count
                }});
        }}
        
        // Check connection status
        function checkConnectionStatus() {{
            fetch('/status')
                .then(function(response) {{ return response.json(); }})
                .then(function(data) {{
                    const banner = document.getElementById('connection-banner');
                    const statusIndicator = document.getElementById('status-indicator');
                    const statusText = document.getElementById('status-text');
                    const wasConnected = isConnected;
                    
                    isConnected = data.connected;
                    
                    if (isConnected) {{
                        banner.classList.remove('show');
                        statusIndicator.classList.remove('disconnected');
                        statusText.textContent = 'LIVE';
                        
                        // If we just connected, reconnect the stream
                        if (!wasConnected) {{
                            showNotification('Camera connected! Reconnecting stream...');
                            setTimeout(function() {{
                                reconnect();
                            }}, 1000);
                        }}
                    }} else {{
                        banner.classList.add('show');
                        statusIndicator.classList.add('disconnected');
                        statusText.textContent = 'OFFLINE';
                    }}
                }})
                .catch(function(err) {{
                    console.error('Error checking connection status:', err);
                    const banner = document.getElementById('connection-banner');
                    banner.classList.add('show');
                    isConnected = false;
                }});
        }}
        
        // Update battery display
        function updateBatteryDisplay(level, charging) {{
            const batteryBar = document.getElementById('battery-bar');
            const batteryLvl = document.getElementById('battery_lvl');
            const chargingStatus = document.getElementById('is_charging');
            
            batteryLvl.textContent = level;
            batteryBar.style.width = level + '%';
            
            // Update battery color based on level
            batteryBar.classList.remove('low', 'charging');
            if (level <= 20) {{
                batteryBar.classList.add('low');
            }}
            
            if (charging === "1") {{
                batteryBar.classList.add('charging');
                chargingStatus.innerHTML = '⚡ Charging';
            }} else {{
                chargingStatus.innerHTML = '🔌 Not Charging';
            }}
        }}
        
        // Update device info
        function updateDeviceInfo() {{
            fetch('/vendor').then(function(r) {{ return r.text(); }}).then(function(data) {{
                document.getElementById('vendor').textContent = data;
            }}).catch(function() {{}});
            
            fetch('/model').then(function(r) {{ return r.text(); }}).then(function(data) {{
                document.getElementById('model').textContent = data;
            }}).catch(function() {{}});
            
            fetch('/version').then(function(r) {{ return r.text(); }}).then(function(data) {{
                document.getElementById('version').textContent = data;
            }}).catch(function() {{}});
            
            fetch('/serial').then(function(r) {{ return r.text(); }}).then(function(data) {{
                document.getElementById('serial').textContent = data;
            }}).catch(function() {{}});
            
            fetch('/ssid').then(function(r) {{ return r.text(); }}).then(function(data) {{
                document.getElementById('ssid').textContent = data;
            }}).catch(function() {{}});
            
            fetch('/capacity').then(function(r) {{ return r.text(); }}).then(function(data) {{
                document.getElementById('capacity').textContent = data + ' mAh';
            }}).catch(function() {{}});
        }}
        
        // Battery, connection, and viewer count update interval
        setInterval(function() {{
            // Check connection status
            checkConnectionStatus();
            
            // Update viewer count
            updateViewerCount();
            
            // Update battery level
            fetch('/battery')
                .then(function(response) {{ return response.text(); }})
                .then(function(level) {{
                    fetch('/charging')
                        .then(function(response) {{ return response.text(); }})
                        .then(function(charging) {{
                            updateBatteryDisplay(level, charging);
                        }})
                        .catch(function(err) {{ console.error('Error fetching charging status:', err); }});
                }})
                .catch(function(err) {{ console.error('Error fetching battery level:', err); }});
            
            // Update device info if connected
            if (isConnected) {{
                updateDeviceInfo();
            }}
        }}, 5000);
        
        // Initial status check
        checkConnectionStatus();
        
        // Handle video stream errors
        document.getElementById('video-stream').addEventListener('error', function() {{
            showNotification('Stream connection lost. Click Reconnect.');
            checkConnectionStatus();
        }});
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'f' || e.key === 'F') {{
                toggleFullscreen();
            }} else if (e.key === 's' || e.key === 'S') {{
                takeScreenshot();
            }} else if (e.key === 'r' || e.key === 'R') {{
                reconnect();
            }} else if (e.key === '+' || e.key === '=') {{
                zoomIn();
            }} else if (e.key === '-' || e.key === '_') {{
                zoomOut();
            }} else if (e.key === '0') {{
                resetTransforms();
            }}
        }});
        
        // Touch gestures for mobile zoom
        let touchStartDistance = 0;
        const videoContainer = document.querySelector('.video-container');
        
        videoContainer.addEventListener('touchstart', function(e) {{
            if (e.touches.length === 2) {{
                touchStartDistance = Math.hypot(
                    e.touches[0].pageX - e.touches[1].pageX,
                    e.touches[0].pageY - e.touches[1].pageY
                );
            }}
        }});
        
        videoContainer.addEventListener('touchmove', function(e) {{
            if (e.touches.length === 2) {{
                e.preventDefault();
                const touchDistance = Math.hypot(
                    e.touches[0].pageX - e.touches[1].pageX,
                    e.touches[0].pageY - e.touches[1].pageY
                );
                
                const delta = touchDistance - touchStartDistance;
                if (Math.abs(delta) > 10) {{
                    if (delta > 0 && zoomLevel < 3) {{
                        zoomLevel += 0.1;
                        applyTransforms();
                        updateZoomIndicator();
                    }} else if (delta < 0 && zoomLevel > 0.5) {{
                        zoomLevel -= 0.1;
                        applyTransforms();
                        updateZoomIndicator();
                    }}
                    touchStartDistance = touchDistance;
                }}
            }}
        }}, {{ passive: false }});
        
        // Initial viewer count update
        updateViewerCount();
    </script>
</body>
</html>'''
            print(f'Serving enhanced page')
            html_bytes = html_data.encode('utf-8')
            self.send_header('Content-Length', str(len(html_bytes)))
            self.end_headers()
            try:
                self.wfile.write(html_bytes)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                print(f'[WARNING] Client disconnected before page could be sent')
            return
        
        elif self.path == '/stream':
            for k, v in self.__class__.HEADERS_BASE().items():
                self.send_header(k, v)
            
            try:
                # Ensure we're connected to the device first
                if not suear_client._connected:
                    suear_client.connect()
                resp = suear_client.open_video()
            except (IOError, OSError, Exception) as e:
                print(f'[ERROR] Failed to connect to camera: {e}')
                import traceback
                traceback.print_exc()
                self.end_headers()
                return

            # Increment stream client counter
            suear_client.stream_clients += 1
            print(f'[INFO] Stream client connected (total: {suear_client.stream_clients})')
            
            last_frame_index = None
            try:
                while suear_client.streaming:
                    frame = suear_client.get_frame()
                    if frame is None:
                        time.sleep(0.01)  # Wait a bit for the next frame
                        continue
                    
                    # Skip if it's the same frame we just sent
                    if last_frame_index == frame.index:
                        time.sleep(0.01)
                        continue
                    
                    last_frame_index = frame.index
                    
                    try:
                        self.end_headers()
                        self.wfile.write(self.__class__.BOUNDARY)
                        self.end_headers()
                        img_headers = self.__class__.HEADERS_IMAGE(len(frame.data))
                        for k, v in img_headers.items():
                            self.send_header(k, v)
                        self.end_headers()
                        self.wfile.write(frame.data)
                        if self.__class__.RENDER_RATE > 0 and frame.index % self.__class__.RENDER_RATE == 0:
                            frame.render()
                    except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                        # Client disconnected
                        print(f'[INFO] Stream client disconnected')
                        break
                    
                    #print(f'Reconstructed frame: {frame.index}')
                    #time.sleep(0.016)  # ~60FPS
            finally:
                # Decrement stream client counter
                suear_client.stream_clients -= 1
                print(f'[INFO] Stream client left (remaining: {suear_client.stream_clients})')
                
                # Only close stream if no more clients
                if suear_client.stream_clients <= 0:
                    print(f'[INFO] All clients disconnected, stopping video stream...')
                    suear_client.streaming = False
                    # Wait for broadcast thread to finish
                    if suear_client.broadcast_thread and suear_client.broadcast_thread.is_alive():
                        suear_client.broadcast_thread.join(timeout=2)
                    suear_client.broadcast_thread = None
                    
                    # Close socket
                    if suear_client.stream_sock is not None:
                        try:
                            if not suear_client.stream_sock._closed:
                                suear_client.stream_sock.close()
                        except:
                            pass
                    suear_client.stream_sock = None
                    
                    # Reset frame buffers for clean restart
                    suear_client.frame_dict.clear()
                    while not suear_client.frame_queue.empty():
                        try:
                            suear_client.frame_queue.get_nowait()
                        except:
                            break
                    with suear_client.frame_lock:
                        suear_client.latest_frame = None
                    
                    # Reset port detection for next connection
                    # (allows trying both ports if camera changes)
                    # Comment this line if you want to remember the port
                    # suear_client.stream_recv_port = None
                    
                    # Small delay to let OS release resources
                    time.sleep(0.3)
                    print(f'[INFO] Video stream stopped and cleaned up')
        return


class JpgFrame:
    BUF_SZ = 131072
    
    def __init__(self, index=None, width=None, height=None, first_chunk_idx=None, coords=None):
        self._buf = bytearray(self.__class__.BUF_SZ)
        if None not in (index, width, height, first_chunk_idx):
            self.init(index, width, height, first_chunk_idx, coords)
        return
    
    
    def init(self, index, width, height, first_chunk_idx, coords=None):
        self.index = int(index)
        self.width = int(width)
        self.height = int(height)
        self.first_chunk_idx = first_chunk_idx
        self.x = None
        self.y = None
        self.z = None
        if coords is not None and type(coords) == tuple and len(coords) == 3:
            self.x = int(coords[0])
            self.y = int(coords[1])
            self.z = int(coords[2])
        self.total = None
        self.complete = False  # True when all chunks have been acquired
        self.chunk_sz = None   # All but the final chunk have the same size
        self.acquired_sz = 0   # Total number of bytes acquired
        self._data = memoryview(self._buf)
    
    
    def add_chunk(self, idx, data, final=0):
        assert not self.complete, 'Attempt to add a chunk to a completed frame'
        if not final:
            if self.chunk_sz is not None:
                assert self.chunk_sz == len(data), f'Chunk size mismatch:  {self.chunk_sz=}  {len(data)=}'
            self.chunk_sz = len(data)
        elif self.chunk_sz is None:
            # Received last chunk before any other chunk... just allow the bad data?
            self.chunk_sz = len(data)
        
        # Chunk index is only 8 bits; 255 rolls over to 0, so we correct this:
        if idx < self.first_chunk_idx:
            idx += 256

        start = self.chunk_sz * (idx - self.first_chunk_idx)
        end = start + len(data)
        
        # Bounds check to prevent buffer overflow
        if end > len(self._data):
            print(f'[WARNING] Frame chunk exceeds buffer size: {end} > {len(self._data)}, skipping')
            return
        
        # Ensure data fits in the slice
        try:
            self._data[start:end] = data
        except ValueError as e:
            print(f'[ERROR] Memoryview assignment error: {e}')
            print(f'  start={start}, end={end}, len(data)={len(data)}, buffer_size={len(self._data)}')
            return
        
        self.acquired_sz += len(data)
        if final:
            self.total = int(final)
        if self.total and self.acquired_sz > self.chunk_sz * (self.total-1):
            self.complete = True
        return
    
    
    @property
    def data(self):
        assert self.complete, 'Attempt to reassemble incomplete frame'
        return self._data[:self.acquired_sz]
    
    
    @property
    def position(self):
        coords = (self.x, self.y, self.z)
        if None not in coords:
            return coords
        return None
    
    
    def render(self, title=None):
        import matplotlib.pyplot
        img = matplotlib.pyplot.imread(BytesIO(self.data), format='jpeg')
        if title is None:
            title = f'Frame {self.index}'
        matplotlib.pyplot.title(title)
        matplotlib.pyplot.imshow(img)
        matplotlib.pyplot.show(block=False)
        matplotlib.pyplot.pause(0.001)



class SuearClient:
    DEFAULT_SERVER = '192.168.1.1'
    COMMAND_PORT = 10005  # UDP
    STREAM_INIT_PORT = 10006  # UDP
    STREAM_RECV_PORTS = [22789, 22785]  # UDP - Try multiple ports for different camera models
    FRAME_CHUNK_SZ = 1456
    UDP_READ_SZ = 8192
    FRAME_QUEUE_MAX = 8
    
    def __init__(self, server=DEFAULT_SERVER, cmd_send_index=0):
        self.server = socket.gethostbyname(server)  # Server host name or IP address
        self.cmd_send_index = int(cmd_send_index) & 0xffff  # Incremented with each message sent to the server (2 bytes)
        self._license = None
        self._camera_config = None
        self._device_info = None
        self._connected = False
        self.command_sock = None
        self.stream_sock = None
        self.stream_recv_port = None  # Will be set to whichever port works (22789 or 22785)
        self.stream_buf = memoryview(bytearray(self.__class__.UDP_READ_SZ))
        self.streaming = False
        self.stream_clients = 0  # Track number of active stream connections
        self.frame_queue = queue.Queue()
        self.frame_dict = {}
        self.frame_reserve = []
        self.frame_reserve_idx = 0
        
        # Frame broadcasting for multiple clients
        self.latest_frame = None  # Store latest frame for clients
        self.frame_lock = threading.Lock()  # Protect latest_frame access
        self.broadcast_thread = None  # Background thread that reads frames
        self.stream_start_lock = threading.Lock()  # Protect stream initialization
        
        for i in range(self.__class__.FRAME_QUEUE_MAX):
            self.frame_reserve.append(JpgFrame())
        return
    
    
    def connect(self):
        if self._connected and self.command_sock is not None:
            return
        print(f'Connecting to {self.server}')
        if not ping(self.server):
            raise IOError(f'[ERROR] No ICMP response from {self.server}')
        self.command_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self._connected = True
    
    
    def disconnect(self):
        self.streaming = False
        if self.command_sock is not None:
            if not self.command_sock._closed:
                self.command_sock.close()
            self.command_sock = None
        if self.stream_sock is not None:
            if not self.stream_sock._closed:
                self.stream_sock.close()
            self.stream_sock = None
        self._connected = False
    
    
    def stream_to_matplotlib(self):
        # Don't use this function
        self.connect()
        self.streaming = True
        self.stream_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (self.server, self.__class__.STREAM_INIT_PORT)
        data = self.__class__.READ_STREAM_REQUEST
        sent = self.stream_sock.sendto(data, server_address)
        assert sent == len(data), f'UDP message was {len(data)} bytes but only {sent} were sent'
        while self.streaming:
            frame = self.get_frame()
            if frame is None:
                continue
            
            frame.render()
            #print(f'Reconstructed frame: {frame.index}')
            #time.sleep(0.016)  # ~60FPS
        
        self.streaming = False
        if self.stream_sock is not None and not self.stream_sock._closed:
            # @TODO: Send EndStream message
            self.stream_sock.close()
        self.stream_sock = None
        return


    def _broadcast_frames(self):
        """Background thread that continuously reads frames from camera and broadcasts to all clients"""
        print('[INFO] Frame broadcast thread started')
        while self.streaming and self.stream_sock is not None and not self.stream_sock._closed:
            try:
                nread = self.stream_sock.recv_into(self.stream_buf)
            except:
                break
            buf = self.stream_buf[:nread]
            offs = 0
        
            # Parse response for multiple messages
            while True:
                read_sz = suear_struct.SuearUdpMsg_StreamChunk.sizeof()
                data = buf[offs:offs+read_sz]
                offs += read_sz
                #if len(data) == 0:
                #    continue
                
                if len(data) < read_sz:
                    if len(data) > 0:
                        print(f'len(data) < suear_struct.SuearUdpMsg_StreamChunk.sizeof()')
                        print(data)
                    break
                
                msg = suear_struct.SuearUdpMsg_StreamChunk.from_bytes(data)
                read_sz = self.__class__.FRAME_CHUNK_SZ
                data = buf[offs:offs+read_sz]
                offs += len(data)
                # if len(data) < read_sz:
                #     print(f'len(data) < read_sz')
                #     print(data)
                #     return frame
                
                if msg.n_frame in self.frame_dict:
                    parse_frame = self.frame_dict[msg.n_frame]
                else:
                    while len(self.frame_dict) >= len(self.frame_reserve):
                        # Discard unfinished frames if no free frame slots are available
                        print('Discarding frame')
                        self.frame_dict.pop(self.frame_queue.get().index, None)
                    parse_frame = self.frame_reserve[self.frame_reserve_idx]
                    self.frame_reserve_idx += 1
                    if self.frame_reserve_idx >= len(self.frame_reserve):
                        self.frame_reserve_idx = 0
                    parse_frame.init(msg.n_frame, msg.res_width, msg.res_height, msg.n_chunk)
                    self.frame_dict[msg.n_frame] = parse_frame
                    self.frame_queue.put(parse_frame)
                
                #print(f'Adding chunk:\n{msg}\n{msg.coordinates=}\n')
                parse_frame.add_chunk(msg.n_chunk, data, msg.total_chunks)
                
                # If a frame enters the "complete" state, pop frames from the queue (and delete them from
                # the dict) until the popped frame is the completed frame
                if parse_frame.complete:
                    #print(f'Reconstructed frame {parse_frame.index}')
                    while True:
                        tmp_frame = self.frame_queue.get()
                        self.frame_dict.pop(tmp_frame.index, None)
                        if parse_frame.index == tmp_frame.index:  
                            break
                    # Store frame for all clients to access
                    with self.frame_lock:
                        self.latest_frame = parse_frame
                    break
        
        print('[INFO] Frame broadcast thread stopped')
    
    
    def get_frame(self):
        """Get the latest frame from the broadcast thread (thread-safe for multiple clients)"""
        if not self.streaming:
            return None
        
        with self.frame_lock:
            return self.latest_frame
    
    
    def mirror_http(self, cert_fpath=None, privkey_fpath=None):
        port = 45100
        HttpHandler.SUEAR_CLIENT = self
        HttpHandler.PORT = port
        server_address = ('0.0.0.0', port)
        httpd = http.server.ThreadingHTTPServer(server_address, HttpHandler)
        if None not in (cert_fpath, privkey_fpath):
            HttpHandler.PROTOCOL = 'https'
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context.load_cert_chain(certfile=cert_fpath, keyfile=privkey_fpath, password='')
            httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        print(f'Serving {HttpHandler.PROTOCOL.upper()} on {HttpHandler.PROTOCOL.lower()}://{server_address[0]}:{server_address[1]}')
        httpd.serve_forever()
    
    
    @property
    def connected(self):
        return self._connected
    
    
    def increment(self):
        """
        Increment and return the command-send-index while restricting it to two bytes
        """
        self.cmd_send_index = int(self.cmd_send_index + 1) & 0xffff
        return self.cmd_send_index

    
    def send_command(self, msg, connecting=False, port=None, sock=None):
        if type(msg) not in (bytes, suear_struct.SuearUdpMsg_0xffeeffee,):
            raise TypeError(f'Bad request message type: {type(msg)}')
        
        if type(msg) == bytes:
            data = b''
            if msg.startswith(b'\xee\xff\xee\xff'):
                data = msg[suear_struct.SuearUdpMsg_0xffeeffee.sizeof():]
                msg = suear_struct.SuearUdpMsg_0xffeeffee.from_bytes(msg)
            else:
                raise ValueError(f'Invalid UDP message magic bytes: {msg[:100]}')
            
            msg.data = data
            msg.length = len(data)
        
        if not (connecting or self.connected):
            self.connect()
        
        msg.id = self.increment()
        if not port:
            port = self.__class__.COMMAND_PORT
        if not sock:
            sock = self.command_sock
        #print(f'\n[Client -> {self.server}:{port}]\n{msg.type_name} {msg}\n{msg.data}\n')
        
        server_address = (self.server, port)
        sock.sendto(bytes(msg), server_address)
        response_data, server = sock.recvfrom(0x1000)#msg.sizeof())
        assert server[0] == self.server, f'Response from unknown host {server[0]}'
        response = msg.__class__.from_bytes(response_data[:msg.__class__.sizeof()])
        response_data = response_data[msg.__class__.sizeof():]
        if response.length > 0:
            # response.data, server = sock.recvfrom(response.length)
            # assert server[0] == self.server, f'Response from unknown host {server[0]}'
            response.data = response_data
            response_data = response_data[response.length:]
        assert len(response_data) == 0, f'Encountered extraneous UDP message data: {response_data}'
        #print(f'[{self.server}:{port} -> Client]\n{response.type_name} {response}\n{response.data}\n\n')
        return response
    

    def open_video(self):
        """
        When this is called, the device starts sending JPEG frames to the client.
        Now supports multiple concurrent clients.
        Thread-safe: uses lock to prevent race conditions during initialization.
        """
        # Use lock to prevent multiple threads from initializing the stream simultaneously
        with self.stream_start_lock:
            if self.streaming:
                # Already streaming, just increment client count
                print(f'[INFO] Additional client connected to stream (total: {self.stream_clients + 1})')
                return
            
            print(f'[INFO] Starting video stream from camera...')
            
            # Clean up any existing socket first
            if self.stream_sock is not None:
                try:
                    self.stream_sock.close()
                except:
                    pass
                self.stream_sock = None
                time.sleep(0.2)  # Give OS time to release the port
            
            # Send stream initialization command
            stream_init_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            response = None
            try:
                msg = b'\xee\xff\xee\xff\x00\x00\x04\x00\x01\x00\x00\x00'
                response = self.send_command(msg, port=self.__class__.STREAM_INIT_PORT, sock=stream_init_sock)
                assert response.err_code == 0, f'UDP message error code {response.err_code}'
            finally:
                stream_init_sock.close()

            # Create and bind the stream receiving socket
            # Try all possible ports (different camera models use different ports)
            ports_to_try = self.__class__.STREAM_RECV_PORTS if self.stream_recv_port is None else [self.stream_recv_port]
            
            bind_success = False
            for port in ports_to_try:
                try:
                    print(f'[INFO] Attempting to bind stream socket on port {port}...')
                    self.stream_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    # Allow address reuse so we can restart immediately after closing
                    self.stream_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    
                    # Windows-specific: also set SO_EXCLUSIVEADDRUSE to prevent port hijacking
                    if sys.platform == 'win32':
                        try:
                            # SO_EXCLUSIVEADDRUSE = 0x0400 << 16 | 0x0005
                            # Actually on Windows we want to NOT set EXCLUSIVEADDRUSE to allow reuse
                            pass
                        except:
                            pass
                    
                    self.stream_sock.bind(('0.0.0.0', port))
                    self.stream_recv_port = port
                    print(f'[INFO] Successfully bound to port {port}')
                    bind_success = True
                    break
                except OSError as e:
                    print(f'[WARNING] Failed to bind to port {port}: {e}')
                    try:
                        self.stream_sock.close()
                    except:
                        pass
                    self.stream_sock = None
                    continue
            
            if not bind_success:
                print(f'[ERROR] Failed to bind stream socket on any port: {self.__class__.STREAM_RECV_PORTS}')
                print(f'[INFO] Attempting cleanup and retry...')
                time.sleep(0.5)
                
                # Retry once more on all ports
                for port in self.__class__.STREAM_RECV_PORTS:
                    try:
                        print(f'[INFO] Retry: Attempting to bind stream socket on port {port}...')
                        self.stream_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        self.stream_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        self.stream_sock.bind(('0.0.0.0', port))
                        self.stream_recv_port = port
                        print(f'[INFO] Socket bind succeeded on retry (port {port})')
                        bind_success = True
                        break
                    except OSError as e2:
                        print(f'[WARNING] Retry failed for port {port}: {e2}')
                        try:
                            self.stream_sock.close()
                        except:
                            pass
                        self.stream_sock = None
                        continue
                
                if not bind_success:
                    print(f'[ERROR] Failed to bind stream socket on retry')
                    self.stream_sock = None
                    raise OSError(f'Could not bind to any stream port: {self.__class__.STREAM_RECV_PORTS}')

            self.streaming = True
            
            # Start the frame broadcast thread
            self.broadcast_thread = threading.Thread(target=self._broadcast_frames, daemon=True)
            self.broadcast_thread.start()
            
            print(f'[INFO] Video stream started successfully on port {self.stream_recv_port}')

            return response


    @property
    def license(self):
        if not self._license:
            msg = b'\xee\xff\xee\xff\x00\x00\x02\x00\x01\x00\x00\x00'
            response = self.send_command(msg)
            self._license = suear_struct.SuearLicenseInfo.from_bytes(response.data)
        return self._license


    @property
    def camera_config(self):
        if not self._camera_config:
            msg = b'\xee\xff\xee\xff\x00\x00\x0c\x00\x01\x00\x00\x00'
            response = self.send_command(msg)
            self._camera_config = response.data
        return self._camera_config


    def device_info(self, update=True):
        if (not self._device_info) or update:
            msg = b'\xee\xff\xee\xff\x00\x00\x01\x00\x01\x00\x00\x00'
            response = self.send_command(msg)
            self._device_info = suear_struct.SuearDeviceInfo.from_bytes(response.data)
        return self._device_info


    @property
    def battery_level(self):
        return int(self.device_info(update=True).battery)


    @property
    def is_charging(self):
        return self.device_info(update=True).is_charging
    
    
    @property
    def vendor(self):
        return self.device_info(update=False).vendor


    @property
    def model(self):
        return self.device_info(update=False).product_id


    @property
    def version(self):
        return self.device_info(update=False).fw_version


    @property
    def ssid(self):
        return self.device_info(update=False).ssid
    

    @property
    def serial_num(self):
        return self.license.serial_num


    @property
    def capacity(self):
        return self.device_info(update=False).capacity
        
        
        
if __name__ == '__main__':
    no_ssl_flag = '--no-ssl'
    if len(sys.argv) < 2 or (len(sys.argv) < 3 and no_ssl_flag not in sys.argv):
        print(f'\nUsage:\n\t{sys.argv[0]} {no_ssl_flag}\n\t{sys.argv[0]} <PEM certificate file> <private key file>\n')
        sys.exit()

    cert_fpath = None
    privkey_fpath = None
    if no_ssl_flag not in sys.argv:
        cert_fpath = sys.argv[1]
        privkey_fpath = sys.argv[2]

    client = SuearClient()
    
    # Try to connect to device, but don't fail if not available yet
    try:
        print(f'Device: {client.vendor} {client.model} {client.version}  (Serial number: {client.serial_num})')
        print(f'Battery: {client.battery_level}% ({"C" if client.is_charging else "Not c"}harging)')
    except (IOError, OSError, Exception) as e:
        print(f'[WARNING] Could not connect to device: {e}')
        print(f'[INFO] Server will start anyway. Connect to the camera WiFi and refresh the webpage.')
    
    client.mirror_http(cert_fpath, privkey_fpath)
