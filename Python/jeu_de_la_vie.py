"""
Jeu de la vie de Conway - version interactive (pygame)
Grille infinie, zoom, deplacement, et import des motifs du wiki
conwaylife.com (formats RLE et plaintext .cells).

Installation :  pip install pygame
Lancement    :  python jeu_de_la_vie.py

Commandes
---------
  Clic gauche (maintenu)  : dessiner des cellules
  Clic droit  (maintenu)  : effacer des cellules

  Molette                 : zoomer / dezoomer (autour de la souris)
  I / O                   : zoomer / dezoomer au clavier
  Fleches                 : se deplacer
  Clic molette (maintenu) : se deplacer en faisant glisser la vue
  H                       : revenir a la vue de depart

  ESPACE                  : lecture / pause
  N                       : avancer d'une seule generation (en pause)
  A / D                   : accelerer / ralentir
  C                       : tout effacer
  R                       : remplissage aleatoire de la zone visible
  1 a 5                   : poser un motif a l'emplacement de la souris
                            1 planeur, 2 vaisseau (LWSS), 3 pulsar,
                            4 R-pentomino, 5 canon a planeurs de Gosper
  ECHAP                   : quitter

Motifs du wiki (trois facons de les importer)
---------------------------------------------
  T                       : taper le nom d'un motif puis ENTREE pour le
                            telecharger (ex : "gosperglidergun", "acorn",
                            "copperhead"). Le nom est celui du fichier .rle
                            indique sur la page du motif. Internet requis.
  Ctrl+V                  : coller un motif copie depuis le wiki
                            (le code RLE ou le contenu d'un fichier .cells)
  Glisser-deposer         : deposer un fichier .rle ou .cells sur la fenetre
  0                       : reposer le dernier motif importe

  Le motif importe est pose centre sur la souris.
"""

import math
import os
import random
import re
import urllib.request

import pygame

# ---------------------------------------------------------------- Parametres
LARGEUR, HAUTEUR = 1000, 700  # taille de la zone de jeu (en pixels)
BANDEAU = 32                  # hauteur de la barre d'information

ZOOMS = [1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 48]   # pixels par cellule
ZOOM_DEPART = 7               # indice dans ZOOMS (ici 10 pixels)
VITESSE_DEPLACEMENT = 600     # pixels par seconde (fleches)

URL_WIKI = "https://conwaylife.com/patterns/{}.rle"
DUREE_MESSAGE = 5000          # millisecondes

FOND = (18, 18, 24)
QUADRILLAGE = (34, 34, 44)
CELLULE = (90, 220, 140)
TEXTE = (230, 230, 235)
FOND_BANDEAU = (28, 28, 38)

# Motifs classiques : "O" = cellule vivante, "." = cellule morte
MOTIFS = {
    1: ("Planeur", [
        ".O.",
        "..O",
        "OOO",
    ]),
    2: ("Vaisseau (LWSS)", [
        "O..O.",
        "....O",
        "O...O",
        ".OOOO",
    ]),
    3: ("Pulsar", [
        "..OOO...OOO..",
        ".............",
        "O....O.O....O",
        "O....O.O....O",
        "O....O.O....O",
        "..OOO...OOO..",
        ".............",
        "..OOO...OOO..",
        "O....O.O....O",
        "O....O.O....O",
        "O....O.O....O",
        ".............",
        "..OOO...OOO..",
    ]),
    4: ("R-pentomino", [
        ".OO",
        "OO.",
        ".O.",
    ]),
    5: ("Canon de Gosper", [
        "........................O...........",
        "......................O.O...........",
        "............OO......OO............OO",
        "...........O...O....OO............OO",
        "OO........O.....O...OO..............",
        "OO........O...O.OO....O.O...........",
        "..........O.....O.......O...........",
        "...........O...O....................",
        "............OO......................",
    ]),
}

# Touches chiffres : on se base sur la POSITION de la touche (scancode) pour
# que la rangee du haut fonctionne aussi sur un clavier AZERTY sans Maj.
_SCANCODES = [pygame.KSCAN_0, pygame.KSCAN_1, pygame.KSCAN_2, pygame.KSCAN_3,
              pygame.KSCAN_4, pygame.KSCAN_5, pygame.KSCAN_6, pygame.KSCAN_7,
              pygame.KSCAN_8, pygame.KSCAN_9]
