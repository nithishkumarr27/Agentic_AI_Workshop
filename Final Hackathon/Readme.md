# 💡 Misconception-Driven Learning Path Correction System

An **Agentic AI-powered education assistant** designed to detect, classify, correct, and track conceptual misconceptions in learners using their real-time learning data — code submissions, quiz logs, and interactions. The system continuously adjusts the learner's roadmap and provides rich feedback and personalized interventions using **Gemini 1.5 Flash**, LangChain agents, and Retrieval-Augmented Generation (RAG).

---

## 🚀 Features

* Multi-Agent System (5 Agentic AI modules)
* LangChain + Gemini 1.5 Flash integration
* RAG-based internal corpus lookup (FAISS/Chroma)
* Real-time roadmap updates with detours
* Personalized correction with micro-challenges and analogies
* Learner and Mentor dashboards

---

## 🧠 Core Technologies

### Backend (AI & Logic Layer)

* **Flask** – REST API framework
* **LangChain** – AgentExecutor, tools, memory, retrievers
* **Gemini 1.5 Flash** – LLM backbone for reasoning
* **RAG (FAISS/Chroma)** – for explanation/code retrieval
* **MongoDB** – for storing learner profiles, roadmaps, misconceptions

### Frontend (UI Layer)

* **ReactJS (Vite)** – JavaScript UI
* **Tailwind CSS** – Utility-first styling

### Dev & Infrastructure

* **Python 3.10+**
* **dotenv / secrets.toml** – Secure config
* **requirements.txt** – Dependency tracking

---

## 🧩 Agent Modules

### 1. Misconception Detection Agent

Detects conceptual issues from learner code and quiz logs.

### 2. Misconception Classification Agent (RAG + Gemini)

Classifies issues and provides explanations using internal corpus.

### 3. Correction Intervention Agent

Delivers remediation packages: coding challenges, analogies, and examples.

### 4. Roadmap Adjustment Agent

Revises learner's roadmap based on correction outcomes.

### 5. Confidence Recovery Tracker Agent

Tracks long-term resolution and recurrence of misconceptions.

---

## 🔄 System Flow

graph TD
    A[Frontend: React App] -->|HTTP Requests| B[Backend: Flask API]
    B --> C[Misconception Detector]
    B --> D[Classification Agent]
    B --> E[Intervention Generator]
    B --> F[Roadmap Adjuster]
    B --> G[Progress Tracker]
    C --> H[Gemini LLM]
    D --> H
    E --> H
    F --> H
    D --> I[FAISS Vector Store]
    B --> J[(MongoDB)]

---

## 📁 Project Structure

```
backend/
├── app.py
├── agents/
│   ├── detect_agent.py
│   ├── classify_agent.py
│   ├── correct_agent.py
│   ├── roadmap_agent.py
│   └── recovery_agent.py
├── rag/
│   ├── rag_utils.py
│   └── rag_corpus.json
├── db.py
├── config.py
├── .env / secrets.toml
├── requirements.txt

frontend/
├── index.html
├── src/
│   ├── App.jsx
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   ├── Roadmap.jsx
│   │   └── Correction.jsx
│   └── components/
│       └── MisconceptionCard.jsx
├── tailwind.config.js
├── vite.config.js
└── .env
```

---

## 📦 Key Python Packages

| Package                    | Purpose                        |
| -------------------------- | ------------------------------ |
| Flask                      | Backend APIs                   |
| LangChain                  | Agent creation, RAG, memory    |
| faiss / chromadb           | Vector similarity search (RAG) |
| pymongo                    | MongoDB interaction            |
| dotenv/toml                | Secure config loading          |
| openai/google-generativeai | Gemini 1.5 Flash integration   |


---

## 📷 Demon video Drive link

link: https://drive.google.com/file/d/1XNBXBjfd1ZVC4OYXIlGnqq3_FuNHWp0n/view?usp=sharing 

---

## 📷 Screenshots

### 📥  Architecture

![Flow Screenshot](public/5ad0d9df-5674-4bf1-9438-de1f373c59e3.png)

### 📥  Flow

![Flow Screenshot](public/37664071-d840-46a4-9448-7368cd96e329.png)


### 📊 application View

![Dashboard Screenshot](public/application_long_screenshot.png)


---

## 🛠 Setup & Run

1. Clone the repo
2. Create `.env` or `secrets.toml` in `backend/`
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   npm install (in frontend folder)
   ```
4. Run backend:

   ```bash
   cd backend && python app.py
   ```
5. Run frontend:

   ```bash
   cd frontend && npm run dev
   ```

---

## 🤝 Contributions

Feel free to fork, improve, and submit a pull request. We welcome collaboration!

---

## 📄 License

MIT License

---

## ✨ Authors & Credits

Built by \[Your Team Name], powered by Gemini 1.5 Flash and LangChain.
