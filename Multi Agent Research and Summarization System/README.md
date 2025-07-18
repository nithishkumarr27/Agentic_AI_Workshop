Here's your **updated full `README.md`** including the new `LangGraph` structure visualization using `st.expander()` and `st.graphviz_chart()`.

---

````markdown
# 🧠 Multi-Agent RAG System (LangGraph + Web + RAG + LLM)

This project implements an intelligent multi-agent research assistant using:

- 🔀 **LangGraph**: Orchestrate dynamic agent workflows
- 🧠 **Gemini 1.5 Flash**: Google LLM for generation and summarization
- 🔍 **DuckDuckGo Search**: Web search integration
- 📄 **RAG via FAISS**: Retrieval-augmented QA from local PDFs, DOCX, and TXT files
- 🧩 **Streamlit**: Intuitive UI with interactive elements

---

## 🖼️ LangGraph Structure

```python
with st.expander("🧩 LangGraph Structure"):
    st.graphviz_chart("""
    digraph {
        Router -> Web;
        Router -> RAG;
        Router -> LLM;
        Web -> Summarizer;
        RAG -> Summarizer;
        LLM -> Summarizer;
    }
    """)
````

This illustrates the flow:

* Query goes through `Router`
* Based on classification, it’s sent to `Web`, `RAG`, or `LLM`
* All paths end at the `Summarizer` node which produces the final output

---

## 🗂 Folder Structure

```
.
├── app.py                # Main Streamlit app
├── my_docs/              # Folder for local PDFs, DOCX, and TXT files
├── .env                  # Environment file containing your Gemini API key
├── README.md             # This file
└── requirements.txt      # Python dependencies
```

---

## ⚙️ Setup Instructions

### 1. 🔑 Environment Setup

Create a `.env` file in the root folder:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

> You can obtain your Gemini API key from [https://makersuite.google.com/app](https://makersuite.google.com/app)

---

### 2. 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

#### Sample `requirements.txt`:

```txt
streamlit
pdfplumber
python-docx
langchain
langgraph
faiss-cpu
duckduckgo-search
python-dotenv
google-generativeai
```

---

### 3. 🏁 Run the Application

```bash
streamlit run app.py
```

---

## 💡 Features

* 🔍 **Ask Anything**: Input a query, get routed to Web, RAG, or LLM
* 🧠 **Automatic Routing**: Classifies queries for best agent path
* 📄 **Document Ingestion**: Reads from local `my_docs/` folder
* 🔎 **Semantic Retrieval**: Uses FAISS + Gemini embeddings
* ✨ **Concise Summarization**: Generates final answers with Gemini LLM
* 🌐 **Live Web Search**: If query needs real-time info

---

## ✏️ Sample Queries

* What is LangGraph?
* Summarize my document on AI safety.
* What's the latest in generative AI?
* Find points from the uploaded PDF on machine learning.

---

## 🔍 How It Works

1. **File Loader**

   * Supports `.pdf`, `.docx`, and `.txt` formats
   * Loads and splits into chunks using LangChain's `RecursiveCharacterTextSplitter`

2. **Vector Store (FAISS)**

   * Embeds content using Gemini Embeddings (`models/embedding-001`)
   * Enables semantic search with `retriever.as_retriever()`

3. **LangGraph Workflow**

   * Router determines query type
   * Three agents: `web_agent`, `rag_agent`, `llm_agent`
   * Summary produced by `summarizer_agent`

4. **Streamlit Interface**

   * User types a query
   * Results are displayed interactively with visual workflow structure

---

## ⚠️ Troubleshooting

* **API Key Not Found**: Ensure `.env` exists and key is valid.
* **No Documents Loaded**: Make sure `my_docs/` contains valid PDF, DOCX, or TXT files.
* **Web Search Errors**: Check internet and `duckduckgo-search` installation.

---

## 🧪 Future Improvements

* Memory and follow-up questions (conversation state)
* File upload UI inside Streamlit
* PDF OCR (scanned documents)
* Chat-style interface

---

## 👤 Author

Built by **NITHISH KUMAR R**
Powered by OpenAI, LangGraph, Google Generative AI, and Streamlit

---
