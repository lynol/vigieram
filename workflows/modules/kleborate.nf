process KLEBORATE {
    tag { sample_id }
    publishDir { "results/${sample_id}/kleborate" }, mode: 'copy'
    errorStrategy 'ignore'

    input:
    tuple val(sample_id), path(assembly)

    output:
    tuple val(sample_id), path("klebsiella_pneumo_complex_output.txt"), emit: result

    script:
    """
    kleborate -a ${assembly} -o . -p kpsc
    """
}
