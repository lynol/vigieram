#!/bin/bash
set -e

SAMPLE=$1

echo "=== $SAMPLE : nettoyage (fastp) ==="
mkdir -p results/$SAMPLE/fastp
fastp \
  -i data/raw/$SAMPLE/${SAMPLE}_1.fastq.gz \
  -I data/raw/$SAMPLE/${SAMPLE}_2.fastq.gz \
  -o results/$SAMPLE/fastp/${SAMPLE}_1.clean.fastq.gz \
  -O results/$SAMPLE/fastp/${SAMPLE}_2.clean.fastq.gz \
  -j results/$SAMPLE/fastp/fastp.json \
  -h results/$SAMPLE/fastp/fastp.html

echo "=== $SAMPLE : assemblage (shovill) ==="
shovill \
  --R1 results/$SAMPLE/fastp/${SAMPLE}_1.clean.fastq.gz \
  --R2 results/$SAMPLE/fastp/${SAMPLE}_2.clean.fastq.gz \
  --outdir results/$SAMPLE/shovill \
  --gsize 4.8M --cpus 4 --force

echo "=== $SAMPLE : confirmation espèce (Kraken2) ==="
mkdir -p results/$SAMPLE/kraken2
kraken2 --db data/reference/kraken2_db \
  --output results/$SAMPLE/kraken2/$SAMPLE.kraken \
  --report results/$SAMPLE/kraken2/$SAMPLE.report \
  --use-names \
  results/$SAMPLE/shovill/contigs.fa

echo "=== $SAMPLE : génotypage + résistance (Mykrobe) ==="
mkdir -p results/$SAMPLE/mykrobe
mykrobe predict \
  --sample $SAMPLE --species typhi --format json \
  --out results/$SAMPLE/mykrobe/$SAMPLE.json \
  --seq results/$SAMPLE/fastp/${SAMPLE}_1.clean.fastq.gz results/$SAMPLE/fastp/${SAMPLE}_2.clean.fastq.gz

echo "=== $SAMPLE : terminé ==="
