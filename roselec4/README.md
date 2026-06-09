# ⚡ ROSELEC v1.2
**Schémas de coffrets électriques — AC + DC/Rectifier — Claude Vision**
*MTN Congo Zone Sud · ROSMS1 · Accès libre · Partage WhatsApp*

---

## Accès — zéro friction

Ouvrir l'application → taper son nom → accès immédiat.
**Superviseur :** taper `Rosly` → vue de tous les schémas de l'équipe.

---

## Partage des schémas

### Bouton "📲 Rapport WhatsApp" dans l'éditeur

1. Finir le schéma
2. Cliquer **📲 Rapport WhatsApp** dans la barre
3. Remplir : nom technicien, site, type de travail, observations
4. Cliquer **Exporter image + ouvrir WhatsApp** :
   - L'image PNG du schéma se télécharge automatiquement
   - WhatsApp s'ouvre avec le rapport pré-rédigé
5. Dans WhatsApp : joindre l'image téléchargée + envoyer dans le groupe

### Format du rapport WhatsApp automatique

```
⚡ ROSELEC — Rapport de site
━━━━━━━━━━━━━━━━━━━━
👷 Technicien : Hilario
📍 Site : DOLISIE4
📅 Date : 09/06/2025 à 14:30
🔧 Travail : Schématisation coffret électrique
⚙️ Mode schéma : AC / BT
━━━━━━━━━━━━━━━━━━━━
📊 Composants schématisés : 8
  • Disj. 2P (×2)
  • Disj. 1P (×4)
  • Diff. 2P
  • Terre PE
🔌 Fils câblés : 12
━━━━━━━━━━━━━━━━━━━━
📝 Observations :
Disjoncteur général à remplacer (suspect)
━━━━━━━━━━━━━━━━━━━━
Schéma généré avec ROSELEC · MTN Congo Zone Sud
```

---

## Déploiement — 3 étapes

### 1. Supabase — SQL Editor

```sql
CREATE TABLE schemas (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_name   text NOT NULL,
  title        text NOT NULL DEFAULT 'Schéma sans titre',
  site         text DEFAULT '',
  type         text DEFAULT 'ac',
  content      text NOT NULL DEFAULT '{}',
  created_at   timestamptz DEFAULT now(),
  updated_at   timestamptz DEFAULT now()
);
ALTER TABLE schemas DISABLE ROW LEVEL SECURITY;
```

### 2. GitHub

```bash
git init && git add .
git commit -m "ROSELEC v1.2"
git remote add origin https://github.com/ROSMS1/roselec.git
git push -u origin main
```

### 3. Streamlit Cloud — Secrets

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
SUPABASE_URL      = "https://xxxx.supabase.co"
SUPABASE_ANON_KEY = "eyJ..."
```

---

## Structure

```
roselec/
├── app.py                  → Application principale (accès libre)
├── analyzer.py             → Claude Vision (AC / DC / Auto)
├── db.py                   → Supabase (stockage schémas)
├── components/
│   └── editor.html         → Éditeur SVG + Rapport WhatsApp
├── requirements.txt
└── .streamlit/
    ├── config.toml
    └── secrets.toml.template
```

---
*ROSELEC v1.2 · ROS + ELEC · MTN Congo Zone Sud*
