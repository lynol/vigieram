import json
import pandas as pd
from pathlib import Path

truth = pd.read_csv('data/reference/tb_selected.csv').set_index('ENA_RUN')

results_dir = Path('results')
rows = []
for acc in truth.index:
    f = results_dir / acc / 'mykrobe' / f'{acc}.json'
    if not f.exists():
        rows.append({'Echantillon': acc, 'MDR_connu': truth.loc[acc, 'MDR'],
                     'MDR_predit': None, 'Accord': None})
        continue
    with open(f) as fh:
        data = json.load(fh)
    result = data[list(data.keys())[0]]
    susc = result['susceptibility']

    def pred(drug):
        return susc.get(drug, {}).get('predict', 'NA').upper()

    is_mdr = pred('Isoniazid') == 'R' and pred('Rifampicin') == 'R'
    rows.append({
        'Echantillon': acc,
        'MDR_connu': truth.loc[acc, 'MDR'],
        'MDR_predit': is_mdr,
        'INH_predit': pred('Isoniazid'),
        'RIF_predit': pred('Rifampicin'),
        'Accord': truth.loc[acc, 'MDR'] == is_mdr,
    })

df = pd.DataFrame(rows)
print(df.to_string(index=False))
df.to_csv('results/tb_validation_table.csv', index=False)

valid = df[df['Accord'].notna()]
n = valid['Accord'].astype(bool).sum()
print(f"\n--- Résumé ---")
print(f"MDR : {n}/{len(valid)} corrects ({100*n/len(valid):.1f}%)")
