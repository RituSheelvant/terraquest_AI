# 🌿 TerraQuest AI

**Gamified Nature Exploration & Environmental Action Platform**

> *Adventure is closer than you think. Discover nature. Complete eco-missions. Make every outing count.*

Built for the **Hacktoberfest Open-Source AI Challenge — Week 1: Touch Grass**

---

## 📖 Project Overview

TerraQuest AI turns the real world into a gamified adventure. It gives users personalised outdoor missions — observing wildlife, photographing flowers, and completing small eco-actions — and tracks their progress through a points-and-badges system.

The platform has two complementary mission categories:

| Category | Focus |
|---|---|
| 🔭 **NatureQuest** | Observe plants, flowers, and creatures performing natural behaviours |
| ♻️ **EcoQuest** | Collect litter, sort recyclables, identify compostable scraps, reduce waste |

**The core philosophy:** the screen starts the adventure. The real world is where the mission happens.

---

## 🎯 Problem Being Addressed

Urban life increasingly disconnects people from the natural world. TerraQuest AI provides a structured, low-barrier entry point for nature connection and environmental action that:

- Requires no special equipment beyond a phone
- Works in any outdoor setting (garden, balcony, park, street)
- Scales from a five-minute observation to a thirty-minute cleanup
- Runs entirely on a local device — no account required, no cloud dependency

---

## 🔭 NatureQuest Missions

Sample missions:

- **Flower Detective** — Photograph a hibiscus or open flower from directly above
- **Leaf Explorer** — Find two leaves with different shapes or vein patterns
- **Butterfly Watch** — Photograph a butterfly resting on a flower, without disturbing it
- **Tiny Explorer** — Observe ants and photograph one carrying food if that behaviour occurs naturally
- **Birdwatcher** — Observe a bird's behaviour and photograph it from a respectful distance
- **Bee Observer** — Watch bees visiting flowers and capture one in the act
- **Morning Dew Hunter** — Find water droplets on leaves and photograph the way they catch light

**Safety principle:** missions never require touching animals, disturbing nests, or manipulating wildlife. Animals are observed as they occur naturally.

---

## ♻️ EcoQuest Missions

Sample missions:

- **Plastic Patrol** — Collect non-hazardous, safely accessible litter
- **Paper Saver** — Identify clean, dry paper suitable for recycling
- **Compost Champion** — Set aside raw fruit and vegetable scraps for composting
- **Waste Detective** — Determine the correct disposal category for a discarded item
- **Cleanup Hero** — Complete a short cleanup in a permitted outdoor area
- **Energy Audit** — Find devices left on standby and switch them off
- **Water Saver** — Identify and implement one daily water-saving change

**Accuracy principle:** the application does not claim all plastic is recyclable, does not invent local recycling rules, and does not fabricate environmental impact measurements such as kilograms diverted or CO₂ saved.

---

## 🎮 Gamification

### Points

| Difficulty | Points |
|---|---|
| Easy | 20 |
| Moderate | 35 |
| Challenging | 50 |

Points are validated in Python. AI-generated point values are ignored and replaced by the validated values above.

### Levels

| Level | Name | Points Required |
|---|---|---|
| 1 | 🌱 Seedling | 0 |
| 2 | 🔭 Explorer | 100 |
| 3 | 🛡️ Nature Guardian | 300 |
| 4 | 🏆 Earth Champion | 600 |
| 5 | 🌍 Planet Protector | 1 000 |

### Badges

| Badge | Condition |
|---|---|
| ⭐ First Quest | Complete your first quest |
| 🌸 Flower Finder | Complete 3 NatureQuest flower missions |
| 🦋 Wildlife Watcher | Complete 3 NatureQuest wildlife missions |
| 🔭 Nature Observer | Complete 10 NatureQuest missions |
| ♻️ Recycling Rookie | Complete your first EcoQuest recycling mission |
| 🧹 Cleanup Hero | Complete 3 EcoQuest cleanup missions |
| 🌿 Compost Champion | Complete 3 EcoQuest composting missions |
| 🛡️ Nature Guardian | Reach Level 3 |

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Frontend / UI | Streamlit |
| Language | Python 3.11+ |
| Persistence | Local JSON files |
| Evidence storage | Local file system |
| AI inference | Open-weight model via configurable provider |
| HTTP client | requests |

No database server, no user registration, no GPS, no paid API requirement.

---

## 🤖 AI Architecture

### Why Open-Weight AI?

TerraQuest AI is built around open-weight models because:

1. **Flexibility** — you choose which model to use and can change it at any time
2. **Prompt control** — mission-generation prompts are fully accessible and modifiable in `ai_generator.py`
3. **Local inference potential** — any OpenAI-compatible local server (Ollama, LM Studio, vLLM) can be plugged in with two environment variables
4. **Privacy** — a local provider sends no data to external services
5. **No mandatory paid API** — the application works fully without any AI provider

### Provider Interface

`ai_generator.py` defines an abstract `AIProvider` base class with two concrete implementations:

```
AIProvider (abstract)
├── HuggingFaceInferenceProvider   ← hosted open-weight models
├── OpenAICompatibleProvider       ← any local/hosted OAI-compatible server
└── FallbackProvider               ← triggers Offline-Friendly Mode
```

Provider selection is automatic based on environment variables. No provider is hardcoded.

### Supported Open-Weight Model

The default model is **Qwen/Qwen2.5-3B-Instruct** (Qwen License — check [Qwen2.5 licensing terms](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct) before commercial use).

