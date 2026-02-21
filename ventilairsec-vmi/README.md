# Ventilairsec VMI Monitor pour Home Assistant

Un addon Home Assistant pour monitorer votre Ventilairsec Purevent VMI via un module EnOcean GPIO raccordé à un Raspberry Pi.

## Fonctionnalités

- 📡 Communication directe avec la VMI via module EnOcean (protocole radio)
- 📊 Historique des données avec base de données SQLite
- 🎨 Dashboard web pour visualiser les données en temps réel
- 🌡️ Support des capteurs externes (CO2, Humidité-Température)
- 🔧 Configuration simple via interface Home Assistant

## Appareils Supportés

### Principaux
- **VMI Purevent** (D1079-01-00) - Échange de chaleur et ventilation
- **Assistant Ventilairsec** (D1079-00-00) - Boîtier de commande

### Capteurs
- **Capteur CO2** (A5-09-04)
- **Capteur Humidité-Température** (A5-04-01)

## Installation

### Prérequis
- Raspberry Pi 3B+ ou supérieur
- Module EnOcean GPIO (ex: TCM-515, USB300)
- Ventilairsec Purevent VMI
- Home Assistant 2024.1.0 ou supérieur

### Étapes

1. **Ajouter le dépôt de l'addon**
   - Home Assistant → Paramètres → Systèmes → Magasin d'Addons
   - Ajouter URL personnalisée: `https://github.com/fortinric88/HA-VMI`

2. **Installer l'addon**
   - Chercher "Ventilairsec VMI Monitor"
   - Cliquer sur Installer

3. **Configuration**
   - Port série: `/dev/ttyAMA0` (défaut pour UART GPIO RPi)
   - Niveau de journalisation: `info`
   - Intervalle de mise à jour: `10` secondes

4. **Démarrer l'addon**
   - Cliquer sur "Démarrer"
   - Consulter les journaux pour vérifier l'initialisation

## Utilisation

### Accès au Dashboard
- URL: `http://homeassistant:5000`
- Affiche les données en temps réel synchronisées avec Home Assistant

### Données Disponibles

#### VMI Purevent
- Température extérieure
- Mode de fonctionnement
- État du chauffage
- Débit d'air
- Puissance de chauffage
- État des capteurs QAI
- Codes d'erreur

#### Capteurs
- Humidité relative (%)
- Température (°C)
- Niveau CO2 (ppm)

## Fichier de Configuration

Location: `/config/ventilairsec/config.json`

```json
{
  "serial_port": "/dev/ttyAMA0",
  "log_level": "info",
  "update_interval": 10,
  "devices": {
    "vmi": {
      "id": "0x0421574F",
      "name": "VMI Purevent",
      "type": "d1079-01-00"
    },
    "assistant": {
      "id": "0x0422407D",
      "name": "Assistant Ventilairsec",
      "type": "d1079-00-00"
    }
  }
}
```

## Troubleshooting

### Module EnOcean non détecté
```bash
# Vérifier la connexion
ls -la /dev/ttyAMA0

# Vérifier les logs
ha addon log ventilairsec-vmi
```

### Aucune donnée reçue
1. Vérifier l'alimentation du module EnOcean
2. S'assurer que les appareils sont appairés (consulter les logs)
3. Vérifier la portée radio (max ~300m en line-of-sight)

### Données incohérentes
- Attendre le prochain cycle de mise à jour (10s par défaut)
- Vérifier la configuration des appareils dans Jeedom

## Intégration Home Assistant

L'addon expose une API REST supportant:
- Récupération des états actuels
- Historique des données
- Configuration dynamique

L'intégration MQTT (optionnelle) peut être activée pour créer des entités Home Assistant natives.

## Support et Documentation

- [Documentation Enocean](https://www.enocean.com/)
- [GitHub Issue Tracker](https://github.com/fortinric88/HA-VMI/issues)

## License

AGPL-3.0

## Auteur

Basé sur les plugins Jeedom Ventilairsec et OpenEnocean
