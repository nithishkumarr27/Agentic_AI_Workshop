# 📚 AI Study Assistant

A Streamlit app that transforms any study PDF into a **concise summary** and an **interactive quiz** using **Gemini 1.5 Flash**.

---

## 🚀 Features

- 📄 PDF text extraction
- ✍️ Bullet-point academic summary generation
- ❓ MCQ quiz generation with answer validation
- ✅ Interactive UI with result feedback and explanations
- 🔁 Retry feature for multiple quiz attempts

---

## 🛠️ Installation

```bash
git clone https://github.com/your-username/ai-study-assistant.git
cd ai-study-assistant
pip install -r requirements.txt
```

---

## 🔑 API Key Setup

This app uses **Google's Gemini API** via LangChain and Google GenAI SDK.
Set your API key in the script or export it in your terminal:

```bash
export GOOGLE_API_KEY="your-gemini-api-key"
```

Or directly configure inside the script:

```python
model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key="your-gemini-api-key",
    ...
)
```

---

## ▶️ Usage

```bash
streamlit run study_assistant.py
```

1. Upload a study-related PDF
2. Wait for summary and quiz to generate
3. Take the quiz and view your score and feedback
4. Retake the quiz as needed

---

## 📝 Example Output

### Summary

```markdown
- Artificial Intelligence (AI) enables machines to mimic human intelligence.
- Key types include Machine Learning, Deep Learning, and NLP.
- Supervised vs unsupervised learning differ in labeled data usage...
```

### Quiz JSON

```json
{
  "questions": [
    {
      "question": "What is the primary difference between supervised and unsupervised learning?",
      "options": {
        "A": "Supervised uses labeled data",
        "B": "Unsupervised uses labeled data",
        "C": "They are the same",
        "D": "None of the above"
      },
      "correct_answer": "A"
    }
  ]
}
```

---

## 📦 requirements.txt

```txt
streamlit
PyPDF2
google-generativeai
langchain-google-genai
```

---

## 📌 Notes

- Requires internet access and a valid Gemini API key
- Handles basic PDFs with extractable text (no OCR)
- JSON parsing is wrapped with error handling for resilience
- Great for students, educators, and self-learners

---

## 📄 License

MIT License – Open for use and modification
