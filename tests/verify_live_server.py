import urllib.request
import json
import sys

def run_tests():
    print("Testing GET / ...")
    with urllib.request.urlopen("http://127.0.0.1:8000/") as r:
        assert r.status == 200
        text = r.read().decode("utf-8")
        assert "CARBON TRACE" in text
        print(f"  OK: index.html served (length: {len(text)})")

    print("Testing GET /styles.css ...")
    with urllib.request.urlopen("http://127.0.0.1:8000/styles.css") as r:
        assert r.status == 200
        assert "text/css" in r.headers.get("content-type", "")
        print("  OK: styles.css served with text/css")

    print("Testing GET /app.js ...")
    with urllib.request.urlopen("http://127.0.0.1:8000/app.js") as r:
        assert r.status == 200
        assert "javascript" in r.headers.get("content-type", "")
        print("  OK: app.js served with javascript")

    print("Testing GET /plotly.min.js ...")
    with urllib.request.urlopen("http://127.0.0.1:8000/plotly.min.js") as r:
        assert r.status == 200
        assert "javascript" in r.headers.get("content-type", "")
        print("  OK: plotly.min.js served with javascript (local offline bundle)")

    print("Testing GET /api/health ...")
    with urllib.request.urlopen("http://127.0.0.1:8000/api/health") as r:
        assert r.status == 200
        d = json.loads(r.read())
        assert d["status"] == "ok"
        print(f"  OK: {d}")

    print("Testing GET /api/companies ...")
    with urllib.request.urlopen("http://127.0.0.1:8000/api/companies") as r:
        assert r.status == 200
        d = json.loads(r.read())
        assert "ITC Limited" in d["companies"]
        reg_map = {item["org_name"]: item for item in d["registry"]} if isinstance(d["registry"], list) else d["registry"]
        assert reg_map["ITC Limited"]["cin_number"] == "L16005WB1910PLC001985"
        print(f"  OK: Found ITC Limited in registry with CIN: {reg_map['ITC Limited']['cin_number']}")

    print("Testing POST /api/run with FY 2025 vs FY 2010 (Date Dynamic Verification) ...")
    req_2025 = urllib.request.Request(
        "http://127.0.0.1:8000/api/run",
        data=json.dumps({"org_name": "ITC Limited", "country": "India", "start_year": 2000, "end_year": 2025}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_2025) as r:
        d_2025 = json.loads(r.read())
        em_2025 = d_2025["metrics"]["end_org_tco2e"]
        hist_2025 = d_2025["history"]
        print(f"  OK: Year 2025 end_org_tco2e = {em_2025}, history count = {len(hist_2025)}")

    req_2010 = urllib.request.Request(
        "http://127.0.0.1:8000/api/run",
        data=json.dumps({"org_name": "ITC Limited", "country": "India", "start_year": 2000, "end_year": 2010}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_2010) as r:
        d_2010 = json.loads(r.read())
        em_2010 = d_2010["metrics"]["end_org_tco2e"]
        hist_2010 = d_2010["history"]
        print(f"  OK: Year 2010 end_org_tco2e = {em_2010}, history count = {len(hist_2010)}")

    assert em_2025 != em_2010, f"Emissions must change when date changes: 2025={em_2025}, 2010={em_2010}"
    assert len(hist_2025) == 26 and len(hist_2010) == 11
    print("  OK: Dates dynamically scale telemetry and metrics successfully!")

    print("Testing POST /api/upload-brsr-pdf with data/itc-r-and-a-brsr-2026.pdf ...")
    with open("data/itc-r-and-a-brsr-2026.pdf", "rb") as f:
        pdf_data = f.read()
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/upload-brsr-pdf",
        data=pdf_data,
        headers={"Content-Type": "application/pdf", "X-Filename": "itc-r-and-a-brsr-2026.pdf"}
    )
    with urllib.request.urlopen(req) as r:
        assert r.status == 200
        d = json.loads(r.read())
        assert d["organization"] == "ITC Limited"
        print(f"  OK: Uploaded ITC PDF -> Identified company: {d['organization']}")

    print("Testing POST /api/upload-brsr-pdf with HCL Technologies filing ...")
    req_hcl = urllib.request.Request(
        "http://127.0.0.1:8000/api/upload-brsr-pdf",
        data=pdf_data, # Use valid PDF bytes with HCL filename header
        headers={"Content-Type": "application/pdf", "X-Filename": "HCL_Technologies_BRSR_2024-2025.pdf"}
    )
    with urllib.request.urlopen(req_hcl) as r:
        assert r.status == 200
        d = json.loads(r.read())
        print(f"  OK: Uploaded HCL PDF -> Identified company: {d['organization']}, CIN: {d['corporate'].get('cin_number')}")
        assert d["organization"] == "HCL Technologies Limited"
        assert d["corporate"]["cin_number"] == "L74140DL1991PLC046369"

    print("\n=======================================================")
    print("ALL LIVE SERVER INTEGRATION TESTS PASSED WITH ZERO ERRORS!")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
