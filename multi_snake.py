import pygame
import random
from datetime import datetime

# ---------------------------------------------------------------------------
# CONSTANTES GLOBALES DU JEU
# ---------------------------------------------------------------------------
# Ici, on définit tout ce qui décrit "l'univers" du jeu :
# - la taille de la grille
# - la taille des cases
# - les couleurs utilisées
# Ces constantes sont ensuite réutilisées partout dans le code.
TAILLE_CASE = 20                 # Taille d'une case en pixels
LARGEUR_GRILLE = 30              # Nombre de cases en largeur
HAUTEUR_GRILLE = 30              # Nombre de cases en hauteur

# Couleurs (au format RGB)
COULEUR_FOND = (0, 0, 0)         # Fond noir
COULEUR_MUR = (100, 100, 100)    # Murs gris
COULEUR_SERPENT = (0, 255, 0)    # (non utilisé directement, mais utile conceptuellement)
COULEUR_TETE = (255, 255, 0)     # Tête en jaune
COULEUR_SERPENT_MORT = (139, 69, 19)  # Serpents morts en marron
COULEUR_NOURRITURE = (255, 0, 0)      # Nourriture en rouge
COULEUR_TEXTE = (255, 255, 255)       # Texte en blanc


# ---------------------------------------------------------------------------
# CLASSE ARENE
# ---------------------------------------------------------------------------
# L'arène représente le terrain de jeu :
# - sa taille (largeur, hauteur)
# - les murs tout autour
# - les segments laissés par les serpents morts (qui deviennent des obstacles)
# ---------------------------------------------------------------------------
class Arene:
    def __init__(self, largeur, hauteur):
        # Dimensions de l'arène en nombre de cases
        self.largeur = largeur
        self.hauteur = hauteur

        # Ensemble des coordonnées des murs (x, y)
        self.murs = set()

        # Ensemble des coordonnées des segments de serpents morts
        self.serpents_morts = set()

        # Création des murs verticaux : colonnes de gauche et de droite
        for y in range(hauteur):
            self.murs.add((0, y))              # mur gauche
            self.murs.add((largeur - 1, y))    # mur droit

        # Création des murs horizontaux : lignes du haut et du bas
        for x in range(largeur):
            self.murs.add((x, 0))              # mur haut
            self.murs.add((x, hauteur - 1))    # mur bas

    def collision(self, pos):
        """
        Vérifie si une position 'pos' = (x, y) est en collision :
        - soit avec un mur
        - soit avec un serpent mort
        - soit en dehors de l'arène
        Retourne True en cas de collision, False sinon.
        """
        x, y = pos

        # Collision avec un mur ou un corps de serpent mort
        if (x, y) in self.murs or (x, y) in self.serpents_morts:
            return True

        # Sécurité : on vérifie aussi qu'on reste dans les bornes de la grille
        if x < 0 or x >= self.largeur or y < 0 or y >= self.hauteur:
            return True

        return False

    def ajouter_serpent_mort(self, segments):
        """
        Quand un serpent meurt, on ajoute tous ses segments
        dans l'ensemble 'serpents_morts', pour que son corps
        reste comme obstacle dans l'arène.
        """
        for s in segments:
            self.serpents_morts.add(s)


# ---------------------------------------------------------------------------
# CLASSE NOURRITURE
# ---------------------------------------------------------------------------
# Représente la nourriture (la "pomme") qui apparaît sur le terrain.
# Elle doit être placée sur une case libre : pas un mur, pas un serpent,
# pas un serpent mort.
# ---------------------------------------------------------------------------
class Nourriture:
    def __init__(self):
        # Coordonnées de la nourriture dans la grille
        self.position = (0, 0)

    def generer(self, arene, serpent):
        """
        Choisit au hasard une case de l'arène pour placer la nourriture.
        On boucle jusqu'à trouver une case libre :
        - qui n'est pas un mur
        - qui n'est pas sur le serpent vivant
        - qui n'est pas sur un serpent mort
        """
        while True:
            x = random.randint(1, arene.largeur - 2)
            y = random.randint(1, arene.hauteur - 2)

            if (x, y) not in arene.murs and (x, y) not in serpent and (x, y) not in arene.serpents_morts:
                self.position = (x, y)
                break


