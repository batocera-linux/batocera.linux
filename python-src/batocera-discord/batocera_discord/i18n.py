"""Overlay strings: English by default, translated from the Batocera ``system.language`` setting."""

from __future__ import annotations

import logging
import subprocess
from typing import Final

from . import paths
from .errors import PROCESS_ERRORS

_logger: Final = logging.getLogger(__name__)

_FR: Final = {
    'Servers': 'Serveurs',
    'Friends': 'Amis',
    'Call': 'Appel',
    'Settings': 'Réglages',
    'Select': 'Choisir',
    'Back': 'Retour',
    'Mic': 'Micro',
    'Sound': 'Son',
    'Close': 'Fermer',
    'Mic muted': 'Micro coupé',
    'Sound off': 'Son coupé',
    'No microphone': 'Pas de micro',
    'no microphone connected': 'aucun micro connecté',
    '{name} · hi-fi mode': '{name} · son HD',
    'available': 'disponible',
    'In call · {name}': 'En appel · {name}',
    'Private call': 'Appel privé',
    'Loading voice channels…': 'Chargement des salons…',
    'No voice channel on this server': 'Aucun salon vocal sur ce serveur',
    'No friends yet': "Aucun ami pour l'instant",
    'Add favorites from the setup page. Your private calls show up here automatically.': (
        "Ajoute des favoris depuis la page de configuration. Tes appels privés s'ajoutent ici automatiquement."
    ),
    'Favorite': 'Favori',
    'Recent call': 'Appel récent',
    'Dial': 'Appeler',
    'Leave call': "Quitter l'appel",
    'Not in a call': "Pas d'appel en cours",
    'Join a channel from Servers or call a friend.': 'Rejoins un salon dans Serveurs ou appelle un ami.',
    'you': 'toi',
    'muted for you': 'muet pour toi',
    'speaking…': 'parle…',
    'sound off': 'son coupé',
    'mic off': 'micro coupé',
    'connected': 'connecté',
    'You are here · ': 'Tu es connecté · ',
    '{count} connected': '{count} connecté(s)',
    'volume': 'volume',
    'mute': 'muet',
    'back': 'retour',
    'Connecting to {name}…': 'Connexion à {name}…',
    'Call left': 'Appel quitté',
    'No microphone connected': 'Aucun micro connecté',
    'Switch your headset to call mode to talk': 'Passe ton casque en mode appel pour parler',
    'Set up Discord': 'Configurer Discord',
    'Scan this code with your phone': 'Scanne ce code avec ton téléphone',
    'Your phone must be on the same network as this console.': 'Ton téléphone doit être sur le même réseau que la console.',
    'The page explains how to create your free Discord application (2 minutes).': (
        'La page explique comment créer ton application Discord gratuite (2 minutes).'
    ),
    'Waiting for your phone…': 'En attente de ton téléphone…',
    'Discord is not installed': "Discord n'est pas installé",
    'Press {button} to install it from Flathub (about 250 MB).': "Appuie sur {button} pour l'installer depuis Flathub (environ 250 Mo).",
    'Installing Discord… {percent}%': 'Installation de Discord… {percent} %',
    'Meanwhile, press {button} to set it up from your phone.': (
        'En attendant, appuie sur {button} pour le configurer depuis ton téléphone.'
    ),
    'Starting Discord…': 'Démarrage de Discord…',
    'Log in to Discord once in its window, then come back here.': (
        'Connecte-toi une fois à Discord dans sa fenêtre, puis reviens ici.'
    ),
    'Show Discord window': 'Afficher la fenêtre Discord',
    'Connecting…': 'Connexion…',
    'Authorization': 'Autorisation',
    'Accept the request in the Discord window: move the pointer with the stick, {button} clicks.': (
        'Accepte la demande dans la fenêtre Discord : le stick déplace le pointeur, {button} clique.'
    ),
    'Something went wrong': 'Un problème est survenu',
    'Starting…': 'Démarrage…',
    'Reconfigure': 'Reconfigurer',
    'Log out': 'Se déconnecter',
    'Connected as {name}': 'Connecté en tant que {name}',
    'Logged out': 'Déconnecté',
    'Open the setup page': 'Ouvrir la page de configuration',
    'Discord ready': 'Discord prêt',
    'Discord: setup required': 'Discord : configuration requise',
}

_CATALOGS: Final = {'fr': _FR}


def _system_language() -> str:
    try:
        result = subprocess.run(
            ['batocera-settings-get', 'system.language'], capture_output=True, text=True, timeout=5, check=False
        )
        value = result.stdout.strip()
    except PROCESS_ERRORS:
        value = ''
    if not value and paths.BATOCERA_CONF.is_file():
        for line in paths.BATOCERA_CONF.read_text(encoding='latin1').splitlines():
            if line.startswith('system.language='):
                value = line.partition('=')[2].strip()
    return value.split('_')[0].lower() or 'en'


class Translator:
    def __init__(self, language: str = 'en', /) -> None:
        self.language = language
        self._catalog: dict[str, str] = _CATALOGS.get(language, {})

    def set_language(self, language: str | None = None, /) -> None:
        self.language = language or _system_language()
        self._catalog = _CATALOGS.get(self.language, {})

    def __call__(self, text: str, /, **values: object) -> str:
        translated = self._catalog.get(text, text)
        return translated.format(**values) if values else translated


# module level translator; the daemon calls ``_.set_language()`` once at startup
_ = Translator()
