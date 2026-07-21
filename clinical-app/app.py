from flask import Flask, render_template, request, redirect
import sqlite3
import pandas as pd
import json
import subprocess
from datetime import date
import csv as csv_module
import re
import unicodedata


def normalize_facility(name):
    if not name:
        return ''
    nfkd = unicodedata.normalize('NFKD', name.strip().lower())
    return ''.join(c for c in nfkd if not unicodedata.combining(c))

ANTIBIOTIC_CODES = {
    'AMP': 'ampicillin', 'AMC': 'amoxicillin-clavulanic acid', 'TZP': 'piperacillin-tazobactam',
    'FEP': 'cefepime', 'CTX': 'cefotaxime', 'FOX': 'cefoxitin', 'CAZ': 'ceftazidime',
    'CRO': 'ceftriaxone', 'CIP': 'ciprofloxacin', 'AMK': 'amikacin', 'GEN': 'gentamicin',
    'TOB': 'tobramycin', 'SXT': 'trimethoprim-sulfamethoxazole', 'IPM': 'imipenem',
    'MEM': 'meropenem', 'PEN': 'penicillin', 'CHL': 'chloramphenicol', 'VAN': 'vancomycin',
    'OXA': 'oxacillin', 'ERY': 'erythromycin', 'CLI': 'clindamycin', 'TCY': 'tetracycline',
    'RIF': 'rifampicin', 'NIT': 'nitrofurantoin', 'NOR': 'norfloxacin', 'COL': 'colistin',
    'KAN': 'kanamycin', 'STR': 'streptomycin', 'LVX': 'levofloxacin', 'MXF': 'moxifloxacin',
    'INH': 'isoniazid', 'EMB': 'ethambutol', 'PZA': 'pyrazinamide', 'LZD': 'linezolid',
}

def load_organism_codes():
    codes = {}
    try:
        with open('../data/reference/whonet_organism_codes.csv') as f:
            reader = csv_module.DictReader(f)
            for row in reader:
                codes[row['code'].upper()] = row['full_name']
    except FileNotFoundError:
        pass
    return codes

ORGANISM_CODES = load_organism_codes()

def load_intrinsic_resistance():
    pairs = set()
    try:
        with open('../data/reference/intrinsic_resistance.csv') as f:
            reader = csv_module.DictReader(f)
            for row in reader:
                org = ORGANISM_CODES.get(row['organism_code'].upper(), row['organism_code'])
                abx = ANTIBIOTIC_CODES.get(row['antibiotic_code'].upper(), row['antibiotic_code'].lower())
                pairs.add((org, abx))
    except FileNotFoundError:
        pass
    return pairs

INTRINSIC_RESISTANT = load_intrinsic_resistance()

def check_biological_plausibility(organism, antibiotic):
    return (organism, antibiotic.lower()) in INTRINSIC_RESISTANT

# Colonnes systematiquement exclues avant tout traitement - jamais stockees
IDENTIFYING_COLUMNS = ['Last name', 'First name', 'Identification number', 'Specimen number', 'Comment']

app = Flask(__name__)
DB = '../data/db/vigieram.db'

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.execute('''CREATE TABLE IF NOT EXISTS clinical_ast (
        id INTEGER PRIMARY KEY, organism TEXT NOT NULL, antibiotic TEXT NOT NULL,
        result TEXT NOT NULL, facility_type TEXT, facility_name TEXT, facility_name_norm TEXT,
        region TEXT, locality TEXT, context TEXT, date_added TEXT NOT NULL, entry_method TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS genomic_surveillance (
        id INTEGER PRIMARY KEY, species TEXT NOT NULL, sample_id TEXT NOT NULL,
        genotype TEXT, resistance_profile TEXT, mdr INTEGER, xdr INTEGER,
        region TEXT, date_added TEXT NOT NULL, source TEXT)''')
    conn.commit()
    conn.close()

def get_genomic_context(organism, region, antibiotic):
    conn = get_conn()

    # Essai 1 : meme region exacte (peu probable pour la CI aujourd'hui, on le signale)
    rows_regional = conn.execute(
        'SELECT * FROM genomic_surveillance WHERE species = ? AND LOWER(region) = LOWER(?)',
        (organism, region)
    ).fetchall()

    scope = 'regionale'
    rows = rows_regional
    if not rows:
        scope = 'mondiale (aucune donnee regionale disponible)'
        rows = conn.execute('SELECT * FROM genomic_surveillance WHERE species = ?', (organism,)).fetchall()
    conn.close()

    if not rows:
        return None

    total = len(rows)
    mdr_pct = round(100 * sum(r['mdr'] or 0 for r in rows) / total, 1)
    xdr_pct = round(100 * sum(r['xdr'] or 0 for r in rows) / total, 1)

    # Comparaison specifique a l'antibiotique saisi, si la donnee existe
    abx_stat = None
    profiles = [json.loads(r['resistance_profile']) for r in rows if r['resistance_profile']]
    if profiles:
        profiles_lower = [{k.lower(): v for k, v in p.items()} for p in profiles]
        matches = [p.get(antibiotic.lower()) for p in profiles_lower if antibiotic.lower() in p]
        if matches:
            r_count = sum(1 for m in matches if m == 'R')
            abx_stat = {'n': len(matches), 'pct_r': round(100 * r_count / len(matches), 1)}

    return {'total': total, 'pct_mdr': mdr_pct, 'pct_xdr': xdr_pct, 'scope': scope, 'abx_stat': abx_stat}

