import pandas as pd

truth = pd.read_csv('data/reference/klebsiella_selected.csv')
truth = truth.set_index('Assembly')

pred = pd.read_csv('results/klebsiella_validation/klebsiella_pneumo_complex_output.txt', sep='\t')
pred = pred.set_index('strain')

rows = []
for acc in truth.index:
    if acc not in pred.index:
        continue
    species = pred.loc[acc, 'enterobacterales__species__species']
    carb_genes = pred.loc[acc, 'klebsiella_pneumo_complex__amr__Bla_Carb_acquired']
    predicted_cre = carb_genes != '-'

    rows.append({
        'Assembly': acc,
        'Species': species,
        'CRE_connu': truth.loc[acc, 'CRE'],
        'CRE_predit': predicted_cre,
        'Genes_carbapenemase': carb_genes,
        'Accord': truth.loc[acc, 'CRE'] == predicted_cre,
    })

df = pd.DataFrame(rows)
print(df.to_string(index=False))
df.to_csv('results/klebsiella_validation_table.csv', index=False)
print(f"\n--- Résumé ---")
print(f"CRE : {df['Accord'].sum()}/{len(df)} corrects ({100*df['Accord'].mean():.1f}%)")
