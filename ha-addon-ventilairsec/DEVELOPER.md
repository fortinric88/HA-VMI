# Guide d'Intégration de l'Addon Ventilairsec VMI

## Pour les développeurs Home Assistant

### Structure du Repository

```
ha-addon-ventilairsec/
├── addon.json                    # Manifest d'addon
├── Dockerfile                    # Image conteneur
├── requirements.txt              # Dépendances Python
├── run.sh                        # Script de démarrage
├── README.md                     # Documentation utilisateur
├── TECHNICAL.md                  # Documentation technique
├── DEVELOPER.md                  # Ce fichier
└── rootfs/
    └── app/
        ├── main.py              # Application principale (Flask)
        ├── enocean_handler.py   # Gestion EnOcean
        ├── data_parser.py       # Parsing messages
        ├── database.py          # Gestion SQLite
        ├── config.default.json  # Configuration par défaut
        ├── templates/
        │   └── index.html       # Frontend Web
        └── static/
            ├── css/
            │   └── style.css
            └── js/
                ├── api.js
                ├── dashboard.js
                └── main.js
```

### Installation en Mode Développement

```bash
# 1. Cloner le repo
git clone https://github.com/fortinric88/HA-VMI.git
cd ha-addon-ventilairsec

# 2. Installer les dépendances Python
pip install -r requirements.txt

# 3. Configuration locale
cp rootfs/app/config.default.json ~/app_config.json

# 4. Lancer localement
python rootfs/app/main.py \
    --config ~/app_config.json \
    --db ~/vmi_db \
    --logs ~/vmi_logs
```

### Modifier le code

#### 1. Ajouter un nouvel endpoint API

**Fichier**: `rootfs/app/main.py`

```python
@app.route('/api/custom-endpoint', methods=['GET', 'POST'])
def custom_endpoint():
    """Description de l'endpoint"""
    try:
        # Votre logique
        return jsonify({'result': 'success'})
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500
```

#### 2. Ajouter la support d'un nouvel appareil EnOcean

**Fichier**: `rootfs/app/data_parser.py`

```python
# Ajouter le type à DEVICE_TYPES
DEVICE_TYPES = {
    ...
    'new-type-code': 'New Device Name'
}

# Ajouter la logique de parsing dans parse()
elif device_type == 'new-type-code':
    return self._parse_new_device(sender_id, data, raw_data)

# Implémenter le parser spécifique
def _parse_new_device(self, sender_id, data, raw_data):
    parsed = {
        'device_id': sender_id,
        'device_type': 'new-type-code',
        'device_name': 'New Device',
        'timestamp': datetime.now().isoformat()
    }
    
    # Votre logique de décodage des données
    # Basée sur la spécification EnOcean
    
    return parsed
```

#### 3. Modifier le frontend Web

**Fichier**: `rootfs/app/templates/index.html`

Les fichiers statiques sont servis depuis `/static/`. Modifiez:
- `static/css/style.css` - styles
- `static/js/api.js` - appels API
- `static/js/dashboard.js` - logique tableau de bord
- `static/js/main.js` - initialisation

#### 4. Ajouter une nouvelle table à la base de données

**Fichier**: `rootfs/app/database.py`

```python
def _create_tables(self):
    # ... code existant ...
    
    # Nouvelle table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS my_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    self.connection.commit()
```

### Testing

#### Test unitaire (EnOcean parsing)

```python
# test_parser.py
from data_parser import DataParser

config = {
    'devices': {
        'vmi': {'id': '0x0421574F', 'type': 'd1079-01-00'}
    }
}

parser = DataParser(config)

# Test données VMI
test_data = {
    'sender_id': '0x0421574F',
    'rorg': 0xD1079,
    'data': [0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0]
}

result = parser.parse(test_data)
assert result is not None
assert result['device_type'] == 'd1079-01-00'
```

#### Test API manuelle

```bash
# Health check
curl http://localhost:5000/api/health

# Lister appareils
curl http://localhost:5000/api/devices

# Lire données actuelles
curl http://localhost:5000/api/current

# Historique (24h)
curl http://localhost:5000/api/history/0x0421574F?hours=24
```

### Processus de contribution

1. **Fork** le repository
2. **Créer une branch** (`git checkout -b feature/mon-feature`)
3. **Commits** avec messages clairs
4. **Push** vers votre fork
5. **Pull Request** avec description détaillée

### Guidelines de Code

- **Python**: PEP 8, docstrings pour les fonctions
- **JavaScript**: camelCase, commentaires sur les blocs complexes
- **Variables**: noms explicites en anglais dans le code, labels en français dans l'UI

### Documentation

- Mettre à jour README.md pour les changements utilisateurs
- Mettre à jour TECHNICAL.md pour l'architecture
- Ajouter des docstrings en français pour le code critique

### Format de Commit

```
[type]: description courte

Description détaillée si nécessaire.

Types: feat|fix|docs|test|refactor|perf|style|build
```

Exemples:
```
feat: add CO2 sensor support
fix: correct temperature parsing for VMI
docs: update installation instructions
```

### Build et Publication

```bash
# Build l'image Docker manuellement
docker build -t ventilairsec-vmi:1.0.0 .

# Tester le build
docker run \
    --device /dev/ttyAMA0 \
    -p 5000:5000 \
    -v /config:/config \
    ventilairsec-vmi:1.0.0

# Publication sur Docker Hub (si applicable)
docker tag ventilairsec-vmi:1.0.0 username/ventilairsec-vmi:1.0.0
docker push username/ventilairsec-vmi:1.0.0
```

### Détection de Bugs

Pour reporter un bug, fournir:
1. Version de l'addon
2. Logs (via `ha addon log`)
3. Configuration (sans infos sensibles)
4. Étapes de reproduction

### Ressources Utiles

- [EnOcean Specifications](https://www.enocean.com/)
- [home-assistant/plugin-base](https://github.com/home-assistant/plugin-base)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLite Documentation](https://www.sqlite.org/)
- [Chart.js Documentation](https://www.chartjs.org/)

## Roadmap

### V1.0 (Actuel)
- ✅ Communication EnOcean basique
- ✅ Support VMI Purevent
- ✅ Dashboard web
- ✅ Historique SQLite

### V1.1 (Prévue)
- [ ] Intégration MQTT natif
- [ ] Notifications d'erreurs
- [ ] Export de données
- [ ] Amélioration UI

### V2.0
- [ ] Support profiles EnOcean étendus
- [ ] Webhooks personnalisés
- [ ] API GraphQL
- [ ] Mobile app

---

**Questions?** Consultez les [Issues GitHub](https://github.com/fortinric88/HA-VMI/issues) ou créez une nouvelle issue.