@app.route('/', methods=['GET', 'POST'])
def entry_form():
    context = None
    organism = None
    if request.method == 'POST':
        organism = request.form['organism']
        antibiotic = request.form['antibiotic']
        region = request.form['region']
        conn = get_conn()
        fname = request.form.get('facility_name', '')
        conn.execute(
            'INSERT INTO clinical_ast (organism, antibiotic, result, facility_type, facility_name, facility_name_norm, region, locality, context, date_added, entry_method) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
            (organism, antibiotic, request.form['result'], request.form['facility_type'],
             fname, normalize_facility(fname), region, request.form.get('locality', ''),
             request.form.get('context', ''), str(date.today()), 'manuel')
        )
        conn.commit()
        conn.close()
        context = get_genomic_context(organism, region, antibiotic)
        implausible = check_biological_plausibility(organism, antibiotic)
        return render_template('entry_form.html', success=True, context=context, organism=organism, antibiotic=antibiotic, implausible=implausible)
    return render_template('entry_form.html', success=False)

@app.route('/mon-etablissement')
def facility_stats():
    facility = request.args.get('facility_name', '')
    if not facility:
        return render_template('facility_select.html')

    conn = get_conn()
    rows = conn.execute(
        'SELECT organism, antibiotic, result, date_added FROM clinical_ast WHERE facility_name_norm = ? ORDER BY date_added',
        (normalize_facility(facility),)
    ).fetchall()
    conn.close()

    stats = {}
    for r in rows:
        key = (r['organism'], r['antibiotic'])
        stats.setdefault(key, {'R': 0, 'I': 0, 'S': 0, 'total': 0})
        stats[key][r['result']] += 1
        stats[key]['total'] += 1

    return render_template('facility_stats.html', facility=facility, stats=stats, n_entries=len(rows))

@app.route('/mon-etablissement/rapport')
def facility_report():
    facility = request.args.get('facility_name', '')
    if not facility:
        return redirect('/mon-etablissement')
    subprocess.run([
        'quarto', 'render', 'facility_report.qmd',
        '-P', f'facility:{facility}',
        '-P', 'db_path:../data/db/vigieram.db',
        '--to', 'pdf'
    ], check=True)
    from flask import send_file
    return send_file('facility_report.pdf', as_attachment=True)

@app.route('/import-whonet', methods=['GET', 'POST'])
def import_whonet():
    if request.method == 'POST':
        file = request.files.get('whonet_file')
        facility_name = request.form.get('facility_name', '')
        region = request.form.get('region', '')
        if not file:
            return "Aucun fichier recu", 400

        df = pd.read_csv(file)
        # Securite : suppression immediate des colonnes potentiellement identifiantes
        df = df.drop(columns=[c for c in IDENTIFYING_COLUMNS if c in df.columns], errors='ignore')

        abx_pattern = re.compile(r'^([A-Za-z]{2,4})_')
        abx_columns = [c for c in df.columns if abx_pattern.match(c)]

        conn = get_conn()
        n_inserted = 0
        n_implausible = 0
        for _, row in df.iterrows():
            raw_organism = str(row.get('Organism', 'Inconnu'))
            organism = ORGANISM_CODES.get(raw_organism.upper(), raw_organism)
            for col in abx_columns:
                result = row.get(col)
                if pd.isna(result) or result not in ('S', 'I', 'R'):
                    continue
                code = abx_pattern.match(col).group(1).upper()
                antibiotic = ANTIBIOTIC_CODES.get(code, code.lower())
                conn.execute(
                    'INSERT INTO clinical_ast (organism, antibiotic, result, facility_type, facility_name, facility_name_norm, region, locality, context, date_added, entry_method) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                    (str(organism), antibiotic, result, 'labo_reference', facility_name, normalize_facility(facility_name), region, '', '', str(date.today()), 'whonet_import')
                )
                n_inserted += 1
                if check_biological_plausibility(str(organism), antibiotic):
                    n_implausible += 1
        conn.commit()
        conn.close()
        return render_template('whonet_result.html', n_rows=len(df), n_inserted=n_inserted, dropped_cols=IDENTIFYING_COLUMNS, n_implausible=n_implausible)
    return render_template('whonet_upload.html')

@app.route('/api/facilities')
def api_facilities():
    conn = get_conn()
    rows = conn.execute('SELECT DISTINCT facility_name FROM clinical_ast WHERE facility_name != ""').fetchall()
    conn.close()
    from flask import jsonify
    return jsonify([r['facility_name'] for r in rows])

@app.route('/mon-etablissement/tendance')
def facility_trend():
    facility = request.args.get('facility_name', '')
    organism = request.args.get('organism', '')
    antibiotic = request.args.get('antibiotic', '')
    conn = get_conn()
    rows = conn.execute('''
        SELECT strftime('%Y-%m', date_added) as month, result, COUNT(*) as n
        FROM clinical_ast
        WHERE facility_name_norm = ? AND organism = ? AND antibiotic = ?
        GROUP BY month, result
        ORDER BY month
    ''', (normalize_facility(facility), organism, antibiotic)).fetchall()
    conn.close()

    months = {}
    for r in rows:
        months.setdefault(r['month'], {'R': 0, 'I': 0, 'S': 0})
        months[r['month']][r['result']] = r['n']

    labels = sorted(months.keys())
    pct_r = []
    totals = []
    for m in labels:
        total = sum(months[m].values())
        totals.append(total)
        pct_r.append(round(100 * months[m]['R'] / total, 1) if total else 0)

    return render_template('facility_trend.html', facility=facility, organism=organism,
                            antibiotic=antibiotic, labels=labels, pct_r=pct_r, totals=totals)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
