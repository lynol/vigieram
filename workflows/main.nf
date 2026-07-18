nextflow.enable.dsl=2

include { FASTP } from './modules/fastp.nf'
include { SHOVILL } from './modules/shovill.nf'
include { KRAKEN2 } from './modules/kraken2.nf'
include { MYKROBE } from './modules/mykrobe.nf'
include { REPORT } from './modules/report.nf'

params.reads = "data/raw/*/*_{1,2}.fastq.gz"
params.kraken_db = "${launchDir}/data/reference/kraken2_db"

workflow {
    read_pairs_ch = Channel.fromFilePairs(params.reads)
    template_ch = Channel.fromPath("${workflow.projectDir}/report/template.qmd").first()

    FASTP(read_pairs_ch)
    SHOVILL(FASTP.out.clean_reads)
    KRAKEN2(SHOVILL.out.assembly)
    MYKROBE(FASTP.out.clean_reads)
    REPORT(MYKROBE.out.result, template_ch)
}
