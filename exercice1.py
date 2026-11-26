from dataclasses import dataclass, asdict, replace
import json

@dataclass(frozen=True, slots=True)
class Livre:
    titre: str
    auteur: str
    annee: int
    prix: float
    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    def promo(self, prix_reduit: float) -> "Livre":
        return replace(self, prix=prix_reduit)

    def __lt__(self, autre: object) -> bool:
        if not isinstance(autre, Livre):
            return NotImplemented
        return self.prix < autre.prix

def livre_depuis_json(chaine_json: str) -> Livre:
    data = json.loads(chaine_json)
    return Livre(
        titre=data["titre"],
        auteur=data["auteur"],
        annee=data["annee"],
        prix=data["prix"],
    )
if __name__ == "__main__":
    livre1 = Livre("Les Misérables", "Victor Hugo", 1862, 11.50)
    json_str = livre1.to_json()
    print("JSON :", json_str)
    livre_promo = livre1.promo(7.90)
    print("Original :", livre1)
    print("En promo :", livre_promo)
    livre_charge = livre_depuis_json(json_str)
    print("Depuis JSON :", livre_charge)
    print("Égaux ? :", livre1 == livre_charge)
    livre2 = Livre("L'Étranger", "Albert Camus", 1942, 8.20)
    livre3 = Livre("Candide", "Voltaire", 1759, 6.00)
    livres_tries = sorted([livre1, livre2, livre3])
    print("Livres triés par prix en ordre croissant :")
    for l in livres_tries:
        print(f"  - {l.titre} ({l.prix} €)")