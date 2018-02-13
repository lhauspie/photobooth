# Photobooth

**WARN** : This documentation still under construction !


Mon projet est de fabriquer un photomaton.  
Ce photomaton doit être capable de :

- Prendre 4 photos
- Assembler ces 4 clichés en une image unique
- Imprimer l'image
- Partager l'image sur un groupe Facebook


## Prés-requis

Pour fabriquer mon photobooth, je me suis muni de :
- un Raspberry Pi 1 model B équipé d'une distrib Raspbian
- un module camera 5MP
- un écran
- une imprimante photo : HP Photosmart A320 series
- trois boutons physiques
- un dongle WiFi

Accessoires :
- une alimentation
- un clavier
- une souris
- un cable HDMI
- une carte SD haut débit

Logiciel :
- Raspbian
- Python 2.7.x
- 

## Installation et configuration


### Installation matérielle


#### Boutons physiques

Bouton Rouge : relié au GPIO 17
Bouton Jaune : relié au GPIO 27
Bouton Vert : relié au GPIO 22

Ces boutons serviront à l'interaction pour :
- Lancer le process principal de prise de vue
- Décider si l'utilisateur souhaite imprimer la photo
- Décider si l'utilisateur souhaite partager la photo sur Facebook (Groupe prédéfini)



#### Caméra

Suivre les instructions présentes dans cette [documentation](https://www.raspberrypi.org/blog/camera-board-available-for-sale/).  
Dans les grandes lignes :
- Brancher correctement la caméra au Rasp
- Activer le support de la caméra avec `sudo raspi-config`
- Tester la caméra avec `raspivid -t 5000 -d`



### Installation logicielle


#### Connexion WiFi

En accord avec [cette doc](http://the-raspberry.com/wifi-config), modifier le fichier `/etc/network/interfaces` :
```bash
auto lo

iface lo inet loopback
iface eth0 inet dhcp

allow-hotplug wlan0
auto wlan0

iface wlan0 inet dhcp
wpa-ssid "SSID_DU_RESEAU"
wpa-psk "MOT_DE_PASSE_DU_RESEAU"
```

Pour connaitre le SSID des réseaux alentour :
```bash
sudo iwlist wlan0 scan
```


#### Dépendance Python pour les API Facebook

**TO BE CONTINUED** [doc](http://facebook-sdk.readthedocs.io/en/latest/install.html)



#### Python Game Photobooth

Se connecter en ssh au Raspberry :
```bash
ssh pi@192.168.1.19
```

Cloner ce repo git dans le dossier `/home/pi` :
```bash
git clone http://www.github.com/lhauspie/photobooth.git
```

Pour lancer le photobooth au démarrage du Rasp, il faut ajouter cette ligne dans le fichier `/etc/rc.local` :
```bash
/home/pi/photobooth/scripts/launcher.sh
```

Le photobooth se lancera alors 40 secondes après le démarrage du Raspberry.



#### Impression

Installation d'un serveur d'impression : Common UNIX Print System (CUPS)

Se connecter en ssh au Raspberry :
```bash
ssh pi@192.168.1.19
```

Mettre à jour les repos du Rasp :
```bash
sudo apt-get update
```

Installer CUPS :
```bash
sudo apt-get install cups
```

Ajouter l'utilisateur `pi` au groupe `lpadmin` :
```bash
sudo usermod -a -G lpadmin pi
```

Configuration de l'imprimante :
- aller sur http://<rasp_ip>:631
- cliquer sur l'onglet `Administration`
- puis sur le bouton `Ajouter une imprimante`
- entrer les login et mot de passe (`pi` / `raspberry`)
- selectionner l'imprimante dans la liste des imprimantes locales (`HP Printer (HPLIP)`)
- **TO BE CONTINUED** [doc](https://www.howtogeek.com/169679/how-to-add-a-printer-to-your-raspberry-pi-or-other-linux-computer/)


Modifier le fichier `~/photobooth/scripts/print_photo.sh` pour correspondre au nom de l'imprimante :
```bash
lp -d <NOM_IMPRIMANTE> /home/pi/photobooth/PB_archive/$1.jpg
```


