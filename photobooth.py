#!/usr/bin/python
# coding: utf8

import pygame
import picamera
import facebook
import time
import io
import os
import subprocess
import threading
import RPi.GPIO as GPIO
import math
import random

from pygame.locals import *

ROOT_FOLDER = "/home/pi/photobooth"
SHOTS_DIRECTORY = ROOT_FOLDER + "/shots/"
ARCHIVE_DIRECTORY = ROOT_FOLDER + "/PB_archive/"
RESSOURCES_DIRECTORY = ROOT_FOLDER + "/ressources/"

COLOR_BLACK  = (  0,   0,   0)
COLOR_WHITE  = (255, 255, 255)
COLOR_RED    = (255,   0,   0)
COLOR_GREEN  = (  0, 255,   0)
COLOR_BLUE   = (  0,   0, 255)
COLOR_YELLOW = (255, 255,   0)
COLOR_GOLD   = (255, 215,   0)

BRIGHTNESS = 55

MODE_PRISE_DE_VUE = "PRISE_DE_VUE"
MODE_PARTAGE = "PARTAGE"
MODE_IMPRESSION = "IMPRESSION"

# GPIO NUMBER
BUTTON_RED = 17
BUTTON_YELLOW = 27
BUTTON_GREEN = 22

BUTTON_PUSHED = 0
BUTTON_RELEASED = 1


LOG_SHARING_ASKED = "01_sharing_asked"
LOG_SHARING_ALLOWED = "02_sharing_allowed"
LOG_SHARING_DENIED = "02_sharing_denied"
LOG_PRINTING_ASKED = "03_printing_asked"
LOG_PRINTING_ALLOWED = "04_printing_allowed"
LOG_PRINTING_DENIED = "04_printing_denied"

# Tres utile si le photobooth est retro affiché via un miroir
DISPLAY_IN_MIRROR_MODE = True


####################################################################
# Classe permettant de servir des messages au hasard
class MessageRandomizer:
    def __init__(self):
        self._citations = []
        self._citations.append("La Cabine PHOTO : Ils ont l'air de bien s'amuser !!");
        self._citations.append("La Cabine PHOTO : Comme ils sont beaux !!");
        self._citations.append("La Cabine PHOTO : Trop la classe !!");
        self._citations.append("La Cabine PHOTO : Allez, faites comme eux... venez essayer !!");
        self._citations.append("La Cabine PHOTO : Cheeeeeeeeese !!");
        self._citations.append("La Cabine PHOTO : Inspirééééé !!");
        self._citations.append("La Cabine PHOTO : On s'amuse comme des petits fous !!");
        self._citations.append("La Cabine PHOTO : Vous aussi, venez vous éclater !!");
        self._citations.append("La Cabine PHOTO : Souriez, vous étes photographiés !!");
        self._citations.append("La Cabine PHOTO : Ils ont osé partager ces clichés !!");
        self._citations.append("La Cabine PHOTO : Wouhaa, trop drôle !!");
        self._citations.append("La Cabine PHOTO : Seul c'est bien, plusieurs c'est mieux !!");
    
    def getRandomMessage(self):
        return random.choice(self._citations)
####################################################################



