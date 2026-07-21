from flask import Flask, render_template
import sqlite3

app = Flask(__name__)
DB = '../data/db/vigieram.db'
MIN_N = 5

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def get_layer1_summary():
    conn = get_conn()
    rows = conn.execute('''
        SELECT species, COUNT(*) as total, SUM(mdr) as mdr_n, SUM(xdr) as xdr_n
        FROM genomic_surveillance GROUP BY species
    ''').fetchall()
    conn.close()
    return [{
        'species': r['species'], 'total': r['total'],
        'pct_mdr': round(100 * (r['mdr_n'] or 0) / r['total'], 1),
        'pct_xdr': round(100 * (r['xdr_n'] or 0) / r['total'], 1),
    } for r in rows]

def get_layer2_summary():
    conn = get_conn()
    n_facilities = conn.execute(
        'SELECT COUNT(DISTINCT facility_name_norm) as n FROM clinical_ast WHERE facility_name_norm != ""'
    ).fetchone()['n']
    n_entries = conn.execute('SELECT COUNT(*) as n FROM clinical_ast').fetchone()['n']

    regional = conn.execute('''
        SELECT region, organism, antibiotic,
               SUM(CASE WHEN result='R' THEN 1 ELSE 0 END) as r,
               COUNT(*) as total
        FROM clinical_ast
        WHERE region != ''
        GROUP BY region, organism, antibiotic
        HAVING total >= ?
        ORDER BY region, organism
    ''', (MIN_N,)).fetchall()
    conn.close()

    regional_stats = [{
        'region': r['region'], 'organism': r['organism'], 'antibiotic': r['antibiotic'],
        'pct_r': round(100 * r['r'] / r['total'], 1), 'n': r['total']
    } for r in regional]

    return {'n_facilities': n_facilities, 'n_entries': n_entries, 'regional_stats': regional_stats}

@app.route('/')
def dashboard():
    layer1 = get_layer1_summary()
    layer2 = get_layer2_summary()
    return render_template('index.html', layer1=layer1, layer2=layer2, min_n=MIN_N)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