_PAVE_NUM = [pygame.K_KP0, pygame.K_KP1, pygame.K_KP2, pygame.K_KP3,
             pygame.K_KP4, pygame.K_KP5, pygame.K_KP6, pygame.K_KP7,
             pygame.K_KP8, pygame.K_KP9]


def chiffre_tape(evenement):
    """Renvoie le chiffre (0 a 9) correspondant a la touche, ou None."""
    if evenement.key in _PAVE_NUM:
        return _PAVE_NUM.index(evenement.key)
    if evenement.scancode in _SCANCODES:
        return _SCANCODES.index(evenement.scancode)
    return None


# ------------------------------------------------------------ Logique du jeu
def generation_suivante(vivantes):
    """Calcule la generation suivante.

    `vivantes` est l'ensemble des coordonnees (x, y) des cellules vivantes.
    La grille est infinie : on ne stocke que les cellules vivantes.

    Regles de Conway :
      - une cellule morte avec exactement 3 voisines vivantes nait ;
      - une cellule vivante avec 2 ou 3 voisines vivantes survit ;
      - dans tous les autres cas, la cellule meurt ou reste morte.
    """
    # On compte, pour chaque case, combien de voisines vivantes elle possede.
    nb_voisines = {}
    for (x, y) in vivantes:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx != 0 or dy != 0:
                    voisine = (x + dx, y + dy)
                    nb_voisines[voisine] = nb_voisines.get(voisine, 0) + 1

    return {
        case
        for case, n in nb_voisines.items()
        if n == 3 or (n == 2 and case in vivantes)
    }


def poser_motif(vivantes, lignes, x0, y0):
    """Ajoute un motif dont le coin haut-gauche est en (x0, y0)."""
    for dy, ligne in enumerate(lignes):
        for dx, caractere in enumerate(ligne):
            if caractere == "O":
                vivantes.add((x0 + dx, y0 + dy))


def poser_cellules(vivantes, cellules, cx, cy):
    """Ajoute un ensemble de cellules en le centrant sur la case (cx, cy)."""
    largeur = max(x for x, _ in cellules) + 1
    hauteur = max(y for _, y in cellules) + 1
    x0, y0 = cx - largeur // 2, cy - hauteur // 2
    for (x, y) in cellules:
        vivantes.add((x0 + x, y0 + y))


# ------------------------------------------------- Import des motifs du wiki
def lire_motif(texte):
    """Convertit le texte d'un motif (RLE ou plaintext) en ensemble de
    cellules (x, y), le coin haut-gauche du motif etant en (0, 0).

    Format RLE (fichiers .rle du wiki), exemple du planeur :
        x = 3, y = 3, rule = B3/S23
        bob$2bo$3o!
      un nombre = repetition, b = morte, o = vivante, $ = fin de ligne,
      ! = fin du motif, lignes commencant par # = commentaires.

    Format plaintext (fichiers .cells), meme planeur :
        !Name: Glider
        .O.
        ..O
        OOO

    Renvoie (cellules, regle) ; regle vaut None si elle n'est pas indiquee.
    Leve ValueError si le texte ne contient aucun motif.
    """
    lignes = [l.strip() for l in texte.replace("\r", "").split("\n")]
    lignes = [l for l in lignes if l]

    regle = None
    entete = next((l for l in lignes if re.match(r"x\s*=", l)), None)
    if entete:
        trouve = re.search(r"rule\s*=\s*([^\s,]+)", entete)
        if trouve:
            regle = trouve.group(1)

    donnees = [l for l in lignes
               if not l.startswith(("#", "!")) and not re.match(r"x\s*=", l)]
    corps = "".join(donnees)
    est_rle = entete is not None or (
        "o" in corps and re.fullmatch(r"[0-9bo$!\s]+", corps) is not None)

    cellules = set()
    if est_rle:
        nombre, x, y = "", 0, 0
        for c in corps:
            if c.isdigit():
                nombre += c
            elif c == "!":
                break
            elif not c.isspace():
                n = int(nombre) if nombre else 1
                nombre = ""
                if c == "$":
                    y += n
                    x = 0
                elif c in "b.":
                    x += n
                elif c.isalpha():            # "o" (ou autre etat vivant)
                    for i in range(n):
                        cellules.add((x + i, y))
                    x += n
                else:
                    raise ValueError("caractere inattendu dans le RLE")
    else:
        # Plaintext : les commentaires commencent par "!" ; on garde les
        # lignes vides internes car elles comptent dans le motif.
        y = 0
        for ligne in texte.replace("\r", "").split("\n"):
            if ligne.startswith("!"):
                continue
            ligne = ligne.rstrip()
            if ligne and re.fullmatch(r"[.O*o ]+", ligne) is None:
                raise ValueError("format de motif non reconnu")
            for x, c in enumerate(ligne):
                if c in "O*o":
                    cellules.add((x, y))
            y += 1

    if not cellules:
        raise ValueError("aucune cellule vivante trouvee")

    # On recale le motif pour que son coin haut-gauche soit en (0, 0).
    x_min = min(x for x, _ in cellules)
    y_min = min(y for _, y in cellules)
    return {(x - x_min, y - y_min) for x, y in cellules}, regle


