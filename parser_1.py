import sqlite3
import requests
from lxml import etree
import json
from urllib.parse import urlparse, parse_qs
import hashlib

DB_PATH = 'vast_ads.db'

CREATE_TABLE_SQL = '''
CREATE TABLE IF NOT EXISTS vast_ads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    call_number INTEGER,
    ad_id TEXT,
    creative_id TEXT,
    ssai_creative_id TEXT,
    title TEXT,
    duration TEXT,
    clickthrough TEXT,
    media_urls TEXT,
    channel_name TEXT,
    adomain TEXT,
    creative_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ad_xml TEXT,
    wrapped_ad INTEGER DEFAULT 0,
    initial_metadata_json TEXT,
    broken_wrapper_url TEXT,
    wrapper_chain TEXT,
    original_wrapper_ad_id TEXT,
    broken_wrapper_ad_id TEXT
)
'''

def setup_db():
    conn = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None, check_same_thread=False)
    cur = conn.cursor()
    
    # Check if broken_wrapper_url column exists, add if not
    cur.execute("PRAGMA table_info(vast_ads)")
    columns = [column[1] for column in cur.fetchall()]
    
    if 'broken_wrapper_url' not in columns:
        cur.execute("ALTER TABLE vast_ads ADD COLUMN broken_wrapper_url TEXT")
        print("✅ Added broken_wrapper_url column")
    
    if 'wrapper_chain' not in columns:
        cur.execute("ALTER TABLE vast_ads ADD COLUMN wrapper_chain TEXT")
        print("✅ Added wrapper_chain column")
    
    if 'original_wrapper_ad_id' not in columns:
        cur.execute("ALTER TABLE vast_ads ADD COLUMN original_wrapper_ad_id TEXT")
        print("✅ Added original_wrapper_ad_id column")
    
    if 'broken_wrapper_ad_id' not in columns:
        cur.execute("ALTER TABLE vast_ads ADD COLUMN broken_wrapper_ad_id TEXT")
        print("✅ Added broken_wrapper_ad_id column")
    
    cur.execute(CREATE_TABLE_SQL)
    conn.commit()
    conn.close()

def make_creative_hash(*fields):
    base = ':'.join([str(f) if f else '' for f in fields])
    return hashlib.sha256(base.encode('utf-8')).hexdigest()

def get_ssai_creative_id(ad_element):
    ssai = ad_element.xpath('.//Extensions/Extension[@type="FreeWheel"]/SSAICreativeId')
    if ssai and ssai[0].text:
        value = ssai[0].text.strip()
        # Remove CDATA if present
        if value.startswith("CDATA[") and value.endswith("]"):
            value = value[6:-1]
        return value
    return None

