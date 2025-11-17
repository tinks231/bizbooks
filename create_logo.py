#!/usr/bin/env python3
"""
BizBooks Logo Generator
Creates a professional business logo for the BizBooks platform
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_bizbooks_logo():
    """Create multiple logo variations for BizBooks"""
    
    # Logo 1: Modern Gradient with Icon
    print("Creating Logo 1: Modern Icon with Text...")
    width, height = 800, 400
    img1 = Image.new('RGB', (width, height), 'white')
    draw1 = ImageDraw.Draw(img1)
    
    # Draw icon: Stylized book with analytics chart
    icon_x, icon_y = 150, 100
    icon_size = 200
    
    # Book shape (rounded rectangle)
    book_color = (41, 128, 185)  # Professional blue
    draw1.rounded_rectangle(
        [(icon_x, icon_y), (icon_x + icon_size - 40, icon_y + icon_size)],
        radius=15,
        fill=book_color
    )
    
    # Book spine highlight
    spine_color = (52, 152, 219)  # Lighter blue
    draw1.rounded_rectangle(
        [(icon_x, icon_y), (icon_x + 30, icon_y + icon_size)],
        radius=15,
        fill=spine_color
    )
    
    # Analytics chart overlay (rising bars)
    chart_colors = [(46, 204, 113), (52, 152, 219), (155, 89, 182)]  # Green, blue, purple
    bar_width = 15
    bar_spacing = 20
    base_x = icon_x + 60
    base_y = icon_y + icon_size - 40
    
    # Rising bars
    heights = [30, 50, 70]
    for i, (h, color) in enumerate(zip(heights, chart_colors)):
        x = base_x + i * bar_spacing
        draw1.rectangle(
            [(x, base_y - h), (x + bar_width, base_y)],
            fill=color
        )
    
    # Add text "BizBooks"
    try:
        # Try to load a nice font (system fonts)
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
        font_tagline = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
    except:
        # Fallback to default
        font_large = ImageFont.load_default()
        font_tagline = ImageFont.load_default()
    
    text_x = 380
    text_y = 140
    
    # "Biz" in bold blue
    draw1.text((text_x, text_y), "Biz", fill=(41, 128, 185), font=font_large)
    
    # "Books" in dark gray
    draw1.text((text_x + 130, text_y), "Books", fill=(52, 73, 94), font=font_large)
    
    # Tagline
    draw1.text((text_x, text_y + 100), "Business Management Suite", fill=(127, 140, 141), font=font_tagline)
    
    img1.save('static/images/bizbooks_logo_1.png')
    print("✅ Logo 1 saved: static/images/bizbooks_logo_1.png")
    
    
    # Logo 2: Minimal Modern (Square Icon)
    print("\nCreating Logo 2: Minimal Square Icon...")
    width2, height2 = 600, 600
    img2 = Image.new('RGB', (width2, height2), 'white')
    draw2 = ImageDraw.Draw(img2)
    
    # Square icon with rounded corners
    icon_size2 = 500
    margin = (width2 - icon_size2) // 2
    
    # Gradient effect using multiple rectangles
    colors = [
        (41, 128, 185),   # Blue
        (52, 152, 219),   # Lighter blue
        (46, 204, 113),   # Green accent
    ]
    
    # Background rounded square
    draw2.rounded_rectangle(
        [(margin, margin), (margin + icon_size2, margin + icon_size2)],
        radius=60,
        fill=(41, 128, 185)
    )
    
    # Stylized "BB" monogram
    try:
        font_mono = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 260)
    except:
        font_mono = ImageFont.load_default()
    
    # Draw "BB" in white
    text_bb = "BB"
    # Center the text
    bbox = draw2.textbbox((0, 0), text_bb, font=font_mono)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (width2 - text_width) // 2 - 20
    text_y = (height2 - text_height) // 2 - 40
    
    draw2.text((text_x, text_y), text_bb, fill='white', font=font_mono)
    
    # Add small chart icon in corner
    chart_x, chart_y = width2 - 150, height2 - 150
    draw2.ellipse([(chart_x, chart_y), (chart_x + 80, chart_y + 80)], fill=(46, 204, 113))
    draw2.text((chart_x + 20, chart_y + 20), "📊", font=ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 40))
    
    img2.save('static/images/bizbooks_logo_square.png')
    print("✅ Logo 2 saved: static/images/bizbooks_logo_square.png")
    
    
    # Logo 3: Horizontal Banner (for headers)
    print("\nCreating Logo 3: Horizontal Banner...")
    width3, height3 = 1200, 300
    img3 = Image.new('RGB', (width3, height3), 'white')
    draw3 = ImageDraw.Draw(img3)
    
    # Small icon on left
    icon_x3, icon_y3 = 50, 50
    icon_size3 = 200
    
    # Rounded square icon
    draw3.rounded_rectangle(
        [(icon_x3, icon_y3), (icon_x3 + icon_size3, icon_y3 + icon_size3)],
        radius=30,
        fill=(41, 128, 185)
    )
    
    # "B" in icon
    try:
        font_icon = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 140)
        font_banner = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 100)
        font_banner_tag = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
    except:
        font_icon = ImageFont.load_default()
        font_banner = ImageFont.load_default()
        font_banner_tag = ImageFont.load_default()
    
    draw3.text((icon_x3 + 45, icon_y3 + 20), "B", fill='white', font=font_icon)
    
    # Text next to icon
    text_x3 = 300
    text_y3 = 80
    
    draw3.text((text_x3, text_y3), "BizBooks", fill=(52, 73, 94), font=font_banner)
    draw3.text((text_x3, text_y3 + 120), "Streamline Your Business Operations", fill=(127, 140, 141), font=font_banner_tag)
    
    img3.save('static/images/bizbooks_logo_banner.png')
    print("✅ Logo 3 saved: static/images/bizbooks_logo_banner.png")
    
    
    # Logo 4: Favicon (small icon for browser tab)
    print("\nCreating Logo 4: Favicon...")
    width4, height4 = 64, 64
    img4 = Image.new('RGB', (width4, height4), (41, 128, 185))
    draw4 = ImageDraw.Draw(img4)
    
    # Simple "B" in white
    try:
        font_fav = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 44)
    except:
        font_fav = ImageFont.load_default()
    
    draw4.text((12, 5), "B", fill='white', font=font_fav)
    
    img4.save('static/images/favicon.png')
    # Also save as .ico for browsers
    img4.save('static/images/favicon.ico', format='ICO')
    print("✅ Favicon saved: static/images/favicon.png & favicon.ico")
    
    
    print("\n" + "="*60)
    print("🎨 ALL LOGOS CREATED SUCCESSFULLY!")
    print("="*60)
    print("\n📁 Logo Files Created:")
    print("   1. bizbooks_logo_1.png      - Main logo with icon (800x400)")
    print("   2. bizbooks_logo_square.png - Square icon for apps (600x600)")
    print("   3. bizbooks_logo_banner.png - Horizontal banner (1200x300)")
    print("   4. favicon.png/ico          - Browser favicon (64x64)")
    print("\n💡 Usage:")
    print("   • Use logo_1 for website headers, business cards")
    print("   • Use logo_square for app icons, social media profiles")
    print("   • Use logo_banner for email signatures, presentations")
    print("   • Use favicon for browser tabs")
    print("\n🎨 Color Palette:")
    print("   • Primary Blue:   #2980b9 (Professional, Trustworthy)")
    print("   • Accent Green:   #2ecc71 (Growth, Success)")
    print("   • Dark Gray:      #34495e (Text, Stability)")
    print("   • Light Gray:     #7f8c8d (Secondary text)")
    print("\n✅ Next Steps:")
    print("   1. Review the logos in static/images/ folder")
    print("   2. Choose your favorite or request modifications")
    print("   3. Update your app templates to use the new logo")
    print("="*60)


if __name__ == "__main__":
    # Create static/images directory if it doesn't exist
    os.makedirs('static/images', exist_ok=True)
    create_bizbooks_logo()

