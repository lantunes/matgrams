Matgrams
========

Exploring chemical composition space with n-gram language models.

The hope is that this way of generating compositions is more efficient that simply enumerating all possible valid 
compositions, in that the compositions generated with the approach described here are more likely to represent stable
compounds, or compounds with properties in general that match those in the training set.

Usage
-----

```
./bin/train_kenlm.sh 20 data/all_formulas_corpus.txt out all_formulas_corpus_n20
```