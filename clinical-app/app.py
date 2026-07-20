from flask import Flask, render_template, request, redirect
import sqlite3
import json
from datetime import date

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
        result TEXT NOT NULL, facility_type TEXT, facility_name TEXT, region TEXT,
        locality TEXT, context TEXT, date_added TEXT NOT NULL, entry_method TEXT)''')
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
        conn.execute(
            'INSERT INTO clinical_ast (organism, antibiotic, result, facility_type, facility_name, region, locality, context, date_added, entry_method) VALUES (?,?,?,?,?,?,?,?,?,?)',
            (organism, antibiotic, request.form['result'], request.form['facility_type'],
             request.form.get('facility_name', ''), region, request.form.get('locality', ''),
             request.form.get('context', ''), str(date.today()), 'manuel')
        )
        conn.commit()
        conn.close()
        context = get_genomic_context(organism, region, antibiotic)
        return render_template('entry_form.html', success=True, context=context, organism=organism, antibiotic=antibiotic)
    return render_template('entry_form.html', success=False)

@app.route('/mon-etablissement')
def facility_stats():
    facility = request.args.get('facility_name', '')
    if not facility:
        return render_template('facility_select.html')

    conn = get_conn()
    rows = conn.execute(
        'SELECT organism, antibiotic, result, date_added FROM clinical_ast WHERE LOWER(facility_name) = LOWER(?) ORDER BY date_added',
        (facility,)
    ).fetchall()
    conn.close()

    stats = {}
    for r in rows:
        key = (r['organism'], r['antibiotic'])
        stats.setdefault(key, {'R': 0, 'I': 0, 'S': 0, 'total': 0})
        stats[key][r['result']] += 1
        stats[key]['total'] += 1

    return render_template('facility_stats.html', facility=facility, stats=stats, n_entries=len(rows))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
