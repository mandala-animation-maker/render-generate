import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def export_carousel():
    # Target directory for exported PNGs
    output_dir = "exported_slides"
    os.makedirs(output_dir, exist_ok=True)

    async with async_playwright() as p:
        # Launch Headless Chromium
        browser = await p.chromium.launch()
        
        # Viewport set to fit 1080x1920 vertical slides
        # device_scale_factor=2 produces ultra-sharp 2160x3840 HD images
        context = await browser.new_context(
            viewport={"width": 1200, "height": 2050},
            device_scale_factor=2 
        )
        page = await context.new_page()

        # Load local HTML file safely cross-platform
        html_file = Path("index.html").resolve()
        print(f"Loading HTML from: {html_file}")
        await page.goto(html_file.as_uri(), wait_until="networkidle")

        # Wait for Google Fonts & FontAwesome CDN assets to finish loading
        await page.evaluate("document.fonts.ready")
        
        # Buffer to allow the inline JS Canvas displacement script to complete rendering
        await page.wait_for_timeout(1500)

        # Query all slide elements
        slides = await page.query_selector_all(".slide")
        print(f"Found {len(slides)} slides to export.")

        for index, slide in enumerate(slides, start=1):
            # 3-digit zero padding format: frame_001.png, frame_002.png, ... frame_060.png
            file_name = f"frame_{index:03d}.png"
            file_path = os.path.join(output_dir, file_name)

            # Take element screenshot
            await slide.screenshot(
                path=file_path,
                type="png",
                omit_background=False
            )
            print(f"✓ Exported: {file_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(export_carousel())
