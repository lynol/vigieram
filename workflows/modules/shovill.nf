process SHOVILL {
    tag { sample_id }
    publishDir { "results/${sample_id}/shovill" }, mode: 'copy'

    input:
    tuple val(sample_id), path(read1), path(read2)
    val gsize

    output:
    tuple val(sample_id), path("contigs.fa"), emit: assembly

    script:
    """
    shovill --R1 ${read1} --R2 ${read2} --outdir . --gsize ${gsize} --cpus 4 --force
    """
}
