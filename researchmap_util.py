#!/usr/bin/env python3

import json
import argparse
import csv
from datetime import datetime
import sys

def load_jsonl_files(filenames):
    data = []
    for fn in filenames:
        with open(fn, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
    return data

def extract_date(item):
    m = item.get('merge', {})
    if 'publication_date' in m:
        return m['publication_date']
    if 'from_event_date' in m:
        return m['from_event_date']
    if 'award_date' in m:
        return m['award_date']
    return None

def extract_title(item):
    m = item.get('merge', {})
    # papers
    if 'paper_title' in m:
        # prefer English, fallback to Japanese
        return (m['paper_title'].get('en', '').strip(), m['paper_title'].get('ja', '').strip())
    # presentations
    if 'presentation_title' in m:
        return (m['presentation_title'].get('en', '').strip(), m['presentation_title'].get('ja', '').strip())
    return (None, None)

def in_date_range(item, start_date=None, end_date=None):
    ds = extract_date(item)
    if not ds:
        return False
    try:
        try:
            d = datetime.strptime(ds, "%Y-%m-%d")
        except ValueError:
            try:
                d = datetime.strptime(ds, "%Y-%m")
            except ValueError:
                d = datetime.strptime(ds, "%Y")
        if start_date and d < start_date:
            return False
        if end_date and d > end_date:
            return False
        return True
    except ValueError:
        print("Warning: Invalid date format in item:", ds, item)
        return True

def categorize(item):
    t = item.get('insert', {}).get('type')
    m = item.get('merge', {})
    langs = m.get('languages', [])
    invited = m.get('invited', False)
    if t == 'presentations':
        if invited:
            return 'Invited Talk'
        if 'jpn' in langs:
            return 'Domestic Presentation'
        if 'eng' in langs:
            return 'International Presentation'
    elif t == 'published_papers':
        return 'Academic Paper'
    elif t == 'awards':
        return 'Award'
    return None

def has_author(item, names, key):
    m = item.get('merge', {})
    for lang in ('ja', 'en'):
        for a in m.get(key, {}).get(lang, []):
            n = a.get('name')
            if n and n in names:
                return True
    return False

if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Convert ResearchMap JSONL to JSON or categorized CSV"
    )
    p.add_argument('filenames', nargs='+',
                   help='One or more ResearchMap JSONL files')
    p.add_argument('--start-date', type=str, default=None,
                   help='YYYY-MM-DD (inclusive)')
    p.add_argument('--end-date',   type=str, default=None,
                   help='YYYY-MM-DD (inclusive)')
    grp = p.add_mutually_exclusive_group()
    grp.add_argument('--jsonl', action='store_true',
                     help='Output filtered items as JSONL')
    grp.add_argument('--csv',   action='store_true',
                     help='Output as a single CSV')
    p.add_argument('--author', type=str, nargs='+', default=None,
                   help='Filter by author name (JA or EN)')
    p.add_argument('--dedupe', action='store_true',
                   help='Omit duplicate items with identical date+title')
    p.add_argument('--output', '-o', type=argparse.FileType('w', encoding='utf-8'),
                   default=sys.stdout,
                   help='Output file (default: stdout)')
    args = p.parse_args()

    # 1) load & initial filter
    all_items = load_jsonl_files(args.filenames)

    sd = datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else None
    ed = datetime.strptime(args.end_date,   "%Y-%m-%d") if args.end_date   else None

    filtered = []
    authors = set(args.author) if args.author else None
    for item in all_items:
        # date range
        if (sd or ed) and not in_date_range(item, sd, ed):
            continue
        # author filter
        if authors and not (
            has_author(item, authors, 'authors')
            or has_author(item, authors, 'winners')
            or has_author(item, authors, 'presenters')
        ):
            continue
        filtered.append(item)

    # 2) dedupe if requested
    if args.dedupe:
        seen = set()
        unique = []
        for item in filtered:
            key = (extract_date(item), *extract_title(item))
            if key not in seen:
                seen.add(key)
                unique.append(item)
        filtered = unique

    # 3) output
    if args.jsonl:
        for item in filtered:
            print(json.dumps(item, ensure_ascii=False), file=args.output)

    elif args.csv:
        writer = csv.writer(args.output)
        writer.writerow(['Date','Category','Title (En)', 'Title (Ja)','Authors (En)', 'Authors (Ja)','Publication/Award/Event',
            'Volume', 'Number', 'Start Page', 'End Page'])
        for item in sorted(filtered, key=lambda it: extract_date(it) or ''):
            m    = item['merge']
            date = extract_date(item) or ''
            cat  = categorize(item) or 'Other'
            title_en, title_ja = extract_title(item)
            auths = {'en': [], 'ja': []}
            if cat == 'Academic Paper':
                key_authors = 'authors'
            elif cat == 'Award':
                key_authors = 'winners'
            else:
                key_authors = 'presenters'
            for lang in ('en', 'ja'):
                auths[lang].extend([a['name'] for a in m.get(key_authors, {}).get(lang,[])])
            publication_name = (m.get('publication_name',{}).get('en')
                     or m.get('publication_name',{}).get('ja')
                     or m.get('award_name',{}).get('en')
                     or m.get('award_name',{}).get('ja')
                     or m.get('event',{}).get('en')
                     or m.get('event',{}).get('ja'))

            volume        = m.get('volume', '') or ''
            number        = m.get('number', '') or ''
            start_page    = m.get('starting_page', '') or m.get('start_page', '') or ''
            end_page      = m.get('ending_page', '') or m.get('end_page', '') or ''

            writer.writerow([
                date,
                cat,
                title_en,
                title_ja,
                "; ".join(auths['en']),
                "; ".join(auths['ja']),
                publication_name,
                volume,
                number,
                start_page,
                end_page
            ])

    else:
        print(json.dumps(filtered, ensure_ascii=False, indent=2),
              file=args.output)

    if args.output is not sys.stdout:
        args.output.close()