def fetch_and_parse_vast(url, headers, max_depth=5, visited=None, is_wrapped=False, wrapper_chain=None):
    import json as _json
    if visited is None:
        visited = set()
    if wrapper_chain is None:
        wrapper_chain = []
    
    if url in visited or max_depth <= 0:
        return [], None, None, None
    visited.add(url)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return [], None, None, None
    
    if response.status_code != 200 or not response.content.strip():
        print(f"❌ Invalid response from {url}: status={response.status_code}, content_length={len(response.content)}")
        return [], None, None, None
    
    parser = etree.XMLParser(recover=True)
    try:
        tree = etree.fromstring(response.content, parser=parser)
    except etree.XMLSyntaxError as e:
        print(f"❌ XML parsing error for {url}: {e}")
        return [], None, None, None
    
    # Check for empty VAST response
    ads = tree.xpath("//Ad")
    if not ads:
        # Check if this is an empty VAST response (like the one in the image)
        vast_element = tree.xpath("//VAST")
        if vast_element:
            vast_attrs = vast_element[0].attrib
            # Check for status="NO_AD" or similar indicators
            if any('NO_AD' in str(v).upper() for v in vast_attrs.values()):
                print(f"⚠️ Empty VAST detected at {url} - NO_AD status")
                return [], response.content.decode(errors='replace'), None, {
                    'broken_url': url,
                    'wrapper_chain': wrapper_chain,
                    'reason': 'NO_AD status in VAST response'
                }
        
        print(f"⚠️ No ads found in VAST response from {url}")
        return [], response.content.decode(errors='replace'), None, {
            'broken_url': url,
            'wrapper_chain': wrapper_chain,
            'reason': 'No ads in VAST response'
        }
    
    initial_metadata = []
    for ad in ads:
        ad_id = ad.get("id", "N/A")
        title = ad.xpath(".//AdTitle/text()")
        duration = ad.xpath(".//Duration/text()")
        click_url = ad.xpath(".//ClickThrough/text()")
        creative_id = ad.xpath(".//Creative/@id")
        creative_id = creative_id[0] if creative_id else None
        media_files = ad.xpath(".//MediaFile")
        media_urls = [mf.text.strip() for mf in media_files if mf.text]
        ssai_creative_id = get_ssai_creative_id(ad)
        adomain = None
        adomain_nodes = ad.xpath('.//AdVerifications/Verification/AdVerificationParameters/Adomain/text()')
        if not adomain_nodes:
            adomain_nodes = ad.xpath('.//Extension[@type="advertiser"]/Adomain/text()')
        if not adomain_nodes:
            adomain_nodes = ad.xpath('.//Advertiser/text()')
        adomain = adomain_nodes[0] if adomain_nodes else None
        creative_hash = make_creative_hash(ssai_creative_id, creative_id, ','.join(media_urls), adomain if adomain else '')
        meta = {
            "ad_id": ad_id,
            "creative_id": creative_id,
            "ssai_creative_id": ssai_creative_id,
            "title": title[0] if title else None,
            "duration": duration[0] if duration else None,
            "clickthrough": click_url[0] if click_url else None,
            "media_urls": media_urls,
            "adomain": adomain,
            "creative_hash": creative_hash
        }
        initial_metadata.append(meta)
    
    final_ads = []
    broken_wrapper_info = None
    
    for idx, ad in enumerate(ads):
        wrapper = ad.find("Wrapper")
        if wrapper is not None:
            vast_ad_tag_uri = wrapper.findtext("VASTAdTagURI")
            if vast_ad_tag_uri:
                current_chain = wrapper_chain + [url]
                child_ads, _, child_initial, child_broken = fetch_and_parse_vast(
                    vast_ad_tag_uri.strip(), headers, max_depth-1, visited, is_wrapped=True, wrapper_chain=current_chain
                )
                
                # If child parsing found a broken wrapper, track it
                if child_broken:
                    # Add the current wrapper ad ID to the broken wrapper info
                    wrapper_ad_id = ad.get("id", "N/A")
                    child_broken['original_wrapper_ad_id'] = wrapper_ad_id
                    broken_wrapper_info = child_broken
                
                if not child_ads:
                    # This wrapper led to no ads - track as broken
                    wrapper_ad_id = ad.get("id", "N/A")
                    broken_wrapper_info = {
                        'broken_url': vast_ad_tag_uri.strip(),
                        'wrapper_chain': current_chain,
                        'reason': 'Wrapper led to no ads',
                        'original_wrapper_ad_id': wrapper_ad_id,
                        'broken_wrapper_ad_id': wrapper_ad_id
                    }
                    print(f"⚠️ Wrapper at {url} (Ad ID: {wrapper_ad_id}) led to no ads via {vast_ad_tag_uri.strip()}")
                    # Don't add any ads from this wrapper since it's broken
                    continue
                
                for c in child_ads:
                    final_ads.append((c[0], True, _json.dumps(initial_metadata[idx] if idx < len(initial_metadata) else {})))
        else:
            final_ads.append((ad, is_wrapped, _json.dumps(initial_metadata[idx] if idx < len(initial_metadata) else {})))
    
    return final_ads, response.content.decode(errors='replace'), initial_metadata, broken_wrapper_info

