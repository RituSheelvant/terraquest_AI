"""
app.py – TerraQuest AI  |  Gamified Nature Exploration & Environmental Action
=============================================================================
Run:  streamlit run app.py
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Page config — must be the very first Streamlit call
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="TerraQuest AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Local modules
# ---------------------------------------------------------------------------

import storage
import missions as mission_lib
from ai_generator import generate_ai_missions, get_provider_status

# ---------------------------------------------------------------------------
# Custom CSS – Forest green / sage / warm cream palette
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap');

  /* ── Global resets ─────────────────────────────────────────────────── */
  html, body, [data-testid="stAppViewContainer"] {
    background: #f5f0e8 !important;
    color: #1a2e1a;
    font-family: 'Inter', sans-serif;
  }
  [data-testid="stHeader"] { background: transparent !important; }
  [data-testid="stSidebar"] { background: #1a3d1a !important; }
  .block-container { padding: 0 !important; max-width: 100% !important; }

  /* ── Variables ──────────────────────────────────────────────────────── */
  :root {
    --forest:    #1e4d1e;
    --forest-mid:#2d6a2d;
    --sage:      #6b9e6b;
    --sage-light:#a8c8a8;
    --cream:     #f5f0e8;
    --warm:      #e8dfc8;
    --earth:     #8b6f47;
    --bark:      #5c4033;
    --sky:       #4a9abe;
    --sun:       #d4a017;
    --text-dark: #1a2e1a;
    --text-mid:  #3d5c3d;
    --shadow:    rgba(30, 77, 30, 0.15);
    --radius:    16px;
    --radius-sm: 10px;
  }

  /* ── Hero section ───────────────────────────────────────────────────── */
  .hero {
    background: linear-gradient(135deg, #1e4d1e 0%, #2d6a2d 40%, #4a7c4a 70%, #6b9e6b 100%);
    padding: 3.5rem 2rem 3rem;
    text-align: center;
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content: "";
    position: absolute; inset: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  }
  .hero-title {
    font-family: 'Outfit', sans-serif;
    font-size: clamp(2rem, 5vw, 3.2rem);
    font-weight: 800;
    color: #f0f7f0;
    margin: 0 0 0.6rem;
    text-shadow: 0 2px 12px rgba(0,0,0,0.3);
    letter-spacing: -0.5px;
  }
  .hero-sub {
    font-size: clamp(1rem, 2.5vw, 1.15rem);
    color: #c8e8c8;
    font-weight: 400;
    max-width: 600px;
    margin: 0 auto 1.6rem;
    line-height: 1.6;
  }
  .hero-badges-row {
    display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;
  }
  .hero-badge {
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 40px;
    color: #e8f5e8;
    font-size: 0.82rem;
    padding: 6px 16px;
    backdrop-filter: blur(8px);
  }

  /* ── Nav tabs ───────────────────────────────────────────────────────── */
  .nav-bar {
    background: #fff;
    border-bottom: 2px solid #d8e8d8;
    display: flex; gap: 0; position: sticky; top: 0; z-index: 100;
    box-shadow: 0 2px 12px rgba(30,77,30,0.08);
  }
  .nav-btn {
    flex: 1; padding: 1rem 0.5rem; text-align: center;
    border: none; background: transparent; cursor: pointer;
    font-family: 'Inter', sans-serif; font-size: 0.9rem; font-weight: 500;
    color: var(--text-mid); transition: all 0.2s;
    border-bottom: 3px solid transparent; margin-bottom: -2px;
  }
  .nav-btn:hover { background: #f0f7f0; color: var(--forest); }
  .nav-btn.active {
    color: var(--forest); border-bottom-color: var(--forest-mid);
    font-weight: 600; background: #f0f7f0;
  }

  /* ── Section containers ─────────────────────────────────────────────── */
  .section-wrap {
    max-width: 1100px; margin: 0 auto;
    padding: 2rem 1.5rem 3rem;
  }
  .section-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.6rem; font-weight: 700;
    color: var(--forest); margin-bottom: 0.3rem;
  }
  .section-sub {
    color: var(--text-mid); margin-bottom: 1.8rem; font-size: 0.95rem;
  }

  /* ── Mission cards ──────────────────────────────────────────────────── */
  .mission-card {
    background: #fff;
    border-radius: var(--radius); padding: 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 16px var(--shadow);
    border-left: 5px solid var(--sage);
    transition: transform 0.2s, box-shadow 0.2s;
    position: relative;
  }
  .mission-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 24px var(--shadow);
  }
  .mission-card.naturequest { border-left-color: #3a8a3a; }
  .mission-card.ecoquest   { border-left-color: #4a9abe; }
  .mission-card.ai-mission::after {
    content: "✨ AI-Personalised";
    position: absolute; top: 12px; right: 14px;
    background: linear-gradient(135deg, #2d6a2d, #4a9abe);
    color: #fff; font-size: 0.7rem; font-weight: 600;
    padding: 3px 10px; border-radius: 20px;
  }

  .card-category {
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; margin-bottom: 6px;
  }
  .nq-label { color: #2d6a2d; }
  .eq-label { color: #2a6a8a; }

  .card-title {
    font-family: 'Outfit', sans-serif; font-size: 1.2rem;
    font-weight: 700; color: var(--text-dark); margin-bottom: 6px;
  }
  .card-desc { color: var(--text-mid); font-size: 0.9rem; line-height: 1.55; }

  .card-meta {
    display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px;
  }
  .pill {
    background: #f0f7f0; color: #2d5a2d; border-radius: 30px;
    font-size: 0.75rem; font-weight: 500; padding: 4px 12px;
    display: inline-flex; align-items: center; gap: 4px;
    border: 1px solid #d8ead8;
  }
  .pill.eco { background: #e8f4fa; color: #1a5a7a; border-color: #c0dcea; }
  .pill.diff-easy       { background: #e8f5e8; color: #2d7a2d; }
  .pill.diff-moderate   { background: #fff8e0; color: #8a6800; }
  .pill.diff-challenging{ background: #fde8e8; color: #8a2020; }

  .safety-box {
    background: #fffbec; border: 1px solid #f0d060; border-radius: var(--radius-sm);
    padding: 10px 14px; margin-top: 12px; font-size: 0.82rem; color: #7a5a00;
    line-height: 1.5;
  }
  .safety-box::before { content: "⚠️  "; }

  /* ── Stat / progress cards ──────────────────────────────────────────── */
  .stat-card {
    background: #fff; border-radius: var(--radius); padding: 1.4rem 1.6rem;
    box-shadow: 0 2px 14px var(--shadow); text-align: center;
  }
  .stat-value {
    font-family: 'Outfit', sans-serif; font-size: 2.4rem; font-weight: 800;
    color: var(--forest); line-height: 1;
  }
  .stat-label { color: var(--text-mid); font-size: 0.82rem; margin-top: 4px; }

  .level-card {
    background: linear-gradient(135deg, #1e4d1e, #2d6a2d);
    border-radius: var(--radius); padding: 1.6rem;
    box-shadow: 0 4px 20px rgba(30,77,30,0.3); color: #e8f5e8;
    text-align: center;
  }
  .level-name {
    font-family: 'Outfit', sans-serif; font-size: 1.6rem; font-weight: 800;
  }
  .level-num { font-size: 0.9rem; opacity: 0.75; margin-top: 2px; }

  .progress-outer {
    background: rgba(255,255,255,0.2); border-radius: 20px;
    height: 12px; margin: 14px 0 6px; overflow: hidden;
  }
  .progress-inner {
    background: linear-gradient(90deg, #a8e8a8, #e8f5a8);
    height: 100%; border-radius: 20px;
    transition: width 0.6s ease;
  }
  .progress-label { font-size: 0.78rem; opacity: 0.8; }

  /* ── Badge grid ─────────────────────────────────────────────────────── */
  .badge-grid { display: flex; gap: 12px; flex-wrap: wrap; }
  .badge-item {
    background: #fff; border-radius: var(--radius-sm); padding: 14px 18px;
    box-shadow: 0 2px 10px var(--shadow); text-align: center;
    min-width: 110px; transition: transform 0.2s;
  }
  .badge-item:hover { transform: scale(1.04); }
  .badge-item.earned {
    background: linear-gradient(135deg, #f0faf0, #e8f7e8);
    border: 2px solid #6ab86a;
  }
  .badge-item.locked { opacity: 0.4; filter: grayscale(0.6); }
  .badge-emoji { font-size: 1.8rem; }
  .badge-name { font-size: 0.75rem; font-weight: 600; color: var(--text-dark); margin-top: 4px; }

  /* ── AI status banner ───────────────────────────────────────────────── */
  .ai-banner {
    border-radius: var(--radius-sm); padding: 10px 16px;
    font-size: 0.82rem; font-weight: 500; margin-bottom: 16px;
    display: flex; align-items: center; gap: 8px;
  }
  .ai-banner.connected {
    background: #e8f5e8; color: #1a5a1a; border: 1px solid #a8d8a8;
  }
  .ai-banner.offline {
    background: #f5f0e0; color: #5a4a20; border: 1px solid #d4c070;
  }
  .ai-banner.unconfigured {
    background: #f0f0f0; color: #404040; border: 1px solid #c0c0c0;
  }

  /* ── History table ──────────────────────────────────────────────────── */
  .history-item {
    background: #fff; border-radius: var(--radius-sm);
    padding: 12px 16px; margin-bottom: 8px;
    display: flex; align-items: center; gap: 14px;
    box-shadow: 0 1px 8px var(--shadow);
  }
  .history-icon { font-size: 1.4rem; }
  .history-info { flex: 1; }
  .history-title { font-weight: 600; color: var(--text-dark); font-size: 0.9rem; }
  .history-meta  { font-size: 0.78rem; color: var(--text-mid); margin-top: 2px; }
  .history-pts   { font-family: 'Outfit', sans-serif; font-weight: 700;
                   color: var(--forest); font-size: 1.1rem; }

  /* ── Setup form ─────────────────────────────────────────────────────── */
  .form-section {
    background: #fff; border-radius: var(--radius); padding: 1.6rem;
    margin-bottom: 1.4rem; box-shadow: 0 2px 14px var(--shadow);
  }
  .form-section-title {
    font-family: 'Outfit', sans-serif; font-weight: 700;
    color: var(--forest); font-size: 1.05rem; margin-bottom: 1rem;
    border-bottom: 2px solid #d8ead8; padding-bottom: 6px;
  }

  /* ── Generate button ────────────────────────────────────────────────── */
  div[data-testid="stButton"] > button.generate-btn {
    background: linear-gradient(135deg, #1e4d1e, #3a8a3a) !important;
    color: #fff !important; border: none !important;
    border-radius: 50px !important; font-size: 1.05rem !important;
    font-weight: 700 !important; padding: 0.8rem 2.5rem !important;
    width: 100% !important; transition: all 0.25s !important;
    box-shadow: 0 4px 16px rgba(30,77,30,0.35) !important;
    font-family: 'Outfit', sans-serif !important;
  }
  div[data-testid="stButton"] > button.generate-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(30,77,30,0.4) !important;
  }

  /* ── Streamlit overrides ─────────────────────────────────────────────── */
  div[data-testid="stMultiSelect"] .stMultiSelect > div {
    border-radius: var(--radius-sm) !important;
    border-color: #c0d8c0 !important;
  }
  .stSelectbox > div > div { border-radius: var(--radius-sm) !important; }
  .stTextArea > div > div { border-radius: var(--radius-sm) !important; }
  div[data-testid="stFileUploader"] {
    border: 2px dashed #a8c8a8 !important;
    border-radius: var(--radius) !important;
    background: #f5fbf5 !important;
  }
  div[data-testid="stExpander"] { border: 1px solid #d8ead8 !important; border-radius: var(--radius-sm) !important; }
  .stSuccess { background: #e8f5e8 !important; border-color: #80c880 !important; }
  .stInfo    { background: #e8f0fa !important; }
  .stWarning { background: #fffbe8 !important; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

def _init_state() -> None:
    if "profile" not in st.session_state:
        st.session_state.profile = storage.load_profile()
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "discover"
    if "generated_missions" not in st.session_state:
        st.session_state.generated_missions = []
    if "ai_status" not in st.session_state:
        st.session_state.ai_status = "none"
    if "ai_label" not in st.session_state:
        st.session_state.ai_label = ""
    if "selected_mission" not in st.session_state:
        st.session_state.selected_mission = None
    if "just_completed" not in st.session_state:
        st.session_state.just_completed = None

_init_state()

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------

st.markdown("""
<div class="hero">
  <div class="hero-title">🌿 TerraQuest AI</div>
  <p class="hero-sub">Adventure is closer than you think.<br>
  Discover nature. Complete eco-missions. Make every outing count.</p>
  <div class="hero-badges-row">
    <span class="hero-badge">🔭 NatureQuest</span>
    <span class="hero-badge">♻️ EcoQuest</span>
    <span class="hero-badge">🎖️ Badges & Levels</span>
    <span class="hero-badge">🤖 Open-Weight AI</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

