"""
ROSELEC — Module Claude Vision
Modes : AC (coffrets BT), DC/Rectifier (48V télécom), Auto
"""
import anthropic
import base64
import json
from io import BytesIO
from PIL import Image
import streamlit as st

SYSTEM = """Tu es un expert en électricité industrielle et systèmes d'énergie télécom.
Tu analyses des photos de coffrets électriques et d'armoires DC 48V.
Réponds UNIQUEMENT avec du JSON valide, sans markdown, sans commentaire."""

PROMPT_AC = """Analyse ces photos de coffret / tableau électrique BT (230V/400V AC).
Identifie chaque composant visible :
Types : disj1p, disj2p, disj3p, diff2p, fusible, contacteur, relais,
  parafoudre, inter, prise, voyant, terre, bornier, compteur

Retourne :
{
  "mode": "ac",
  "coffret": {
    "type": "tableau_distribution|armoire_basse_tension|autre",
    "tension": "230V|400V",
    "observations": "état général"
  },
  "composants": [
    {
      "type": "disj2p",
      "label": "Disjoncteur Général",
      "amperage": "63A",
      "poles": 2,
      "marque": "Schneider",
      "ref": "iC60N",
      "etat": "ok",
      "position": "rangée 1"
    }
  ]
}"""

PROMPT_DC = """Analyse ces photos d'un système DC 48V télécom
(armoire rectifier, rack batterie, baie DC, coffret distribution DC).

Types : rectifier, battery_string, controller, fuse_dc, mcb_dc,
  barre_dc, shunt, lvc, pdu_dc, surge_dc, load_output

Retourne :
{
  "mode": "dc",
  "systeme": {
    "type": "armoire_rectifier|rack_batterie|baie_dc|coffret_distribution_dc",
    "tension_nominale": "-48V|+48V|24V",
    "capacite_totale": "ex: 6x50A=300A",
    "autonomie_estimee": "ex: 4h",
    "observations": "état général, alarmes"
  },
  "composants": [
    {
      "type": "rectifier",
      "label": "Rectifier R4850G5 #1",
      "valeur": "48V/50A",
      "marque": "Huawei",
      "ref": "R4850G5",
      "etat": "ok",
      "position": "slot 1"
    }
  ]
}"""

PROMPT_AUTO = """Analyse ces photos d'équipement électrique.
Détermine si c'est AC (coffret BT) ou DC (armoire rectifier 48V télécom).
Retourne le JSON selon le mode détecté :
- AC : {"mode":"ac","coffret":{...},"composants":[...]}
- DC : {"mode":"dc","systeme":{...},"composants":[...]}
Identifie tous les composants avec le maximum de détails."""


def _to_b64(img: Image.Image) -> str:
    buf = BytesIO()
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def analyze(images: list, mode: str = "auto") -> dict:
    if not images:
        return {"error": "Aucune image fournie."}
    key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not key:
        return {"error": "Clé API non configurée (st.secrets)."}

    prompt = {"ac": PROMPT_AC, "dc": PROMPT_DC}.get(mode, PROMPT_AUTO)
    client = anthropic.Anthropic(api_key=key)

    content = [
        {"type": "image", "source": {
            "type": "base64", "media_type": "image/jpeg",
            "data": _to_b64(img)
        }} for img in images[:4]
    ]
    content.append({"type": "text", "text": prompt})

    try:
        resp = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2000,
            system=SYSTEM,
            messages=[{"role": "user", "content": content}],
        )
        raw = resp.content[0].text.strip().replace("```json","").replace("```","").strip()
        return json.loads(raw)
    except json.JSONDecodeError as e:
        return {"error": f"Réponse non parsable : {e}"}
    except anthropic.APIError as e:
        return {"error": f"Erreur API Claude : {e}"}
    except Exception as e:
        return {"error": f"Erreur : {e}"}
