# backend/generate_sample_xai.py
"""
Generate sample XAI images for testing embedded visuals in reports.
Creates synthetic GradCAM, overlay, and mask images.
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "app", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_gradcam_image(nodule_id: int, size: int = 256) -> str:
    """Create a synthetic GradCAM heatmap image."""
    # Create gradient base
    img = Image.new('RGB', (size, size), (20, 20, 40))
    draw = ImageDraw.Draw(img)
    
    # Draw heatmap circles (hot spots)
    center_x = size // 2 + np.random.randint(-30, 30)
    center_y = size // 2 + np.random.randint(-30, 30)
    
    # Draw multiple concentric circles for heatmap effect
    colors = [
        (255, 0, 0),    # Red (hot)
        (255, 100, 0),  # Orange
        (255, 200, 0),  # Yellow
        (100, 200, 100), # Green
        (0, 100, 200),  # Blue (cold)
    ]
    
    for i, color in enumerate(colors):
        radius = 80 - i * 15
        draw.ellipse(
            [center_x - radius, center_y - radius, 
             center_x + radius, center_y + radius],
            fill=color,
            outline=None
        )
    
    # Apply blur for smooth heatmap
    img = img.filter(ImageFilter.GaussianBlur(radius=15))
    
    # Save
    path = os.path.join(OUTPUT_DIR, f"nodule_{nodule_id}_gradcam.png")
    img.save(path)
    print(f"  ✅ Created: {path}")
    return path


def create_overlay_image(nodule_id: int, size: int = 256) -> str:
    """Create a synthetic CT overlay with nodule boundary."""
    # Create grayscale CT-like background
    base = np.random.randint(30, 80, (size, size), dtype=np.uint8)
    # Add some texture
    for _ in range(100):
        x, y = np.random.randint(0, size, 2)
        r = np.random.randint(5, 20)
        base[max(0,y-r):min(size,y+r), max(0,x-r):min(size,x+r)] += 20
    
    img = Image.fromarray(base, mode='L').convert('RGBA')
    draw = ImageDraw.Draw(img)
    
    # Draw nodule circle
    center_x = size // 2 + np.random.randint(-30, 30)
    center_y = size // 2 + np.random.randint(-30, 30)
    radius = np.random.randint(20, 40)
    
    # Draw nodule boundary (red circle)
    draw.ellipse(
        [center_x - radius, center_y - radius,
         center_x + radius, center_y + radius],
        outline=(255, 50, 50, 255),
        width=3
    )
    
    # Add label
    draw.text((10, 10), f"Nodule #{nodule_id}", fill=(255, 255, 0, 255))
    
    # Save
    path = os.path.join(OUTPUT_DIR, f"nodule_{nodule_id}_overlay.png")
    img.save(path)
    print(f"  ✅ Created: {path}")
    return path


def create_mask_file(nodule_id: int, size: int = 64) -> str:
    """Create a synthetic 3D segmentation mask (.npy)."""
    # Create 3D binary mask
    mask = np.zeros((size, size, size), dtype=np.uint8)
    
    # Create spherical nodule
    center = size // 2
    radius = np.random.randint(8, 15)
    
    for z in range(size):
        for y in range(size):
            for x in range(size):
                dist = np.sqrt((x-center)**2 + (y-center)**2 + (z-center)**2)
                if dist < radius:
                    mask[z, y, x] = 1
    
    # Save
    path = os.path.join(OUTPUT_DIR, f"nodule_{nodule_id}_mask.npy")
    np.save(path, mask)
    print(f"  ✅ Created: {path}")
    return path


def main():
    print("=" * 60)
    print("🎨 Generating Sample XAI Images for Testing")
    print("=" * 60)
    print(f"\n📁 Output: {OUTPUT_DIR}\n")
    
    # Generate for nodules 1-7 (matching sample findings)
    nodule_ids = [1, 2, 3, 4, 5, 6, 7, 70, 71, 72]
    
    for nid in nodule_ids:
        print(f"\n📦 Nodule #{nid}:")
        create_gradcam_image(nid)
        create_overlay_image(nid)
        create_mask_file(nid)
    
    print(f"\n✅ Done! Generated XAI assets for {len(nodule_ids)} nodules.")
    print(f"📁 Files saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