# ---------------------------------------------------------------------------
# CLASSE SERPENT
# ---------------------------------------------------------------------------
# Modélise le serpent du joueur courant :
# - une liste de segments (coordonnées des cases)
# - une direction (dx, dy)
# - une variable 'grandir_de' pour savoir combien de segments ajouter
#   après avoir mangé de la nourriture.
# ---------------------------------------------------------------------------
class Serpent:
    def __init__(self, arene):
        # On place la tête du serpent au centre de l'arène
        x = arene.largeur // 2
        y = arene.hauteur // 2

        # Le serpent commence avec 3 segments alignés horizontalement
        self.segments = [(x, y), (x - 1, y), (x - 2, y)]

        # Direction initiale : vers la droite (dx = 1, dy = 0)
        self.direction = (1, 0)

        # Nombre de segments à ajouter (quand on mange)
        self.grandir_de = 0

    def changer_direction(self, dx, dy):
        """
        Change la direction du serpent.
        On empêche le demi-tour direct pour éviter une collision instantanée
        avec son propre corps.
        """
        ancien_dx, ancien_dy = self.direction

        # Si la nouvelle direction est exactement l'opposé, on ignore
        if dx == -ancien_dx and dy == -ancien_dy:
            return

        self.direction = (dx, dy)

    def avancer(self):
        """
        Fait avancer le serpent d'une case dans sa direction actuelle.
        - On calcule la nouvelle tête
        - On l'ajoute au début de la liste des segments
        - On enlève la queue (sauf si le serpent doit grandir)
        Retourne la nouvelle position de la tête.
        """
        tete_x, tete_y = self.segments[0]
        dx, dy = self.direction

        # Calcul de la nouvelle position de la tête
        nouvelle_tete = (tete_x + dx, tete_y + dy)

        # On insère la tête au début de la liste
        self.segments.insert(0, nouvelle_tete)

        # Si le serpent doit grandir, on ne supprime pas la queue
        if self.grandir_de > 0:
            self.grandir_de -= 1
        else:
            # Sinon on supprime le dernier segment pour garder la même longueur
            self.segments.pop()

        return nouvelle_tete

    def grandir(self):
        """
        Demande au serpent de grandir d'un segment
        au prochain déplacement.
        """
        self.grandir_de += 1


# ---------------------------------------------------------------------------
# CLASSE SCORE
# ---------------------------------------------------------------------------
# Gère les scores des joueurs :
# - un tableau de scores (un score par joueur)
# - le calcul du classement final
# - la sauvegarde des scores dans un fichier texte
# ---------------------------------------------------------------------------
class Score:
    def __init__(self, nb):
        # Liste des scores : index = numéro du joueur
        self.scores = [0] * nb

        # Police de caractères Pygame pour afficher le texte
        self.police = None

    def ajouter(self, joueur):
        """Ajoute 1 point au joueur donné."""
        self.scores[joueur] += 1

    def classement(self):
        """
        Retourne une liste triée des joueurs selon leurs scores.
        Chaque élément est un tuple (index_joueur, score).
        """
        return sorted(enumerate(self.scores), key=lambda x: x[1], reverse=True)

    def sauvegarder(self):
        """
        Enregistre le classement dans un fichier texte 'scores.txt',
        avec la date et l'heure de la partie.
        """
        with open("scores.txt", "a") as f:
            f.write("\n--- Partie du " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " ---\n")
            rang = 1
            for joueur, points in self.classement():
                f.write(f"{rang}. Joueur {joueur+1} : {points} points\n")
                rang += 1


