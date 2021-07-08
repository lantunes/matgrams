import csv
import re
from pymatgen import Composition, Element

plain_atom_group = "(?P<plain_atom>%s)" % "|".join(reversed(sorted([e.symbol for e in Element], key=len)))
num_group = "(?P<num>[0-9]+)"
FORMULA_RE = "%s|%s" % (plain_atom_group, num_group)


def tokenize(formula):
    tokens = []
    for i in re.finditer(FORMULA_RE, formula):
        value = i.group()
        tokens.append(value)
    return tokens


if __name__ == '__main__':

    out_file = "../out/all_formulas_corpus.txt"
    formulas_file = "../out/all_formulas.csv"

    with open(formulas_file, "rt") as f, open(out_file, "wt") as outf:
        reader = csv.reader(f)
        for line in reader:
            formula = line[1]
            comp = Composition(formula)
            formula = str(comp).replace(" ", "")
            toks = tokenize(formula)
            assert "".join(toks) == formula, "%s, %s" % (toks, formula)
            outf.write("%s\n" % " ".join(toks))
