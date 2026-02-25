import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import os
import time
import re
from datetime import datetime

# =============================================================================
# YAPILANDIRMA
# =============================================================================
BASE_URL = "https://markerdb.ca/categories/all"
DATA_DIR = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data"
OUTPUT_JSON = os.path.join(DATA_DIR, "MARKERDB_GLOBAL_DATABASE.json")
OUTPUT_REPORT = os.path.join(DATA_DIR, "MARKERDB_SCRAPING_REPORT.txt")
CHECKPOINT_FILE = os.path.join(DATA_DIR, "markerdb_checkpoint.txt")

os.makedirs(DATA_DIR, exist_ok=True)

class MarkerDBComprehensiveScraper:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        self.data = []
        self.start_page = self.load_checkpoint()
        self.latest_sample = "" # Görsel teyit için
        
        self.stats = {
            "total_markers": 0,
            "hmdb_found": 0,
            "hmdb_missing": 0,
            "pages_processed": 0,
            "pages_failed": [],
            "start_time": datetime.now(),
            "errors": []
        }

    def load_checkpoint(self):
        if os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE, 'r') as f:
                return int(f.read().strip())
        return 1

    def save_checkpoint(self, page):
        with open(CHECKPOINT_FILE, 'w') as f:
            f.write(str(page))

    def extract_hmdb_id(self, img_tag):
        if not img_tag or not img_tag.get('src'): return None
        match = re.search(r'HMDB\d{5,7}', img_tag['src'])
        return match.group(0) if match else None

    def parse_page(self, page_num):
        url = f"{BASE_URL}?page={page_num}"
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code != 200:
                self.stats["pages_failed"].append(page_num)
                self.stats["errors"].append(f"Page {page_num}: HTTP {response.status_code}")
                return False
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', id='enzymes')
            if not table:
                self.stats["errors"].append(f"Page {page_num}: Table 'enzymes' not found.")
                return False

            rows = table.find('tbody').find_all('tr')
            for row in rows:
                tds = row.find_all('td')
                if len(tds) < 4: continue

                mdbid = tds[0].get_text().strip()
                hmdb_id = self.extract_hmdb_id(tds[1].find('img'))
                
                if hmdb_id: self.stats["hmdb_found"] += 1
                else: self.stats["hmdb_missing"] += 1
                
                name_text = tds[2].get_text().strip()
                m_type = name_text.split(':')[0] if ':' in name_text else "Unknown"
                m_name = name_text.split(':')[-1].strip()
                
                conditions = []
                for li in tds[3].find_all('li'):
                    a_tag = li.find('a', href=True)
                    if a_tag:
                        conditions.append({
                            "condition_name": a_tag.get_text().strip(),
                            "condition_id": a_tag['href'].split('/')[-1]
                        })

                # SANITY CHECK: Son çekilen veriyi hafızada tut
                self.latest_sample = f"{m_name} ({len(conditions)} conditions)"

                self.data.append({
                    "mdbid": mdbid,
                    "hmdb_id": hmdb_id,
                    "marker_name": m_name,
                    "type": m_type,
                    "associated_conditions": conditions
                })
                self.stats["total_markers"] += 1
            
            self.stats["pages_processed"] += 1
            return True
        except Exception as e:
            self.stats["errors"].append(f"Page {page_num}: Exception - {str(e)}")
            return False

    def print_status(self, current_page, total_pages):
        elapsed = (datetime.now() - self.stats["start_time"]).total_seconds()
        pages_done = current_page - self.start_page + 1
        avg_time_per_page = elapsed / pages_done if pages_done > 0 else 0
        remaining_pages = total_pages - current_page
        eta_min = (remaining_pages * avg_time_per_page) / 60

        # KONSOL ÇIKTISINA LATEST SAMPLE EKLENDİ
        print(f"\r[P {current_page}/{total_pages}] "
              f"Hits: {self.stats['hmdb_found']} | "
              f"ETA: {eta_min:.1f}m | "
              f"Latest: {self.latest_sample[:30]}...          ", end="")

    def generate_final_report(self):
        end_time = datetime.now()
        duration = end_time - self.stats["start_time"]
        
        # VERİ ÖNİZLEMESİ (Sanity check için rapora ilk 5 kaydı ekle)
        preview = "\n3. DATA CONTENT PREVIEW (First 5 records):\n"
        for item in self.data[:5]:
            conds = ", ".join([c['condition_name'] for c in item['associated_conditions'][:2]])
            preview += f"   - {item['marker_name']} [{item['hmdb_id']}]: {conds}...\n"

        report = [
            f"{'='*60}",
            f"   MARKERDB GLOBAL EXTRACTION REPORT",
            f"   Status: {'COMPLETED' if len(self.stats['pages_failed'])==0 else 'STOPPED/FAILED'}",
            f"{'='*60}\n",
            f"1. RUNTIME INFO:",
            f"   - Total Duration      : {duration}",
            f"   - Pages Processed     : {self.stats['pages_processed']}",
            f"   - Markers Total       : {self.stats['total_markers']}\n",
            f"2. QUALITY CONTROL:",
            f"   - HMDB Mapping Rate   : {round(self.stats['hmdb_found']/self.stats['total_markers']*100, 2) if self.stats['total_markers']>0 else 0}%",
            f"   - HMDB Found / Missing: {self.stats['hmdb_found']} / {self.stats['hmdb_missing']}",
            preview,
            f"{'='*60}"
        ]
        
        with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
            f.write("\n".join(report))
        
        print("\n\n" + "\n".join(report))

    def run(self, total_pages=1235):
        print(f"🚀 Discovery Engine V4.1 (Enhanced Audit) Started.")
        
        try:
            for p in range(self.start_page, total_pages + 1):
                success = self.parse_page(p)
                self.print_status(p, total_pages)
                
                if p % 50 == 0:
                    self.save_to_json()
                    self.save_checkpoint(p)
                
                time.sleep(0.4)

            self.save_to_json()
            self.generate_final_report()
            if os.path.exists(CHECKPOINT_FILE): os.remove(CHECKPOINT_FILE)

        except KeyboardInterrupt:
            print("\n\n🛑 User Interrupted. Saving current progress...")
            self.save_to_json()
            self.save_checkpoint(p)
            self.generate_final_report()

    def save_to_json(self):
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    scraper = MarkerDBComprehensiveScraper()
    scraper.run(total_pages=1235)