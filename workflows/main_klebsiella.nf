nextflow.enable.dsl=2

include { KLEBORATE } from './modules/kleborate.nf'
include { REPORT_KLEBSIELLA } from './modules/report_klebsiella.nf'

params.assemblies = "data/raw/klebsiella/fasta/*.fna"

workflow {
    assembly_ch = Channel.fromPath(params.assemblies)
        .map { file -> tuple(file.simpleName, file) }

    template_ch = Channel.fromPath("${workflow.projectDir}/report/template_klebsiella.qmd").first()

    KLEBORATE(assembly_ch)
    REPORT_KLEBSIELLA(KLEBORATE.out.result, template_ch)
}
