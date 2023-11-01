#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import requests
import xml.etree.ElementTree as ET
import zipfile


# Fonction pour télécharger un module Kodi
def download_module(module_name, module_version):
    module_url = f"http://ftp.halifax.rwth-aachen.de/xbmc/addons/matrix/{module_name}/{module_name}-{module_version}.zip"
    module_zip_path = os.path.join(KODI_TEMP_DIR, f"{module_name}-{module_version}.zip")
    
    if os.path.exists(module_zip_path):
        print(f"Le module {module_name} (version {module_version}) est déjà téléchargé.")
        return module_zip_path
    else:
        print(f"Téléchargement du module {module_name} (version {module_version})...")
        response = requests.get(module_url)
        if response.status_code == 200:
            with open(module_zip_path, 'wb') as file:
                file.write(response.content)
            print(f"Le module {module_name} (version {module_version}) a été téléchargé avec succès.")
            return module_zip_path
        else:
            print(f"Échec du téléchargement du module {module_name} (version {module_version}).")
            return None

# Fonction pour dézipper un module Kodi
def unzip_module(module_name, module_version):
    module_zip_path = os.path.join(KODI_TEMP_DIR, f"{module_name}-{module_version}.zip")
    module_dir = os.path.join(KODI_ADDONS_DIR, f"{module_name}")

    if os.path.exists(module_dir):
        print(f"Le module {module_name} (version {module_version}) est déjà dézippé.")
        return module_dir
    else:
        print(f"Dézippage du module {module_name} (version {module_version})...")
        with zipfile.ZipFile(module_zip_path, 'r') as zip_ref:
            zip_ref.extractall(KODI_ADDONS_DIR)
        print(f"Le module {module_name} (version {module_version}) a été dézippé avec succès.")
        return module_dir


# Fonction pour résoudre et installer les dépendances d'un add-on
def resolve_dependencies(addon_xml):
    tree = ET.parse(addon_xml)
    root = tree.getroot()

    for elem in root.iter("import"):
        addon = elem.attrib["addon"]
        version = elem.attrib["version"]
        if addon != "xbmc.python":
            download_module(addon, version)
            addon_dir = unzip_module(addon,version)
            resolve_dependencies(addon_dir + '/addon.xml')

# Exemple d'utilisation du script
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Syntax : {sys.argv[0]} <addon_name> <addon_version> [kodi_addons_dir] [kodi_temp_dir]")
        sys.exit(1)

    addon_name = sys.argv[1]
    addon_version = sys.argv[2]
    KODI_ADDONS_DIR = sys.argv[3] if len(sys.argv) > 3 else './addons'
    KODI_TEMP_DIR = sys.argv[4] if len(sys.argv) > 4 else './temp'
    
    # Télécharger le module principal
    download_status = download_module(addon_name, addon_version)
    if download_status :

        addon_dir = unzip_module(addon_name,addon_version)

        # Résoudre les dépendances
        resolve_dependencies(addon_dir + '/addon.xml')

