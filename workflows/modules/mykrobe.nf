process MYKROBE {
    tag { sample_id }
    publishDir { "results/${sample_id}/mykrobe" }, mode: 'copy'

    input:
    tuple val(sample_id), path(read1), path(read2)

    output:
    tuple val(sample_id), path("${sample_id}.json"), emit: result

    script:
    """
    mykrobe predict \
      --sample ${sample_id} --species typhi --format json \
      --out ${sample_id}.json \
      --seq ${read1} ${read2}
    """
}
