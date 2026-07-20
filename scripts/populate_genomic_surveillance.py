import sqlite3
import pandas as pd
from datetime import date
import json
from pathlib import Path

conn = sqlite3.connect('data/db/vigieram.db')
conn.execute('DELETE FROM genomic_surveillance')  # on repart propre
today = str(date.today())

# --- Typhi : region + profil de resistance detaille depuis Mykrobe ---
typhi = pd.read_csv('results/validation_table.csv')
country_r1 = pd.read_csv('data/reference/selected_samples.csv').set_index('Data Accession')['Country'].to_dict()
country_r2 = pd.read_csv('data/reference/selected_samples_round2.csv').set_index('Data Accession')['Country'].to_dict()
countries = {**country_r1, **country_r2}

for _, r in typhi.iterrows():
    sid = r['Echantillon']
    region = countries.get(sid, countries.get(sid + '.1', 'Inconnue'))
    profile = None
    jf = Path(f'results/{sid}/mykrobe/{sid}.json')
    if jf.exists():
        with open(jf) as f:
            d = json.load(f)
        susc = d[list(d.keys())[0]]['susceptibility']
        profile = json.dumps({k: v.get('predict', 'NA').upper() for k, v in susc.items()})
    conn.execute(
        'INSERT INTO genomic_surveillance (species, sample_id, genotype, resistance_profile, mdr, xdr, region, date_added, source) VALUES (?,?,?,?,?,?,?,?,?)',
        ('Salmonella Typhi', sid, r.get('Genotype_predit', ''), profile,
         int(bool(r.get('MDR_predit', False))), int(bool(r.get('XDR_predit', False))), region, today, 'public_data')
    )

# --- Klebsiella : region depuis Location, pas de profil detaille (structure gene/classe differente) ---
kleb = pd.read_csv('results/klebsiella_validation_table.csv')
kleb_loc = pd.read_csv('data/reference/klebsiella_selected.csv').set_index('Assembly')['Location'].to_dict()
for _, r in kleb.iterrows():
    if r['Species'] == 'ECHEC PIPELINE':
        continue
    acc = r['Assembly']
    region = kleb_loc.get(acc, 'Inconnue')
    conn.execute(
        'INSERT INTO genomic_surveillance (species, sample_id, mdr, xdr, region, date_added, source) VALUES (?,?,?,?,?,?,?)',
        ('Klebsiella pneumoniae', acc, 0, int(bool(r.get('CRE_predit', False))), region, today, 'public_data')
    )

# --- TB : pas de colonne region disponible dans CRyPTIC_reuse_table -> honnetement marque "Inconnue" ---
tb = pd.read_csv('results/tb_validation_table.csv')
for _, r in tb.iterrows():
    sid = r['Echantillon']
    profile = None
    jf = Path(f'results/{sid}/mykrobe/{sid}.json')
    if jf.exists():
        with open(jf) as f:
            d = json.load(f)
        susc = d[list(d.keys())[0]]['susceptibility']
        profile = json.dumps({k: v.get('predict', 'NA').upper() for k, v in susc.items()})
    conn.execute(
        'INSERT INTO genomic_surveillance (species, sample_id, resistance_profile, mdr, region, date_added, source) VALUES (?,?,?,?,?,?,?)',
        ('Mycobacterium tuberculosis', sid, profile, int(bool(r.get('MDR_predit', False))), 'Inconnue', today, 'public_data')
    )

conn.commit()
n = conn.execute('SELECT COUNT(*) FROM genomic_surveillance').fetchone()[0]
print(f"{n} lignes inserees")
conn.close()
