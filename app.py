import streamlit as st
from groq import Groq
from google import genai
import os
from dotenv import load_dotenv
import pypdf

# Configuration de la page Streamlit
st.set_page_config(page_title="PDF Chatbot", layout="wide", page_icon="💬")

# Charger les clés API depuis le fichier tok.env
load_dotenv(dotenv_path="tok.env")


# ==========================================
# 1. INTERFACE : LA BARRE LATÉRALE
# ==========================================
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Choix du modèle (Identifiants techniques mis à jour)
    model_selct = st.selectbox(
        "AI Modell", 
        ["Llama 3.3 70B (Groq)", "Mixtral 8x7B (Groq)", "Gemini 2.5 Flash (Google)"]
    )

    st.markdown("---")
    temperature = st.slider("Temperature (Creativity)", 0.0, 1.5, 0.7)

    # Zone d'importation STRICTEMENT réservée aux PDFs
    file_upload = st.file_uploader("Drag and Drop a File", type=["pdf"])

    if file_upload:
        st.success("Fichier PDF chargé avec succès !")
    else:
        st.info("Veuillez charger un fichier au format PDF uniquement.")


# Initialisation de la mémoire (Session State) pour le modèle choisi
if model_selct not in st.session_state:
    st.session_state[model_selct] = []

# Initialisation du client Groq
groq_client = None
if os.environ.get("GROQ_API_KEY"):
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Initialisation du client Google Gemini
# CODE CORRIGÉ (Force l'utilisation de la clé API)
google_client = None

# On récupère la clé soit depuis les secrets Streamlit, soit depuis l'environnemen

gemini_key = os.environ.get("GEMINI_API_KEY")

if gemini_key:
    # Passer api_key= ici coupe court à toute tentative d'authentification OAuth cloud
    google_client = genai.Client(api_key=gemini_key)


# ==========================================
# 2. FONCTION : EXTRACTION DE TEXTE DU PDF
# ==========================================
def extraire_texte_pdf(fichier_de_base):
    lecteur = pypdf.PdfReader(fichier_de_base)
    texte_total = ""
    for page in lecteur.pages:
        texte_de_la_page = page.extract_text()
        if texte_de_la_page:
            texte_total += texte_de_la_page + "\n"
    return texte_total


# ==========================================
# 3. MOTEURS IA : FONCTION DE RÉPONSE
# ==========================================
def ai_response(message_history):
    MODELS_MAPPING = {
        "Llama 3.3 70B (Groq)": {"source": "groq", "id": "llama-3.3-70b-versatile"},      
        "Mixtral 8x7B (Groq)": {"source": "groq", "id": "openai/gpt-oss-120b"}, 
        "Gemini 2.5 Flash (Google)": {"source": "google", "id": "gemini-2.5-flash"}
    }

    select_model = MODELS_MAPPING[model_selct]
    source = select_model["source"]
    model_id = select_model["id"]

    if source == "groq":
        if not groq_client:
            return "Erreur: La clé GROQ_API_KEY est manquante."
        try:
            completion = groq_client.chat.completions.create(
                model=model_id,
                messages=message_history,
                temperature=temperature
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Erreur Groq: {str(e)}"
    
    elif source == "google":
        if not google_client:
            return "Erreur: La clé GEMINI_API_KEY est manquante."
        try:
            # Pour Gemini, on lui envoie la dernière question ou le texte du PDF injecté
            derniere_question = message_history[-1]["content"]
            response = google_client.models.generate_content(
                model=model_id,
                contents=derniere_question,
            )
            return response.text
        except Exception as e:
            return f"Erreur Google Gemini: {str(e)}"


# ==========================================
# 4. AFFICHAGE : HISTORIQUE DU CHAT
# ==========================================
st.title(f"💬 ChatAI creer par GOJO avec les model de Groq")
st.info(f"Please use Mixtral 8x7B. It is the only model that I get the access!")

for message in st.session_state[model_selct]:
    # On n'affiche pas visuellement la consigne "system" contenant tout le texte du PDF
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# ==========================================
# 5. LOGIQUE : TRAITEMENT AUTOMATIQUE DU PDF
# ==========================================
if file_upload:
    # L'interrupteur intègre le modèle actuel pour éviter les conflits au changement de modèle
    cle_interrupteur = f"{file_upload.name}_{model_selct}_deja_lu"
    
    if cle_interrupteur not in st.session_state:
        with st.spinner("Analyse et lecture du document PDF..."):
            contenu_du_pdf = extraire_texte_pdf(file_upload)
            
            if contenu_du_pdf.strip():
                # On injecte le texte brut sous forme de rôle 'system' pour guider l'IA
                consigne_systeme = f"L'utilisateur a chargé un document PDF. Voici son contenu texte :\n\n{contenu_du_pdf}\n\nUtilise impérativement ces informations pour répondre aux questions de l'utilisateur."
                st.session_state[model_selct].append({"role": "system", "content": consigne_systeme})
                
                # Activation de l'interrupteur
                st.session_state[cle_interrupteur] = True
                st.success(f"Le document '{file_upload.name}' a été mémorisé avec succès !")
                with st.chat_message("assistant"):
                    with st.spinner("Analyse du contenu pour vous faire un résumé..."):
                        # On simule une question de l'utilisateur pour forcer l'IA à résumer immédiatement
                        prompt_resume = [{"role": "user", "content": "Fais-moi un résumé clair, structuré et concis de ce document en quelques puces."}]
                        # On fusionne temporairement la mémoire du PDF avec notre demande de résumé
                        analyse_ia = ai_response(st.session_state[model_selct] + prompt_resume)
                    
                    # On affiche le résumé intelligent
                    st.markdown("### 📝 Analyse initiale du document :")
                    st.write(analyse_ia)
                    
                    # Optionnel : On sauvegarde ce résumé dans le fil de discussion pour ne pas le perdre
                    st.session_state[model_selct].append({"role": "assistant", "content": analyse_ia})
                    
            else:
                st.error("Impossible d'extraire du texte de ce PDF. Vérifiez qu'il ne s'agit pas d'une image scannée.")


# ==========================================
# 6. ENTRÉE : ZONE DE TEXTE & ENVOI
# ==========================================
user_input = st.chat_input("Posez votre question sur le PDF ici...")

if user_input:
    # 1. Afficher et sauvegarder le message de l'utilisateur
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state[model_selct].append({"role": "user", "content": user_input})

    # 2. Demander la réponse à l'IA et l'afficher
    with st.chat_message("assistant"):
        with st.spinner("L'IA réfléchit..."):
            response = ai_response(st.session_state[model_selct])
        st.markdown(response)
        
    # 3. Sauvegarder la réponse de l'IA dans l'historique
    st.session_state[model_selct].append({"role": "assistant", "content": response})
