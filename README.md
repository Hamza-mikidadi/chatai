# 💬 Chatbot IA Multi-Modèles d'Analyse PDF

Bienvenue sur mon projet de Chatbot intelligent ! Cette application permet de charger un document PDF et d'en extraire instantanément un résumé ou de poser des questions interactives sur son contenu.

## 🚀 Tester l'application en direct
Cliquez sur le lien ci-dessous pour ouvrir et tester l'application directement dans votre navigateur (aucun téléchargement requis) :

👉👉 **[CLIQUEZ ICI POUR TESTER L'APPLICATION EN LIGNE](https://chatai-67yb.onrender.com)**


---

## 🛠️ Fonctionnalités & Technologies
- **Interface Utilisateur :** Développée en **Streamlit** pour une expérience fluide.
- **Moteurs d'IA (LLMs) :** Intégration de **Llama 3.3 70B** et **Mixtral** via l'API ultra-rapide de **Groq**, et de **Gemini 2.5 Flash** (Google).
- **Traitement de Documents :** Extraction de texte automatisée grâce à la bibliothèque Python **pypdf**.
- **Gestion de la Mémoire :** Conservation intelligente de l'historique de discussion par modèle grâce au `st.session_state`.
