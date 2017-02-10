#!/usr/bin/python

from configparser import ConfigParser

def config(fichier='bases.cfg', section='localhost'):

    """ retourne db :parametre de connexion postgres
        lu dans dans fichier ,section """
    # creer un parser 
    parser = ConfigParser()
    #lire le fichier de config
    parser.read(fichier)
    #prendre elements de section par defaut localhost
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('section {0} pas trouve  fichier {1}'.format(section,fichier))
    return db

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79
