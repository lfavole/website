import argparse
import itertools
import os
import random
import re
import sys
from pathlib import Path

import django
import pyphen
import requests

try:
    FOLDER = Path(__file__).parent.parent
    sys.path.insert(0, str(FOLDER))
    os.environ["DJANGO_SETTINGS_MODULE"] = f"{FOLDER.name}.settings"
    django.setup()
    from django.utils.translation import gettext as _
except:  # noqa

    def _(message: str):
        return message


def french_synonyms(word):
    """
    Return all the synonyms of a French word.
    """
    try:
        req = requests.get(f"https://crisco4.unicaen.fr/des/synonymes/{word}")
        req.raise_for_status()
    except requests.RequestException:
        return []

    data = req.text

    table = re.search(r"(?s)<table[^>]*>(.*?)</table>", data)

    if not table:
        return []

    syn = re.findall(r"<a[^>]+>(?:&nbsp;)*([\w '-]+)(?:&nbsp;)*</a>", table.group(1))
    return syn


def factorial(number):
    """
    Return the factorial of a number.
    """
    ret = 1
    for i in range(1, number + 1):
        ret *= i
    return ret


def pseudo_complete(*words, syllables_n=3, words_n=1, verbose=False):
    """
    Create a pseudo with different words.
    Return the synonyms and the pseudos (for the webpage).
    """
    parts = []  # all the syllables

    dic = pyphen.Pyphen(lang="fr_FR")
    words = list(set(word.lower() for word in words))

    syn_ret = {}
    for word in words.copy():
        syn = french_synonyms(word)
        if not syn:
            continue
        syn_ret[word] = syn
        if verbose:
            print(_("Synonyms of %s: ") % (word,) + ", ".join(syn))
        words.extend(syn)
    words = list(set(word.lower() for word in words))

    if verbose:
        print()

    for word in words:
        syllables = dic.inserted(word).split("-")
        parts.extend(syllables)

    if syllables_n > len(parts):
        raise ValueError(_("Not enough syllables (only %d)!") % (len(parts),))

    ret = []

    total_max = factorial(len(parts)) // factorial(len(parts) - syllables_n)  # number of permutations
    if words_n > total_max:
        raise ValueError(_("Not enough combinations (maximum = %d)!") % (total_max,))
    total = total_max if words_n == 0 else words_n  # 0 = all the possible arrangements

    if total >= total_max * 0.2:
        # use permutations if we request more than 20% of the list (faster)
        permutations = itertools.permutations(parts, syllables_n)

        def get_name():  # type: ignore
            return "".join(next(permutations))

    else:
        # otherwise, use random

        def get_name():  # type: ignore
            parts_copy = parts.copy()  # to be able to generate several names
            nom_final = ""  # final name
            for _ in range(syllables_n):
                i = random.randint(0, len(parts_copy) - 1)
                nom_final += parts_copy.pop(i)
            return nom_final

    while total > 0:
        try:
            final_name = get_name()
        except StopIteration as exc:
            raise ValueError(
                _("Not enough combinations without a whole word in them (maximum = %d)!") % (total_max - total,)
            ) from exc
        stop = False
        for word in words:
            if word in final_name:  # don't keep the name if there is a word in them
                stop = True
                break
        if stop:
            continue
        final_name = final_name.title().strip()  # add caps, remove spaces
        if final_name in ret:  # add the name if it is not already there
            continue
        ret.append(final_name)
        total -= 1

    return {"synonyms": syn_ret, "pseudos": ret}


def pseudo(*args, **kwargs):
    """
    Create a pseudo with different words.
    """
    return pseudo_complete(*args, **kwargs)["pseudos"]


def get_args_interactive():
    """
    Prompt for the arguments interactively.
    """
    suffix = _(":") + " "
    words = []
    while True:
        word = input(_("Word") + suffix).strip()
        if word == "stop":
            break
        words.append(word)

    syllables_n = int(input(_("Syllables number") + suffix))

    words_n = int(input(_("Number of pseudos to generate") + suffix))

    print()

    ret = argparse.Namespace()
    ret.WORD = words
    ret.syllables_n = syllables_n
    ret.words_n = words_n
    ret.verbose = True
    return ret


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("WORD", nargs="*", help="words to use")
    parser.add_argument("--syllables-n", type=int, default=3, help="syllables number")
    parser.add_argument("--words-n", type=int, default=10, help="number of pseudos to generate")
    parser.add_argument("-v", "--verbose", action="store_true", help="show information during the generation process")

    args = parser.parse_args()

    if not args.WORD:
        args = get_args_interactive()

    pseudos = pseudo(*args.WORD, syllables_n=args.syllables_n, words_n=args.words_n, verbose=args.verbose)

    for result in pseudos:
        print(result)


if __name__ == "__main__":
    main()
