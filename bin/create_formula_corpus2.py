import csv
from pymatgen import Composition
import itertools


if __name__ == '__main__':

    out_file = "../out/all_formulas_corpus2b.txt"
    formulas_file = "../data/all_formulas.csv"

    with open(formulas_file, "rt") as f, open(out_file, "wt") as outf:
        reader = csv.reader(f)
        for line in reader:
            formula = line[1]
            comp = Composition(formula)
            formula = str(comp).replace(" ", "")
            toks = comp.alphabetical_formula.split(" ")

            for t in itertools.permutations(toks):
                outf.write("%s\n" % " ".join(t))
