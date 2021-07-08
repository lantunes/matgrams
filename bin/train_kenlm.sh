#!/bin/sh
# This script assumes the kenlm bin folder is on the PATH; the bin folder is usually found in the kenlm build folder.
# This script expects 4 arguments:
#  1. the language model order (e.g. 10)
#  2. the location of the corpus text file (e.g. "data/all_formulas_corpus.txt")
#  3. the destination directory for the output (e.g. "out")
#  4. a name to use for the generated .arpa and .klm files (e.g. "all_formulas_corpus_n20")

lmplz -o $1 --discount_fallback --text $2 --arpa $3/$4.arpa

build_binary $3/$4.arpa $3/$4.klm