from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)
DB = '../data/db/vigieram.db'

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS clinical_ast (
            id INTEGER PRIMARY KEY,
            organism TEXT NOT NULL,
            antibiotic TEXT NOT NULL,
            result TEXT NOT NULL,
            facility_type TEXT,
            region TEXT,
            context TEXT,
            date_added TEXT NOT NULL,
            entry_method TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS genomic_surveillance (
            id INTEGER PRIMARY KEY,
            species TEXT NOT NULL,
            sample_id TEXT NOT NULL,
            genotype TEXT,
            resistance_profile TEXT,
            mdr INTEGER,
            xdr INTEGER,
            region TEXT,
            date_added TEXT NOT NULL,
            source TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_genomic_context(organism):
    conn = get_conn()
    row = conn.execute(
        'SELECT COUNT(*) as total, SUM(mdr) as mdr_count, SUM(xdr) as xdr_count '
        'FROM genomic_surveillance WHERE species = ?', (organism,)
    ).fetchone()
    conn.close()
    if not row or row['total'] == 0:
        return None
    return {
        'total': row['total'],
        'pct_mdr': round(100 * (row['mdr_count'] or 0) / row['total'], 1),
        'pct_xdr': round(100 * (row['xdr_count'] or 0) / row['total'], 1),
    }

@app.route('/', methods=['GET', 'POST'])
def entry_form():
    context = None
    if request.method == 'POST':
        organism = request.form['organism']
        conn = get_conn()
        conn.execute(
            'INSERT INTO clinical_ast (organism, antibiotic, result, facility_type, region, context, date_added, entry_method) VALUES (?,?,?,?,?,?,?,?)',
            (organism, request.form['antibiotic'], request.form['result'],
             request.form['facility_type'], request.form['region'], request.form.get('context', ''),
             str(date.today()), 'manuel')
        )
        conn.commit()
        conn.close()
        context = get_genomic_context(organism)
        return render_template('entry_form.html', success=True, context=context, organism=organism)
    return render_template('entry_form.html', success=False)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
