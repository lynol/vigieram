import sqlite3
import pandas as pd
from datetime import date

conn = sqlite3.connect('data/db/vigieram.db')
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

today = str(date.today())

typhi = pd.read_csv('results/validation_table.csv')
for _, r in typhi.iterrows():
    conn.execute(
        'INSERT INTO genomic_surveillance (species, sample_id, genotype, mdr, xdr, date_added, source) VALUES (?,?,?,?,?,?,?)',
        ('Salmonella Typhi', r['Echantillon'], r.get('Genotype_predit', ''),
         int(bool(r.get('MDR_predit', False))), int(bool(r.get('XDR_predit', False))), today, 'public_data')
    )

kleb = pd.read_csv('results/klebsiella_validation_table.csv')
for _, r in kleb.iterrows():
    conn.execute(
        'INSERT INTO genomic_surveillance (species, sample_id, mdr, xdr, date_added, source) VALUES (?,?,?,?,?,?)',
        ('Klebsiella pneumoniae', r['Assembly'], 0, int(bool(r.get('CRE_predit', False))), today, 'public_data')
    )

tb = pd.read_csv('results/tb_validation_table.csv')
for _, r in tb.iterrows():
    conn.execute(
        'INSERT INTO genomic_surveillance (species, sample_id, mdr, date_added, source) VALUES (?,?,?,?,?)',
        ('Mycobacterium tuberculosis', r['Echantillon'], int(bool(r.get('MDR_predit', False))), today, 'public_data')
    )

conn.commit()
n = conn.execute('SELECT COUNT(*) FROM genomic_surveillance').fetchone()[0]
print(f"{n} lignes inserees dans genomic_surveillance")
conn.close()
