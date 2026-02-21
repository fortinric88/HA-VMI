# Documentation technique de l'addon Ventilairsec VMI

## Architecture Générale

```
┌─────────────────────────────────────────────────────────┐
│           Home Assistant Container                       │
├─────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────┐ │
│  │        Ventilairsec VMI Monitor Addon              │ │
│  │ ┌────────────────────────────────────────────────┐ │ │
│  │ │ main.py                                        │ │ │
│  │ │  - Application Flask                           │ │ │
│  │ │  - Gestion des threads                         │ │ │
│  │ │  - API REST                                    │ │ │
│  │ └────────────────────────────────────────────────┘ │ │
│  │ ┌────────────────────────────────────────────────┐ │ │
│  │ │ enocean_handler.py                             │ │ │
│  │ │  - Communication série via /dev/ttyAMA0        │ │ │
│  │ │  - Décodage des paquets EnOcean                │ │ │
│  │ │  - Thread de réception                         │ │ │
│  │ └────────────────────────────────────────────────┘ │ │
│  │ ┌────────────────────────────────────────────────┐ │ │
│  │ │ data_parser.py                                 │ │ │
│  │ │  - Parsing des messages EnOcean                │ │ │
│  │ │  - Décodage VMI Purevent                       │ │ │
│  │ │  - Décodage capteurs (CO2, Temp/Humidité)     │ │ │
│  │ └────────────────────────────────────────────────┘ │ │
│  │ ┌────────────────────────────────────────────────┐ │ │
│  │ │ database.py                                    │ │ │
│  │ │  - Gestion SQLite                              │ │ │
│  │ │  - Stockage historique                         │ │ │
│  │ │  - Requêtes/Statistiques                       │ │ │
│  │ └────────────────────────────────────────────────┘ │ │
│  │ ┌────────────────────────────────────────────────┐ │ │
│  │ │ Dossier: templates/ static/                    │ │ │
│  │ │  - Interface web (HTML, CSS, JS)               │ │ │
│  │ │  - Dashboard et graphiques                     │ │ │
│  │ └────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────┘ │
│              ▲                           ▲              │
└──────────────┼───────────────────────────┼──────────────┘
               │                           │
               │ (Port 5000)               │ (/dev/ttyAMA0)
               │ HTTP/WebSocket            │ Série EnOcean
               ▼                           ▼
        ┌─────────────┐          ┌──────────────────┐
        │   Client    │          │ Module EnOcean   │
        │   Web       │          │   GPIO USB/UART  │
        └─────────────┘          └──────────────────┘
                                       │
                                       │ Radiofréquence
                                       ▼
                               ┌────────────────────┐
                               │ VMI Purevent       │
                               │ + Capteurs EnOcean │
                               └────────────────────┘
```

## Protocole EnOcean

### Format des paquets
- **Standard**: Profile 4BS (42 bits) - Télémétrie
- **Spécialité**: D1079-01-00 (VMI Purevent)
- **Détection**: Auto-détection par RORG + FUNC + TYPE

### Appareils Supportés

#### VMI Purevent (D1079-01-00)
- **Adresse**: 0x0421574F
- **RORG**: 0xD1079
- **Fonction**: 0x01
- **Type**: 0x00
- **Données**: Télémétrie temps réel sur 8 octets + status

**Champs informatifs**:
- Température extérieure (°C)
- Mode de fonctionnement (numérique)
- État système
- Puissance de chauffage (%)
- Débit d'air (m³/h)
- Codes d'erreur

#### Assistant Ventilairsec (D1079-00-00)
- **Adresse**: 0x0422407D
- **RORG**: 0xD1079
- **Fonction**: 0x00
- **Type**: 0x00
- **Rôle**: Commande et affichage local

#### Capteur CO2 (A5-09-04)
- **Adresse**: 0x81003227
- **RORG**: 0xA5
- **Format**: 4 octets
- **Plage**: 0-2500 ppm

#### Capteur Température/Humidité (A5-04-01)
- **Adresse**: 0x810054F5
- **RORG**: 0xA5
- **Format**: 4 octets
- **Température**: -20°C à +60°C
- **Humidité**: 0-100%

## Base de Données

### Schéma SQLite

```sql
-- Table des lectures
CREATE TABLE readings (
    id INTEGER PRIMARY KEY,
    device_id TEXT NOT NULL,           -- ID EnOcean (hex)
    device_type TEXT,                  -- Type d'appareil
    device_name TEXT,                  -- Nom convivial
    metric_name TEXT,                  -- Nom de la métrique
    metric_value REAL,                 -- Valeur numérique
    metric_unit TEXT,                  -- Unité
    raw_data TEXT,                     -- Données brutes
    timestamp DATETIME,                -- Moment de la lecture
    recorded_at DATETIME DEFAULT NOW   -- Enregistré à
);

-- Table des appareils connus
CREATE TABLE devices (
    id TEXT PRIMARY KEY,               -- ID EnOcean
    name TEXT,                         -- Nom
    type TEXT,                         -- Type
    last_seen DATETIME,                -- Dernière activité
    status TEXT                        -- online/offline
);

-- Table des paramètres
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
```

