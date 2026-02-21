# Quick Start - Ventilairsec VMI Monitor pour Home Assistant

## Installation Rapide

### Option 1: Via le magasin d'addons Home Assistant (Recommandé)

1. **Ajouter le repository**
   - Home Assistant → Paramètres → Systèmes → Magasin d'Addons
   - Bouton ⋮ (coin supérieur droit) → "Dépôts personnalisés"
   - URL: `https://github.com/fortinric88/HA-VMI`
   - Cliquer "Créer"

2. **Installer l'addon**
   - Le repository apparaît dans le magasin
   - Chercher "Ventilairsec VMI Monitor"
   - Cliquer "Installer"

3. **Configurer**
   - Onglet "Configuration"
   - Port série: `/dev/ttyAMA0` (défaut RPi)
   - Cliquer "Enregistrer"

4. **Démarrer**
   - Onglet "Info"
   - Bouton "Démarrer"
   - Attendre "Addon détecté" = ✓ En ligne

5. **Accéder au dashboard**
   - URL: `http://<ip-homeassistant>:5000`

### Option 2: Installation manuelle

```bash
# 1. SSH sur Home Assistant
ssh root@<ip-homeassistant>

# 2. Cloner le repository
cd /addons
git clone https://github.com/fortinric88/HA-VMI.git

# 3. Recharger les addons
ha addons reload

# 4. Installer via UI ou CLI
ha addon install ventilairsec-vmi
ha addon start ventilairsec-vmi
```

## Prérequis Matériel

- **Raspberry Pi 3B+** ou supérieur
- **Module EnOcean USB** (ex: TCM-515, USB300)
  - Connecté à: `/dev/ttyUSB0` ou `/dev/ttyAMA0`
- **Home Assistant** 2024.1.0+

## Configuration Initiale

Après le démarrage, vérifiez les logs:

```bash
ha addon log ventilairsec-vmi

# Sortie attendue:
# ...
# EnOcean Base ID: XXXXXXXX
# Device detected: VMI Purevent (0x0421574F)
# ...
```

## Dépannage d'Installation

### "Module not found on /dev/ttyAMA0"

1. Vérifier la connexion physique
2. Dans la config, essayer:
   - `/dev/ttyUSB0` (si USB)
   - `/dev/ttyS0` (UART par défaut)

Trouver le bon port:
```bash
ls /dev/tty*
# Ou pour voir les périphériques
dmesg | grep tty
```

### "Impossible de confirmer la connexion"

- Attendre 30 secondes après le démarrage
- Vérifier l'alimentation du module EnOcean (LED verte)
- Redémarrer l'addon: `ha addon restart ventilairsec-vmi`

## Utilisation

### Dashboard Web (Port 5000)

- **Tableau de Bord**: Données en temps réel de tous les appareils
- **Historique**: Graphiques 24h avec Min/Max/Moyenne
- **Paramètres**: Configuration et liste des appareils

### Intégration Home Assistant (Optionnel)

L'addon expose une API REST. Pour créer des automatisations:

```yaml
# Example automation
automation:
  - alias: Alert temperature
    trigger:
      platform: numeric_state
      entity_id: sensor.vmi_temperature
      above: 28
    action:
      - service: notify.telegram
        data:
          message: "VMI temp too high: {{ states.sensor.vmi_temperature.state }}°C"
```

### Accès via Mobile

```
http://<ip-homeassistant>:5000
```

## Mise à Jour

L'addon se met à jour automatiquement quand une nouvelle version est disponible.

Pour forcer une vérification:
```bash
ha addons update
ha addon update ventilairsec-vmi
```

## Sauvegarde & Restauration

### Sauvegarde

Home Assistant sauvegarde automatiquement:
- Configuration: `/config/ventilairsec/config.json`
- Base de données: `/config/ventilairsec/db/ventilairsec.db`
- Logs: `/config/ventilairsec/logs/`

### Restaurer après réinstallation

```bash
# Les fichiers sont dans le répertoire config
# Ils seront automatiquement restaurés
```

## Support & Documentation

- **Documentation Complète**: [README.md](README.md)
- **Documentation Technique**: [TECHNICAL.md](TECHNICAL.md)
- **Pour Développeurs**: [DEVELOPER.md](DEVELOPER.md)
- **Issues & Bug Reports**: https://github.com/fortinric88/HA-VMI/issues

## FAQ

**Q: Peut-on l'utiliser sans Home Assistant?**
R: Non, c'est conçu spécifiquement pour Home Assistant.

**Q: Combien de devices peuvent être supportés?**
R: Jusqu'à 50-100 appareils EnOcean peuvent être détectés.

**Q: Les données sont-elles chiffrées?**
R: Non, utilisez un VPN/firewall pour la sécurité.

**Q: L'addon peut-il envoyer des commandes à la VMI?**
R: V2.0+ supportera les commandes bidirectionnelles.

## License

AGPL-3.0 - Voici le texte complet de la license.

---

**Premiers pas reussis?** 🎉 Félicitations! Consultez la [documentation complète](README.md) pour plus de fonctionnalités.
