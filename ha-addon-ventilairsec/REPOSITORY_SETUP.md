# Home Assistant Repository Configuration

Pour ajouter cet addon à la boutique d'addons Home Assistant, il faut créer un repository conforme.

## Structure du Repository

```
HA-VMI/                          # Root du repository HA
├── ha-addon-ventilairsec/       # Dossier de l'addon (ce dossier)
│   ├── addon.json
│   ├── Dockerfile
│   ├── run.sh
│   ├── requirements.txt
│   ├── repository.json
│   ├── README.md
│   ├── TECHNICAL.md
│   ├── DEVELOPER.md
│   ├── QUICKSTART.md
│   └── rootfs/
│       ├── install.sh
│       └── app/
│           ├── main.py
│           ├── enocean_handler.py
│           ├── data_parser.py
│           ├── database.py
│           ├── config.default.json
│           ├── __init__.py
│           ├── templates/
│           │   └── index.html
│           └── static/
│               ├── css/
│               │   └── style.css
│               └── js/
│                   ├── api.js
│                   ├── dashboard.js
│                   └── main.js
└── .github/
    └── workflows/
        └── build.yml           # CI/CD pour tester les builds
```

## Configuration du Repository Home Assistant

### Fichier addon.json

Le fichier [addon.json](addon.json) définit les métadonnées de l'addon.

Éléments essentiels:
- `id`: Identifiant unique en minuscules avec tirets
- `name`: Nom lisible
- `version`: Format semver (MAJOR.MINOR.PATCH)
- `slug`: Identifiant court pour l'URL
- `arch`: Architectures supportées
- `homeassistant`: Version minimale requise
- `ports`: Ports exposés
- `devices`: Périphériques requis

### Fichier repository.json

Le fichier [repository.json](repository.json) contient les métadonnées du repository.

### Structure Dockerfile

Le [Dockerfile](Dockerfile):
- Utilise l'image de base Home Assistant appropriée (armv7, arm64, amd64)
- Installe les dépendances système
- Installe les dépendances Python via pip
- Copie le code de l'addon

### Script run.sh

Le [run.sh](run.sh):
- Préparation des répertoires
- Chargement de la configuration
- Lancement de l'application principale

## Ajouter le Repository à Home Assistant

### Via l'Interface Web

1. **Ouvrir Home Assistant**
   - URL: `http://<ip>:8123`

2. **Naviguer vers**
   - Paramètres (Gear icon) → Systèmes → Add-ons Store (coin inférieur droit)

3. **Ajouter le repository**
   - Bouton ⋮ (menu) → "Dépôts personnalisés"
   - Coller: `https://github.com/fortinric88/HA-VMI`
   - Cliquer "Créer"

4. **Chercher l'addon**
   - Le repository apparaîtra dans la liste
   - Chercher "Ventilairsec VMI Monitor"
   - Installer normalement

### Via ligne de commande

```bash
# SSH sur Home Assistant
ssh root@<ip>

# Ajouter le repository
curl -X POST http://localhost:5000/api/addons/repository/add \
  -H "Content-Type: application/json" \
  -d '{"repository": "https://github.com/fortinric88/HA-VMI"}'
```

## Build local pour tester

```bash
# 1. Cloner le repo
git clone https://github.com/fortinric88/HA-VMI.git
cd HA-VMI/ha-addon-ventilairsec

# 2. Build l'image
docker build -t ventilairsec-vmi:latest .

# 3. Tester localement
docker run \
    -p 5000:5000 \
    -v ~/addon-test:/config \
    --device /dev/ttyAMA0 \
    ventilairsec-vmi:latest
```

## Validation du Repository

Home Assistant vérifie automatiquement:

1. ✅ Structure des fichiers
2. ✅ Validité du JSON (addon.json)
3. ✅ Disponibilité des images Docker
4. ✅ Licences compatibles (AGPL-3.0 ✓)
5. ✅ Documentations requises

## Fichiers Requis pour Certification

Pour que l'addon soit certifié par Home Assistant:

- ✅ `addon.json` - Configuration de l'addon
- ✅ `Dockerfile` - Image conteneur
- ✅ `run.sh` - Point d'entrée
- ✅ `requirements.txt` - Dépendances Python
- ✅ `README.md` - Documentation utilisateur
- ✅ Icônes (optionnel mais recommandé)

## Prochaines Étapes

1. **Tester localement** - Assurer que tout fonctionne
2. **Documentation** - Compléter les guides
3. **Soumettre** - Créer une Pull Request vers Home Assistant Add-ons
4. **Publicité** - Partager sur les forums Home Assistant

## Ressources

- [Home Assistant Add-on Development Documentation](https://developers.home-assistant.io/docs/add-ons)
- [Add-on Configuration Reference](https://developers.home-assistant.io/docs/add-ons/configuration/)
- [Docker Best Practices for Home Assistant](https://developers.home-assistant.io/docs/add-ons/tutorial_python/)
- [Home Assistant Community Forums](https://community.home-assistant.io/)

## Support

Pour les questions relatives au repository:
- Créer une [Issue GitHub](https://github.com/fortinric88/HA-VMI/issues)
- Contacter via GitHub Discussions

---

**Note**: Ce repository est compatible avec Home Assistant 2024.1.0 et supérieur.
