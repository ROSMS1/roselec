"""
ROSELEC v1.1 — app.py corrigé
"""

import streamlit as st
import streamlit.components.v1 as stc
from pathlib import Path
from PIL import Image
import json, io

EDITOR_HTML = Path(__file__).parent / "components" / "editor.html"
AUDIT_HTML  = Path(__file__).parent / "components" / "audit.html"

st.set_page_config(
    page_title="ROSELEC — Schémas électriques",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SUPERVISOR_NAME = "Rosly"

st.markdown("""
<style>
#MainMenu,header,footer{visibility:hidden}
.block-container{padding:0 !important;max-width:100% !important}
.stApp{background:#f4f6f9}
.re-header{background:#1565C0;padding:12px 24px;display:flex;align-items:center;gap:14px}
.re-logo{font-size:24px;font-weight:800;color:#fff;letter-spacing:-.5px;line-height:1}
.re-logo span{color:#FFC107}
.re-tagline{font-size:12px;color:rgba(255,255,255,.7);line-height:1.3}
.re-user{margin-left:auto;background:rgba(255,255,255,.15);border-radius:20px;
  padding:4px 14px;font-size:13px;color:#fff;font-weight:500}
.welcome-wrap{max-width:380px;margin:80px auto;background:#fff;
  border-radius:16px;padding:36px;border:1px solid #dde3ec;
  box-shadow:0 8px 32px rgba(21,101,192,.08);text-align:center}
.wlogo{font-size:40px;font-weight:800;color:#1565C0;letter-spacing:-.5px;margin-bottom:4px}
.wlogo span{color:#FFC107}
.wsub{font-size:12px;color:#999;margin-bottom:28px}
.stButton>button{border-radius:8px !important;font-size:13px !important}
</style>
""", unsafe_allow_html=True)


def show_welcome():
    st.markdown("""
    <div class="welcome-wrap">
      <div class="wlogo">ROS<span>ELEC</span></div>
      <div class="wsub">Schémas de coffrets électriques · MTN Congo Zone Sud</div>
    </div>
    """, unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        name = st.text_input("Votre nom", placeholder="Ex : Hilario, Christ, Elvis…", max_chars=40)
        if st.button("Accéder à l'application →", type="primary", use_container_width=True):
            if not name.strip():
                st.error("Saisir votre nom pour continuer.")
            else:
                st.session_state["tech_name"] = name.strip()
                st.rerun()
        st.markdown(
            "<p style='font-size:11px;color:#ccc;margin-top:12px'>"
            "Aucun mot de passe requis · Vos schémas sont sauvegardés sous votre nom</p>",
            unsafe_allow_html=True,
        )


if "tech_name" not in st.session_state:
    show_welcome()
    st.stop()

tech_name = st.session_state["tech_name"]
is_super  = tech_name.strip().lower() == SUPERVISOR_NAME.lower()

st.markdown(f"""
<div class="re-header">
  <div>
    <div class="re-logo">ROS<span>ELEC</span></div>
    <div class="re-tagline">Schémas de coffrets électriques · AC + DC/Rectifier · Claude Vision</div>
  </div>
  <div class="re-user">{'👑' if is_super else '👷'} {tech_name}</div>
</div>
""", unsafe_allow_html=True)

col_ctrl, col_editor = st.columns([1, 3], gap="small")

with col_ctrl:

    if st.button("🔄 Changer de nom", use_container_width=True):
        for k in ["tech_name","ai_result","load_schema","send_ai","pending_inject"]:
            st.session_state.pop(k, None)
        st.rerun()

    st.markdown("---")
    st.markdown("### 📷 Analyser un coffret")

    mode_choice = st.radio("Type",
        ["⚡ AC — Coffret BT", "🔋 DC — Rectifier 48V", "🔍 Auto"],
        horizontal=True, label_visibility="collapsed")
    mode_key = "ac" if "AC" in mode_choice else "dc" if "DC" in mode_choice else "auto"

    uploaded = st.file_uploader("Photos (1 à 4)",
        type=["jpg","jpeg","png","webp"],
        accept_multiple_files=True,
        label_visibility="collapsed")

    if uploaded:
        cols_img = st.columns(min(len(uploaded), 2))
        for i, f in enumerate(uploaded[:4]):
            with cols_img[i % 2]:
                st.image(Image.open(f), use_column_width=True, caption=f.name[:18])

    if st.button("🤖 Analyser avec Claude Vision", type="primary",
                 use_container_width=True, disabled=not uploaded):
        try:
            import analyzer
            with st.spinner("Analyse en cours…"):
                imgs = []
                for f in uploaded[:4]:
                    f.seek(0)
                    imgs.append(Image.open(io.BytesIO(f.read())))
                result = analyzer.analyze(imgs, mode_key)
                st.session_state["ai_result"] = result
                if "error" in result:
                    st.error(f"Erreur : {result['error']}")
                else:
                    n = len(result.get("composants", []))
                    st.success(f"✅ {n} composant(s) détecté(s)")
        except Exception as e:
            st.error(f"Erreur : {e}")

    if "ai_result" in st.session_state:
        res = st.session_state["ai_result"]
        if "error" not in res:
            info = res.get("coffret") or res.get("systeme", {})
            if info:
                is_dc = res.get("mode") == "dc"
                t   = (info.get("type","") or "").replace("_"," ").title()
                v   = info.get("tension_nominale") or info.get("tension","")
                cap = info.get("capacite_totale","")
                obs = info.get("observations","")
                bg  = "#FFF8E1" if is_dc else "#E8F5E9"
                st.markdown(
                    f"<div style='background:{bg};border-radius:7px;padding:9px;"
                    f"font-size:12px;margin:6px 0'>"
                    f"<b>{'🔋' if is_dc else '⚡'} {t}</b> · {v}"
                    f"{'<br>'+cap if cap else ''}"
                    f"{'<br><span style=\"color:#555\">'+obs+'</span>' if obs else ''}"
                    f"</div>", unsafe_allow_html=True)
            for c in res.get("composants", []):
                e_icon = {"ok":"✅","alarme":"⚠️","defaut":"🔴","hs":"❌","suspect":"⚠️"}.get(c.get("etat","ok"),"✅")
                val   = c.get("valeur") or c.get("amperage","")
                parts = [p for p in [val, c.get("marque",""), c.get("ref","")] if p]
                st.markdown(
                    f"{e_icon} **{c.get('label', c.get('type','?'))}**  \n"
                    f"<small style='color:#777'>{' · '.join(parts)}</small>",
                    unsafe_allow_html=True)
            with st.expander("JSON brut", expanded=False):
                st.json(res)
            st.divider()
            if st.button("➡️ Envoyer vers l'éditeur", type="primary", use_container_width=True):
                st.session_state["pending_inject"] = json.dumps(res, ensure_ascii=False)
                st.rerun()

    st.markdown("---")
    st.markdown("### 🗂 Mes schémas")

    try:
        import db as database
        my_schemas = database.list_schemas(tech_name)
    except Exception:
        my_schemas = []

    if my_schemas:
        for s in my_schemas:
            updated = s.get("updated_at","")[:10]
            is_dc_s = s.get("type") == "dc"
            c1, c2  = st.columns([5, 1])
            with c1:
                lbl = (f"{'🔋' if is_dc_s else '⚡'} **{s.get('title','—')}**  \n"
                       f"<small>{s.get('site','')} · {updated}</small>")
                if st.button(lbl, key="load_"+s["id"], use_container_width=True):
                    full = database.load_schema(s["id"])
                    if full:
                        st.session_state["load_schema"] = full
                        st.rerun()
            with c2:
                if st.button("🗑", key="del_"+s["id"]):
                    database.delete_schema(s["id"], tech_name)
                    st.rerun()
    else:
        st.caption("Aucun schéma sauvegardé.")

    if st.button("🔄 Actualiser", use_container_width=True):
        st.rerun()

    if is_super:
        st.markdown("---")
        st.markdown("### 👑 Tous les schémas — équipe")
        try:
            import db as database
            all_s = database.list_all_schemas()
        except Exception:
            all_s = []
        if all_s:
            by_tech: dict = {}
            for s in all_s:
                by_tech.setdefault(s.get("owner_name","?"), []).append(s)
            for owner, slist in sorted(by_tech.items()):
                with st.expander(f"👷 {owner} — {len(slist)} schéma(s)", expanded=False):
                    for s in slist:
                        is_dc_s = s.get("type") == "dc"
                        if st.button(
                            f"{'🔋' if is_dc_s else '⚡'} {s.get('title','—')} · {s.get('site','')}",
                            key="sv_"+s["id"], use_container_width=True):
                            full = database.load_schema(s["id"])
                            if full:
                                st.session_state["load_schema"] = full
                                st.rerun()
        else:
            st.caption("Aucun schéma dans la base.")

    st.markdown("---")
    with st.expander("📖 Guide rapide", expanded=False):
        st.markdown("""
**Workflow :**
1. Charger 1-4 photos → **Analyser**
2. **Envoyer vers l'éditeur**
3. Cliquer les chips pour placer
4. Mode **Fil** `W` → tracer connexions
5. **💾 Sauvegarder**

**Superviseur :** taper `Rosly` → accès global
        """)


# ── COLONNE DROITE — ONGLETS ──────────────────────────────────────────────────
with col_editor:
    tab_editor, tab_audit = st.tabs([
        "⚡ Éditeur de schéma",
        "🔍 Audit — Existant + Correctif",
    ])

    with tab_editor:
        editor_html = EDITOR_HTML.read_text("utf-8")
        inject = ""

        if "pending_inject" in st.session_state:
            payload = st.session_state.pop("pending_inject")
            inject += f"""<script>
            var _att = 0;
            var _tmr = setInterval(function(){{
              _att++;
              var frames = document.querySelectorAll('iframe');
              for(var i=0;i<frames.length;i++){{
                try{{ frames[i].contentWindow.postMessage({{type:'ai_result',payload:{payload}}},'*'); }}catch(e){{}}
              }}
              if(_att>15) clearInterval(_tmr);
            }}, 400);
            </script>"""

        if "load_schema" in st.session_state:
            payload = json.dumps(st.session_state.pop("load_schema"), ensure_ascii=False)
            inject += f"""<script>(function(){{
              var p={payload};
              function s(){{var f=document.querySelector('iframe');
                if(f&&f.contentWindow)f.contentWindow.postMessage({{type:'load_schema',payload:p}},'*');}}
              setTimeout(s,600);setTimeout(s,1500);
            }})();</script>"""

        if inject:
            st.markdown(inject, unsafe_allow_html=True)

        stc.html(editor_html, height=730, scrolling=False)
        st.caption(f"💾 Sauvegarder dans la barre · schémas sous **{tech_name}**")

    with tab_audit:
        st.markdown(
            "<div style='background:#E3F2FD;border-left:4px solid #1565C0;"
            "border-radius:0 6px 6px 0;padding:10px 14px;font-size:13px;margin-bottom:10px'>"
            "<b>🔍 Module Audit</b> — Schéma existant + Schéma correctif côte à côte.<br>"
            "<small style='color:#555'>Utiliser <b>⊕ Copier → Correctif</b> comme point de départ.</small>"
            "</div>", unsafe_allow_html=True)

        if "load_audit" in st.session_state:
            payload = json.dumps(st.session_state.pop("load_audit"), ensure_ascii=False)
            st.markdown(
                f"""<script>(function(){{var p={payload};
                  function s(){{var f=document.querySelectorAll('iframe')[1];
                    if(f&&f.contentWindow)f.contentWindow.postMessage({{type:'load_audit',payload:p}},'*');}}
                  setTimeout(s,800);setTimeout(s,1800);
                }})();</script>""", unsafe_allow_html=True)

        audit_html = AUDIT_HTML.read_text("utf-8")
        stc.html(audit_html, height=760, scrolling=False)
        st.caption("💾 Sauvegarder · 🖼 Exporter PNG · 📲 Rapport WhatsApp")
