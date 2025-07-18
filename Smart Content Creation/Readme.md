# 🤖 Agentic AI Content Refinement

This Streamlit app simulates a **conversation between two AI agents**:

- ✍️ **Content Creator**: Drafts technical content using Gemini
- 🧐 **Content Critic**: Evaluates and provides feedback to improve quality

The agents iterate across multiple turns to refine AI-generated content collaboratively.

---

## 🚀 Features

- Gemini 1.5 Flash via LangChain & Google GenAI SDK
- Multi-turn back-and-forth between agents
- Markdown-structured output generation
- Simulated feedback cycle using AutoGen
- Fully browser-based interface with Streamlit

---

## 🛠️ Installation

```bash
git clone https://github.com/your-username/agentic-content-refinement.git
cd agentic-content-refinement
pip install -r requirements.txt
```

---

## 🔑 API Key Setup

This app uses **Google's Gemini API** via:

- `langchain-google-genai`
- `google-generativeai`
- `autogen` LLM config

Set your API key in the Python script or as an environment variable:

```bash
export GOOGLE_API_KEY="your-gemini-api-key"
```

---

## ▶️ Usage

```bash
streamlit run app.py
```

1. Enter a discussion topic (e.g., "Agentic AI")
2. Choose the number of conversation turns
3. Click **Start Simulation**
4. Review each step of content generation and refinement

---

## 💡 Example Output

### ✅ Final Content (Turn 5)

```markdown
## Agentic AI: A New Paradigm in Autonomy

### Key Concepts

Agentic AI enables autonomous decision-making through multi-agent collaboration...

### Technical Foundations

- LLM-based tool use
- Role-based prompting
- Context-aware reasoning

### Real-World Applications

- Code analysis
- Competitive research
- Educational content generation

### Future Implications

Agentic frameworks could replace many traditional RPA flows in knowledge work...
```

---

## 📦 requirements.txt

```txt
streamlit
google-generativeai
langchain-google-genai
pyautogen
```

---

## 📌 Notes

- This app uses a custom `GeminiAgent` wrapper to enable deepcopy for AutoGen compatibility.
- Intended for educational, R\&D, and demonstration purposes.
- Extendable with additional agents or UI features like PDF export or sidebar controls.

---

## 📄 License

MIT License – Use freely with attribution.
