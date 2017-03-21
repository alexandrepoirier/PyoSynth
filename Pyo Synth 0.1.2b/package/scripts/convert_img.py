from wx.tools import img2py
import os

def listImgFiles(path):
    """
    Prend un chemin d'acces en paramtre et retourne une liste
    de toutes les images s'y trouvant, avec leur chemin d'acces complet.
    Note : ne fouille pas les sous-dossiers.
    """
    list = [os.path.join(path,f) for f in os.listdir(path) if os.path.isfile(os.path.join(path,f))]
    if list[0].find('DS_Store') != -1: del list[0]
    return list
    

def convertImagesToPy(list, target):
    """
    Prend une liste de chemins d'acces a des images prealablement creee avec listImgFiles() et
    en deuxieme parametre le nom du fichier cible avec l'endroit ou il doit etre depose.
    """
    for i in range(len(list)):
        img2py.img2py(list[i], target, True)
    print "\n#############################################################"
    print "# Done converting %d files to %s." % (len(list), target)
    print "#############################################################\n"
    
#convertImagesToPy(listImgFiles("img/controls/menu-buttons"), "img/controls/menu-buttons/pyimg.py")
convertImagesToPy(listImgFiles("../img/interface"), "../img/interface/pyimg.py")