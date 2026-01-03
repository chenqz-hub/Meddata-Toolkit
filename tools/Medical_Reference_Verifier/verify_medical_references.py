import urllib.request
import urllib.parse
import json
import re
import time
import ssl
import sys
import os
import tkinter as tk
from tkinter import filedialog
import zipfile
import xml.etree.ElementTree as ET

# ==========================================
# Medical Reference Verifier & RIS Generator
# ==========================================
# This script verifies a list of medical references against PubMed and Crossref databases.
# It also fetches full metadata to generate an RIS file for EndNote/Zotero.
#
# Usage:
# 1. Run this script: python verify_medical_references.py
# 2. A dialog box will appear. Select your file (.docx, .txt, .md).
# ==========================================

# Configuration
TIMEOUT_SECONDS = 60  # Increased timeout for better stability

# Ignore SSL certificate errors (fixes common network issues)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def clean_text(text):
    return re.sub(r'[^\w\s]', '', text).lower()

def read_docx_text(path):
    """Extracts text from a .docx file using only standard libraries (no python-docx needed)."""
    try:
        with zipfile.ZipFile(path) as zf:
            xml_content = zf.read('word/document.xml')
        
        # Parse XML
        root = ET.fromstring(xml_content)
        
        # Define namespace for Word
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        lines = []
        # Iterate over paragraphs
        for p in root.findall('.//w:p', ns):
            # Iterate over text runs
            texts = [node.text for node in p.findall('.//w:t', ns) if node.text]
            if texts:
                lines.append(''.join(texts))
        return lines
    except Exception as e:
        print(f"Error parsing .docx: {e}")
        return []

def get_safe_str(data, key, default=""):
    """Safely get string from dict."""
    return str(data.get(key, default))

def format_ris_entry(meta):
    """Converts a metadata dictionary to an RIS string."""
    ris = "TY  - JOUR\n"
    ris += f"TI  - {meta.get('title', '')}\n"
    
    for author in meta.get('authors', []):
        ris += f"AU  - {author}\n"
        
    ris += f"JO  - {meta.get('journal', '')}\n"
    ris += f"PY  - {meta.get('year', '')}\n"
    ris += f"VL  - {meta.get('volume', '')}\n"
    ris += f"IS  - {meta.get('issue', '')}\n"
    ris += f"SP  - {meta.get('pages', '')}\n"
    
    if meta.get('doi'):
        ris += f"DO  - {meta.get('doi')}\n"
    if meta.get('pmid'):
        ris += f"AN  - {meta.get('pmid')}\n" # Accession Number often used for PMID
        ris += f"DB  - PubMed\n"
        
    ris += "ER  - \n\n"
    return ris

def fetch_pubmed_details(pmid):
    """Fetches full metadata for a PMID using eSummary."""
    try:
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json&api_key="
        headers = {'User-Agent': 'MedicalReferenceVerifier/1.0'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, context=ctx, timeout=TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode())
            
        result = data.get('result', {}).get(str(pmid), {})
        if not result:
            return None
            
        # Extract fields
        authors = [a.get('name', '') for a in result.get('authors', [])]
        
        # Extract DOI from elocationid or articleids
        doi = ""
        for aid in result.get('articleids', []):
            if aid.get('idtype') == 'doi':
                doi = aid.get('value')
                break
        if not doi and 'elocationid' in result:
             if 'doi' in result['elocationid']:
                 doi = result['elocationid'].replace('doi: ', '').strip()

        return {
            "title": result.get('title', ''),
            "authors": authors,
            "journal": result.get('source', ''),
            "year": result.get('pubdate', '').split(' ')[0], # '2023 Jun 15' -> '2023'
            "volume": result.get('volume', ''),
            "issue": result.get('issue', ''),
            "pages": result.get('pages', ''),
            "doi": doi,
            "pmid": pmid,
            "source": "PubMed"
        }
    except Exception as e:
        print(f"Error fetching PubMed details: {e}")
        return None

def check_pubmed(title, year):
    """Queries PubMed database for the reference."""
    try:
        # Search by title and year
        search_term = f"{title}[Title]"
        if year:
            search_term += f" AND {year}[pdat]"
            
        query = urllib.parse.quote(search_term)
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&term={query}&api_key="
        
        headers = {'User-Agent': 'MedicalReferenceVerifier/1.0'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, context=ctx, timeout=TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode())
            
        if int(data['esearchresult']['count']) > 0:
            pmid = data['esearchresult']['idlist'][0]
            # Fetch details immediately
            details = fetch_pubmed_details(pmid)
            if details:
                return {"status": "Verified (PubMed)", "data": details}
            return {"status": "Verified (PubMed)", "id": pmid} # Fallback if details fail
        else:
            # Try without year if failed
            if year:
                return check_pubmed(title, None)
            return None
            
    except Exception as e:
        return {"status": "Error", "error": str(e)}

