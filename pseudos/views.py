from django.shortcuts import redirect, render

from .forms import PseudosForm
from .gen_pseudos import pseudo_complete


def _normaliser(liste):
    liste = [e.strip() for e in liste]
    nv_liste = []
    nv_liste_lower = []
    for e in liste:
        if e.lower() not in nv_liste_lower:
            nv_liste.append(e)
            nv_liste_lower.append(e.lower())
    liste = [e for e in nv_liste if e]
    return liste


def _str_to_list(liste):
    return _normaliser(liste.split("\n"))


def _log(*words):
    import datetime
    from pathlib import Path

    now = str(datetime.datetime.now())
    with open(Path(__file__).parent / "words.txt", "a") as f:
        f.write("\n".join(now + " - " + word for word in words) + "\n")


def add(request, name: str):
    """
    Add a pseudo (when clicking on a name on the results).
    """
    if name:
        s_words = request.session.get("pseudos_words") or []
        s_last_words = request.session.get("pseudos_last_words") or []
        s_words.append(name)
        s_last_words.append(name)
        request.session["pseudos_words"] = s_words
        request.session["pseudos_last_words"] = s_last_words[0:10]
    return redirect("pseudos:home")


def home(request):
    """
    Home page with the form.
    """
    s_words = _str_to_list(request.session.get("pseudos_words", "")) or []
    s_last_words = _str_to_list(request.session.get("pseudos_last_words", "")) or []

    if request.method == "POST":
        form = PseudosForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            words = _str_to_list(data["words"])
            _log(*words)
            request.session["pseudos_last_words"] = "\n".join(words)
            s_words = words + s_words
            s_words = _normaliser(s_words)[0:10]
            request.session["pseudos_words"] = "\n".join(s_words)
            try:
                resultat = pseudo_complete(
                    *words,
                    syllables_n=data["syllables_n"],
                    words_n=data["words_n"],
                    allow_word=data["allow_word"],
                )
            except ValueError as err:
                form.add_error("words", str(err))
            else:
                return render(
                    request,
                    "pseudos/result.html",
                    {
                        "words": words,
                        "synonyms": resultat["synonyms"],
                        "pseudos": resultat["pseudos"],
                    },
                )

    else:
        initial = {"words": s_last_words} if s_last_words else {}
        form = PseudosForm(initial=initial)
    return render(
        request,
        "pseudos/home.html",
        {
            "form": form,
            "words": s_words,
        },
    )
