process FASTP {
    tag { sample_id }
    publishDir { "results/${sample_id}/fastp" }, mode: 'copy'

    input:
    tuple val(sample_id), path(reads)

    output:
    tuple val(sample_id), path("${sample_id}_1.clean.fastq.gz"), path("${sample_id}_2.clean.fastq.gz"), emit: clean_reads
    path("fastp.json")
    path("fastp.html")

    script:
    """
    fastp \
      -i ${reads[0]} \
      -I ${reads[1]} \
      -o ${sample_id}_1.clean.fastq.gz \
      -O ${sample_id}_2.clean.fastq.gz \
      -j fastp.json \
      -h fastp.html
    """
}
