
# 🎓 Personalized Learning Assistant

An intelligent assistant that generates **learning materials**, **quizzes**, and **project ideas** based on any topic and skill level using **Google Gemini AI** and **Serper API**. Built with Python, Streamlit, and CrewAI.

---

## 🚀 Features

- 🔍 **Searches curated learning materials** (videos, articles, exercises) for any topic  
- 📝 **Generates quizzes** to test understanding with multiple-choice questions  
- 🚧 **Suggests project ideas** based on user-selected skill level (Beginner, Intermediate, Advanced)  
- 🤖 Powered by **Gemini 1.5 Flash** for content generation  
- 🔎 Uses **Serper API** for real-time web searches  
- 🧠 Modular agent-based architecture via **CrewAI**  
- 💡 Clean and interactive UI built using **Streamlit**

---

## 📦 Tech Stack

- Python 🐍  
- [Streamlit](https://streamlit.io/)  
- [Google Gemini API](https://ai.google.dev/)  
- [Serper API](https://serper.dev/)  
- [CrewAI](https://docs.crewai.com/)  
- [LangChain](https://www.langchain.com/) (for Gemini LLM wrapper)

---

## 📁 Project Structure

```

├── main.py                # Main Streamlit app
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation

````

---

## 🔑 Environment Variables

Create a `.env` file in the root directory with the following:

```env
GEMINI_API_KEY=your_google_gemini_api_key
SERPER_API_KEY=your_serper_api_key
````

---

## ⚙️ Installation & Running Locally

1. **Clone the repo**

```bash
git clone https://github.com/your-username/personalized-learning-assistant.git
cd personalized-learning-assistant
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Add your `.env` file** (as shown above)

5. **Run the Streamlit app**

```bash
streamlit run main.py
```

---

## 🧪 Example Use Case

* **Topic:** Machine Learning
* **Level:** Intermediate
* ✅ You get:

  * Top videos, articles, and exercises on Machine Learning
  * 3 quiz questions to test your knowledge
  * 3 practical projects tailored for intermediate learners

---

## ✅ To-Do / Improvements

* [ ] Add user authentication to save progress
* [ ] Allow export to PDF or share learning path
* [ ] Enhance quiz with interactive inputs and score tracking
* [ ] Add more agent collaboration using CrewAI workflows

---

## 🙌 Acknowledgements

* [Google Generative AI](https://ai.google.dev/)
* [Serper API](https://serper.dev/)
* [CrewAI Framework](https://docs.crewai.com/)
* [Streamlit](https://streamlit.io/)
* [LangChain](https://www.langchain.com/)

---