### Performances
- Index sur (device_id, timestamp) pour requêtes rapides
- Rétention par défaut: 30 jours
- Nettoyage automatique des données anciennes

## API REST

### Endpoints

#### Health Check
```
GET /api/health
Response: { status, timestamp, enocean_connected }
```

#### Liste des appareils
```
GET /api/devices
Response: [{ id, name, type }, ...]
```

#### Lectures actuelles
```
GET /api/current
Response: { device_id: { name, type, last_update, metrics }, ... }
```

#### Historique device
```
GET /api/history/{device_id}?hours=24
Response: [{ timestamp, metric_name, metric_value }, ...]
```

#### Historique métrique
```
GET /api/reading/{device_id}/{metric}?hours=24
Response: [{ timestamp, value }, ...]
```

## Configuration

### Fichier config.json

```json
{
  "serial_port": "/dev/ttyAMA0",
  "log_level": "info",
  "update_interval": 10,
  "web_port": 5000,
  "devices": {
    "vmi": {
      "id": "0x0421574F",
      "name": "VMI Purevent",
      "type": "d1079-01-00",
      "enabled": true
    },
    "sensors": [
      {
        "id": "0x81003227",
        "name": "Capteur CO2",
        "type": "a5-09-04",
        "enabled": true
      }
    ]
  }
}
```

## Flux de Données

1. **Réception** (EnOceanHandler)
   - Écoute sur /dev/ttyAMA0 (57600 baud)
   - Accumule les paquets dans une queue thread-safe

2. **Traitement** (DataParser)
   - Identifie le type d'appareil via sender_id
   - Applique le parsing spécifique au type
   - Retourne une structure JSON normalisée

3. **Stockage** (Database)
   - Insère dans SQLite
   - Met à jour le statut de l'appareil
   - Indexe par timestamp

4. **API REST** (main.py)
   - Exécute les requêtes GET basées sur des plages horaires
   - Calcule les statistiques min/max/avg
   - Retourne JSON pour le frontend

5. **Affichage** (Interface Web)
   - Graphiques Chart.js avec historique 24h
   - Cards en temps réel
   - Statistiques et alertes

## Développement

### Ajouter un nouvel appareil EnOcean

1. Dans `config.default.json`, ajouter l'appareil avec son ID et type
2. Dans `data_parser.py`, ajouter une méthode `_parse_<type>` 
3. Implémenter le décodage spécifique au protocole EnOcean
4. Retourner un dict avec `device_id`, `device_type`, `device_name` et les métriques

### Exemple: Ajouter un capteur de mouvement (F6-02-01)

```python
def _parse_motion_sensor(self, sender_id, data, raw_data):
    parsed = {
        'device_id': sender_id,
        'device_type': 'f6-02-01',
        'device_name': 'Motion Sensor',
        'timestamp': datetime.now().isoformat()
    }
    
    # F6-02-01: 1 octet, bit 7 = motion
    if len(data) >= 1:
        motion = (data[0] >> 7) & 1
        parsed['motion_detected'] = bool(motion)
    
    return parsed
```

## Logging

- **Fichier**: `/config/ventilairsec/logs/`
- **Niveaux**: debug, info, warning, error
- **Format**: `timestamp - module - level - message`

## Performance & Ressources

- **Mémoire**: ~50-100 MB en fonctionnement
- **CPU**: <1% (inactif), <5% pendant traitement
- **Disque**: ~1-2 MB par jour de données (24h)
- **Bande passante**: <1 Kbps (EnOcean), ~100 Kbps (Web)

## Sécurité

- Pas d'authentification par défaut (localhost seulement)
- CORS activé pour la même origine
- Validation des entrées sur les paramètres API
- Pas de stockage de sensibles (identifiants, tokens)

## Troubleshooting

### Module EnOcean non détecté
```bash
# Vérifier le port
ls -la /dev/ttyAMA0

# Tester la connection
stty -F /dev/ttyAMA0
```

### Pas de données reçues
- Vérifier l'alimentation du module
- Vérifier l'appairage des appareils
- Consulter les logs: `ha addon log ventilairsec-vmi` 

### Performance lente
- Vérifier la taille de la base de données
- Exécuter le nettoyage `POST /api/cleanup`
- Réduire le nombre d'appareils

## Prochains développements possibles

- [ ] Intégration MQTT pour Home Assistant
- [ ] Support ENO profiles supplémentaires (capteurs additionnels)
- [ ] Webhooks pour notifications
- [ ] Export CSV/GraphQL
- [ ] Graphiques web avancés (D3.js)
- [ ] Machine Learning pour prédictions