####################################################################
# Loading est une sous-classe de threading.Thread
class Loading(threading.Thread):
    def __init__(self, photobooth):
        # appel au super-constructeur
        threading.Thread.__init__(self)
        # boolean pour savoir quand arreter le thread (While running)
        self._running = True
        # chargement de l'image de chargement
        self._original_image = pygame.image.load(RESSOURCES_DIRECTORY + "loading.png")
        # image de chargement tourne d'un angle de _rotation_angle
        self._rotated_image = None
        # angle de rotation de l'image de chargement
        self._rotation_angle = 0
        # initialise la surface de dessin
        self._photobooth = photobooth
        # permet de connaitre le mode dans lequel on se trouve : permet de gerer les evenements de maniere differentes en fonction du mode 
        self._current_mode = MODE_PRISE_DE_VUE
        
    # permet de faire tourner dans le sens horaire l'image de chargement en son centre de 45 degres
    def centered_rotate_image(self):
        orig_rect = self._original_image.get_rect()
        self._rotation_angle -= 45
        if (self._rotation_angle < 360):
            self._rotation_angle += 360
        self._rotated_image = pygame.transform.rotate(self._original_image, self._rotation_angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = self._rotated_image.get_rect().center
        self._rotated_image = self._rotated_image.subsurface(rot_rect).copy()
        
        
    # le comportement du thread
    def run(self):
        while (self._running):
            self.centered_rotate_image()
            self._photobooth._display_surf.fill(COLOR_BLACK)
            self._photobooth._display_surf.blit(self._rotated_image, (self._photobooth._display_surf.get_rect().centerx - 250, self._photobooth._display_surf.get_rect().centery - 250))
            pygame.display.flip() # Simply update the entire contents of the surface
            time.sleep(0.5)
        
        
    def stop(self):
        self._running = False
        # on attend 1 seconde pour etre sur que le run puisse finir son dernier tour tranquillement
        time.sleep(1)
####################################################################



####################################################################
# FacebookPublisher est une sous-classe de threading.Thread
class FacebookPublisher(threading.Thread):
    LONG_LIVED_PAGE_ACCESS_TOKEN = "XXXXXxXxXXXXxXXXXxXxXXXXxXX9xxXxxxXX99xxxx9x99XxXXXxxXxXXxXXx9XXXx9xXxxXXxxxxXxX9Xx9XXX9xxX99XXXXXx9xxXxxXxXXXXXxxxXxxxXXxxxXxXXxxXX9XXXxXX9XX9xxXXxxX99XXxx9XXXxxXXXxxXXxXxxxxXXXX"
    GROUP_ID = "9999999999999999"
    
    def __init__(self, path):
        # appel au super-constructeur
        threading.Thread.__init__(self)
        self._graph = facebook.GraphAPI(FacebookPublisher.LONG_LIVED_PAGE_ACCESS_TOKEN)
        self._photo_path = path
        self._messageRandomizer = MessageRandomizer()

    def run(self):
        image = open(self._photo_path)
        self._graph.put_photo(image, self._messageRandomizer.getRandomMessage(), FacebookPublisher.GROUP_ID)
####################################################################



####################################################################
# class Main    
class Photobooth:
    def __init__(self):
        # pour savoir si le pygame est en cours de lancement
        self._running = True
        # pour savoir si le photobooth est en attente de lancement du processus principal
        self._current_mode = MODE_PRISE_DE_VUE
        # la zone d'affichage
        self._display_surf = None
        # la camera
        self._camera = picamera.PiCamera()
        self._camera.iso = 800
        self._camera.brightness = 70
        self._camera.contrast = 75
        self._camera.resolution = (900, 600) # 900 x 600 pour garder un ratio 15 x 10 prevu pour l'impression
        self._camera.preview_alpha = 220 # rends l'affichage un peu transparent pour pouvoir afficher du texte par transparence
		# cle de shoot permettant de stocker les 4 photos du processus
        self._shooting_key = None

        self._button_red_pushed = False
        self._button_yellow_pushed = False
        self._button_green_pushed = False
        
        # le materiel chinois nous oblige a faire un compteur qui nous permet de voir depuis combien de tour le bouton a ete relache
        # il semblerait que le mecanisme interne du bouton physique rebondisse pendant l'appuis ce qui donne des faux OK de pushed and released 
        self._nombre_tour_apres_relachement_button_red = 0
        self._nombre_tour_apres_relachement_button_yellow = 0
        self._nombre_tour_apres_relachement_button_green = 0
        

    def on_init(self):
        print "on_init"
        pygame.init()
        pygame.mouse.set_visible(False)
        displayInfo = pygame.display.Info()
        self.size = displayInfo.current_w, displayInfo.current_h
        self._display_surf = pygame.display.set_mode(self.size, pygame.FULLSCREEN)
        self._font_600 = pygame.font.Font(None, 600)
        self._font_400 = pygame.font.Font(None, 400)
        self._font_200 = pygame.font.Font(None, 200)
        self._font_100 = pygame.font.Font(None, 100)
        #set up GPIO using BCM numbering
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUTTON_RED, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(BUTTON_YELLOW, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(BUTTON_GREEN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # on charge les ressources statiques des l'init pour eviter les chargements multiples d'une meme ressource
        self._static_image_bouton_vert = pygame.image.load(RESSOURCES_DIRECTORY + "BoutonVert.png")
        self._static_image_bouton_vert = pygame.transform.flip(self._static_image_bouton_vert, DISPLAY_IN_MIRROR_MODE, False) # Flip
        self._static_image_bouton_vert_rect = self._static_image_bouton_vert.get_rect()
        self._static_image_bouton_vert_rect.centerx = 475
        self._static_image_bouton_vert_rect.centery = self._display_surf.get_height() - 65
        
        self._static_image_bouton_rouge = pygame.image.load(RESSOURCES_DIRECTORY + "BoutonRouge.png")
        self._static_image_bouton_rouge = pygame.transform.flip(self._static_image_bouton_rouge, DISPLAY_IN_MIRROR_MODE, False)
        self._static_image_bouton_rouge_rect = self._static_image_bouton_rouge.get_rect()
        self._static_image_bouton_rouge_rect.centerx = self._display_surf.get_width() - 475
        self._static_image_bouton_rouge_rect.centery = self._display_surf.get_height() - 65
        
        self._static_label_souriez = self._font_400.render("Souriez !!!", 1, COLOR_YELLOW)
        self._static_label_souriez = pygame.transform.flip(self._static_label_souriez, DISPLAY_IN_MIRROR_MODE, False)
        self._static_label_souriez_rect = self._static_label_souriez.get_rect()
        self._static_label_souriez_rect.centerx = self._display_surf.get_rect().centerx
        self._static_label_souriez_rect.centery = self._display_surf.get_rect().centery

        self._static_label_oui = self._font_200.render("OUI", 1, COLOR_YELLOW)
        self._static_label_oui = pygame.transform.flip(self._static_label_oui, DISPLAY_IN_MIRROR_MODE, False)
        self._static_label_oui_rect = self._static_label_oui.get_rect()
        self._static_label_oui_rect.centerx = 175
        self._static_label_oui_rect.centery = self._display_surf.get_height() - 55
        
        self._static_label_non = self._font_200.render("NON", 1, COLOR_YELLOW)
        self._static_label_non = pygame.transform.flip(self._static_label_non, DISPLAY_IN_MIRROR_MODE, False)
        self._static_label_non_rect = self._static_label_non.get_rect()
        self._static_label_non_rect.centerx = self._display_surf.get_width() - 175
        self._static_label_non_rect.centery = self._display_surf.get_height() - 55

        self._static_label_fini = self._font_200.render("C'est fini, MERCI !!!", 1, COLOR_YELLOW)
        self._static_label_fini = pygame.transform.flip(self._static_label_fini, DISPLAY_IN_MIRROR_MODE, False)
        self._static_label_fini_rect = self._static_label_fini.get_rect()
        self._static_label_fini_rect.centerx = self._display_surf.get_rect().centerx
        self._static_label_fini_rect.centery = self._display_surf.get_rect().centery

        self._camera.start_preview()


    def on_pygame_event(self, event):
        print "on_pygame_event"
        print "current_mode : " + self._current_mode
        
        if event.type == QUIT:
            self._running = False
        
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            self._running = False

        if event.type == KEYDOWN and event.key == K_SPACE:
            self.on_button_pushed(BUTTON_YELLOW)

        if event.type == KEYDOWN and event.key == K_RIGHT:
            self.on_button_pushed(BUTTON_GREEN)
        
        if event.type == KEYDOWN and event.key == K_LEFT:
            self.on_button_pushed(BUTTON_RED)
        
        pygame.event.clear()


    def on_button_pushed(self, buttonPushed):
        print "on_button_pushed : " + str(buttonPushed)
        print "current_mode : " + self._current_mode
        
        if self._current_mode == MODE_PRISE_DE_VUE:
            if buttonPushed == BUTTON_YELLOW:
                self.on_run_process(4)
                self.ask_to_share()

        elif self._current_mode == MODE_PARTAGE:
            if buttonPushed == BUTTON_GREEN: # say YES to share on facebook
                self.log(LOG_SHARING_ALLOWED)
                self.on_share()
                self.ask_to_print()
            if buttonPushed == BUTTON_RED: # say NO to share on facebook
                self.log(LOG_SHARING_DENIED)
                self.ask_to_print()
        
        elif self._current_mode == MODE_IMPRESSION:
            if buttonPushed == BUTTON_GREEN: # say YES to print the shooting
                self.log(LOG_PRINTING_ALLOWED)
                self.on_print()
                self.display_finish_message()
            if buttonPushed == BUTTON_RED: # say NO to print the shooting
                self.log(LOG_PRINTING_DENIED)
                self.display_finish_message()
            
        else:
            pass


    # point de depart suite a l'appuis sur le bouton de lancement
    def on_run_process(self, numberOfShoot):
        print "on_run_process"
        # on indique que le photobooth est en cours de prise de vue
        self._current_mode == MODE_PRISE_DE_VUE
        
        # on initialise une cle de prise de vue
        # cette cle nous servira tout au long du processus de prise de vue et d'assemblage
        self._shooting_key = "20" + time.strftime('%y%m%d%H%M%S', time.localtime())

        # on cree le dossier pour reunir les 4 prises de vue en vue de l'assemblage
        os.makedirs(SHOTS_DIRECTORY + self._shooting_key)
        
        # on prend les 4 photos
        for x in range (1, 1 + numberOfShoot, 1):
            self.take_one_picture("00" + str(x))

        # on les assemble
        self.assemble_shots()


    # methode unitaire de prise de vue avec :
    # - un decompte
    # - un message de "soyez pret"
    # - un shoot photo
    def take_one_picture(self, pictureName):
        print "take_one_picture"
        
        # count down before taking picture
        self.count_down(5)#5
        self.get_ready(1)#1
        self.shoot(pictureName)
    
    
    # methode permettant d'afficher un decompte de num a 0
    def count_down(self, num):
        for x in range (num, 0, -1):
            self._display_surf.fill(COLOR_BLACK)
            label = self._font_600.render(str(x), 1, COLOR_YELLOW)
            label = pygame.transform.flip(label, True, False)
            labelRect = label.get_rect()
            labelRect.centerx = self._display_surf.get_rect().centerx
            labelRect.centery = self._display_surf.get_rect().centery
            self._display_surf.blit(label, labelRect)
            pygame.display.flip() # Simply update the entire contents of the surface
            time.sleep(1)
        
    
    # methode d'affichage d'un message de "soyer pret" pendant une duree de timeToWaitBeforeShooting
    def get_ready(self, timeToWaitBeforeShooting):
        self._display_surf.fill(COLOR_BLACK)
        self._display_surf.blit(self._static_label_souriez, self._static_label_souriez_rect)
        pygame.display.flip() # Simply update the entire contents of the surface
        time.sleep(timeToWaitBeforeShooting)


    # methode permettant de prendre une photo, on flash avec l'ecran en affichant un ecran blanc pendant la prise de vue
    def shoot(self, pictureName):
        picturePath = SHOTS_DIRECTORY + self._shooting_key + "/" + pictureName + ".jpg"

        # flash the screen to emulate flash
        self._display_surf.fill(COLOR_WHITE)
        pygame.display.flip() # Simply update the entire contents of the surface
        
        self._camera.stop_preview()
        self._camera.capture(picturePath)
        
        self._display_surf.fill(COLOR_BLACK)
        pygame.display.flip() # Simply update the entire contents of the surface
        
        self._camera.start_preview()
        

    # methode permettant de faire l'assemblage et montage des 4 photos
    def assemble_shots(self):
        loading = Loading(self)

        self._camera.stop_preview()
        # on affiche l'ecran de chargement
        loading.start()
        # on appel un script sh fait-maison qui utilise la librairie imagemagick pour le montage
        try:
            subprocess.check_call([ROOT_FOLDER + "/scripts/assemble_shots.sh", self._shooting_key])
        finally:
            loading.stop()
        
        # clean the display surface
        self._display_surf.fill(COLOR_BLACK)
        pygame.display.flip() # Simply update the entire contents of the surface
        
        
    def ask_to_share(self):
        print "DO YOU WANT TO SHARE ?"
        self.log(LOG_SHARING_ASKED)

        image = pygame.image.load(ARCHIVE_DIRECTORY + self._shooting_key + ".jpg")
        image = pygame.transform.flip(image, True, False)
        image = pygame.transform.scale(image, (math.trunc((self._display_surf.get_height()-120)*1.5), self._display_surf.get_height()-120))
        image_rect = image.get_rect()
        image_rect.centerx = self._display_surf.get_rect().centerx
        image_rect.centery = self._display_surf.get_rect().centery - 60
        
        question_1 = self._font_100.render("Voulez-vous publier votre photo", 1, COLOR_YELLOW)
        question_1 = pygame.transform.flip(question_1, True, False)
        question_1_rect = question_1.get_rect()
        question_1_rect.centerx = self._display_surf.get_rect().centerx
        question_1_rect.centery = self._display_surf.get_rect().centery + 140

        question_2 = self._font_100.render("sur la page Facebook du mariage ?", 1, COLOR_YELLOW)
        question_2 = pygame.transform.flip(question_2, True, False)
        question_2_rect = question_2.get_rect()
        question_2_rect.centerx = self._display_surf.get_rect().centerx
        question_2_rect.centery = self._display_surf.get_rect().centery + 215
        
        self._display_surf.fill(COLOR_BLACK)
        self._display_surf.blit(image, image_rect)
        self._display_surf.blit(question_1, question_1_rect)
        self._display_surf.blit(question_2, question_2_rect)
        self._display_surf.blit(self._static_label_oui, self._static_label_oui_rect)
        self._display_surf.blit(self._static_image_bouton_vert, self._static_image_bouton_vert_rect)
        self._display_surf.blit(self._static_label_non, self._static_label_non_rect)
        self._display_surf.blit(self._static_image_bouton_rouge, self._static_image_bouton_rouge_rect)
        pygame.display.flip() # Simply update the entire contents of the surface
        
        self._current_mode = MODE_PARTAGE
        
        
    def on_share(self):
        print "SHARED TO FACEBOOK"
        facebookPublisher = FacebookPublisher(ARCHIVE_DIRECTORY + self._shooting_key + ".jpg")
        facebookPublisher.start()
        
        
    def ask_to_print(self):
        print "DO YOU WANT TO PRINT ?"
        self.log(LOG_PRINTING_ASKED)

        image = pygame.image.load(ARCHIVE_DIRECTORY + self._shooting_key + ".jpg")
        image = pygame.transform.flip(image, True, False)
        image = pygame.transform.scale(image, (math.trunc((self._display_surf.get_height()-120)*1.5), self._display_surf.get_height()-120))
        image_rect = image.get_rect()
        image_rect.centerx = self._display_surf.get_rect().centerx
        image_rect.centery = self._display_surf.get_rect().centery - 60
        
        question = self._font_100.render("Voulez-vous imprimer votre photo ?", 1, COLOR_YELLOW)
        question = pygame.transform.flip(question, True, False)
        question_rect = question.get_rect()
        question_rect.centerx = self._display_surf.get_rect().centerx
        question_rect.centery = self._display_surf.get_rect().centery + 175

        self._display_surf.fill(COLOR_BLACK)
        self._display_surf.blit(image, image_rect)
        self._display_surf.blit(question, question_rect)
        self._display_surf.blit(self._static_label_oui, self._static_label_oui_rect)
        self._display_surf.blit(self._static_image_bouton_vert, self._static_image_bouton_vert_rect)
        self._display_surf.blit(self._static_label_non, self._static_label_non_rect)
        self._display_surf.blit(self._static_image_bouton_rouge, self._static_image_bouton_rouge_rect)
        pygame.display.flip() # Simply update the entire contents of the surface

        self._current_mode = MODE_IMPRESSION
        
        
    def on_print(self):
        print "SEND TO PRINTER"
        subprocess.check_call([ROOT_FOLDER + "/scripts/print_photo.sh", self._shooting_key])
        
        
    def display_finish_message(self):
        self._display_surf.fill(COLOR_BLACK)
        self._display_surf.blit(self._static_label_fini, self._static_label_fini_rect)
        pygame.display.flip() # Simply update the entire contents of the surface
        time.sleep(3)
        
        self._display_surf.fill(COLOR_BLACK)
        pygame.display.flip() # Simply update the entire contents of the surface
        
        self._camera.start_preview()
        self._current_mode = MODE_PRISE_DE_VUE
        
        
    def on_loop(self):
        pass
        
        
    def on_render(self):
        pass
        
        
    def on_cleanup(self):
        print "on_cleanup"
        self._camera.close()
        pygame.mouse.set_visible(True)
        pygame.quit()
        
        
    def on_execute(self):
        print "on_execute"
        if self.on_init() == False:
            self._running = False
 
        compteur = 0
        while (self._running):
            compteur += 1
            # print "Tour numero : " + str(compteur)
            
            # on gere ici le CLAVIER
            for event in pygame.event.get():
                self.on_pygame_event(event)
            
            """
            on se dit que si on reste appuye sur un bouton sans le relacher
            on va valider toutes les questions sans s'en rendre compte
            donc on va declencher le processus seulement une fois le bouton relache
            """
            
            # on gere ici le bouton ROUGE
            etat_bouton_rouge = GPIO.input(BUTTON_RED)
            if etat_bouton_rouge == BUTTON_PUSHED:
                # print "Circuit RED-17 closed"
                self._button_red_pushed = True
                self._nombre_tour_apres_relachement_button_red = 0
            if etat_bouton_rouge == BUTTON_RELEASED:
                self._nombre_tour_apres_relachement_button_red += 1
                # on fait un test sur 15 tours
                # 15 tours de boucle releve plus du choix delibere de lacher le bouton que du rebond du mecanisme interne du bouton
                if self._nombre_tour_apres_relachement_button_red > 15 and self._button_red_pushed == True:
                    print "Circuit RED-17 closed and reopened"
                    self._button_red_pushed = False
                    self.on_button_pushed(BUTTON_RED)

            # on gere ici le bouton JAUNE
            etat_bouton_jaune = GPIO.input(BUTTON_YELLOW)
            if etat_bouton_jaune == BUTTON_PUSHED:
                # print "Circuit YELLOW-27 closed"
                self._button_yellow_pushed = True
                self._nombre_tour_apres_relachement_button_yellow = 0
            if etat_bouton_jaune == BUTTON_RELEASED:
                self._nombre_tour_apres_relachement_button_yellow += 1
                # on fait un test sur 15 tours
                # 15 tours de boucle releve plus du choix delibere de lacher le bouton que du rebond du mecanisme interne du bouton
                if self._nombre_tour_apres_relachement_button_yellow > 15 and self._button_yellow_pushed == True:
                    print "Circuit YELLOW-27 closed and reopened"
                    self._button_yellow_pushed = False
                    self.on_button_pushed(BUTTON_YELLOW)

            # on gere ici le bouton VERT
            etat_bouton_vert = GPIO.input(BUTTON_GREEN)
            if etat_bouton_vert == BUTTON_PUSHED:
                # print "Circuit GREEN-22 closed"
                self._button_green_pushed = True
                self._nombre_tour_apres_relachement_button_green = 0
            if etat_bouton_vert == BUTTON_RELEASED:
                self._nombre_tour_apres_relachement_button_green += 1
                # on fait un test sur 15 tours
                # 15 tours de boucle releve plus du choix delibere de lacher le bouton que du rebond du mecanisme interne du bouton
                if self._nombre_tour_apres_relachement_button_green > 15 and self._button_green_pushed == True:
                    print "Circuit GREEN-22 closed and reopened"
                    self._button_green_pushed = False
                    self.on_button_pushed(BUTTON_GREEN)

            # possibilite d'arreter le photobooth en appuyant sur les 3 boutons simultanement
            if etat_bouton_rouge == BUTTON_PUSHED and etat_bouton_jaune == BUTTON_PUSHED and etat_bouton_vert == BUTTON_PUSHED:
                self._running = False

            self.on_loop()
            self.on_render()
        self.on_cleanup()
    
    
    def log(self, message):
        print "log " + message
        try:
            print "trying to open file"
            logFile = open(SHOTS_DIRECTORY + self._shooting_key + "/" + message + ".log", "w")
        finally:
            print "finally close file"
            logFile.close()            


if __name__ == "__main__" :
    thePhotobooth = Photobooth()
    thePhotobooth.on_execute()
