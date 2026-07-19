process REPORT_KLEBSIELLA {
    tag { sample_id }
    publishDir { "results/${sample_id}/report" }, mode: 'copy'

    input:
    tuple val(sample_id), path(kleborate_result)
    path(template)

    output:
    path("*.html")
    path("*.pdf")

    script:
    """
    quarto render ${template} \
      -P sample_id:${sample_id} \
      -P kleborate_file:${kleborate_result} \
      --to html

    quarto render ${template} \
      -P sample_id:${sample_id} \
      -P kleborate_file:${kleborate_result} \
      --to pdf
    """
}
