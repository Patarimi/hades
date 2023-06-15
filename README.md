# HADES
## High-frequency Analog DESigner
This project is a prototype. Its goal is to create a technological and
software-agnostic design flow,
from device sizing to layout and implementation.

## Flow envisagé

Pour la partie "bloc" (schéma contenant des composants électronique)
- Saisie d'une architecture avec visualisation du schéma.
- Dimensionnement des composants (méthode gm/id, optimisation, ...). On crée 
le lien entre spécifications (gain, consommation, ...) et dimension (largeur, longueur de grille, ...)
- Placement des composants (système de matrice) et routage par directive (fils XX placé sur la 3ième ligne).
- Implémentation dans une technologie cible avec execution en boucle des étapes suivante + extraction des parasites.

Pour la partie "module" (schéma contenant uniquement des blocs)
- 