# ---------------------------------------------------------------------------
# CLASSE JEU
# ---------------------------------------------------------------------------
# C'est la classe principale qui :
# - initialise Pygame
# - crée l'arène, les scores, la fenêtre
# - gère la boucle principale du jeu (tour par tour pour chaque joueur)
# - gère l'affichage à l'écran
# - affiche l'écran final de classement
# ---------------------------------------------------------------------------
class Jeu:
    def __init__(self, nb_joueurs=4):
        pygame.init()

        # Nombre de joueurs de la partie
        self.nb_j = nb_joueurs

        # Création de l'arène de jeu
        self.arene = Arene(LARGEUR_GRILLE, HAUTEUR_GRILLE)

        # Initialisation de la fenêtre Pygame
        self.ecran = pygame.display.set_mode(
            (LARGEUR_GRILLE * TAILLE_CASE, HAUTEUR_GRILLE * TAILLE_CASE)
        )
        pygame.display.set_caption("Multi-Snake Nadir")

        # Gestionnaire de score
        self.score = Score(nb_joueurs)
        self.score.police = pygame.font.Font(None, 28)

        # Horloge pour contrôler la vitesse d'animation
        self.horloge = pygame.time.Clock()

    # -------------------------------------------------------------------
    # DESSIN DU SERPENT 
    # -------------------------------------------------------------------
    def dessiner_serpent(self, serpent):
        """
        Dessine le serpent avec un rendu réaliste :
        - segments arrondis
        - dégradé de couleur sur le corps
        - yeux sur la tête dans la direction du mouvement
        """
        for i, (x, y) in enumerate(serpent.segments):

            # Conversion des coordonnées grille -> pixels
            x_pix = x * TAILLE_CASE
            y_pix = y * TAILLE_CASE

            # Dégradé de vert : la tête est plus claire que le corps
            if i == 0:
                couleur = COULEUR_TETE
            else:
                # Plus le segment est loin de la tête, plus il est foncé
                vert = max(50, 255 - i * 10)
                couleur = (0, vert, 0)

            # Dessin du segment du serpent avec des angles arrondis
            pygame.draw.rect(
                self.ecran,
                couleur,
                (x_pix, y_pix, TAILLE_CASE, TAILLE_CASE),
                border_radius=8
            )

            # Si c'est la tête, on dessine aussi les yeux
            if i == 0:

                dx, dy = serpent.direction

                # Les yeux sont placés en fonction de la direction
                if dy == -1:      # vers le haut
                    oeil1 = (x_pix + 6, y_pix + 5)
                    oeil2 = (x_pix + 14, y_pix + 5)

                elif dy == 1:     # vers le bas
                    oeil1 = (x_pix + 6, y_pix + 15)
                    oeil2 = (x_pix + 14, y_pix + 15)

                elif dx == -1:    # vers la gauche
                    oeil1 = (x_pix + 5, y_pix + 6)
                    oeil2 = (x_pix + 5, y_pix + 14)

                else:             # vers la droite
                    oeil1 = (x_pix + 15, y_pix + 6)
                    oeil2 = (x_pix + 15, y_pix + 14)

                # Dessin des yeux (deux petits cercles noirs)
                pygame.draw.circle(self.ecran, (0, 0, 0), oeil1, 3)
                pygame.draw.circle(self.ecran, (0, 0, 0), oeil2, 3)

    def attendre_demarrage(self):
        """
        Affiche un écran d'accueil et attend que l'utilisateur
        appuie sur Entrée pour commencer la partie.
        """
        police_titre = pygame.font.Font(None, 48)
        police_txt = pygame.font.Font(None, 32)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return True

            self.ecran.fill(COULEUR_FOND)

            titre = police_titre.render("MULTI-SNAKE NADIR", True, COULEUR_TEXTE)
            info1 = police_txt.render("Appuie sur ENTREE pour commencer", True, COULEUR_TEXTE)
            info2 = police_txt.render("Puis utilise les fleches du clavier", True, COULEUR_TEXTE)

            self.ecran.blit(titre, (140, 180))
            self.ecran.blit(info1, (110, 260))
            self.ecran.blit(info2, (125, 310))

            pygame.display.flip()
            self.horloge.tick(10)

    # -------------------------------------------------------------------
    # BOUCLE PRINCIPALE DU JEU
    # -------------------------------------------------------------------
    def boucle(self):
        """
        Gère le déroulement complet de la partie :
        - pour chaque joueur :
            - le joueur contrôle son serpent
            - quand il meurt, on passe au joueur suivant
        - à la fin, on affiche un écran de classement.
        """
        en_jeu = True  # Permet de quitter proprement la partie

        if not self.attendre_demarrage():
            return

        # On fait jouer chaque joueur l'un après l'autre
        for joueur in range(self.nb_j):
            if not en_jeu:
                break

            # Création d'un nouveau serpent pour ce joueur
            serpent = Serpent(self.arene)

            # Génération de la première nourriture
            nourriture = Nourriture()
            nourriture.generer(self.arene, serpent.segments)

            vivant = True  # Si False, ce joueur a perdu

            # ----------------------------
            # BOUCLE DU SERPENT COURANT
            # ----------------------------
            while vivant:

                # Gestion des événements Pygame (clavier, fermeture fenêtre)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        vivant = False
                        en_jeu = False

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            serpent.changer_direction(0, -1)
                        elif event.key == pygame.K_DOWN:
                            serpent.changer_direction(0, 1)
                        elif event.key == pygame.K_LEFT:
                            serpent.changer_direction(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            serpent.changer_direction(1, 0)

                if not vivant:
                    break

                # Le serpent avance d'une case
                nouvelle_tete = serpent.avancer()

                # Si le serpent mange la nourriture
                if nouvelle_tete == nourriture.position:
                    serpent.grandir()
                    self.score.ajouter(joueur)
                    nourriture.generer(self.arene, serpent.segments)

                # Vérifier les collisions mortelles :
                # - avec un mur ou un corps mort
                # - avec son propre corps (auto-collision)
                if self.arene.collision(nouvelle_tete) or nouvelle_tete in serpent.segments[1:]:
                    self.arene.ajouter_serpent_mort(serpent.segments)
                    vivant = False
                    break

                # ---------- AFFICHAGE GRAPHIQUE ----------
                self.ecran.fill(COULEUR_FOND)

                # Dessin des murs
                for (mx, my) in self.arene.murs:
                    pygame.draw.rect(
                        self.ecran,
                        COULEUR_MUR,
                        (mx * TAILLE_CASE, my * TAILLE_CASE, TAILLE_CASE, TAILLE_CASE)
                    )

                # Dessin des corps des serpents morts
                for (sx, sy) in self.arene.serpents_morts:
                    pygame.draw.rect(
                        self.ecran,
                        COULEUR_SERPENT_MORT,
                        (sx * TAILLE_CASE, sy * TAILLE_CASE, TAILLE_CASE, TAILLE_CASE)
                    )

                # Dessin de la nourriture
                pygame.draw.rect(
                    self.ecran,
                    COULEUR_NOURRITURE,
                    (nourriture.position[0] * TAILLE_CASE,
                     nourriture.position[1] * TAILLE_CASE,
                     TAILLE_CASE, TAILLE_CASE)
                )

                # Dessin du serpent actuel
                self.dessiner_serpent(serpent)

                # Affichage des scores de chaque joueur en haut à gauche
                for i, sc in enumerate(self.score.scores):
                    txt = self.score.police.render(f"Joueur {i+1} : {sc}", True, COULEUR_TEXTE)
                    self.ecran.blit(txt, (10, 10 + i * 25))

                pygame.display.flip()

                # Contrôle de la vitesse du jeu : 8 "ticks" par seconde
                self.horloge.tick(8)

        # --------------------------------------------------------------------
        # ÉCRAN FINAL : CLASSEMENT DES JOUEURS
        # --------------------------------------------------------------------
        classement = self.score.classement()
        self.score.sauvegarder()  # Sauvegarde des scores dans scores.txt

        # Affichage du classement final
        self.ecran.fill(COULEUR_FOND)

        titre = pygame.font.Font(None, 48).render("FIN DE LA PARTIE", True, COULEUR_TEXTE)
        self.ecran.blit(titre, (50, 50))

        y = 150
        police = pygame.font.Font(None, 36)
        rang = 1

        for joueur, points in classement:
            ligne = police.render(f"{rang}. Joueur {joueur+1} : {points} pts", True, COULEUR_TEXTE)
            self.ecran.blit(ligne, (50, y))
            y += 40
            rang += 1

        pygame.display.flip()

        # On attend que l'utilisateur ferme la fenêtre
        attendre = True
        while attendre:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    attendre = False

        pygame.quit()


# ---------------------------------------------------------------------------
# LANCEMENT DU JEU
# ---------------------------------------------------------------------------
# Ce bloc est le point d'entrée du programme :
# - il crée un objet Jeu avec 4 joueurs
# - il lance la boucle principale du jeu
if __name__ == "__main__":
    jeu = Jeu(nb_joueurs=4)
    jeu.boucle()