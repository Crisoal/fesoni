# 🛍️ Fesoni — Smart Product Discovery Engine

Fesoni is an AI-powered product discovery platform that helps users find brands, styles, and products that align with their cultural identity, aesthetic preferences, and personality — without using any personal or behavioral data.

Built for the **Qloo LLM Hackathon 2025**, Fesoni combines the **Qloo Taste AI™ API** with **GEMNINI API** to semantically map cultural preferences (like movies, music, fashion, and travel) to real-world products across domains like fashion, books, home decor, and wellness.

---

## 🌟 Key Features

- 🔮 **Taste Profiling via Chat:** Users describe themselves (e.g., “I love Afrobeats, Studio Ghibli, and minimalist design”), and GPT-4 + Qloo build a cultural taste graph.
- 🔗 **Qloo Integration:** Uses Qloo’s cross-domain affinities to expand cultural tastes across different lifestyle categories.
- 🎯 **Product Matching:** GPT-4 maps expanded taste signals to a curated or real product database (Amazon, Walmart, etc.)
- 🖼️ **Dynamic UI:** Clean, responsive frontend powered by React and styled-components.
- 🔒 **Privacy-First:** No behavioral tracking or personal history required — only cultural preferences.

---

## 🚀 Tech Stack

- **Frontend:** React.js (with Bootstrap or Tailwind)
- **Backend:** Node.js or Flask (for API middleware)
- **LLM:** GEMINI API
- **Cultural Intelligence:** Qloo Taste AI™ API
- **Product Data:** Curated JSON dataset or Amazon/Walmart Product API (Affiliate-based)

---

## 🧪 Sample Use Case

> **User Input:** “I love A24 films, ambient music, and Scandinavian furniture.”
>
> **Fesoni Response:**
> - COS clothing (Minimalist fashion)
> - MUBI subscription (Indie films)
> - Kinfolk magazine (Design lifestyle)
> - Norm Architects (Danish furniture)
> - Art books on surrealism and mood lighting playlists

---

## 🔑 Environment Variables (`.env`)

```env
REACT_APP_QLOO_API_KEY=your-qloo-api-key
REACT_APP_GEMINI_API_KEY=your-gemini-api-key
REACT_APP_AMAZON_ACCESS_KEY=your-amazon-access-key
REACT_APP_AMAZON_SECRET_KEY=your-amazon-secret-key
REACT_APP_AMAZON_ASSOCIATE_TAG=your-tag
REACT_APP_WALMART_API_KEY=your-walmart-key
