import kenlm
import numpy as np
from pymatgen import Composition, Element
from pymatgen.core.composition import CompositionError
import csv
import warnings

warnings.filterwarnings("ignore", category=UserWarning)


def normalize(probs):
    prob_factor = 1 / sum(probs)
    return [prob_factor * p for p in probs]


def get_score(lm, v, context):
    return lm.score(context + " " + v, bos=False, eos=False)


def get_arpa_vocab(arpa_file_path, exclude_unk=True):
    with open(arpa_file_path, 'r') as f:
        lines = f.readlines()

    tokens = []

    in_1_grams = False
    for line in lines:
        if line.startswith('\\1'):
            in_1_grams = True
        if in_1_grams and not line.startswith('\\'):
            vals = line.split('\t')
            if len(vals) == 3:
                if exclude_unk and vals[1] == '<unk>':
                    continue
                tokens.append(vals[1])
        if in_1_grams and line.startswith("\\2"):
            break

    return tokens


def sample(lm, vocab, n):
    ctx = [np.random.choice([e.symbol for e in Element])]

    while not ctx or ctx[-1] != "</s>":
        scores = []
        for v in vocab:
            score = 10 ** get_score(lm, v, " ".join(ctx[-n:]))
            scores.append(score)

        c = np.random.choice(vocab, p=normalize(scores))
        ctx.append(c)

    return " ".join(ctx[:-1])


if __name__ == '__main__':
    n = 10
    lm = kenlm.Model("../out/all_formulas_corpus_n20.klm")

    vocab = get_arpa_vocab("../out/all_formulas_corpus_n20.arpa")
    vocab.remove("<s>")

    all_formulas = set()
    with open("../out/all_formulas.csv", "rt") as f:
        reader = csv.reader(f)
        for line in reader:
            all_formulas.add(line[1])

    samples = []
    for i in range(100):
        s = sample(lm, vocab, n)
        formula = s.replace(" ", "")
        if not formula:
            print("empty formula: %s" % formula)
            continue
        try:
            comp = Composition(formula)
        except CompositionError:
            print("invalid formula: %s" % formula)
            continue
        score = lm.score(s, bos=False, eos=False)
        reduced_formula = comp.reduced_formula
        if reduced_formula in all_formulas:
            print("EXISTS: %s" % reduced_formula)
        samples.append((reduced_formula, score))

    samples = sorted(samples, key=lambda v: v[1])

    for sample in samples:
        print(sample)
