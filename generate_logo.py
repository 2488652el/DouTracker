#!/usr/bin/env python
"""
Logo & Icon Generator for 抖音博主数据面板
Generates SVG logo + multi-resolution PNG icons for Web/PWA/Desktop

Requirements: pip install Pillow cairosvg    (cairosvg optional, Pillow required)
"""

import os
import sys
import struct
import zlib
import base64

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
#  Logo Design Concept:
#  - Hexagonal base (data/network feel)
#  - Play triangle in center (Douyin/video identity)
#  - Bar chart elements (data analytics)
#  - Color: Gradient from #6366f1 (indigo) to #ec4899 (pink)
#    reflecting "data meets creativity" / Douyin vibe
# ============================================================

LOGO_SVG = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#6366f1;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#8b5cf6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#ec4899;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="play" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#f0f0ff;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="bar1" x1="0%" y1="100%" x2="0%" y2="0%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.95" />
      <stop offset="100%" style="stop-color:#e0e7ff;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="bar2" x1="0%" y1="100%" x2="0%" y2="0%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.85" />
      <stop offset="100%" style="stop-color:#e0e7ff;stop-opacity:0.95" />
    </linearGradient>
    <linearGradient id="bar3" x1="0%" y1="100%" x2="0%" y2="0%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.75" />
      <stop offset="100%" style="stop-color:#e0e7ff;stop-opacity:0.9" />
    </linearGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="4" stdDeviation="12" flood-color="#6366f1" flood-opacity="0.35"/>
    </filter>
    <filter id="innerGlow">
      <feGaussianBlur in="SourceAlpha" stdDeviation="3" result="blur"/>
      <feOffset dx="0" dy="0"/>
      <feComposite in2="SourceAlpha" operator="arithmetic" k2="-1" k3="1"/>
      <feFlood flood-color="#ffffff" flood-opacity="0.15"/>
      <feComposite operator="in" in2="SourceGraphic"/>
      <feMerge>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <!-- Rounded rectangle background -->
  <rect x="40" y="40" width="432" height="432" rx="96" ry="96"
        fill="url(#bg)" filter="url(#shadow)"/>

  <!-- Subtle inner highlight ring -->
  <rect x="44" y="44" width="424" height="424" rx="92" ry="92"
        fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="2"/>

  <!-- Play triangle (Douyin identity) -->
  <polygon points="195,155 195,365 400,260"
           fill="url(#play)" opacity="0.95"/>

  <!-- Bar chart bars on the right side of the play button (representing data) -->
  <rect x="310" y="280" width="32" height="80" rx="6" fill="url(#bar1)" opacity="0.7"/>
  <rect x="354" y="240" width="32" height="120" rx="6" fill="url(#bar2)" opacity="0.85"/>
  <rect x="398" y="210" width="32" height="150" rx="6" fill="url(#bar3)" opacity="0.95"/>

  <!-- Small dot accent top-right -->
  <circle cx="440" cy="100" r="10" fill="rgba(255,255,255,0.25)"/>

  <!-- Bottom text area hint -->
  <rect x="100" y="420" width="312" height="6" rx="3" fill="rgba(255,255,255,0.15)"/>