Any instruction-tuned model available through the configured provider can be used by setting `HF_MODEL_ID` or `OPENAI_COMPAT_MODEL`.

### AI Status Transparency

The application displays one of two statuses — never fabricated:

- **🤖 Open-Weight AI Connected** — shown only after a successful real API request
- **📋 Offline-Friendly Mode** — shown when predefined missions are used

Predefined missions are never labelled as AI-generated.

---

## 📦 Installation

### Prerequisites

- Python 3.11 or later
- `pip`

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-username/terraquest-ai.git
cd terraquest-ai

# 2. (Recommended) Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Running the Application

```bash
streamlit run app.py
```

The application opens in your browser at `http://localhost:8501`.

**The app is fully functional without any AI provider.** Predefined, curated missions are served in Offline-Friendly Mode.

---

## ⚙️ Configuring an AI Provider

### Option A — Hugging Face Inference API (hosted)

> ⚠️ Using a hosted provider means mission-generation prompts are sent to Hugging Face servers. No photos or personal data are sent.

1. Create a free account at [huggingface.co](https://huggingface.co)
2. Generate an API token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
3. Create a `.env` file in the project root:

```env
HF_API_TOKEN=hf_your_token_here
# Optional: override the model
HF_MODEL_ID=Qwen/Qwen2.5-3B-Instruct
```

4. Load the environment before running:

```bash
# Windows PowerShell
$env:HF_API_TOKEN="hf_your_token_here"
streamlit run app.py

# macOS / Linux
export HF_API_TOKEN="hf_your_token_here"
streamlit run app.py
```

Or use a tool such as `python-dotenv` to load `.env` automatically.

### Option B — OpenAI-Compatible Local Server (e.g. Ollama, LM Studio, vLLM)

If you have a local inference server running:

```bash
# Example: Ollama running locally
$env:OPENAI_COMPAT_BASE_URL="http://localhost:11434/v1"
$env:OPENAI_COMPAT_API_KEY="ollama"   # any non-empty string for local servers
$env:OPENAI_COMPAT_MODEL="qwen2.5:3b"
streamlit run app.py
```

```bash
# Example: LM Studio
$env:OPENAI_COMPAT_BASE_URL="http://localhost:1234/v1"
$env:OPENAI_COMPAT_API_KEY="lm-studio"
$env:OPENAI_COMPAT_MODEL="Qwen2.5-3B-Instruct"
streamlit run app.py
```

### Option C — No provider (Offline-Friendly Mode)

Run without any environment variables. The app serves curated predefined missions and clearly labels them as such.

---

## 📁 Fallback Behaviour

When no provider is configured or a request fails:

1. The app automatically falls back to predefined missions in `missions.py`
2. Missions are filtered and ranked by environment, flora/fauna selection, difficulty, and completion history
3. The UI displays **📋 Offline-Friendly Mode** — never a false "AI Connected" label
4. All gamification features (points, badges, levels, history) work identically

---

## 💾 Data Storage and Privacy

All data is stored locally in the `data/` directory:

```
data/
├── profile.json          # points, badges, completion history
├── mission_history.json  # per-mission completion records
└── evidence/             # uploaded photos (safe filenames, local only)
```

- Nothing in `data/` is committed to Git (see `.gitignore`)
- No photos or notes are sent to any external service
- When using a hosted AI provider (Option A / B with remote URL), only the mission-generation prompt is sent — no images, no personal data

---

## ⚠️ Safety Considerations

Safety constraints are enforced in Python code (`missions.py`, `ai_generator.py`), not only through AI prompts.

Mission templates never instruct users to:

- Touch unknown plants or animals
- Disturb nests or wildlife
- Handle broken glass, medical waste, batteries, chemicals, or sharp objects
- Handle unknown substances
- Enter roads, drains, or restricted areas
- Trespass on private property

AI-generated missions are validated against these constraints before display.

---

## 🚧 Limitations

- Evidence is **not** automatically verified. Users self-certify completion.
- There is **no image recognition** or species identification. Do not claim the app has identified a species.
- No **social features**, leaderboards, or multiplayer components.
- No **GPS** integration; environment is user-selected.
- **Local recycling rules vary** by area. The app does not invent local waste collection policies.
- Hosted inference sends prompts to the configured provider's servers. This is disclosed clearly.
- The Hugging Face free tier may rate-limit or cold-start models. Retry if a 503 is returned.
- A single completion per mission ID is enforced. Duplicate awards are prevented in Python.

---

## 🔭 Future Improvements

- Optional local Ollama integration (when Ollama is installed and running)
- Image recognition for basic plant/insect identification (on-device model)
- Community mission packs (curated by biologists, conservationists)
- Seasonal mission calendars
- Export of personal impact data as a shareable summary
- Multi-language support
- Accessibility improvements (screen reader labels, high-contrast theme)
- Progressive Web App (PWA) packaging for mobile

---

## 📜 Licence

See `LICENSE` for details. The application code is open source. Model licensing (e.g. Qwen2.5) must be checked separately for your use case.

---

## 🙏 Acknowledgements

- [Streamlit](https://streamlit.io) — rapid Python web apps
- [Qwen2.5](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct) — open-weight instruction model by Alibaba Cloud
- [Hugging Face](https://huggingface.co) — open-weight model hosting and inference API
- Hacktoberfest Open-Source AI Challenge organisers
#   t e r r a q u e s t _ A I  
 