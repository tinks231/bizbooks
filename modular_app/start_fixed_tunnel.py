#!/usr/bin/env python3
"""
Start Cloudflare tunnel and save the URL for easy access
The URL remains fixed as long as the tunnel is running
"""
import subprocess
import time
import re
import os
import qrcode
from datetime import datetime

print("=" * 60)
print("🚀 Starting Fixed Cloudflare Tunnel")
print("=" * 60)

# Start cloudflare tunnel
print("\n📡 Starting tunnel to https://127.0.0.1:5001...")
tunnel_process = subprocess.Popen(
    ['cloudflared', 'tunnel', '--url', 'https://127.0.0.1:5001', '--no-tls-verify'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True
)

# Wait and capture the URL
print("⏳ Waiting for tunnel URL...")
public_url = None

for line in tunnel_process.stdout:
    print(line.strip())
    if 'trycloudflare.com' in line:
        # Extract URL
        match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
        if match:
            public_url = match.group(0)
            break

if not public_url:
    print("❌ Failed to get tunnel URL")
    exit(1)

print("\n" + "=" * 60)
print("✅ TUNNEL READY!")
print("=" * 60)
print(f"\n🌍 PUBLIC URL: {public_url}")
print(f"\n📱 Employees can access from ANYWHERE (WiFi or Mobile Data):")
print(f"   {public_url}/attendance")
print(f"\n👨‍💼 Admin Dashboard:")
print(f"   {public_url}/admin")

# Save URL to file
url_file = os.path.join(os.path.dirname(__file__), 'current_tunnel_url.txt')
with open(url_file, 'w') as f:
    f.write(f"Public URL: {public_url}\n")
    f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"\nEmployee Attendance: {public_url}/attendance\n")
    f.write(f"Admin Dashboard: {public_url}/admin\n")

print(f"\n💾 URL saved to: {url_file}")

# Generate QR code for employee attendance
try:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"{public_url}/attendance")
    qr.make(fit=True)
    
    qr_file = os.path.join(os.path.dirname(__file__), 'attendance_qr_current.png')
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_file)
    print(f"📱 QR Code saved to: {qr_file}")
    print(f"   Print this QR code for employees to scan!")
except Exception as e:
    print(f"⚠️  Could not generate QR code: {e}")

print("\n" + "=" * 60)
print("⚠️  IMPORTANT NOTES:")
print("=" * 60)
print("• This URL is STABLE as long as the tunnel is running")
print("• If you restart the tunnel, you'll get a NEW URL")
print("• Keep this terminal window open!")
print("• Press Ctrl+C to stop the tunnel")
print("=" * 60)

# Keep process running
try:
    tunnel_process.wait()
except KeyboardInterrupt:
    print("\n\n🛑 Stopping tunnel...")
    tunnel_process.terminate()
    print("✅ Tunnel stopped")

