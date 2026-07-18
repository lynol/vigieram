import json
import pandas as pd

samples = ["ERR2093255", "ERR2093334", "SRR8878443", "ERR319495",
           "ERR4790678", "ERR731380", "ERR586799", "ERR319410", "ERR998638"]

truth = pd.read_csv('data/reference/typhoid-consortium-meta/TGC_data.csv', low_memory=False)
truth = truth.set_index('Data Accession')

def get_pred(susc, antibiotic):
    return susc.get(antibiotic, {}).get('predict', 'NA')

rows = []
for s in samples:
    with open(f'results/{s}/mykrobe/{s}.json') as f:
        data = json.load(f)
    result = data[list(data.keys())[0]]
    genotype = result['phylogenetics']['lineage']['lineage'][0]
    susc = result['susceptibility']

    mdr_abx = ['ampicillin', 'chloramphenicol', 'trimethoprim', 'sulfonamides']
    is_mdr = all(get_pred(susc, a) == 'R' for a in mdr_abx)
    is_xdr = is_mdr and get_pred(susc, 'ciprofloxacin') == 'R' and get_pred(susc, 'ceftriaxone') == 'R'

    t = truth.loc[s] if s in truth.index else None
    rows.append({
        'Echantillon': s,
        'Genotype_predit': genotype,
        'Genotype_connu': t['Final_genotype'] if t is not None else 'NA',
        'MDR_predit': is_mdr,
        'MDR_connu': t['MDR'] if t is not None else 'NA',
        'XDR_predit': is_xdr,
        'XDR_connu': t['XDR'] if t is not None else 'NA',
    })

df = pd.DataFrame(rows)
print(df.to_string(index=False))
df.to_csv('results/validation_table.csv', index=False)
print("\nSauvegardé dans results/validation_table.csv")
