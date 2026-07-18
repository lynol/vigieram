process KRAKEN2 {
    tag { sample_id }
    publishDir { "results/${sample_id}/kraken2" }, mode: 'copy'

    input:
    tuple val(sample_id), path(contigs)

    output:
    tuple val(sample_id), path("${sample_id}.report"), emit: report
    path("${sample_id}.kraken")

    script:
    """
    kraken2 --db ${params.kraken_db} \
      --output ${sample_id}.kraken \
      --report ${sample_id}.report \
      --use-names \
      ${contigs}
    """
}
