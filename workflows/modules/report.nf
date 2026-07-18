process REPORT {
    tag { sample_id }
    publishDir { "results/${sample_id}/report" }, mode: 'copy'

    input:
    tuple val(sample_id), path(mykrobe_json)
    path(template)

    output:
    path("*.html")
    path("*.pdf")

    script:
    """
    quarto render ${template} \
      -P sample_id:${sample_id} \
      -P mykrobe_json:${mykrobe_json} \
      --to html

    quarto render ${template} \
      -P sample_id:${sample_id} \
      -P mykrobe_json:${mykrobe_json} \
      --to pdf
    """
}