def telecharger_motif(nom):
    """Telecharge le fichier RLE d'un motif depuis conwaylife.com.

    `nom` est le nom du fichier indique sur la page wiki du motif (par
    exemple "gosperglidergun"), ou directement une adresse http(s).
    """
    nom = nom.strip()
    if nom.lower().startswith(("http://", "https://")):
        url = nom
    else:
        nom = re.sub(r"[\s\-'_]", "", nom.lower())
        nom = re.sub(r"\.(rle|cells)$", "", nom)
        url = URL_WIKI.format(nom)
    requete = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(requete, timeout=10) as reponse:
        return reponse.read().decode("utf-8", errors="replace")


def lire_presse_papiers():
    """Renvoie le texte du presse-papiers ("" si indisponible)."""
    try:
        import tkinter
        racine = tkinter.Tk()
        racine.withdraw()
        texte = racine.clipboard_get()
        racine.destroy()
        return texte
    except Exception:
        return ""


def regle_standard(regle):
    """Vrai si la regle indiquee est celle de Conway (ou absente)."""
    if regle is None:
        return True
    return regle.upper().replace("B", "").replace("S", "") in ("3/23", "23/3")


# -------------------------------------------------------------------- Camera
class Camera:
    """Fait le lien entre les cases de la grille et les pixels de l'ecran.

    (x, y)  : coordonnees (dans la grille) du coin haut-gauche de la vue
    taille  : taille d'une cellule a l'ecran, en pixels (= niveau de zoom)
    """

    def __init__(self):
        self.reinitialiser()

    def reinitialiser(self):
        self.x = 0.0
        self.y = 0.0
        self.niveau = ZOOM_DEPART

    @property
    def taille(self):
        return ZOOMS[self.niveau]

    def case(self, px, py):
        """Case de la grille situee sous le pixel (px, py) de la fenetre."""
        return (math.floor(px / self.taille + self.x),
                math.floor((py - BANDEAU) / self.taille + self.y))

    def pixel(self, x, y):
        """Pixel (coin haut-gauche) ou s'affiche la case (x, y)."""
        return (math.floor((x - self.x) * self.taille),
                math.floor((y - self.y) * self.taille) + BANDEAU)

    def deplacer(self, dpx, dpy):
        """Decale la vue de (dpx, dpy) pixels."""
        self.x += dpx / self.taille
        self.y += dpy / self.taille

    def zoomer(self, sens, px, py):
        """Zoome (sens=+1) ou dezoome (sens=-1) en gardant fixe le point
        de la grille situe sous le pixel (px, py)."""
        nouveau = max(0, min(len(ZOOMS) - 1, self.niveau + sens))
        if nouveau == self.niveau:
            return
        # Point de la grille sous la souris avant le zoom...
        gx = px / self.taille + self.x
        gy = (py - BANDEAU) / self.taille + self.y
        self.niveau = nouveau
        # ...qui doit rester sous la souris apres le zoom.
        self.x = gx - px / self.taille
        self.y = gy - (py - BANDEAU) / self.taille

    def zone_visible(self):
        """Renvoie (x_min, y_min, x_max, y_max) des cases visibles."""
        x_min, y_min = self.case(0, BANDEAU)
        x_max, y_max = self.case(LARGEUR - 1, BANDEAU + HAUTEUR - 1)
        return x_min, y_min, x_max, y_max


