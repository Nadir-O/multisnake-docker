# MultiSnake Docker

Projet réalisé dans le cadre du cours Network and Cloud.

Ce projet consiste à exécuter un jeu Snake développé en Python dans un conteneur Docker. L’affichage du jeu se fait dans un navigateur web grâce à noVNC.

## Fichiers du projet

multi_snake.py : code du jeu  
Dockerfile : construction de l’image Docker  
start.sh : script de démarrage du conteneur  
requirements.txt : dépendances Python  

## Lancer le projet

Ouvrir un terminal dans le dossier du projet, c’est-à-dire dans le dossier qui contient les fichiers du projet.

Construire l’image Docker :

docker build -t multisnake-gui .

Lancer ensuite le conteneur :

docker run --name multisnake-test -p 6081:6080 multisnake-gui

Ouvrir ensuite le navigateur à l’adresse suivante :

http://localhost:6081/vnc.html

Cliquer sur Connecter.

Quand l’écran du jeu apparaît, appuyer sur Entrée pour démarrer la partie.

## Relancer le jeu après la fin

Quand la partie est terminée, la méthode utilisée pour relancer correctement le jeu est de supprimer l’ancien conteneur puis d’en recréer un nouveau.

Dans le terminal, exécuter :

docker rm -f multisnake-test  
docker run --name multisnake-test -p 6081:6080 multisnake-gui

Puis rouvrir dans le navigateur :

http://localhost:6081/vnc.html

Cliquer sur Connecter puis appuyer sur Entrée.

## Technologies utilisées

Python  
Pygame  
Docker  
Xvfb  
x11vnc  
noVNC  

## Auteur

Projet réalisé par Nadir dans le cadre du cours Network and Cloud.