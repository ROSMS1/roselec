"""
ROSELEC — Module Supabase
Stockage des schémas sans Auth complexe.
Le technicien choisit son nom au login → utilisé comme owner_name.
"""
import streamlit as st
from supabase import create_client, Client
import json
from datetime import datetime


@st.cache_resource
def get_db() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_ANON_KEY"],
    )


# ── SQL À EXÉCUTER UNE FOIS DANS SUPABASE ──────────────────────────────────
# CREATE TABLE schemas (
#   id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
#   owner_name   text NOT NULL,          -- nom du technicien (ex: "Hilario")
#   title        text NOT NULL DEFAULT 'Schéma sans titre',
#   site         text DEFAULT '',
#   type         text DEFAULT 'ac',      -- ac | dc
#   content      text NOT NULL DEFAULT '{}',
#   created_at   timestamptz DEFAULT now(),
#   updated_at   timestamptz DEFAULT now()
# );
# -- Pas de RLS : accès public en lecture/écriture (protégé par le login partagé)
# ALTER TABLE schemas DISABLE ROW LEVEL SECURITY;

def save_schema(owner: str, data: dict) -> dict:
    try:
        db = get_db()
        payload = {
            "owner_name": owner,
            "title":      data.get("title", "Schéma sans titre"),
            "site":       data.get("site", ""),
            "type":       data.get("type", "ac"),
            "content":    json.dumps(data.get("content", {})),
            "updated_at": datetime.utcnow().isoformat(),
        }
        sid = data.get("id")
        if sid:
            res = db.table("schemas").update(payload).eq("id", sid).execute()
        else:
            res = db.table("schemas").insert(payload).execute()
        return {"ok": True, "data": res.data[0] if res.data else {}}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def list_schemas(owner: str) -> list:
    try:
        res = (get_db().table("schemas")
               .select("id,title,site,type,updated_at,owner_name")
               .eq("owner_name", owner)
               .order("updated_at", desc=True)
               .execute())
        return res.data or []
    except Exception:
        return []


def list_all_schemas() -> list:
    """Vue superviseur — tous les schémas de tous les techniciens."""
    try:
        res = (get_db().table("schemas")
               .select("id,title,site,type,updated_at,owner_name")
               .order("updated_at", desc=True)
               .limit(100)
               .execute())
        return res.data or []
    except Exception:
        return []


def load_schema(sid: str) -> dict:
    try:
        res = get_db().table("schemas").select("*").eq("id", sid).single().execute()
        data = res.data
        if data:
            data["content"] = json.loads(data.get("content", "{}"))
        return data or {}
    except Exception:
        return {}


def delete_schema(sid: str, owner: str) -> bool:
    try:
        get_db().table("schemas").delete().eq("id", sid).eq("owner_name", owner).execute()
        return True
    except Exception:
        return False