def grille_aleatoire(camera, densite=0.25, cote_max=200):
    """Remplit au hasard la zone visible (limitee a cote_max cases de cote
    pour que la simulation reste fluide quand on est tres dezoome)."""
    x_min, y_min, x_max, y_max = camera.zone_visible()
    cx, cy = (x_min + x_max) // 2, (y_min + y_max) // 2
    demi = cote_max // 2
    x_min, x_max = max(x_min, cx - demi), min(x_max, cx + demi)
    y_min, y_max = max(y_min, cy - demi), min(y_max, cy + demi)
    return {
        (x, y)
        for x in range(x_min, x_max + 1)
        for y in range(y_min, y_max + 1)
        if random.random() < densite
    }


# ----------------------------------------------------------------- Affichage
def dessiner(ecran, police, camera, vivantes, generation, en_cours, vitesse,
             aide):
    ecran.fill(FOND)
    taille = camera.taille
    x_min, y_min, x_max, y_max = camera.zone_visible()

    # Quadrillage (masque quand les cellules sont trop petites)
    if taille >= 5:
        for x in range(x_min, x_max + 2):
            px, _ = camera.pixel(x, 0)
            pygame.draw.line(ecran, QUADRILLAGE,
                             (px, BANDEAU), (px, BANDEAU + HAUTEUR))
        for y in range(y_min, y_max + 2):
            _, py = camera.pixel(0, y)
            pygame.draw.line(ecran, QUADRILLAGE, (0, py), (LARGEUR, py))

    # Cellules vivantes (seulement celles qui sont dans la vue)
    marge = 1 if taille >= 5 else 0
    cote = taille - marge
    for (x, y) in vivantes:
        if x_min <= x <= x_max and y_min <= y <= y_max:
            px, py = camera.pixel(x, y)
            pygame.draw.rect(ecran, CELLULE,
                             (px + marge, py + marge, cote, cote))

    # Bandeau d'information (dessine en dernier, par-dessus la grille)
    pygame.draw.rect(ecran, FOND_BANDEAU, (0, 0, LARGEUR, BANDEAU))
    etat = "LECTURE" if en_cours else "PAUSE"
    info = (f"{etat} | Gen. {generation} | Pop. {len(vivantes)}"
            f" | {vitesse} gen/s | Zoom {taille} px | {aide}")
    ecran.blit(police.render(info, True, TEXTE), (8, 8))

    pygame.display.flip()


