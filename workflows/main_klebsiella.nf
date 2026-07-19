nextflow.enable.dsl=2

include { KLEBORATE } from './modules/kleborate.nf'

params.assemblies = "data/raw/klebsiella/fasta/*.fna"

workflow {
    assembly_ch = Channel.fromPath(params.assemblies)
        .map { file -> tuple(file.simpleName, file) }

    KLEBORATE(assembly_ch)
}
