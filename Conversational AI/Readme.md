# 👔 Competitor Intelligence Agent - README

This is an agent-based Streamlit app that performs automated **competitor analysis for clothing stores** using **Gemini 1.5 Flash** and **AutoGen agents**.

---

## 🚀 Features

- 🤖 **Agentic Workflow** with 3 assistant agents:

  - `Research_Analyst`: Analyzes competitors and foot traffic
  - `Strategy_Consultant`: Recommends strategies based on data
  - `Report_Compiler`: Compiles a business-ready report

- 📊 **Customizable Analysis**

  - Location selection
  - Detail level: Summary / Detailed / Comprehensive
  - Number of competitors

- 📥 **Downloadable Markdown Reports**

---

## 🧠 How It Works

Agents communicate through a `GroupChat` using LangGraph’s `GroupChatManager`. Each agent receives prompts tailored to their role. The system uses Gemini 1.5 Flash via LangChain's `ChatGoogleGenerativeAI`.

The final output is a markdown-formatted business report containing:

- Competitor overview
- Market insights
- Strategic recommendations

---

## 🛠️ Installation

```bash
pip install -r requirements.txt
```

---

## 🔑 API Keys

This app uses Google Gemini via LangChain. Add your API key in the sidebar or set it as an environment variable:

```bash
export GOOGLE_API_KEY="your-gemini-api-key"
```

---

## ▶️ Usage

```bash
streamlit run competitor_analysis_agentic.py
```

Then:

- Enter your Gemini API key in the sidebar
- Set the location, number of competitors, and detail level
- Click **Generate Report**

---

## 📦 `requirements.txt`

```txt
autogen
google-generativeai
langchain-google-genai
langchain-core
streamlit
```

---

## 📄 Example Output

```
## Competitive Analysis: Koramangala, Bangalore

### 1. Competitor Overview
| Name | Type | Foot Traffic | Price Range |
|------|------|---------------|--------------|
| ...  | ...  | ...           | ...          |

### 2. Market Analysis
- Insight 1
- Insight 2

### 3. Strategic Recommendations
- Stay open late on weekends
- Focus on budget-conscious students

### 4. Executive Summary
Clear, concise recommendations for market leadership.
```

---

## 📌 Notes

- You can extend this framework for other industries (e.g., restaurants, salons)
- Consider adding persistent storage or PDF export in future iterations
