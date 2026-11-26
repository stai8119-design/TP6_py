from dataclasses import dataclass, asdict, FrozenInstanceError
import json
import unittest

@dataclass(frozen=True, slots=True)
class Film:
    titre: str
    realisateur: str
    annee: int
    note: float
    def __post_init__(self):
        if not isinstance(self.titre, str) or not self.titre.strip():
            raise ValueError("Le titre doit être une chaîne non vide")
        if not isinstance(self.realisateur, str) or not self.realisateur.strip():
            raise ValueError("Le réalisateur doit être une chaîne non vide")
        if isinstance(self.annee, bool) or not isinstance(self.annee, int):
            raise TypeError("L'année doit être un entier")
        if self.annee < 1888:
            raise ValueError("L'année est trop ancienne")
        if isinstance(self.note, bool) or not isinstance(self.note, (int, float)):
            raise TypeError("La note doit être un nombre")
        object.__setattr__(self, "note", float(self.note))
        if not (0.0 <= self.note <= 10.0):
            raise ValueError("La note doit être entre 0 et 10")
    def est_classique(self) -> bool:
        return self.annee < 2000
    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)
    @classmethod
    def from_json(cls, chaine: str) -> "Film":
        if not isinstance(chaine, str):
            raise TypeError("Il faut passer une chaîne JSON")
        data = json.loads(chaine)
        if not isinstance(data, dict):
            raise ValueError("Le JSON doit représenter un objet")
        return cls(
            titre=data.get("titre"),
            realisateur=data.get("realisateur"),
            annee=data.get("annee"),
            note=data.get("note"),
        )
    def __lt__(self, autre: object) -> bool:
        if not isinstance(autre, Film):
            return NotImplemented
        return self.note < autre.note

class ListeFavoris:
    def __init__(self, films: list[Film] | None = None):
        self.films: list[Film] = list(films) if films else []
    def ajouter(self, film: Film) -> None:
        if not isinstance(film, Film):
            raise TypeError("Seul un objet Film peut être ajouté")
        self.films.append(film)
    def to_json(self) -> str:
        return json.dumps([asdict(f) for f in self.films], ensure_ascii=False)

    @classmethod
    def from_json(cls, chaine: str) -> "ListeFavoris":
        data = json.loads(chaine)
        if not isinstance(data, list):
            raise ValueError("Le JSON doit être une liste")
        films = [Film.from_json(json.dumps(item, ensure_ascii=False)) for item in data]
        return cls(films)

class TestFilm(unittest.TestCase):
    def test_creation_et_methodes_base(self):
        f = Film("Le Fabuleux Destin d'Amélie Poulain", "Jean-Pierre Jeunet", 2001, 8.3)
        self.assertEqual(f.titre, "Le Fabuleux Destin d'Amélie Poulain")
        self.assertFalse(f.est_classique())
        ancien = Film("Le Dictateur", "Charlie Chaplin", 1940, 8.4)
        self.assertTrue(ancien.est_classique())
    def test_immutabilite_et_slots(self):
        f = Film("Intouchables", "Olivier Nakache", 2011, 8.5)
        with self.assertRaises((AttributeError, FrozenInstanceError, TypeError)):
            f.note = 9.0
        with self.assertRaises((AttributeError, FrozenInstanceError, TypeError)):
            f.duree = 112
        self.assertFalse(hasattr(f, "__dict__"))
    def test_json_aller_retour(self):
        f = Film("La Cité de Dieu", "Fernando Meirelles", 2002, 8.6)
        texte = f.to_json()
        reconstruit = Film.from_json(texte)
        self.assertEqual(reconstruit, f)
        self.assertEqual(json.loads(texte)["realisateur"], "Fernando Meirelles")

    def test_comparaison_par_note(self):
        f1 = Film("Film A", "Réal A", 2010, 6.5)
        f2 = Film("Film B", "Réal B", 2015, 8.8)
        f3 = Film("Film C", "Réal C", 2005, 7.2)
        tries = sorted([f1, f2, f3])
        self.assertEqual([f.note for f in tries], [6.5, 7.2, 8.8])

    def test_liste_favoris_json(self):
        f1 = Film("Les Évadés", "Frank Darabont", 1994, 9.3)
        f2 = Film("Parasite", "Bong Joon-ho", 2019, 8.5)
        fav = ListeFavoris([f1])
        fav.ajouter(f2)
        json_fav = fav.to_json()
        fav_charge = ListeFavoris.from_json(json_fav)
        self.assertEqual(len(fav_charge.films), 2)
        self.assertEqual(fav_charge.films[1], f2)

    def test_cas_limites_et_erreurs(self):
        for titre_invalide in ["", "   ", None]:
            with self.subTest(titre=titre_invalide):
                with self.assertRaises(ValueError):
                    Film(titre_invalide, "Réal", 2020, 7.0)
        for annee_invalide in ["2020", True, 1800]:
            with self.subTest(annee=annee_invalide):
                with self.assertRaises((TypeError, ValueError)):
                    Film("Titre", "Réal", annee_invalide, 7.0)
        for note_invalide in [-0.1, 10.5, "huit", True]:
            with self.subTest(note=note_invalide):
                with self.assertRaises((TypeError, ValueError)):
                    Film("Titre", "Réal", 2020, note_invalide)
        with self.assertRaises(json.JSONDecodeError):
            Film.from_json("{json_invalide")


if __name__ == "__main__":
    unittest.main(verbosity=2)