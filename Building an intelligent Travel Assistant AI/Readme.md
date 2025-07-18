# 🌍 Intelligent Travel Assistant (Streamlit + LangChain + Gemini)

An interactive, intelligent travel assistant app built using **Streamlit**, **LangChain**, and **Gemini 2.5 Flash**. It fetches current weather, suggests top attractions, recommends accommodations, and offers travel tips — all in a structured, emoji-enhanced format.

---

## 🚀 Features

- Get **real-time weather** from WeatherAPI and OpenWeather
- Discover **top 5 attractions** with descriptions using DuckDuckGo
- Receive **custom hotel/stay recommendations** based on your travel style
- Structured response including:

  - Weather Report ☀️🌧️❄️
  - Top Attractions 🏰🏞️🎭
  - Where to Stay 🛏️🏨
  - Travel Tips 💡

- Uses **LangChain agents + tools**
- Powered by **Gemini 2.5 Flash** for LLM-based summarization and reasoning

---

## 🔧 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API Keys

In `app.py`, replace with your own keys:

```python
WEATHER_API_KEY = "your_weatherapi_key"
GEMINI_API_KEY = "your_google_api_key"
```

### 3. Run the App

```bash
streamlit run app.py
```

---

## 📄 requirements.txt

```txt
streamlit==1.36.0
langchain
langchain-community
langchain-core
google-generativeai
requests
```

---

## 🚨 Tools Used

- `get_current_weather(location)`: Live weather data via WeatherAPI/OpenWeather fallback
- `get_top_attractions(location)`: Summarizes DuckDuckGo results for top places
- `get_accommodation_recommendations(location, travel_style)`: Tailored stay suggestions

---

## 🤝 Technologies

- **Streamlit**: UI interface
- **LangChain**: Tool orchestration
- **Google Gemini**: LLM responses
- **DuckDuckGoSearchAPIWrapper**: Search results
- **WeatherAPI + OpenWeatherMap**: Weather data

---

## 📈 Sample Query

> "Plan a 3-day foodie trip to Chennai on a mid-range budget"

**Output Includes:**

- Weather Report
- Top 5 attractions with brief descriptions
- Recommended food-focused hotels/stays
- Travel tips customized to trip duration and style

---

## 🚀 Ready to Deploy

Perfect for travel agencies, itinerary generators, and personal AI travel planners.

**Author:** NITHISH KUMAR R
**License:** MIT