col_n1, col_n2, col_n3 = st.columns(3)
with col_n1:
    if st.button("🗺️  Discover", key="nav_discover", use_container_width=True):
        st.session_state.active_tab = "discover"
with col_n2:
    if st.button("📋  Quest Board", key="nav_quests", use_container_width=True):
        st.session_state.active_tab = "quests"
with col_n3:
    if st.button("🌱  My Impact", key="nav_impact", use_container_width=True):
        st.session_state.active_tab = "impact"

tab = st.session_state.active_tab
st.markdown("---")

# ===========================================================================
# TAB: DISCOVER
# ===========================================================================

if tab == "discover":
    st.markdown('<div class="section-wrap">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">🗺️ Plan Your Quest</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Tell us about your surroundings so we can personalise your missions.</p>', unsafe_allow_html=True)

    # AI provider status
    ai_config_status, ai_config_msg = get_provider_status()
    if ai_config_status == "configured":
        st.markdown(f'<div class="ai-banner connected">🌐 {ai_config_msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="ai-banner unconfigured">ℹ️ {ai_config_msg}</div>',
            unsafe_allow_html=True,
        )

    with st.form(key="discover_form"):
        # ── Environment ──────────────────────────────────────────────────
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<p class="form-section-title">📍 Where are you?</p>', unsafe_allow_html=True)
        env_options = [
            "Home garden", "Balcony or terrace", "Public park", "Urban street",
            "College or school campus", "Countryside", "Other outdoor environment",
        ]
        environment = st.multiselect(
            "Select all environments that apply",
            options=env_options,
            default=["Public park"],
            key="sel_environment",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Flora ────────────────────────────────────────────────────────
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<p class="form-section-title">🌺 Available Flora</p>', unsafe_allow_html=True)
        flora_options = [
            "Hibiscus", "Rose", "Marigold", "Sunflower", "Other flowers",
            "Trees and leaves", "Grass and small plants", "Other or unknown plants",
        ]
        flora = st.multiselect(
            "Select plants / flowers you can see",
            options=flora_options,
            default=["Trees and leaves", "Grass and small plants"],
            key="sel_flora",
        )
        extra_plants = st.text_input(
            "Describe any other plants (optional)",
            placeholder="e.g. jasmine vine, cactus, fern",
            key="extra_plants",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Fauna ────────────────────────────────────────────────────────
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<p class="form-section-title">🦋 Available Fauna</p>', unsafe_allow_html=True)
        fauna_options = [
            "Squirrels", "Butterflies", "Bees", "Ants", "Birds",
            "Spiders", "Other insects", "Other wildlife", "No animals observed yet",
        ]
        fauna = st.multiselect(
            "Select animals you have observed or are likely to see",
            options=fauna_options,
            default=["Birds", "Ants"],
            key="sel_fauna",
        )
        extra_animals = st.text_input(
            "Describe any other creatures (optional)",
            placeholder="e.g. pigeons, lizards, frogs",
            key="extra_animals",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Preferences ──────────────────────────────────────────────────
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<p class="form-section-title">⚙️ Your Preferences</p>', unsafe_allow_html=True)
        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            time_available = st.selectbox(
                "Time available",
                options=[5, 10, 15, 30],
                index=2,
                format_func=lambda x: f"{x} minutes",
                key="sel_time",
            )
        with p_col2:
            category_pref = st.selectbox(
                "Mission type",
                options=["Both", "NatureQuest", "EcoQuest"],
                index=0,
                key="sel_category",
            )
        with p_col3:
            difficulty = st.selectbox(
                "Difficulty",
                options=["Easy", "Moderate", "Challenging"],
                index=0,
                key="sel_difficulty",
            )
        st.markdown("</div>", unsafe_allow_html=True)

        submitted = st.form_submit_button(
            "🌿 Generate My Quests",
            use_container_width=True,
        )

    if submitted:
        if not environment:
            st.error("Please select at least one environment.")
        elif not flora and not fauna:
            st.warning("Select at least some flora or fauna to help personalise your missions.")
        else:
            profile = st.session_state.profile
            history = storage.load_mission_history()
            completed_titles = [h["title"] for h in history]

            context = {
                "environment":        environment,
                "flora":              flora,
                "fauna":              fauna,
                "extra_plants":       extra_plants,
                "extra_animals":      extra_animals,
                "time_available":     time_available,
                "category_preference": category_pref,
                "difficulty":         difficulty,
                "completed_ids":      profile.get("completed_mission_ids", []),
                "completed_titles":   completed_titles,
            }

            with st.spinner("Finding your perfect quests…"):
                result_missions, ai_status, ai_label = generate_ai_missions(context)

            st.session_state.generated_missions = result_missions
            st.session_state.ai_status = ai_status
            st.session_state.ai_label = ai_label
            st.session_state.active_tab = "quests"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# TAB: QUEST BOARD
# ===========================================================================

elif tab == "quests":
    st.markdown('<div class="section-wrap">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">📋 Quest Board</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Choose a quest, head outside, and complete your mission!</p>', unsafe_allow_html=True)

    # AI status banner
    ai_status = st.session_state.get("ai_status", "none")
    ai_label  = st.session_state.get("ai_label", "")
    if ai_status == "ai":
        st.markdown(f'<div class="ai-banner connected">🤖 {ai_label}</div>', unsafe_allow_html=True)
    elif ai_status == "fallback":
        st.markdown(f'<div class="ai-banner offline">📋 {ai_label}</div>', unsafe_allow_html=True)

    # Success notification
    if st.session_state.just_completed:
        jc = st.session_state.just_completed
        st.success(
            f"🎉 **{jc['title']}** completed! You earned **{jc['points']} points**."
            + (f" New badge: **{', '.join(jc['new_badges'])}**!" if jc.get("new_badges") else "")
        )
        st.session_state.just_completed = None

    missions_to_show = st.session_state.generated_missions
    profile = st.session_state.profile

    if not missions_to_show:
        st.info("You haven't generated any quests yet. Head to **Discover** to personalise your missions!")
        if st.button("Browse all predefined missions"):
            missions_to_show = mission_lib.get_all_predefined_missions()
        else:
            st.markdown("</div>", unsafe_allow_html=True)
            st.stop()

    if not missions_to_show:
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    # ── Category tabs ─────────────────────────────────────────────────────
    nq_missions = [m for m in missions_to_show if m.get("category") == "NatureQuest"]
    eq_missions = [m for m in missions_to_show if m.get("category") == "EcoQuest"]

    q_tab1, q_tab2 = st.tabs([
        f"🔭 NatureQuest ({len(nq_missions)})",
        f"♻️ EcoQuest ({len(eq_missions)})",
    ])

    completed_ids = profile.get("completed_mission_ids", [])

    def render_mission_card(m: dict) -> None:
        is_done = m["id"] in completed_ids
        is_ai   = m.get("ai_generated", False)
        cat     = m.get("category", "NatureQuest")
        diff    = m.get("difficulty", "Easy")
        cat_cls = "naturequest" if cat == "NatureQuest" else "ecoquest"
        cat_label_cls = "nq-label" if cat == "NatureQuest" else "eq-label"
        cat_emoji = "🔭" if cat == "NatureQuest" else "♻️"
        diff_cls = {"Easy": "diff-easy", "Moderate": "diff-moderate", "Challenging": "diff-challenging"}.get(diff, "diff-easy")
        pill_cls = "" if cat == "NatureQuest" else "eco"
        ai_cls   = " ai-mission" if is_ai else ""

        done_ribbon = "✅ Completed" if is_done else ""

        st.markdown(f"""
        <div class="mission-card {cat_cls}{ai_cls}">
          <p class="card-category {cat_label_cls}">{cat_emoji} {cat}</p>
          <p class="card-title">{m['title']} {done_ribbon}</p>
          <p class="card-desc">{m['description']}</p>
          <div class="card-meta">
            <span class="pill {diff_cls}">⚡ {diff}</span>
            <span class="pill {pill_cls}">⏱ {m.get('duration_minutes', 10)} min</span>
            <span class="pill {pill_cls}">🏅 {m.get('points', 20)} pts</span>
          </div>
          <div class="safety-box">{m.get('safety', '')}</div>
        </div>
        """, unsafe_allow_html=True)

        # Expand for details + completion
        with st.expander("View task details & submit evidence"):
            st.markdown(f"**📌 Task:** {m.get('task', '')}")
            st.markdown(f"**📷 Evidence required:** {m.get('evidence', '')}")

            if is_done:
                st.success("You have already completed this mission. Great work!")
                return

            st.markdown("---")
            st.markdown("### 📸 Submit Your Evidence")
            st.caption(
                "Evidence is user-submitted and is not automatically verified by AI. "
                "Complete the real-world activity first, then return to submit."
            )

            uid = m["id"].replace("-", "_")
            uploaded = st.file_uploader(
                "Upload a photo (JPG, PNG, WEBP — max 10 MB)",
                type=["jpg", "jpeg", "png", "webp", "gif"],
                key=f"upload_{uid}",
            )
            if uploaded and uploaded.size > 10 * 1024 * 1024:
                st.error("File too large. Please upload an image under 10 MB.")
                uploaded = None
            if uploaded:
                st.image(uploaded, caption="Your evidence preview", use_container_width=True)

            observation = st.text_area(
                "Optional observation note",
                placeholder="What did you see? Any interesting behaviour or detail?",
                key=f"obs_{uid}",
                max_chars=500,
            )

            confirm = st.checkbox(
                "I have completed this real-world activity safely and responsibly.",
                key=f"confirm_{uid}",
            )

            if st.button(f"✅ Complete Mission: {m['title']}", key=f"complete_{uid}"):
                if not confirm:
                    st.warning("Please confirm that you have completed the activity.")
                elif cat == "NatureQuest" and not uploaded:
                    st.warning("Please upload a photo as evidence for NatureQuest missions.")
                else:
                    # Award points
                    old_badges = set(profile.get("badges", []))
                    profile, pts_awarded = storage.award_points(profile, m)
                    new_badges = list(set(profile.get("badges", [])) - old_badges)

                    # Save evidence
                    evidence_filename = None
                    if uploaded:
                        evidence_filename = storage.save_evidence(uploaded, m["id"])

                    # Record history
                    storage.record_mission_completion(m, observation, evidence_filename)
                    storage.save_profile(profile)

                    st.session_state.profile = profile
                    st.session_state.just_completed = {
                        "title":      m["title"],
                        "points":     pts_awarded,
                        "new_badges": new_badges,
                    }
                    st.rerun()

    with q_tab1:
        if nq_missions:
            for m in nq_missions:
                render_mission_card(m)
        else:
            st.info("No NatureQuest missions in this batch. Generate new quests or browse all below.")
            if st.button("Load all NatureQuest missions", key="load_nq"):
                st.session_state.generated_missions = (
                    st.session_state.generated_missions
                    + mission_lib.get_predefined_by_category("NatureQuest")
                )
                st.rerun()

    with q_tab2:
        if eq_missions:
            for m in eq_missions:
                render_mission_card(m)
        else:
            st.info("No EcoQuest missions in this batch. Generate new quests or browse all below.")
            if st.button("Load all EcoQuest missions", key="load_eq"):
                st.session_state.generated_missions = (
                    st.session_state.generated_missions
                    + mission_lib.get_predefined_by_category("EcoQuest")
                )
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# TAB: MY IMPACT
# ===========================================================================

elif tab == "impact":
    st.markdown('<div class="section-wrap">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">🌱 My Impact</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Your journey so far — every quest counts.</p>', unsafe_allow_html=True)

    profile = st.session_state.profile
    total_pts = profile.get("total_points", 0)
    level_info = storage.get_level(total_pts)
    next_level  = storage.get_next_level(total_pts)
    pct         = storage.level_progress_pct(total_pts)

    # ── Level card ─────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="level-card">
      <div style="font-size:2.4rem">{"🌱🔭🛡️🏆🌍"[level_info['level']-1]}</div>
      <div class="level-name">{level_info['name']}</div>
      <div class="level-num">Level {level_info['level']}</div>
      <div class="progress-outer">
        <div class="progress-inner" style="width:{pct:.1f}%"></div>
      </div>
      <div class="progress-label">
        {total_pts} pts
        {"— MAX LEVEL 🎉" if next_level is None else f"→ {next_level['name']} at {next_level['required']} pts ({next_level['required']-total_pts} to go)"}
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Stats row ───────────────────────────────────────────────────────────
    s1, s2, s3, s4 = st.columns(4)
    total_completed = profile.get("naturequest_count", 0) + profile.get("ecoquest_count", 0)

    with s1:
        st.markdown(f"""
        <div class="stat-card">
          <div class="stat-value">{total_pts}</div>
          <div class="stat-label">Total Points</div>
        </div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="stat-card">
          <div class="stat-value">{total_completed}</div>
          <div class="stat-label">Quests Completed</div>
        </div>""", unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="stat-card">
          <div class="stat-value">{profile.get('naturequest_count',0)}</div>
          <div class="stat-label">🔭 NatureQuest</div>
        </div>""", unsafe_allow_html=True)
    with s4:
        st.markdown(f"""
        <div class="stat-card">
          <div class="stat-value">{profile.get('ecoquest_count',0)}</div>
          <div class="stat-label">♻️ EcoQuest</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Badges ──────────────────────────────────────────────────────────────
    st.markdown('<p class="section-title" style="font-size:1.2rem">🎖️ Badges</p>', unsafe_allow_html=True)

    BADGE_EMOJI = {
        "First Quest":       "⭐",
        "Flower Finder":     "🌸",
        "Wildlife Watcher":  "🦋",
        "Nature Observer":   "🔭",
        "Recycling Rookie":  "♻️",
        "Cleanup Hero":      "🧹",
        "Compost Champion":  "🌿",
        "Nature Guardian":   "🛡️",
    }

    earned_set = set(profile.get("badges", []))
    badge_html = '<div class="badge-grid">'
    for badge_name, badge_desc in storage.BADGE_DEFINITIONS.items():
        emoji = BADGE_EMOJI.get(badge_name, "🏅")
        is_earned = badge_name in earned_set
        cls = "earned" if is_earned else "locked"
        badge_html += f"""
        <div class="badge-item {cls}" title="{badge_desc}">
          <div class="badge-emoji">{emoji}</div>
          <div class="badge-name">{badge_name}</div>
        </div>"""
    badge_html += "</div>"
    st.markdown(badge_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Mission history ──────────────────────────────────────────────────────
    st.markdown('<p class="section-title" style="font-size:1.2rem">📜 Recent History</p>', unsafe_allow_html=True)
    history = storage.load_mission_history()

    if history:
        for entry in reversed(history[-15:]):
            cat   = entry.get("category", "NatureQuest")
            icon  = "🔭" if cat == "NatureQuest" else "♻️"
            title = entry.get("title", "Mission")
            pts   = entry.get("points", 0)
            diff  = entry.get("difficulty", "")
            ts    = entry.get("completed_at", "")[:10]
            obs   = entry.get("observation", "")

            st.markdown(f"""
            <div class="history-item">
              <div class="history-icon">{icon}</div>
              <div class="history-info">
                <div class="history-title">{title}</div>
                <div class="history-meta">{ts} · {diff} · {cat}{(' · "' + obs[:60] + '…"') if obs else ''}</div>
              </div>
              <div class="history-pts">+{pts}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No completed missions yet — your adventure starts on the Quest Board!")

    # ── Encouragement ────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    encouragement_msgs = [
        "🌳 The forest is waiting. One small step outside can change your day.",
        "🌸 Even five minutes in nature can shift your mood. What will you discover today?",
        "♻️ Small eco-actions add up. Ready for your next EcoQuest?",
        "🦋 Every observation matters. Nature is full of surprises — go find one!",
        "🌱 You're making a difference, one quest at a time. Keep going!",
    ]
    import hashlib
    msg_idx = int(hashlib.md5(str(total_pts).encode()).hexdigest(), 16) % len(encouragement_msgs)
    st.info(encouragement_msgs[msg_idx])

    st.markdown("</div>", unsafe_allow_html=True)
