import kenlm
import numpy as np
from pymatgen import Composition, Element
from pymatgen.core.composition import CompositionError
from smact.screening import pauling_test
from smact import Element as smact_element
import itertools
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


def sample(lm, vocab, n, num_element_types, force):
    ctx = [np.random.choice([e.symbol for e in Element])]

    for _ in range(num_element_types - 1):
        if ctx[-1] == "</s>":
            break
        scores = []
        for v in vocab:
            score = 10 ** get_score(lm, v, " ".join(ctx[-n:]))
            scores.append(score)

        c = np.random.choice(vocab, p=normalize(scores))

        if c == "</s>" and force:
            continue

        ctx.append(c)

    if "</s>" in ctx:
        ctx.remove("</s>")
    return " ".join(ctx)


def to_smact_elem(pymatgen_elem):
    try:
        return smact_element(pymatgen_elem.name)
    except NameError as err:
        print(err)


if __name__ == '__main__':
    n = 2
    num_element_types = 4  # at most quaternary compounds should be generated
    force = True  # if True, the number of element types must be exact
    n_generated = 1000
    klm_file = "../out/all_formulas_corpus2_n2.klm"
    arpa_file = "../out/all_formulas_corpus2_n2.arpa"
    all_formulas_file = "../data/all_formulas.csv"
    n_invalid = 0
    n_existing = 0
    n_charge_neutral_checkable = 0
    n_charge_neutral = 0

    lm = kenlm.Model(klm_file)

    vocab = get_arpa_vocab(arpa_file)
    vocab.remove("<s>")

    all_formulas = set()
    with open(all_formulas_file, "rt") as f:
        reader = csv.reader(f)
        for line in reader:
            all_formulas.add(line[1])

    samples = []
    for i in range(n_generated):
        s = sample(lm, vocab, n, num_element_types, force)
        formula = s.replace(" ", "")
        if not formula:
            print("empty formula: %s" % formula)
            continue
        try:
            comp = Composition(formula)
        except CompositionError:
            print("invalid formula: %s" % formula)
            n_invalid += 1
            continue

        reduced_formula = comp.reduced_formula
        print("valid formula: %s" % reduced_formula)

        # check if passes SMACT filter
        smact_elements = [to_smact_elem(e) for e in comp.elements]
        if not any([None in smact_elements]):
            n_charge_neutral_checkable += 1
            ox_combos = [e.oxidation_states for e in smact_elements]
            # multiply the charges by the number of atoms in the reduced formula
            ox_combos = [tuple([comp.to_reduced_dict[comp.elements[i].name]*o for o in oc]) for i, oc in enumerate(ox_combos)]
            electronegs = [e.pauling_eneg for e in smact_elements]
            n_neutral = 0
            for ox_states in itertools.product(*ox_combos):
                if sum(ox_states) == 0:
                    n_neutral += 1
                    n_charge_neutral += 1
                    # electroneg_ok = pauling_test(ox_states, electronegs)
                    # if electroneg_ok:
                    #     print("electroneg OK!")
                    break
            print("is neutral: %s" % (n_neutral > 0 or len(smact_elements) == 1))
        else:
            print("could not check charge neutrality")

        score = lm.score(s, bos=False, eos=False)
        print("score: %s" % score)
        if reduced_formula in all_formulas:
            print("EXISTS")
            n_existing += 1
        samples.append((reduced_formula, score))

        print(". . . . .")

    samples = sorted(samples, key=lambda v: v[1])

    distinct_samples = set()
    for sample in samples:
        distinct_samples.add(sample[0])
        print(sample)

    print("- - - - ")
    print("num valid: %s / %s (%s %%)" %
          (n_generated - n_invalid, n_generated, ((n_generated - n_invalid)/n_generated)*100.0))
    print("num existing: %s / %s (%s %%)" % (n_existing, n_generated, (n_existing/n_generated)*100.0))
    print("num charge neutral: %s / %s (%s %%)" %
          (n_charge_neutral, n_charge_neutral_checkable, (n_charge_neutral/n_charge_neutral_checkable)*100.0))
    print("num unique: %s / %s (%s %%)" % (len(distinct_samples), len(samples), (len(distinct_samples)/len(samples))*100.0))