# ------------------------------------------------------- Boucle principale
def main():
    pygame.init()
    ecran = pygame.display.set_mode((LARGEUR, BANDEAU + HAUTEUR))
    pygame.display.set_caption("Jeu de la vie de Conway")
    police = pygame.font.SysFont("consolas,dejavusansmono,monospace", 15)
    horloge = pygame.time.Clock()

    camera = Camera()
    vivantes = set()
    poser_motif(vivantes, MOTIFS[5][1], 5, 5)   # canon au demarrage

    generation = 0
    en_cours = False
    vitesse = 10              # generations par seconde
    temps_accumule = 0.0

    motif_importe = None      # dernier motif importe du wiki (touche 0)
    saisie = None             # texte en cours de frappe (touche T), ou None
    message = ""              # message temporaire affiche dans le bandeau
    fin_message = 0

    def afficher(texte):
        nonlocal message, fin_message
        message = texte
        fin_message = pygame.time.get_ticks() + DUREE_MESSAGE

    def importer(texte, nom):
        """Lit un motif (RLE ou plaintext) et le pose sous la souris."""
        nonlocal motif_importe
        try:
            cellules, regle = lire_motif(texte)
        except ValueError:
            afficher(f"Motif illisible : {nom}")
            return
        motif_importe = cellules
        poser_cellules(vivantes, cellules, *camera.case(*pygame.mouse.get_pos()))
        if regle_standard(regle):
            afficher(f"{nom} : {len(cellules)} cellules (0 pour reposer)")
        else:
            afficher(f"{nom} : attention, prevu pour la regle {regle}")

    continuer = True
    while continuer:
        dt = horloge.tick(60) / 1000   # secondes ecoulees depuis la derniere image
        souris = pygame.mouse.get_pos()

        # --- Evenements
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                continuer = False

            elif evenement.type == pygame.MOUSEWHEEL:
                if evenement.y != 0:
                    camera.zoomer(1 if evenement.y > 0 else -1, *souris)

            elif evenement.type == pygame.MOUSEMOTION:
                if evenement.buttons[1]:          # clic molette maintenu
                    camera.deplacer(-evenement.rel[0], -evenement.rel[1])

            elif evenement.type == pygame.DROPFILE:
                nom = os.path.basename(evenement.file)
                try:
                    with open(evenement.file, encoding="utf-8",
                              errors="replace") as fichier:
                        importer(fichier.read(), nom)
                except OSError:
                    afficher(f"Fichier illisible : {nom}")

            elif evenement.type == pygame.KEYDOWN and saisie is not None:
                # Mode saisie : on tape le nom d'un motif du wiki
                if evenement.key == pygame.K_ESCAPE:
                    saisie = None
                elif evenement.key == pygame.K_BACKSPACE:
                    saisie = saisie[:-1]
                elif evenement.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    nom, saisie = saisie.strip(), None
                    if nom:
                        try:
                            importer(telecharger_motif(nom), nom)
                        except Exception:
                            afficher(f"Introuvable sur le wiki : {nom}")
                elif evenement.unicode.isprintable() and len(saisie) < 60:
                    saisie += evenement.unicode

            elif evenement.type == pygame.KEYDOWN:
                touche = evenement.key
                chiffre = chiffre_tape(evenement)
                if touche == pygame.K_ESCAPE:
                    continuer = False
                elif touche == pygame.K_SPACE:
                    en_cours = not en_cours
                elif touche == pygame.K_v and evenement.mod & (
                        pygame.KMOD_CTRL | pygame.KMOD_META):
                    texte = lire_presse_papiers()
                    if texte.strip():
                        importer(texte, "Motif colle")
                    else:
                        afficher("Presse-papiers vide")
                elif touche == pygame.K_t:
                    saisie = ""
                elif touche == pygame.K_n and not en_cours:
                    vivantes = generation_suivante(vivantes)
                    generation += 1
                elif touche == pygame.K_a:
                    vitesse = min(60, vitesse + 2)
                elif touche == pygame.K_d:
                    vitesse = max(1, vitesse - 2)
                elif touche == pygame.K_i:
                    camera.zoomer(1, *souris)
                elif touche == pygame.K_o:
                    camera.zoomer(-1, *souris)
                elif touche == pygame.K_h:
                    camera.reinitialiser()
                elif touche == pygame.K_c:
                    vivantes = set()
                    generation = 0
                    en_cours = False
                elif touche == pygame.K_r:
                    vivantes = grille_aleatoire(camera)
                    generation = 0
                elif chiffre in MOTIFS:
                    x, y = camera.case(*souris)
                    poser_motif(vivantes, MOTIFS[chiffre][1], x, y)
                elif chiffre == 0:
                    if motif_importe:
                        poser_cellules(vivantes, motif_importe,
                                       *camera.case(*souris))
                    else:
                        afficher("Aucun motif importe (T, Ctrl+V ou glisser)")

        # --- Deplacement aux fleches (touches maintenues)
        touches = pygame.key.get_pressed()
        pas = VITESSE_DEPLACEMENT * dt
        camera.deplacer(
            (touches[pygame.K_RIGHT] - touches[pygame.K_LEFT]) * pas,
            (touches[pygame.K_DOWN] - touches[pygame.K_UP]) * pas,
        )

        # --- Dessin a la souris (clic maintenu, hors bandeau)
        gauche, _, droit = pygame.mouse.get_pressed()
        if (gauche or droit) and souris[1] >= BANDEAU:
            case = camera.case(*souris)
            if gauche:
                vivantes.add(case)
            else:
                vivantes.discard(case)

        # --- Simulation
        if en_cours:
            temps_accumule += dt
            while temps_accumule >= 1 / vitesse:
                vivantes = generation_suivante(vivantes)
                generation += 1
                temps_accumule -= 1 / vitesse
        else:
            temps_accumule = 0.0

        # --- Texte de droite du bandeau
        if saisie is not None:
            aide = f"Motif du wiki : {saisie}_  (ENTREE valider)"
        elif message and pygame.time.get_ticks() < fin_message:
            aide = message
        else:
            aide = "T: motif du wiki  Ctrl+V: coller"

        dessiner(ecran, police, camera, vivantes, generation, en_cours,
                 vitesse, aide)

    pygame.quit()


if __name__ == "__main__":
    main()
