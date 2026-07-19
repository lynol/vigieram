nextflow.enable.dsl=2

include { FASTP } from './modules/fastp.nf'
include { SHOVILL } from './modules/shovill.nf'
include { KRAKEN2 } from './modules/kraken2.nf'
include { MYKROBE } from './modules/mykrobe.nf'
include { REPORT } from './modules/report.nf'

params.species = 'typhi'
params.kraken_db = "${launchDir}/data/reference/kraken2_db"

workflow {
    def reads_glob       = params.species == 'tb' ? 'data/raw/tb/*/*_{1,2}.fastq.gz' : 'data/raw/*/*_{1,2}.fastq.gz'
    def template_name    = params.species == 'tb' ? 'template_tb.qmd' : 'template.qmd'
    def gsize            = params.species == 'tb' ? '4.4M' : '4.8M'
    def mykrobe_species  = params.species == 'tb' ? 'tb' : 'typhi'

    read_pairs_ch = Channel.fromFilePairs(reads_glob)
    template_ch = Channel.fromPath("${workflow.projectDir}/report/${template_name}").first()

    FASTP(read_pairs_ch)
    SHOVILL(FASTP.out.clean_reads, gsize)
    KRAKEN2(SHOVILL.out.assembly)
    MYKROBE(FASTP.out.clean_reads, mykrobe_species)
    REPORT(MYKROBE.out.result, template_ch)
}