</svg>'''

# Save SVG
svg_path = os.path.join(OUTPUT_DIR, "logo.svg")
with open(svg_path, "w", encoding="utf-8") as f:
    f.write(LOGO_SVG)
print(f"[OK] SVG Logo -> {svg_path}")


# ============================================================
# Generate PNG icons at standard sizes using PIL
# ============================================================
try:
    from PIL import Image, ImageDraw, ImageFont
    import re as _re

    ICON_SIZES = {
        "favicon-16": 16,
        "favicon-32": 32,
        "favicon-48": 48,
        "apple-57": 57,
        "apple-60": 60,
        "apple-72": 72,
        "apple-76": 76,
        "apple-114": 114,
        "apple-120": 120,
        "apple-144": 144,
        "apple-152": 152,
        "android-36": 36,
        "android-48": 48,
        "android-72": 72,
        "android-96": 96,
        "android-144": 144,
        "android-192": 192,
        "pwa-128": 128,
        "pwa-512": 512,
        "windows-ico": 256,
    }

    def hex_to_rgb(hex_str):
        hex_str = hex_str.lstrip("#")
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

    def interpolate_color(c1, c2, t):
        return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

    bg_start = hex_to_rgb("#6366f1")
    bg_mid = hex_to_rgb("#8b5cf6")
    bg_end = hex_to_rgb("#ec4899")

    def draw_logo(size):
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        margin = int(size * 0.08)
        r = size - 2 * margin
        rx = int(r * 0.22)

        # Background rounded rect
        for y in range(margin, margin + r):
            t = y / (margin + r)
            if t < 0.5:
                c = interpolate_color(bg_start, bg_mid, t * 2)
            else:
                c = interpolate_color(bg_mid, bg_end, (t - 0.5) * 2)
            # Simple alpha blend for rounded corners
            y_rel = y - margin
            corner_curve = 0
            if y_rel < rx:
                corner_curve = int((rx**2 - (rx - y_rel)**2)**0.5) if y_rel <= rx else 0
            top_curve = 0
            if y_rel > r - rx:
                dist_from_bottom = r - y_rel
                if dist_from_bottom <= rx:
                    top_curve = int((rx**2 - (rx - dist_from_bottom)**2)**0.5)

            x_start = margin + max(0, rx - corner_curve)
            x_end = margin + r - max(0, rx - corner_curve)
            if top_curve:
                x_start = margin + max(0, rx - top_curve)
                x_end = margin + r - max(0, rx - top_curve)

            for x in range(x_start, x_end + 1):
                img.putpixel((x, y), (*c, 255))

        # Play triangle
        tri_y_top = margin + int(r * 0.22)
        tri_y_bot = margin + int(r * 0.78)
        tri_y_mid = margin + int(r * 0.50)
        tri_x_left = margin + int(r * 0.28)
        tri_x_right = margin + int(r * 0.62)

        # Fill triangle
        for y in range(tri_y_top, tri_y_bot + 1):
            if y <= tri_y_mid:
                frac = (y - tri_y_top) / (tri_y_mid - tri_y_top) if tri_y_mid > tri_y_top else 0
            else:
                frac = (tri_y_bot - y) / (tri_y_bot - tri_y_mid) if tri_y_bot > tri_y_mid else 0
            x_offset = int(frac * (tri_x_right - tri_x_left))
            x_left = tri_x_left + (tri_x_right - tri_x_left) // 2 - x_offset // 2
            x_right = tri_x_left + (tri_x_right - tri_x_left) // 2 + x_offset // 2
            for x in range(x_left, x_right + 1):
                img.putpixel((x, y), (255, 255, 255, 242))

        # Bar charts
        bar_bottom = margin + int(r * 0.78)
        bar_width = int(r * 0.055)
        bar_gap = int(r * 0.03)
        bar_x_start = margin + int(r * 0.65)

        bar_heights = [
            int(r * 0.25),
            int(r * 0.38),
            int(r * 0.48),
        ]
        bar_alphas = [0.75, 0.85, 0.95]

        for i, (h, alpha) in enumerate(zip(bar_heights, bar_alphas)):
            bx = bar_x_start + i * (bar_width + bar_gap)
            for y in range(bar_bottom - h, bar_bottom):
                for x in range(bx, bx + bar_width):
                    px = max(0, min(x, size - 1))
                    py = max(0, min(y, size - 1))
                    a = int(alpha * 255)
                    img.putpixel((px, py), (255, 255, 255, a))

        return img

    print(f"\n[Generating PNG icons...]")
    for name, size in ICON_SIZES.items():
        icon = draw_logo(size)
        png_path = os.path.join(OUTPUT_DIR, f"icon-{name}.png")
        icon.save(png_path, "PNG")
        print(f"  {png_path} ({size}x{size})")

    # Generate favicon.ico (multi-res)
    ico_path = os.path.join(OUTPUT_DIR, "favicon.ico")
    ico_images = [draw_logo(s) for s in [16, 32, 48]]
    ico_images[0].save(ico_path, format="ICO",
                       sizes=[(16, 16), (32, 32), (48, 48)],
                       append_images=ico_images[1:])
    print(f"\n  {ico_path} (16/32/48)")

    print(f"\n[OK] All icons generated!")

except ImportError:
    print("\n[!] Pillow not installed. Install with: pip install Pillow")
    print("[!] PNG icons not generated. SVG logo is available.")


# ============================================================
# Generate base64 data URI versions for inline use
# ============================================================
def svg_to_data_uri(svg_str):
    encoded = base64.b64encode(svg_str.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"

data_uri = svg_to_data_uri(LOGO_SVG)
uri_path = os.path.join(OUTPUT_DIR, "logo-data-uri.txt")
with open(uri_path, "w", encoding="utf-8") as f:
    f.write(data_uri)
print(f"\n[OK] Base64 data URI -> {uri_path}")
print(f"  Length: {len(data_uri)} chars")
