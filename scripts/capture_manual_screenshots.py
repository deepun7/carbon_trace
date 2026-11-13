import os
import time
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = os.path.abspath("manual_assets/screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def capture_all():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a high-DPI viewport for razor-sharp PDF printing
        context = browser.new_context(
            viewport={"width": 1440, "height": 1000},
            device_scale_factor=2
        )
        page = context.new_page()

        print("Navigating to http://127.0.0.1:8000/ ...")
        page.goto("http://127.0.0.1:8000/", wait_until="networkidle")
        time.sleep(2) # Allow counter animations and Plotly rendering to stabilize

        # 1. Full Dashboard Overview
        full_overview_path = os.path.join(SCREENSHOT_DIR, "00_full_dashboard_overview.png")
        page.screenshot(path=full_overview_path)
        print(f"Captured: {full_overview_path}")

        # 2. Screenshot 1: Top Editorial Header Bar & 4-Step Regulatory Stepper
        # We capture the workspace header + regulatory stepper section
        header_el = page.locator(".workspace-header")
        stepper_el = page.locator(".regulatory-stepper")
        # Combine or capture the top container
        top_bar_path = os.path.join(SCREENSHOT_DIR, "01_top_header_and_stepper.png")
        # Take screenshot of workspace-header and stepper together by clipping or bounding box
        box_header = header_el.bounding_box()
        box_stepper = stepper_el.bounding_box()
        if box_header and box_stepper:
            clip_top = {
                "x": box_header["x"],
                "y": box_header["y"],
                "width": max(box_header["width"], box_stepper["width"]),
                "height": (box_stepper["y"] + box_stepper["height"]) - box_header["y"]
            }
            page.screenshot(path=top_bar_path, clip=clip_top)
            print(f"Captured: {top_bar_path}")

        # 3. Screenshot 2: Left Atelier Control Panel
        sidebar_el = page.locator("aside.sidebar")
        sidebar_path = os.path.join(SCREENSHOT_DIR, "02_atelier_control_panel.png")
        sidebar_el.screenshot(path=sidebar_path)
        print(f"Captured: {sidebar_path}")

        # 4. Screenshot 3: Top 4 Animated Glassmorphic KPI Cards
        kpi_el = page.locator(".kpi-grid")
        kpi_path = os.path.join(SCREENSHOT_DIR, "03_kpi_cards.png")
        kpi_el.screenshot(path=kpi_path)
        print(f"Captured: {kpi_path}")

        # 5. Screenshot 4: Tab 01 — Trajectory & ML Walk-Forward Forecast Chart
        # Click on Tab 01 to ensure active and resized
        page.locator('button[data-tab="tab-trajectory"]').click()
        time.sleep(1)
        tab1_el = page.locator("#tab-trajectory")
        tab1_path = os.path.join(SCREENSHOT_DIR, "04_tab01_trajectory_ml_forecast.png")
        tab1_el.screenshot(path=tab1_path)
        print(f"Captured: {tab1_path}")

        # 6. Screenshot 5: Tab 02 — BRSR Principle 6 & GHG Scopes View
        page.locator('button[data-tab="tab-brsr"]').click()
        time.sleep(1.5) # allow Plotly resize and re-render
        tab2_el = page.locator("#tab-brsr")
        tab2_path = os.path.join(SCREENSHOT_DIR, "05_tab02_brsr_scopes_view.png")
        tab2_el.screenshot(path=tab2_path)
        print(f"Captured: {tab2_path}")

        # 7. Screenshot 6: Live PDF Upload Demonstration
        # Upload data/itc-r-and-a-brsr-2026.pdf
        pdf_file_path = os.path.abspath("data/itc-r-and-a-brsr-2026.pdf")
        if os.path.exists(pdf_file_path):
            print(f"Uploading BRSR PDF: {pdf_file_path} ...")
            file_input = page.locator("#pdfInput")
            file_input.set_input_files(pdf_file_path)
            time.sleep(3) # wait for extraction and render
            pdf_demo_path = os.path.join(SCREENSHOT_DIR, "06_live_pdf_upload_demonstration.png")
            page.screenshot(path=pdf_demo_path)
            print(f"Captured: {pdf_demo_path}")

        # 8. Screenshot 7a: Tab 03 — Executive Markdown Report Viewer & Regulatory Trail
        page.locator('button[data-tab="tab-report"]').click()
        time.sleep(1)
        tab3_el = page.locator("#tab-report")
        tab3_path = os.path.join(SCREENSHOT_DIR, "07_tab03_executive_report_viewer.png")
        tab3_el.screenshot(path=tab3_path)
        print(f"Captured: {tab3_path}")

        # 9. Screenshot 7b: Tab 04 — 5-Agent Execution Logs & Citation Audit
        page.locator('button[data-tab="tab-logs"]').click()
        time.sleep(1)
        tab4_el = page.locator("#tab-logs")
        tab4_path = os.path.join(SCREENSHOT_DIR, "08_tab04_agent_logs_and_citations.png")
        tab4_el.screenshot(path=tab4_path)
        print(f"Captured: {tab4_path}")

        browser.close()
        print("All live screenshots captured successfully!")

if __name__ == "__main__":
    capture_all()