def parse_vast_and_store(url, call_number):
    conn = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None, check_same_thread=False)
    cur = conn.cursor()

    headers = {
        "User-Agent": "StreamDevice/1.0"
    }

    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    csid = query_params.get("csid", [""])[0]
    csid_parts = csid.split("/")
    channel_name = csid_parts[1] if len(csid_parts) >= 2 else None

    ads, last_xml, _, broken_wrapper_info = fetch_and_parse_vast(url, headers)
    
    # Debug logging for broken wrapper storage
    print(f"🔍 DEBUG: broken_wrapper_info exists: {broken_wrapper_info is not None}")
    if broken_wrapper_info:
        print(f"🔍 DEBUG: broken_wrapper_info: {broken_wrapper_info}")
        print(f"🔍 DEBUG: original_wrapper_ad_id: {broken_wrapper_info.get('original_wrapper_ad_id')}")
    print(f"🔍 DEBUG: ads count: {len(ads) if ads else 0}")
    
    # Store broken wrapper records when a wrapper leads to broken URLs
    # This can happen even if other valid ads are found in the same VAST response
    if broken_wrapper_info and broken_wrapper_info.get('original_wrapper_ad_id'):
        print(f"🔗 Storing broken wrapper record: {broken_wrapper_info['broken_url']}")
        
        # Create a placeholder ad record for the broken wrapper
        cur.execute("""
            INSERT INTO vast_ads (
                call_number, ad_id, creative_id, ssai_creative_id, title, duration, clickthrough, media_urls,
                channel_name, adomain, creative_hash, ad_xml, wrapped_ad, initial_metadata_json,
                broken_wrapper_url, wrapper_chain, original_wrapper_ad_id, broken_wrapper_ad_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            call_number,
            broken_wrapper_info.get('original_wrapper_ad_id', 'broken_wrapper'),
            None,  # creative_id
            None,  # ssai_creative_id
            f"Broken Wrapper: {broken_wrapper_info['reason']}",
            None,  # duration
            None,  # clickthrough
            json.dumps([]),  # media_urls
            channel_name,
            None,  # adomain
            None,  # creative_hash
            f"<VAST><Ad id='{broken_wrapper_info.get('original_wrapper_ad_id', 'broken_wrapper')}'><Wrapper><VASTAdTagURI>{broken_wrapper_info['broken_url']}</VASTAdTagURI></Wrapper></Ad></VAST>",
            1,  # wrapped_ad = True
            json.dumps({}),  # initial_metadata_json
            broken_wrapper_info['broken_url'],
            json.dumps(broken_wrapper_info['wrapper_chain']),
            broken_wrapper_info.get('original_wrapper_ad_id'),
            broken_wrapper_info.get('broken_wrapper_ad_id')
        ))
        
        conn.commit()
        conn.close()
        return f"❌ No valid ads found. Broken wrapper detected and stored: {broken_wrapper_info['broken_url']} - {broken_wrapper_info['reason']}"
    
    if not ads:
        conn.close()
        return f"❌ No valid Inline ads found."

    for ad, wrapped_flag, initial_metadata_json in ads:
        ad_id = ad.get("id", "N/A")
        title = ad.xpath(".//AdTitle/text()")
        duration = ad.xpath(".//Duration/text()")
        click_url = ad.xpath(".//ClickThrough/text()")
        creative_id = ad.xpath(".//Creative/@id")
        creative_id = creative_id[0] if creative_id else None
        media_files = ad.xpath(".//MediaFile")
        media_urls = [mf.text.strip() for mf in media_files if mf.text]

        ssai_creative_id = get_ssai_creative_id(ad)

        adomain = None
        adomain_nodes = ad.xpath('.//AdVerifications/Verification/AdVerificationParameters/Adomain/text()')
        if not adomain_nodes:
            adomain_nodes = ad.xpath('.//Extension[@type="advertiser"]/Adomain/text()')
        if not adomain_nodes:
            adomain_nodes = ad.xpath('.//Advertiser/text()')
        adomain = adomain_nodes[0] if adomain_nodes else None

        # --- NEW: If no adomain, follow clickthrough and get domain ---
        if adomain is None and click_url and click_url[0]:
            try:
                resp = requests.get(click_url[0], headers=headers, timeout=5, allow_redirects=True)
                final_url = resp.url
                adomain = urlparse(final_url).netloc
            except Exception:
                adomain = None
        # -------------------------------------------------------------

        creative_hash = make_creative_hash(ssai_creative_id, creative_id, ','.join(media_urls), adomain if adomain else '')

        ad_xml = etree.tostring(ad, pretty_print=True, encoding='unicode')

        # Prepare wrapper chain and broken URL info
        # Only mark as broken if this specific ad is a wrapper that led to the broken URL
        wrapper_chain_json = None
        broken_wrapper_url = None
        
        # Check if this specific ad is a wrapper that led to a broken URL
        original_wrapper_ad_id = None
        broken_wrapper_ad_id = None
        
        if wrapped_flag and broken_wrapper_info:
            ad_wrapper = ad.find("Wrapper")
            if ad_wrapper is not None:
                ad_wrapper_url = ad_wrapper.findtext("VASTAdTagURI")
                if ad_wrapper_url and ad_wrapper_url.strip() == broken_wrapper_info['broken_url']:
                    wrapper_chain_json = json.dumps(broken_wrapper_info['wrapper_chain'])
                    broken_wrapper_url = broken_wrapper_info['broken_url']
                    original_wrapper_ad_id = broken_wrapper_info.get('original_wrapper_ad_id')
                    broken_wrapper_ad_id = broken_wrapper_info.get('broken_wrapper_ad_id')
                    print(f"🔗 Marking ad {ad_id} as having broken wrapper: {broken_wrapper_url}")
                    print(f"   Original wrapper ad ID: {original_wrapper_ad_id}")
                    print(f"   Broken wrapper ad ID: {broken_wrapper_ad_id}")

        cur.execute("""
            INSERT INTO vast_ads (
                call_number, ad_id, creative_id, ssai_creative_id, title, duration, clickthrough, media_urls,
                channel_name, adomain, creative_hash, ad_xml, wrapped_ad, initial_metadata_json,
                broken_wrapper_url, wrapper_chain, original_wrapper_ad_id, broken_wrapper_ad_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            call_number,
            ad_id,
            creative_id,
            ssai_creative_id,
            title[0] if title else None,
            duration[0] if duration else None,
            click_url[0] if click_url else None,
            json.dumps(media_urls),
            channel_name,
            adomain,
            creative_hash,
            ad_xml,
            int(wrapped_flag),
            initial_metadata_json,
            broken_wrapper_url,
            wrapper_chain_json,
            original_wrapper_ad_id,
            broken_wrapper_ad_id
        ))

    conn.commit()
    conn.close()
    
    if broken_wrapper_info:
        return f"✅ Parsed and stored {len(ads)} ads. ⚠️ Broken wrapper detected: {broken_wrapper_info['broken_url']} - {broken_wrapper_info['reason']}"
    return f"✅ Parsed and stored {len(ads)} ads."

# Ensure table exists at import
setup_db()
