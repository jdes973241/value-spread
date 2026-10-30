#!/usr/bin/env python3
"""
Monthly Auto-Updater for Global Value Spread Dashboard
Source: Kenneth R. French Data Library (Dartmouth)
- US 2x3 Size & Book-to-Market:
  https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/6_Portfolios_2x3_CSV.zip
- Developed ex-US 2x3 Size & Book-to-Market:
  https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Developed_ex_US_6_Portfolios_ME_BE-ME_CSV.zip
- Emerging Markets 2x3 Size & Book-to-Market:
  https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Emerging_6_Portfolios_ME_BE-ME_CSV.zip
"""

import io, json, math, os, re, urllib.request, zipfile

URLS = {
    "us": "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/6_Portfolios_2x3_CSV.zip",
    "dev": "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Developed_ex_US_6_Portfolios_ME_BE-ME_CSV.zip",
    "em": "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Emerging_6_Portfolios_ME_BE-ME_CSV.zip",
}

CALIB = {
    "large": {"us": {"mu": 1.12, "sd": 0.24}, "dev": {"mu": 1.05, "sd": 0.22}, "em": {"mu": 1.15, "sd": 0.25}},
    "small": {"us": {"mu": 1.25, "sd": 0.26}, "dev": {"mu": 1.18, "sd": 0.23}, "em": {"mu": 1.22, "sd": 0.25}},
}

def download_and_extract_csv(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (ValueSpreadUpdater/1.0)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw_bytes = resp.read()
    with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
        csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        return zf.read(csv_names[0]).decode("latin-1", errors="ignore")

def parse_beme_section(csv_text: str):
    lines = csv_text.splitlines()
    in_beme = False
    records = {}
    for line in lines:
        if "Value Weight Average of BE/ME" in line:
            in_beme = True
            continue
        if in_beme:
            stripped = line.strip()
            if not stripped:
                if records:
                    break
                continue
            parts = [p.strip() for p in stripped.split(",")]
            if len(parts) >= 7 and re.match(r"^\d{6}$", parts[0]):
                ym = f"{parts[0][:4]}/{parts[0][4:6]}"
                try:
                    s_lo, s_hi, b_lo, b_hi = float(parts[1]), float(parts[3]), float(parts[4]), float(parts[6])
                    if s_lo > 0 and s_hi > 0 and b_lo > 0 and b_hi > 0:
                        records[ym] = (s_lo, s_hi, b_lo, b_hi)
                except ValueError:
                    continue
    return records

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(repo_root, "data", "value_spread_data.json")
    html_path = os.path.join(repo_root, "index.html")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    fetched = {mkt: parse_beme_section(download_and_extract_csv(url)) for mkt, url in URLS.items()}
    last_month = data["months"][-1]
    new_months = sorted(m for m in fetched["us"].keys() if m > last_month)
    if not new_months:
        print(f"No new months after {last_month} found yet.")
        return
    for ym in new_months:
        data["months"].append(ym)
        for mkt in ("us", "dev", "em"):
            rec = fetched[mkt].get(ym)
            if rec:
                s_lo, s_hi, b_lo, b_hi = rec
                z_large = round((math.log(b_hi / b_lo) - CALIB["large"][mkt]["mu"]) / CALIB["large"][mkt]["sd"], 2)
                z_small = round((math.log(s_hi / s_lo) - CALIB["small"][mkt]["mu"]) / CALIB["small"][mkt]["sd"], 2)
                w = 0.80 if mkt == "us" else (0.82 if mkt == "dev" else 0.84)
                z_all = round(w * z_large + (1.0 - w) * z_small, 2)
            else:
                z_large, z_small, z_all = data["large"][mkt][-1], data["small"][mkt][-1], data["all"][mkt][-1]
            data["large"][mkt].append(z_large)
            data["small"][mkt].append(z_small)
            data["all"][mkt].append(z_all)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        new_json_str = json.dumps(data, separators=(",", ":"))
        html_updated = re.sub(r"const INITIAL_MULTI_DATA = \{.*?\};", f"const INITIAL_MULTI_DATA = {new_json_str};", html, count=1, flags=re.DOTALL)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_updated)

if __name__ == "__main__":
    main()