def check_crossref(raw_ref):
    """Queries Crossref database for the reference."""
    try:
        query = urllib.parse.quote(raw_ref)
        url = f"https://api.crossref.org/works?query.bibliographic={query}&rows=1"
        
        headers = {'User-Agent': 'MedicalReferenceVerifier/1.0 (mailto:example@example.com)'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, context=ctx, timeout=TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode())
            
        if data['message']['items']:
            item = data['message']['items'][0]
            
            # Extract fields
            authors = []
            for a in item.get('author', []):
                name = f"{a.get('family', '')}, {a.get('given', '')}"
                authors.append(name.strip(', '))
                
            year = ""
            if 'published-print' in item:
                year = item['published-print']['date-parts'][0][0]
            elif 'published-online' in item:
                year = item['published-online']['date-parts'][0][0]
                
            meta = {
                "title": item.get('title', [''])[0],
                "authors": authors,
                "journal": item.get('container-title', [''])[0],
                "year": str(year),
                "volume": item.get('volume', ''),
                "issue": item.get('issue', ''),
                "pages": item.get('page', ''),
                "doi": item.get('DOI', ''),
                "source": "Crossref"
            }
            
            return {"status": "Verified (Crossref)", "data": meta}
        return None
    except Exception as e:
        return {"status": "Error", "error": str(e)}

def verify_reference(ref_line):
    """Orchestrates the verification process for a single reference line."""
    # 1. Extract Title and Year
    text = re.sub(r'^\[?\d+\]?\.?\s*', '', ref_line)
    
    year_match = re.search(r'(19|20)\d{2}', text)
    year = year_match.group(0) if year_match else None
    
    parts = text.split('. ')
    title = ""
    if len(parts) >= 2:
        title = parts[1].strip()
        if title.endswith('.'):
            title = title[:-1]
    else:
        title = text
        
    # 2. Try PubMed first
    pm_result = check_pubmed(title, year)
    if pm_result and "Verified" in pm_result['status']:
        return pm_result
        
    # 3. Try Crossref if PubMed failed
    cr_result = check_crossref(text)
    if cr_result and "Verified" in cr_result['status']:
        return cr_result
        
    return {"status": "Not Found", "searched_title": title}

def main():
    print("==========================================")
    print("   Medical Reference Verifier & RIS Gen   ")
    print("==========================================")
    
    root = tk.Tk()
    root.withdraw()

    print("Waiting for file selection...")
    input_path = filedialog.askopenfilename(
        title="Select Reference File",
        filetypes=[("Documents", "*.docx;*.txt;*.md"), ("All Files", "*.*")]
    )

    if not input_path:
        print("No file selected. Operation cancelled.")
        return

    print(f"Selected file: {input_path}")
    
    input_dir = os.path.dirname(input_path)
    input_filename = os.path.basename(input_path)
    output_report = os.path.join(input_dir, os.path.splitext(input_filename)[0] + "_verification_report.txt")
    output_ris = os.path.join(input_dir, os.path.splitext(input_filename)[0] + "_verified_refs.ris")

    try:
        if input_path.lower().endswith('.docx'):
            print("Reading .docx file...")
            lines = read_docx_text(input_path)
            # Filter out empty lines
            lines = [line.strip() for line in lines if line.strip()]
        else:
            with open(input_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
        
        ref_pattern = re.compile(r'^\s*(?:\[\d+\]|\d+\.)\s+')
        numbered_refs = [line for line in lines if ref_pattern.match(line)]

        
        if numbered_refs:
            print(f"Detected {len(numbered_refs)} numbered references.")
            references = numbered_refs
        else:
            print("No numbered references detected. Treating all lines as references.")
            references = lines
            
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    print(f"Found {len(references)} references to verify.")
    print("-" * 80)
    print(f"{'ID':<3} | {'Source':<10} | {'Status':<10} | {'Details'}")
    print("-" * 80)

    # Clear output files
    with open(output_report, "w", encoding="utf-8") as f:
        f.write(f"Verification Report for: {input_filename}\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-" * 80 + "\n")
        
    with open(output_ris, "w", encoding="utf-8") as f:
        f.write("") # Clear file

    success_count = 0
    
    for i, ref in enumerate(references, 1):
        result = verify_reference(ref)
        
        source = "-"
        status = "❌ Fail"
        details = ""
        
        if result and "Verified" in result.get('status', ''):
            status = "✅ OK"
            if 'data' in result:
                meta = result['data']
                source = meta.get('source', 'Unknown')
                details = meta.get('doi') or meta.get('pmid') or meta.get('title')
                
                # Write to RIS
                ris_entry = format_ris_entry(meta)
                with open(output_ris, "a", encoding="utf-8") as f:
                    f.write(ris_entry)
                success_count += 1
            else:
                # Fallback if data fetch failed but ID found
                source = "PubMed" if "PubMed" in result['status'] else "Crossref"
                details = result.get('id', '')
        else:
            details = result.get('searched_title', '') if result else "Unknown Error"
        
        output_line = f"{i:<3} | {source:<10} | {status:<10} | {str(details)[:50]}"
        print(output_line)
        
        with open(output_report, "a", encoding="utf-8") as f:
            f.write(output_line + "\n")
        
        time.sleep(1)

    print("-" * 80)
    print(f"Done! {success_count}/{len(references)} references verified and exported.")
    print(f"1. Verification Report: {output_report}")
    print(f"2. EndNote Import File: {output_ris}")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
