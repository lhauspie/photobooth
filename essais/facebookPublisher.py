# coding: utf8

import facebook
import warnings
import urllib
import subprocess
import urlparse
import random


# Test
# Procedure
# pour poster un message
# au nom d'une personne via
# une application sur un groupe Facebook

#LaCabinePhoto
APP_ID = "999999999999999"
APP_SECRET = "0d00000de0eab00000d00eb000000f00"
"""
Ces informations APP_ID et APP_SECRET sont presentes dans le dashboard de l'application
    page de developpement : https://developers.facebook.com/
        dans MyApps / MonApplicationFacebook (ex : https://developers.facebook.com/apps/999999999999999/dashboard/)
        relever le App ID et le App Secret
"""

#Logan HAUSPIE pour LaCabinePhoto
USER_ACCESS_TOKEN = "XXXXXxXxXXXXxXXXxXX9XXxXxXXxXXxxXxXXXxXxxX9X9X9XXXxX9xxxX9XXXXxxXXX99x9X99xXX9xXxXX9xxxXXXx9xXXXXX9xxxx9xXx9XX9X9XxxxXxx9xXxxXXXXXxxx9XXXxXX9xXXXxXX9XXxxX9xXx9xXxxXxxxxxX9X9xx9x9XxXXx999X9XXXXXxXX99xXX"
"""
Pour obtenir le USER_ACCESS_TOKEN, il faut le demander a Facebook de la maniere suivante :
    Manuellement :
        Page du GraphAPI Explorer : https://developers.facebook.com/tools/explorer
        Choisir l'application dans la liste déroulante application (ex : La cabine photo)
        Cliquer sur "Get Token" puis "Get User Access Token"
        Donner tous les droits necessaire a ce qu'on veut faire dans l'application (user_managed_groups, manage_pages, publish_actions, publish_pages)
        Cliquer sur "Get Access Token"
"""

#LoganAkaJocker pour LaCabinePhoto
LONG_LIVED_USER_ACCESS_TOKEN = "XXXXXxXxXXXXxXXXXxXxXXXXxXX9xxXxxxXX99xxxx9x99XxXXXxxXxXXxXXx9XXXx9xXxxXXxxxxXxX9Xx9XXX9xxX99XXXXXx9xxXxxXxXXXXXxxxXxxxXXxxxXxXXxxXX9XXXxXX9XX9xxXXxxX99XXxx9XXXxxXXXxxXXxXxxxxXXXX"
"""
Pour avoir un token de long vie (60 jours), il faut lire la doc https://developers.facebook.com/docs/facebook-login/access-tokens#extending
On nous explique devoir faire un
GET /oauth/access_token?  
    grant_type=fb_exchange_token&           
    client_id={app-id}&
    client_secret={app-secret}&
    fb_exchange_token={short-lived-token}

Pour publier sur un groupe au nom d'une personne => LONG_LIVED_USER_ACCESS_TOKEN
https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=<APP_ID>&client_secret=<APP_SECRET>&fb_exchange_token=<USER_ACCESS_TOKEN>
"""
# XXXXXxXxXXXXxXXXXxXxXXXXxXX9xxXxxxXX99xxxx9x99XxXXXxxXxXXxXXx9XXXx9xXxxXXxxxxXxX9Xx9XXX9xxX99XXXXXx9xxXxxXxXXXXXxxxXxxxXXxxxXxXXxxXX9XXXxXX9XX9xxXXxxX99XXxx9XXXxxXXXxxXXxXxxxxXXXX
# https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=999999999999999&client_secret=0d00000de0eab00000d00eb000000f00&fb_exchange_token=XXXXXxXxXXXXxXXXxXX9XXxXxXXxXXxxXxXXXxXxxX9X9X9XXXxX9xxxX9XXXXxxXXX99x9X99xXX9xXxXX9xxxXXXx9xXXXXX9xxxx9xXx9XX9X9XxxxXxx9xXxxXXXXXxxx9XXXxXX9xXXXxXX9XXxxX9xXx9xXxxXxxxxxX9X9xx9x9XxXXx999X9XXXXXxXX99xXX


#LoganAkaJocker pour LaCabinePhoto
LONG_LIVED_USER_ACCESS_TOKEN = "XXXXXxXxXXXXxXXXXxXxXXXXxXX9xxXxxxXX99xxxx9x99XxXXXxxXxXXxXXx9XXXx9xXxxXXxxxxXxX9Xx9XXX9xxX99XXXXXx9xxXxxXxXXXXXxxxXxxxXXxxxXxXXxxXX9XXXxXX9XX9xxXXxxX99XXxx9XXXxxXXXxxXXxXxxxxXXXX"
#Group de test de la Cabine Photo
GROUP_ID = "9999999999999999"


#Poster un message
lion_gif = open("lion.gif")
warnings.filterwarnings('ignore', category=DeprecationWarning)
# Try to post something on the wall.
try:
    print 'Try to post HelloWorld with LONG_LIVED_USER_ACCESS_TOKEN'
    facebook_graph = facebook.GraphAPI(LONG_LIVED_USER_ACCESS_TOKEN)
    facebook_graph.put_wall_post('LONG_LIVED_USER_ACCESS_TOKEN - Hello from Python !!', profile_id = GROUP_ID)

    citations = []
    citations.append("La Cabine PHOTO : Ils ont l'air de bien s'amuser !!")
    citations.append("La Cabine PHOTO : Comme ils sont beaux !!")
    citations.append("La Cabine PHOTO : Trop la classe !!")
    citations.append("La Cabine PHOTO : Allez, faites comme eux... venez essayer !!")
    citations.append("La Cabine PHOTO : Cheeeeeeeeese !!")
    citations.append("La Cabine PHOTO : Inspirééééé !!")
    citations.append("La Cabine PHOTO : On s'amuse comme des petits fous !!")
    citations.append("La Cabine PHOTO : Vous aussi venez vous éclater !!")
    citations.append("La Cabine PHOTO : un")
    citations.append("La Cabine PHOTO : deux")
    citations.append("La Cabine PHOTO : trois")
    citations.append("La Cabine PHOTO : quatre")
    
    print 'Try to post a random message with LONG_LIVED_USER_ACCESS_TOKEN'
    facebook_graph.put_wall_post(random.choice(citations), profile_id = GROUP_ID)
	# 
    facebook_graph.put_photo(lion_gif, "LONG_LIVED_USER_ACCESS_TOKEN - 010 - test de post de photos sur le Groupe de test éèà", GROUP_ID)
except facebook.GraphAPIError as e:
    print 'Something went wrong when using LONG_LIVED_USER_ACCESS_TOKEN:', e.type, e.message
