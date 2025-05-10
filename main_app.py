

# # medical_rag_chatbot/main_app.py

# import streamlit as st
# import os
# from dotenv import load_dotenv
# import re
# from datetime import datetime

# # --- Define SCRIPT_DIR, ASSETS_DIR, DATA_DIR first for robustness ---
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
# DATA_DIR = os.path.join(SCRIPT_DIR, "data")

# # Make sure rag_pipeline and utils are found by adding SCRIPT_DIR to sys.path
# import sys
# if SCRIPT_DIR not in sys.path: # Avoid adding duplicates if already there
#     sys.path.append(SCRIPT_DIR)

# # Now try to import from rag_pipeline
# # This assumes rag_pipeline.py is in the SCRIPT_DIR
# try:
#     from rag_pipeline import load_and_process_pdf, query_rag_pipeline, get_existing_vector_store, OPENAI_API_KEY
# except ImportError as e:
#     st.error(
#         f"Critical Error: Could not import modules from 'rag_pipeline.py'. "
#         f"Please ensure 'rag_pipeline.py' and 'utils.py' are in the same directory as 'main_app.py' ({SCRIPT_DIR}) "
#         f"and all dependencies are installed. Specific error: {e}"
#     )
#     st.stop()
# # utils.py is implicitly used by rag_pipeline.py

# # --- Page Configuration ---
# favicon_path = os.path.join(ASSETS_DIR, "favicon.png")
# st.set_page_config(
#     page_title="TATA md AI Medical Advisor",
#     page_icon=favicon_path if os.path.exists(favicon_path) else "🩺",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

# # --- Define Theme Colors ---
# bg_color = "#141E30" 
# text_color_yellow = "#FFFACD" 
# text_color_blue = "#87CEFA"   
# primary_accent_pink = "#FF3CAC"  
# secondary_accent_blue = "#2B86C5" 
# secondary_accent_purple = "#784BA0" 
# dark_theme_bg_accent = "#243B55" 
# highlight_color_medication = "#FFB74D" 
# highlight_color_positive_icon = "#66BB6A" 
# highlight_color_negative_icon = "#EF5350" 
# expander_header_bg_color = f"linear-gradient(135deg, rgba(255, 60, 172, 0.4) 0%, rgba(43, 134, 197, 0.5) 100%)"
# expander_content_bg_color = f"rgba(43, 134, 197, 0.15)"
# card_bg_color = f"rgba({int(secondary_accent_blue[1:3], 16)}, {int(secondary_accent_blue[3:5], 16)}, {int(secondary_accent_blue[5:7], 16)}, 0.4)"
# card_border_color = f"rgba({int(primary_accent_pink[1:3], 16)}, {int(primary_accent_pink[3:5], 16)}, {int(primary_accent_pink[5:7], 16)}, 0.3)"
# analysis_done_chat_bg = f"rgba({int(secondary_accent_blue[1:3], 16)}, {int(secondary_accent_blue[3:5], 16)}, {int(secondary_accent_blue[5:7], 16)}, 0.25)"

# # --- Custom CSS ---
# st.markdown(f"""
# <style>
#     /* Base styles - Default text is Yellow */
#     body, .stApp, .stChatInput, .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {{
#         background-color: {bg_color} !important; 
#         background-image: linear-gradient(to bottom right, {bg_color}, {dark_theme_bg_accent}) !important;
#         color: {text_color_yellow} !important;
#         font-family: 'Inter', sans-serif;
#     }}
#     p, li, span, div {{
#         color: {text_color_yellow};
#     }}
#     a, a:visited {{
#         color: {text_color_blue} !important;
#         text-decoration: none;
#     }}
#     a:hover {{
#         color: #5DADE2 !important; /* secondary_accent_blue_lighter */
#         text-decoration: underline;
#     }}

#     .gradient-text {{
#         background: linear-gradient(90deg, {primary_accent_pink} 0%, {secondary_accent_purple} 50%, {secondary_accent_blue} 100%);
#         -webkit-background-clip: text;
#         -webkit-text-fill-color: transparent;
#         background-clip: text;
#         font-weight: 800;
#     }}

#     .main-header {{ font-size: 3.0rem; font-weight: 700; margin-bottom: 0.5rem; text-align: center; }}
#     .sub-header {{ font-size: 1.1rem; color: {text_color_blue} !important; opacity: 0.9; text-align: center; margin-bottom: 2rem; }}

#     .section-header {{
#         font-size: 2.0rem;
#         color: {primary_accent_pink} !important; 
#         margin-top: 2.5rem;
#         margin-bottom: 1.5rem;
#         font-weight: 700;
#         text-align: center;
#         text-shadow: 0 0 8px rgba({int(primary_accent_pink[1:3],16)}, {int(primary_accent_pink[3:5],16)}, {int(primary_accent_pink[5:7],16)}, 0.3);
#     }}
    
#     .stChatMessage {{
#         background: {card_bg_color}; 
#         backdrop-filter: blur(10px);
#         -webkit-backdrop-filter: blur(10px);
#         border-radius: 0.8rem;
#         border: 1px solid {card_border_color}; 
#         padding: 1.2rem 1.8rem;
#         margin-bottom: 1.2rem;
#         box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
#     }}
#      .stChatMessage p, .stChatMessage li, .stChatMessage span, .stChatMessage div {{
#         color: {text_color_yellow} !important; 
#     }}

#     div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message {{
#         background: {analysis_done_chat_bg} !important; 
#         border: 1px solid {secondary_accent_blue} !important;
#         padding: 1rem; 
#         border-radius: 0.5rem; 
#         margin: -0.2rem -0.8rem; /* Adjust to better fit within chat message padding */
#     }}
#     div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message *,
#     div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message p,
#     div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message li,
#     div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message span {{
#         color: {text_color_yellow} !important; 
#     }}

#     .highlight-disease {{
#         color: {text_color_yellow} !important; 
#         font-weight: bold;
#         font-size: 1.4em;
#         display: block;
#         text-align: center;
#         margin-bottom: 0.75rem;
#         padding: 0.3rem;
#         border-radius: 5px;
#     }}
    
#     .highlight-medication {{
#         color: {highlight_color_medication} !important; 
#         font-weight: bold;
#         background-color: rgba(255, 183, 77, 0.15);
#         padding: 0.1em 0.3em;
#         border-radius: 3px;
#     }}

#     .treatment-guidance-subheader {{
#         font-size: 1.2rem;
#         font-weight: bold;
#         margin-top: 0.8rem;
#         margin-bottom: 0.6rem;
#         padding-bottom: 0.4rem;
#         border-bottom: 1px solid {card_border_color}; 
#     }}
#     .pharma-header {{ color: {text_color_blue} !important; }} 
#     .lifestyle-header {{ color: {text_color_blue} !important; }} 
#     .dietary-header {{ color: {text_color_yellow} !important; }} 
#     .dos-donts-header {{ color: {text_color_blue} !important; }} 
#     .redflags-header {{ color: {primary_accent_pink} !important; }} 

#     .symptoms-analyzed-box {{
#         background-color: rgba(20, 30, 48, 0.6);
#         border: 1px solid {secondary_accent_blue}; 
#         border-radius: 8px;
#         padding: 12px 15px;
#         margin-bottom: 18px;
#         font-size: 0.95em;
#     }}
#     .symptoms-analyzed-box b {{ color: {text_color_blue} !important; font-weight: 700; }}
#     .symptom-item {{
#         display: inline-block;
#         background-color: {secondary_accent_blue};
#         color: {text_color_yellow} !important; 
#         padding: 4px 10px;
#         border-radius: 15px;
#         margin: 4px;
#         font-size: 0.9em;
#         border: 1px solid {primary_accent_pink}; 
#     }}

#     .disclaimer-box {{
#         background-color: rgba(36, 59, 85, 0.3);
#         border: 1px dashed {primary_accent_pink}; 
#         color: {text_color_blue} !important; 
#         padding: 1rem;
#         border-radius: 0.5rem;
#         margin-top: 1.5rem;
#         font-size: 0.85em;
#     }}
#     .disclaimer-box i b {{ color: {primary_accent_pink} !important; }}

#     .stButton > button {{
#         background: linear-gradient(90deg, {primary_accent_pink} 0%, {secondary_accent_purple} 100%);
#         color: {text_color_yellow} !important; 
#         border: none;
#         border-radius: 0.5rem;
#         padding: 0.7rem 1.5rem;
#         font-weight: 600;
#         transition: all 0.3s ease;
#         box-shadow: 0 2px 5px rgba(0,0,0,0.2);
#     }}
#     .stButton > button:hover {{
#         transform: translateY(-3px) scale(1.03);
#         box-shadow: 0 12px 25px rgba(0, 0, 0, 0.25);
#         filter: brightness(1.1);
#     }}
    
#     div[data-testid="stFileUploader"] section {{
#          background-color: {card_bg_color}; 
#          border: 1px dashed {primary_accent_pink}; 
#          border-radius: 0.5rem;
#          padding: 1rem;
#     }}
#      div[data-testid="stFileUploader"] section small {{ color: {text_color_blue} !important; }}

#     .stProgress > div > div > div {{
#         background: linear-gradient(90deg, {primary_accent_pink} 0%, {secondary_accent_purple} 100%);
#     }}

#     .stChatInput > div > div > textarea {{
#         background-color: {card_bg_color}; 
#         border: 1px solid {card_border_color}; 
#         border-radius: 0.5rem;
#         color: {text_color_yellow} !important; 
#         padding: 1rem;
#         box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
#     }}
#     .stChatInput > div > div > textarea:focus {{
#         border: 1px solid {primary_accent_pink};
#         box-shadow: 0 0 0 3px rgba({int(primary_accent_pink[1:3],16)},{int(primary_accent_pink[3:5],16)},{int(primary_accent_pink[5:7],16)},0.25);
#     }}

#     section[data-testid="stSidebar"] > div:first-child {{ 
#         background-color: {bg_color} !important; 
#         background-image: linear-gradient(to bottom right, {bg_color}, {dark_theme_bg_accent}) !important;
#         border-right: 1px solid {card_border_color} !important; 
#     }}
#     section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
#     section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] li,
#     section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] span,
#     section[data-testid="stSidebar"] label, 
#     section[data-testid="stSidebar"] div[data-baseweb="input"] > div,
#     section[data-testid="stSidebar"] {{ 
#         color: {text_color_yellow} !important; 
#     }}
#     section[data-testid="stSidebar"] a {{ color: {text_color_blue} !important; }}
#     section[data-testid="stSidebar"] .stHeadingContainer h2 {{ 
#         text-align: center;
#         color: {primary_accent_pink} !important; 
#     }}
#     section[data-testid="stSidebar"] .stImage {{ 
#         margin-left: auto; 
#         margin-right: auto; 
#         display: block; 
#     }}
#     section[data-testid="stSidebar"] .stButton > button {{ 
#         background: linear-gradient(90deg, {primary_accent_pink} 0%, {secondary_accent_purple} 100%);
#         color: {text_color_yellow} !important; 
#     }}
#     section[data-testid="stSidebar"] .stAlert {{ 
#         border-radius: 0.5rem;
#         border-left-width: 5px !important;
#         background-color: rgba(0,0,0,0.3) !important; 
#         margin-left: 0.5rem; 
#         margin-right: 0.5rem;
#     }}
#     section[data-testid="stSidebar"] .stAlert p {{ color: {text_color_yellow} !important; }}
#     section[data-testid="stSidebar"] .stAlert[data-baseweb="alert"][role="status"] {{ border-left-color: #4CAF50 !important; }}
#     section[data-testid="stSidebar"] .stAlert[data-baseweb="alert"][role="note"] {{ border-left-color: {secondary_accent_blue} !important; }}
#     section[data-testid="stSidebar"] .stAlert[data-baseweb="alert"][role="alert"] {{ border-left-color: #F44336 !important; }}

#     .streamlit-expanderHeader {{
#         background: {expander_header_bg_color} !important; 
#         backdrop-filter: blur(8px); 
#         -webkit-backdrop-filter: blur(8px);
#         border-radius: 0.7rem !important;
#         color: {text_color_yellow} !important; 
#         border: 1px solid {card_border_color} !important; 
#         padding: 0.9rem 1.2rem !important;
#         font-weight: 600;
#         box-shadow: 0 2px 10px rgba(0,0,0,0.1);
#     }}
#     .streamlit-expanderContent {{
#         background-color: {expander_content_bg_color} !important; 
#         backdrop-filter: blur(12px); 
#         -webkit-backdrop-filter: blur(12px);
#         border-radius: 0 0 0.7rem 0.7rem !important;
#         border: 1px solid {card_border_color} !important; 
#         border-top: none !important;
#         padding: 1.5rem;
#     }}
#     .streamlit-expanderContent p, .streamlit-expanderContent li, .streamlit-expanderContent span, .streamlit-expanderContent div {{
#         color: {text_color_yellow} !important; 
#     }}
#     .streamlit-expanderContent strong {{
#         color: {text_color_blue} !important; 
#     }}
#     .streamlit-expanderHeader > div > svg {{ 
#         fill: {text_color_yellow} !important; 
#     }}

#     #MainMenu {{visibility: hidden;}}
#     footer {{visibility: hidden;}}

#     ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
#     ::-webkit-scrollbar-track {{ background: rgba(20, 30, 48, 0.3); border-radius: 10px; }}
#     ::-webkit-scrollbar-thumb {{
#         background: linear-gradient(180deg, {primary_accent_pink} 0%, {secondary_accent_purple} 100%);
#         border-radius: 10px;
#         border: 2px solid rgba(20, 30, 48, 0.3);
#     }}
#     ::-webkit-scrollbar-thumb:hover {{
#         background: linear-gradient(180deg, {primary_accent_pink} 30%, {secondary_accent_purple} 100%);
#         filter: brightness(1.2);
#     }}

#     .dos-list ul, .donts-list ul {{ list-style-type: none; padding-left: 0; }}
#     .dos-list li::before {{ content: '👍'; color: {highlight_color_positive_icon}; font-weight: bold; display: inline-block; width: 1.5em; margin-left: -1.5em; }}
#     .dos-list li {{ color: {text_color_yellow} !important; }} 
#     .donts-list li::before {{ content: '👎'; color: {highlight_color_negative_icon}; font-weight: bold; display: inline-block; width: 1.5em; margin-left: -1.5em; }}
#     .donts-list li {{ color: {text_color_yellow} !important; }} 
#     .foods-eat-list ul, .foods-avoid-list ul {{ list-style-type: none; padding-left: 0; }}
#     .foods-eat-list li::before {{ content: '✅ '; color: {highlight_color_positive_icon}; font-weight: bold; }}
#     .foods-eat-list li {{ color: {text_color_yellow} !important; }} 
#     .foods-avoid-list li::before {{ content: '❌ '; color: {highlight_color_negative_icon}; font-weight: bold; }}
#     .foods-avoid-list li {{ color: {text_color_yellow} !important; }} 
#     .foods-eat-list-title, .foods-avoid-list-title {{ color: {text_color_yellow} !important; }}
#     .dos-list-title, .donts-list-title {{ color: {text_color_blue} !important; }}
# </style>
# """, unsafe_allow_html=True)


# # --- Load Environment Variables ---
# load_dotenv() 
# if not OPENAI_API_KEY: 
#     st.error("OpenAI API key not found. Please set it in your .env file or environment variables.")
#     st.stop()

# # --- Create Data and Assets Directories if they don't exist ---
# if not os.path.exists(DATA_DIR):
#     os.makedirs(DATA_DIR)
# if not os.path.exists(ASSETS_DIR):
#     os.makedirs(ASSETS_DIR)

# # --- Session State Initialization ---
# if "vector_store_loaded" not in st.session_state:
#     st.session_state.vector_store_loaded = False
# if "vector_store" not in st.session_state:
#     st.session_state.vector_store = None
# if "processed_pdf_name" not in st.session_state:
#     st.session_state.processed_pdf_name = None
# if "messages" not in st.session_state:
#     st.session_state["messages"] = [{"role": "assistant", "content": "Welcome! Please upload a medical reference PDF to begin."}]


# # --- Helper Function to Parse LLM Response ---
# def parse_llm_response(response_text):
#     parsed_data = {
#         "predicted_disease": "Not specified by AI.",
#         "reasoning": "Reasoning not provided or an error occurred parsing the response.",
#         "pharmacological": "Pharmacological information not found in provided documents. Consult a healthcare professional.",
#         "non_pharmacological_lifestyle": "Lifestyle guidance not found in provided documents. Consult a healthcare professional.",
#         "dietary_recommendations": "Dietary advice not found in provided documents. Consult a healthcare professional.",
#         "foods_to_eat": "", 
#         "foods_to_avoid": "",
#         "general_dos_donts": "General Do's & Don'ts not found in provided documents. Consult a healthcare professional.",
#         "dos": "", 
#         "donts": "",
#         "when_to_seek_help": "If symptoms are severe, worsen rapidly, or if you have concerns, consult a medical professional immediately.",
#         "disclaimer": "This AI-generated information is for educational purposes only and NOT a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider."
#     }
#     # Regex patterns to find sections
#     disease_match = re.search(r"\*\*Predicted Disease:\*\*\s*(.*?)(?=\n\s*\*\*Reasoning:\*\*|\n\n|\Z)", response_text, re.DOTALL | re.IGNORECASE)
#     if disease_match: parsed_data["predicted_disease"] = disease_match.group(1).strip()

#     reasoning_match = re.search(r"\*\*Reasoning:\*\*\s*(.*?)(?=\n\s*\*\*Treatment Guidance:\*\*|\n\n|\Z)", response_text, re.DOTALL | re.IGNORECASE)
#     if reasoning_match: parsed_data["reasoning"] = reasoning_match.group(1).strip()

#     treatment_guidance_match = re.search(r"\*\*Treatment Guidance:\*\*\s*(.*?)(?=\n\s*\*\*Disclaimer:\*\*|\n\n|\Z)", response_text, re.DOTALL | re.IGNORECASE)
#     if treatment_guidance_match:
#         treatment_text = treatment_guidance_match.group(1).strip()

#         pharma_match = re.search(r"\*\*Pharmacological(?: \(Medications\))?:\*\*\s*(.*?)(?=\n\s*\*\*Non-Pharmacological & Lifestyle:\*\*|\n\n|\Z)", treatment_text, re.DOTALL | re.IGNORECASE)
#         if pharma_match: parsed_data["pharmacological"] = pharma_match.group(1).strip()

#         non_pharma_match = re.search(r"\*\*Non-Pharmacological & Lifestyle:\*\*\s*(.*?)(?=\n\s*\*\*Dietary Recommendations:\*\*|\n\n|\Z)", treatment_text, re.DOTALL | re.IGNORECASE)
#         if non_pharma_match: parsed_data["non_pharmacological_lifestyle"] = non_pharma_match.group(1).strip()

#         diet_match_full = re.search(r"\*\*Dietary Recommendations:\*\*\s*(.*?)(?=\n\s*\*\*General Do's & Don'ts:\*\*|\n\n|\Z)", treatment_text, re.DOTALL | re.IGNORECASE)
#         if diet_match_full:
#             diet_text_full = diet_match_full.group(1).strip()
#             parsed_data["dietary_recommendations"] = diet_text_full # Store the full block as fallback
            
#             eat_match = re.search(r"\*\*Foods to Eat:\*\*\s*(.*?)(?=\n\s*\*\*Foods to Avoid:\*\*|\n\n|\Z)", diet_text_full, re.DOTALL | re.IGNORECASE)
#             if eat_match: 
#                 parsed_data["foods_to_eat"] = "\n".join([item.strip().lstrip("-* ").strip() for item in eat_match.group(1).strip().splitlines() if item.strip().lstrip("-* ").strip()])
            
#             avoid_match = re.search(r"\*\*Foods to Avoid:\*\*\s*(.*?)(?:\n\n|\Z)", diet_text_full, re.DOTALL | re.IGNORECASE) # Avoid matching beyond this section
#             if avoid_match: 
#                 parsed_data["foods_to_avoid"] = "\n".join([item.strip().lstrip("-* ").strip() for item in avoid_match.group(1).strip().splitlines() if item.strip().lstrip("-* ").strip()])
        
#         dos_donts_full_match = re.search(r"\*\*General Do's & Don'ts:\*\*\s*(.*?)(?=\n\s*\*\*When to Seek Professional Help(?: \(Red Flags\))?:\*\*|\n\n|\Z)", treatment_text, re.DOTALL | re.IGNORECASE)
#         if dos_donts_full_match:
#             dos_donts_text_full = dos_donts_full_match.group(1).strip()
#             parsed_data["general_dos_donts"] = dos_donts_text_full # Store full block as fallback

#             do_match = re.search(r"\*\*Do(?:'s)?:\*\*\s*(.*?)(?=\n\s*\*\*Don't(?:s)?:\*\*|\n\n|\Z)", dos_donts_text_full, re.DOTALL | re.IGNORECASE)
#             if do_match: 
#                 parsed_data["dos"] = "\n".join([item.strip().lstrip("-* ").strip() for item in do_match.group(1).strip().splitlines() if item.strip().lstrip("-* ").strip()])
            
#             dont_match = re.search(r"\*\*Don't(?:s)?:\*\*\s*(.*?)(?:\n\n|\Z)", dos_donts_text_full, re.DOTALL | re.IGNORECASE) # Avoid matching beyond this section
#             if dont_match: 
#                 parsed_data["donts"] = "\n".join([item.strip().lstrip("-* ").strip() for item in dont_match.group(1).strip().splitlines() if item.strip().lstrip("-* ").strip()])

#         seek_help_match = re.search(r"\*\*When to Seek Professional Help(?: \(Red Flags\))?:\*\*\s*(.*?)(?:\n\n|\Z)", treatment_text, re.DOTALL | re.IGNORECASE)
#         if seek_help_match: parsed_data["when_to_seek_help"] = seek_help_match.group(1).strip()
    
#     disclaimer_llm_match = re.search(r"\*\*Disclaimer:\*\*\s*(.*?)(?:\n\n|\Z)", response_text, re.DOTALL | re.IGNORECASE)
#     if disclaimer_llm_match: parsed_data["disclaimer"] = disclaimer_llm_match.group(1).strip()

#     return parsed_data

# # --- Functions ---
# def initialize_vector_store():
#     vs = get_existing_vector_store()
#     if vs:
#         st.session_state.vector_store = vs
#         st.session_state.vector_store_loaded = True
#         st.session_state.processed_pdf_name = "Previously processed medical texts"
#         if len(st.session_state.messages) == 1 and "Welcome!" in st.session_state.messages[0]["content"]:
#             st.session_state.messages[0] = {"role": "assistant", "content": "Welcome! Medical knowledge base active. How can I assist with your symptoms?"}


# # --- UI Layout ---
# st.markdown(f"""
# <div style="text-align: center; padding-top: 2rem; padding-bottom: 1rem;">
#     <h1 class='main-header'><span class='gradient-text'>TATA md AI Medical Advisor</span></h1>
#     <p class='sub-header'>
#         Leveraging medical literature to offer insights on symptoms. <br>
#         <em>This tool provides information for educational purposes only and is not a substitute for professional medical advice.</em>
#     </p>
# </div>
# """, unsafe_allow_html=True)

# # --- Sidebar ---
# with st.sidebar:
#     logo_path = os.path.join(ASSETS_DIR, "tatmd.png") 
#     default_logo_url = "https://www.tatamd.com/images/logo_TATA%20MD.svg"

#     if os.path.exists(logo_path):
#         st.image(logo_path, width=180, use_container_width=True) 
#     else:
#         st.markdown(f"""
#             <div style="text-align: center; margin-bottom: 1rem;">
#                 <img src="{default_logo_url}" 
#                      alt="TATA MD Logo" 
#                      style="width: 180px; margin-bottom: 10px;"
#                      onerror="this.style.display='none'; this.parentElement.innerHTML+='<p style=\'color:{text_color_yellow};\'>TATA MD Logo (fallback)</p>';"> 
#             </div>
#         """, unsafe_allow_html=True)

#     st.markdown(f"<h2 style='text-align: center; color: {primary_accent_pink}; margin-bottom: 1rem;'>Knowledge Base</h2>", unsafe_allow_html=True)

#     if not st.session_state.vector_store_loaded and st.session_state.vector_store is None:
#         with st.spinner("Checking for existing knowledge base..."):
#             initialize_vector_store()

#     if st.session_state.vector_store_loaded:
#         st.success(f"Active KB: {st.session_state.processed_pdf_name or 'Loaded'}")
#     else:
#         st.info("Upload a PDF to activate the Knowledge Base.")

#     uploaded_file_sb = st.file_uploader("Upload Medical Reference (PDF)", type="pdf", key="pdf_uploader_sidebar")

#     if st.button("Process PDF & Build KB", key="process_button_sidebar", help="Upload and process a new PDF to create or update the knowledge base."):
#         if uploaded_file_sb is not None:
#             file_path = os.path.join(DATA_DIR, uploaded_file_sb.name)
#             with open(file_path, "wb") as f: f.write(uploaded_file_sb.getbuffer())
            
#             with st.spinner(f"Processing {uploaded_file_sb.name}... This may take a while."):
#                 st.session_state.vector_store = None 
#                 st.session_state.vector_store_loaded = False
#                 st.session_state.processed_pdf_name = None
                
#                 processed_vs = load_and_process_pdf(file_path) # From rag_pipeline.py
                
#                 if processed_vs:
#                     st.session_state.vector_store = processed_vs
#                     st.session_state.vector_store_loaded = True
#                     st.session_state.processed_pdf_name = uploaded_file_sb.name
#                     st.session_state.messages = [{"role": "assistant", "content": f"Knowledge base from '{uploaded_file_sb.name}' is ready. How can I assist?"}]
#                 else:
#                     st.session_state.messages = [{"role": "assistant", "content": f"Failed to process '{uploaded_file_sb.name}'. Please try again or use a different PDF."}]
#                     st.error(f"Failed to process '{uploaded_file_sb.name}'.")
#             st.rerun()
#         else:
#             st.warning("Please upload a PDF file first.")

#     st.markdown("---")
#     st.markdown(f"<p style='font-size: 0.8em; text-align: center; opacity: 0.7; color: {text_color_blue} !important;'>Powered by Advanced AI</p>", unsafe_allow_html=True)


# # --- Main Chat Interface ---
# st.markdown("<div class='section-header'>Symptom Analysis & Guidance</div>", unsafe_allow_html=True)

# chat_container = st.container()
# with chat_container:
#     for i, msg in enumerate(st.session_state.messages):
#         is_structured_response = isinstance(msg["content"], dict) and "predicted_disease" in msg["content"]
        
#         with st.chat_message(msg["role"], avatar="🧑‍⚕️" if msg["role"] == "assistant" else "👤"):
#             if msg["role"] == "user":
#                 st.markdown(f"<div style='text-align: right; color: {text_color_yellow} !important; padding: 0.5rem;'>{msg['content']}</div>", unsafe_allow_html=True)
            
#             elif is_structured_response:
#                 # Apply the .analysis-complete-message class to this wrapping div
#                 st.markdown("<div class='analysis-complete-message'>", unsafe_allow_html=True) 
#                 data = msg["content"]

#                 symptoms_input_string = data.get("symptoms_input", "")
#                 if symptoms_input_string:
#                     symptom_list = [s.strip() for s in symptoms_input_string.split(',') if s.strip()]
#                     if not symptom_list and symptoms_input_string:
#                         symptom_list = [s.strip() for s in symptoms_input_string.splitlines() if s.strip()]
#                     if not symptom_list and symptoms_input_string:
#                         symptom_list = [symptoms_input_string.strip()]
                    
#                     symptoms_html_items = "".join([f"<div class='symptom-item'>{symptom}</div>" for symptom in symptom_list])
#                     symptoms_box_html = f"""
#                     <div class='symptoms-analyzed-box'>
#                         <b>Symptoms Analyzed:</b>
#                         {symptoms_html_items}
#                     </div>
#                     """
#                     st.markdown(symptoms_box_html, unsafe_allow_html=True)

#                 st.markdown(f"##### <span class='highlight-disease'>{data.get('predicted_disease', 'Not specified by AI.')}</span>", unsafe_allow_html=True)
                
#                 reasoning_content = data.get('reasoning', 'Reasoning not provided.')
#                 default_reasoning_phrases = ["AI could not provide specific reasoning.", "AI could not provide specific reasoning based on the context.", "Reasoning not provided or an error occurred parsing the response."]
#                 if reasoning_content and reasoning_content.strip() not in default_reasoning_phrases:
#                     with st.expander("View Reasoning", expanded=False):
#                         st.markdown(reasoning_content) 
#                 else:
#                     st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{reasoning_content}</p>", unsafe_allow_html=True)

#                 st.markdown(f"<hr style='border-color: {card_border_color}; margin-top:1rem; margin-bottom:1rem;'>", unsafe_allow_html=True)
#                 st.markdown(f"<h4 style='color: {text_color_yellow}; text-align:center; margin-bottom:1rem;'>Treatment Guidance</h4>", unsafe_allow_html=True)

#                 # Pharmacological
#                 with st.expander("💊 Pharmacological (Medications)", expanded=True):
#                     st.markdown(f"<div class='treatment-guidance-subheader pharma-header'>Medications</div>", unsafe_allow_html=True)
#                     pharma_text = data.get('pharmacological', "Pharmacological information not found in provided documents. Consult a healthcare professional.")
#                     pharma_text_highlighted = re.sub(
#                         r'\b([A-Z][a-zA-Z0-9\-\(\)]*\s?(?:[A-Z][a-zA-Z0-9\-\(\)]*)*\s?\d*\s?(?:mg|mcg|ml|IU|grams|units|tablets|capsules|puffs|drops|applications|patches)?)\b', 
#                         r"<span class='highlight-medication'>\1</span>", 
#                         pharma_text
#                     )
#                     st.markdown(pharma_text_highlighted, unsafe_allow_html=True)

#                 # Non-Pharmacological & Lifestyle
#                 default_lifestyle_msg = "Lifestyle guidance not found in provided documents. Consult a healthcare professional."
#                 with st.expander("🌿 Non-Pharmacological & Lifestyle"):
#                     st.markdown(f"<div class='treatment-guidance-subheader lifestyle-header'>Lifestyle & Home Care</div>", unsafe_allow_html=True)
#                     lifestyle_content = data.get('non_pharmacological_lifestyle', default_lifestyle_msg).strip()
#                     if not lifestyle_content or lifestyle_content == default_lifestyle_msg or "not found" in lifestyle_content.lower():
#                          st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{default_lifestyle_msg}</p>", unsafe_allow_html=True)
#                     else:
#                         st.markdown(lifestyle_content)

#                 # Dietary Recommendations
#                 default_diet_msg = "Dietary advice not found in provided documents. Consult a healthcare professional."
#                 with st.expander("🥗 Dietary Recommendations"):
#                     st.markdown(f"<div class='treatment-guidance-subheader dietary-header'>Dietary Advice</div>", unsafe_allow_html=True)
#                     foods_eat_md = ""; foods_avoid_md = ""
#                     if data.get("foods_to_eat"):
#                         foods_eat_md = f"<strong class='foods-eat-list-title'>Foods to Eat:</strong>\n<div class='foods-eat-list'><ul>" + "".join([f"<li>{item.strip()}</li>" for item in data.get("foods_to_eat").splitlines() if item.strip()]) + "</ul></div>"
#                     if data.get("foods_to_avoid"):
#                         foods_avoid_md = f"<strong class='foods-avoid-list-title'>Foods to Avoid:</strong>\n<div class='foods-avoid-list'><ul>" + "".join([f"<li>{item.strip()}</li>" for item in data.get("foods_to_avoid").splitlines() if item.strip()]) + "</ul></div>"
                    
#                     full_dietary_text = data.get('dietary_recommendations', default_diet_msg).strip()
#                     if foods_eat_md or foods_avoid_md:
#                         if foods_eat_md: st.markdown(foods_eat_md, unsafe_allow_html=True)
#                         if foods_avoid_md: st.markdown(foods_avoid_md, unsafe_allow_html=True)
#                     elif full_dietary_text and full_dietary_text != default_diet_msg and "not found" not in full_dietary_text.lower():
#                         st.markdown(full_dietary_text)
#                     else:
#                         st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{default_diet_msg}</p>", unsafe_allow_html=True)
                
#                 # General Do's & Don'ts
#                 default_dos_donts_msg = "General Do's & Don'ts not found in provided documents. Consult a healthcare professional."
#                 with st.expander("👍👎 General Do's & Don'ts"):
#                     st.markdown(f"<div class='treatment-guidance-subheader dos-donts-header'>General Advice</div>", unsafe_allow_html=True)
#                     dos_md = ""; donts_md = ""
#                     if data.get("dos"):
#                         dos_md = f"<strong class='dos-list-title'>Do:</strong>\n<div class='dos-list'><ul>" + "".join([f"<li>{item.strip()}</li>" for item in data.get("dos").splitlines() if item.strip()]) + "</ul></div>"
#                     if data.get("donts"):
#                         donts_md = f"<strong class='donts-list-title'>Don't:</strong>\n<div class='donts-list'><ul>" + "".join([f"<li>{item.strip()}</li>" for item in data.get("donts").splitlines() if item.strip()]) + "</ul></div>"

#                     full_dos_donts_text = data.get('general_dos_donts', default_dos_donts_msg).strip()
#                     if dos_md or donts_md:
#                         if dos_md: st.markdown(dos_md, unsafe_allow_html=True)
#                         if donts_md: st.markdown(donts_md, unsafe_allow_html=True)
#                     elif full_dos_donts_text and full_dos_donts_text != default_dos_donts_msg and "not found" not in full_dos_donts_text.lower():
#                         st.markdown(full_dos_donts_text)
#                     else:
#                         st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{default_dos_donts_msg}</p>", unsafe_allow_html=True)

#                 # Red Flags
#                 with st.expander("🚨 When to Seek Professional Help (Red Flags)", expanded=True):
#                     st.markdown(f"<div class='treatment-guidance-subheader redflags-header'>Urgent Care / Red Flags</div>", unsafe_allow_html=True)
#                     seek_help_text = data.get('when_to_seek_help', "If symptoms are severe, worsen rapidly, or if you have concerns, consult a medical professional immediately.")
#                     st.error(seek_help_text) # st.error naturally styles it as a warning

#                 st.markdown(f"<hr style='border-color: {card_border_color}; margin-top:1.5rem; margin-bottom:1rem;'>", unsafe_allow_html=True)
#                 st.markdown("<div class='disclaimer-box'>" +
#                             f"<i><b>Disclaimer:</b> {data.get('disclaimer')}</i>" +
#                             "</div>", unsafe_allow_html=True)
#                 st.markdown("</div>", unsafe_allow_html=True) # Close the analysis-complete-message div
            
#             else: # Standard assistant message (not structured response)
#                 st.markdown(f"<div style='padding: 0.5rem; color: {text_color_yellow} !important;'>{str(msg['content'])}</div>", unsafe_allow_html=True)


# if user_symptoms := st.chat_input("Describe symptoms (e.g., 'fever, persistent cough, body aches')...", key="symptom_input_main"):
#     if not st.session_state.vector_store_loaded or st.session_state.vector_store is None:
#         st.session_state.messages.append({"role": "user", "content": user_symptoms})
#         st.session_state.messages.append({"role": "assistant", "content": "⚠️ Please upload and process a medical reference PDF first to enable symptom analysis."})
#     else:
#         st.session_state.messages.append({"role": "user", "content": user_symptoms})
        
#         with st.status("🧑‍⚕️ AI Advisor is thinking...", expanded=True) as status_ui:
#             st.write("Reviewing symptoms against medical knowledge base...") 
#             try:
#                 raw_response = query_rag_pipeline(user_symptoms, st.session_state.vector_store) # From rag_pipeline.py
#                 status_ui.update(label="Formatting guidance...", state="running")
#                 parsed_response_data = parse_llm_response(raw_response)
#                 assistant_response_content = {"symptoms_input": user_symptoms, **parsed_response_data}
#                 st.session_state.messages.append({"role": "assistant", "content": assistant_response_content})
#                 status_ui.update(label="Guidance ready!", state="complete", expanded=False)
#             except Exception as e:
#                 error_message = f"An error occurred during analysis: {str(e)}. Please check application logs or try rephrasing your query. Ensure 'rag_pipeline.py' and its dependencies are functional and the OpenAI API key is valid."
#                 st.session_state.messages.append({"role": "assistant", "content": error_message})
#                 status_ui.update(label="Error processing request.", state="error", expanded=True)
#                 st.error(error_message) # Also show error in main UI
#     st.rerun()

# # --- Footer ---
# st.markdown(f"""
# <div style="position: fixed; bottom: 0; left: 0; right: 0; background: rgba({int(bg_color[1:3], 16)}, {int(bg_color[3:5], 16)}, {int(bg_color[5:7], 16)}, 0.9); backdrop-filter: blur(5px); padding: 0.5rem; text-align: center; border-top: 1px solid {card_border_color}; z-index: 99;">
#     <p style="margin: 0; font-size: 0.8rem; opacity: 0.7; color: {text_color_blue} !important;">
#         TATA md AI Medical Advisor © {datetime.now().year} - For Informational Purposes Only
#     </p>
# </div>
# """, unsafe_allow_html=True)





# medical_rag_chatbot/main_app.py

import streamlit as st
import os
from dotenv import load_dotenv
import re
from datetime import datetime
import json

# --- Define SCRIPT_DIR, ASSETS_DIR, DATA_DIR first for robustness ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
DATA_DIR = os.path.join(SCRIPT_DIR, "data")

# Make sure rag_pipeline and utils are found by adding SCRIPT_DIR to sys.path
import sys
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

try:
    from rag_pipeline import load_and_process_pdf, query_rag_pipeline, get_existing_vector_store, OPENAI_API_KEY
except ImportError as e:
    st.error(
        f"Critical Error: Could not import modules from 'rag_pipeline.py'. "
        f"Please ensure 'rag_pipeline.py' and 'utils.py' are in the same directory as 'main_app.py' ({SCRIPT_DIR}) "
        f"and all dependencies are installed. Specific error: {e}"
    )
    st.stop()

# --- Page Configuration ---
favicon_path = os.path.join(ASSETS_DIR, "favicon.png")
st.set_page_config(
    page_title="TATA md AI Medical Advisor",
    page_icon=favicon_path if os.path.exists(favicon_path) else "🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Define Theme Colors (using your provided theme) ---
bg_color = "#141E30"
text_color_yellow = "#FFFACD"
text_color_blue = "#87CEFA"
primary_accent_pink = "#FF3CAC"
secondary_accent_blue = "#2B86C5"
secondary_accent_purple = "#784BA0"
dark_theme_bg_accent = "#243B55"
highlight_color_medication = "#FFB74D" # Orange for medication names
highlight_color_med_purpose = "#AED581" # Light Green for purpose
highlight_color_med_dosage = "#FFF176" # Light Yellow for dosage (use with caution)
highlight_color_med_notes = "#BCAAA4" # Light Brown/Grey for notes
highlight_color_positive_icon = "#66BB6A"
highlight_color_negative_icon = "#EF5350"
expander_header_bg_color = f"linear-gradient(135deg, rgba(255, 60, 172, 0.4) 0%, rgba(43, 134, 197, 0.5) 100%)"
expander_content_bg_color = f"rgba(43, 134, 197, 0.15)"
card_bg_color = f"rgba({int(secondary_accent_blue[1:3], 16)}, {int(secondary_accent_blue[3:5], 16)}, {int(secondary_accent_blue[5:7], 16)}, 0.4)"
card_border_color = f"rgba({int(primary_accent_pink[1:3], 16)}, {int(primary_accent_pink[3:5], 16)}, {int(primary_accent_pink[5:7], 16)}, 0.3)"
analysis_done_chat_bg = f"rgba({int(secondary_accent_blue[1:3], 16)}, {int(secondary_accent_blue[3:5], 16)}, {int(secondary_accent_blue[5:7], 16)}, 0.25)"


# --- Custom CSS (Using your provided CSS, with additions for medication details) ---
st.markdown(f"""
<style>
    /* Base styles - Default text is Yellow */
    body, .stApp, .stChatInput, .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {{
        background-color: {bg_color} !important;
        background-image: linear-gradient(to bottom right, {bg_color}, {dark_theme_bg_accent}) !important;
        color: {text_color_yellow} !important;
        font-family: 'Inter', sans-serif;
    }}
    p, li, span, div {{
        color: {text_color_yellow};
    }}
    a, a:visited {{
        color: {text_color_blue} !important;
        text-decoration: none;
    }}
    a:hover {{
        color: #5DADE2 !important; /* secondary_accent_blue_lighter */
        text-decoration: underline;
    }}

    .gradient-text {{
        background: linear-gradient(90deg, {primary_accent_pink} 0%, {secondary_accent_purple} 50%, {secondary_accent_blue} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
    }}

    .main-header {{ font-size: 3.0rem; font-weight: 700; margin-bottom: 0.5rem; text-align: center; }}
    .sub-header {{ font-size: 1.1rem; color: {text_color_blue} !important; opacity: 0.9; text-align: center; margin-bottom: 2rem; }}

    .section-header {{
        font-size: 2.0rem;
        color: {primary_accent_pink} !important;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        font-weight: 700;
        text-align: center;
        text-shadow: 0 0 8px rgba({int(primary_accent_pink[1:3],16)}, {int(primary_accent_pink[3:5],16)}, {int(primary_accent_pink[5:7],16)}, 0.3);
    }}

    .stChatMessage {{
        background: {card_bg_color};
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 0.8rem;
        border: 1px solid {card_border_color};
        padding: 1.2rem 1.8rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }}
     .stChatMessage p, .stChatMessage li, .stChatMessage span, .stChatMessage div {{
        color: {text_color_yellow} !important;
    }}

    div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message {{
        background: {analysis_done_chat_bg} !important;
        border: 1px solid {secondary_accent_blue} !important;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: -0.2rem -0.8rem;
    }}
    div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message *,
    div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message p,
    div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message li,
    div[data-testid="stChatMessageContent-assistant"] div.analysis-complete-message span {{
        color: {text_color_yellow} !important;
    }}

    .highlight-disease {{
        color: {text_color_yellow} !important;
        font-weight: bold;
        font-size: 1.4em;
        display: block;
        text-align: center;
        margin-bottom: 0.75rem;
        padding: 0.3rem;
        border-radius: 5px;
    }}

    /* Medication specific styling */
    .medication-item {{
        border-left: 3px solid {highlight_color_medication};
        padding-left: 10px;
        margin-bottom: 15px;
    }}
    .medication-item .med-drug-name strong {{ color: {highlight_color_medication} !important; font-size: 1.1em; }}
    .medication-item .med-purpose span {{ color: {highlight_color_med_purpose} !important; }}
    .medication-item .med-dosage span {{ color: {highlight_color_med_dosage} !important; font-style: italic; }}
    .medication-item .med-notes span {{ color: {highlight_color_med_notes} !important; }}
    .medication-item p {{ margin-bottom: 0.3rem !important; }}


    .treatment-guidance-subheader {{
        font-size: 1.2rem;
        font-weight: bold;
        margin-top: 0.8rem;
        margin-bottom: 0.6rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid {card_border_color};
    }}
    .pharma-header {{ color: {text_color_blue} !important; }}
    .lifestyle-header {{ color: {text_color_blue} !important; }}
    .dietary-header {{ color: {text_color_yellow} !important; }}
    .dos-donts-header {{ color: {text_color_blue} !important; }}
    .redflags-header {{ color: {primary_accent_pink} !important; }}

    .symptoms-analyzed-box {{
        background-color: rgba(20, 30, 48, 0.6);
        border: 1px solid {secondary_accent_blue};
        border-radius: 8px;
        padding: 12px 15px;
        margin-bottom: 18px;
        font-size: 0.95em;
    }}
    .symptoms-analyzed-box b {{ color: {text_color_blue} !important; font-weight: 700; }}
    .symptom-item {{
        display: inline-block;
        background-color: {secondary_accent_blue};
        color: {text_color_yellow} !important;
        padding: 4px 10px;
        border-radius: 15px;
        margin: 4px;
        font-size: 0.9em;
        border: 1px solid {primary_accent_pink};
    }}

    .disclaimer-box {{
        background-color: rgba(36, 59, 85, 0.3);
        border: 1px dashed {primary_accent_pink};
        color: {text_color_blue} !important;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1.5rem;
        font-size: 0.85em;
    }}
    .disclaimer-box i b {{ color: {primary_accent_pink} !important; }}

    .stButton > button {{
        background: linear-gradient(90deg, {primary_accent_pink} 0%, {secondary_accent_purple} 100%);
        color: {text_color_yellow} !important;
        border: none;
        border-radius: 0.5rem;
        padding: 0.7rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }}
    .stButton > button:hover {{
        transform: translateY(-3px) scale(1.03);
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.25);
        filter: brightness(1.1);
    }}

    div[data-testid="stFileUploader"] section {{
         background-color: {card_bg_color};
         border: 1px dashed {primary_accent_pink};
         border-radius: 0.5rem;
         padding: 1rem;
    }}
     div[data-testid="stFileUploader"] section small {{ color: {text_color_blue} !important; }}

    .stProgress > div > div > div {{
        background: linear-gradient(90deg, {primary_accent_pink} 0%, {secondary_accent_purple} 100%);
    }}

    .stChatInput > div > div > textarea {{
        background-color: {card_bg_color};
        border: 1px solid {card_border_color};
        border-radius: 0.5rem;
        color: {text_color_yellow} !important;
        padding: 1rem;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
    }}
    .stChatInput > div > div > textarea:focus {{
        border: 1px solid {primary_accent_pink};
        box-shadow: 0 0 0 3px rgba({int(primary_accent_pink[1:3],16)},{int(primary_accent_pink[3:5],16)},{int(primary_accent_pink[5:7],16)},0.25);
    }}

    section[data-testid="stSidebar"] > div:first-child {{
        background-color: {bg_color} !important;
        background-image: linear-gradient(to bottom right, {bg_color}, {dark_theme_bg_accent}) !important;
        border-right: 1px solid {card_border_color} !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] li,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div[data-baseweb="input"] > div,
    section[data-testid="stSidebar"] {{
        color: {text_color_yellow} !important;
    }}
    section[data-testid="stSidebar"] a {{ color: {text_color_blue} !important; }}
    section[data-testid="stSidebar"] .stHeadingContainer h2 {{
        text-align: center;
        color: {primary_accent_pink} !important;
    }}
    section[data-testid="stSidebar"] .stImage {{
        margin-left: auto;
        margin-right: auto;
        display: block;
    }}
    section[data-testid="stSidebar"] .stButton > button {{
        background: linear-gradient(90deg, {primary_accent_pink} 0%, {secondary_accent_purple} 100%);
        color: {text_color_yellow} !important;
    }}
    section[data-testid="stSidebar"] .stAlert {{
        border-radius: 0.5rem;
        border-left-width: 5px !important;
        background-color: rgba(0,0,0,0.3) !important;
        margin-left: 0.5rem;
        margin-right: 0.5rem;
    }}
    section[data-testid="stSidebar"] .stAlert p {{ color: {text_color_yellow} !important; }}
    section[data-testid="stSidebar"] .stAlert[data-baseweb="alert"][role="status"] {{ border-left-color: #4CAF50 !important; }}
    section[data-testid="stSidebar"] .stAlert[data-baseweb="alert"][role="note"] {{ border-left-color: {secondary_accent_blue} !important; }}
    section[data-testid="stSidebar"] .stAlert[data-baseweb="alert"][role="alert"] {{ border-left-color: #F44336 !important; }}

    .streamlit-expanderHeader {{
        background: {expander_header_bg_color} !important;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border-radius: 0.7rem !important;
        color: {text_color_yellow} !important;
        border: 1px solid {card_border_color} !important;
        padding: 0.9rem 1.2rem !important;
        font-weight: 600;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    .streamlit-expanderContent {{
        background-color: {expander_content_bg_color} !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 0 0 0.7rem 0.7rem !important;
        border: 1px solid {card_border_color} !important;
        border-top: none !important;
        padding: 1.5rem;
    }}
    .streamlit-expanderContent p, .streamlit-expanderContent li, .streamlit-expanderContent span, .streamlit-expanderContent div {{
        color: {text_color_yellow} !important;
    }}
    .streamlit-expanderContent strong {{
        color: {text_color_blue} !important;
    }}
    .streamlit-expanderHeader > div > svg {{
        fill: {text_color_yellow} !important;
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{ background: rgba(20, 30, 48, 0.3); border-radius: 10px; }}
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, {primary_accent_pink} 0%, {secondary_accent_purple} 100%);
        border-radius: 10px;
        border: 2px solid rgba(20, 30, 48, 0.3);
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(180deg, {primary_accent_pink} 30%, {secondary_accent_purple} 100%);
        filter: brightness(1.2);
    }}

    .dos-list ul, .donts-list ul {{ list-style-type: none; padding-left: 0; }}
    .dos-list li::before {{ content: '👍'; color: {highlight_color_positive_icon}; font-weight: bold; display: inline-block; width: 1.5em; margin-left: -1.5em; }}
    .dos-list li {{ color: {text_color_yellow} !important; }}
    .donts-list li::before {{ content: '👎'; color: {highlight_color_negative_icon}; font-weight: bold; display: inline-block; width: 1.5em; margin-left: -1.5em; }}
    .donts-list li {{ color: {text_color_yellow} !important; }}
    .foods-eat-list ul, .foods-avoid-list ul {{ list-style-type: none; padding-left: 0; }}
    .foods-eat-list li::before {{ content: '✅ '; color: {highlight_color_positive_icon}; font-weight: bold; }}
    .foods-eat-list li {{ color: {text_color_yellow} !important; }}
    .foods-avoid-list li::before {{ content: '❌ '; color: {highlight_color_negative_icon}; font-weight: bold; }}
    .foods-avoid-list li {{ color: {text_color_yellow} !important; }}
    .foods-eat-list-title, .foods-avoid-list-title {{ color: {text_color_yellow} !important; }}
    .dos-list-title, .donts-list-title {{ color: {text_color_blue} !important; }}
</style>
""", unsafe_allow_html=True)


# --- Load Environment Variables ---
load_dotenv()
if not OPENAI_API_KEY:
    st.error("OpenAI API key not found. Please set it in your .env file or environment variables.")
    st.stop()

if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
if not os.path.exists(ASSETS_DIR): os.makedirs(ASSETS_DIR)

# --- Session State ---
if "vector_store_loaded" not in st.session_state: st.session_state.vector_store_loaded = False
if "vector_store" not in st.session_state: st.session_state.vector_store = None
if "processed_pdf_name" not in st.session_state: st.session_state.processed_pdf_name = None
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Welcome! Please upload a medical reference PDF to begin."}]

# --- Default "Not Found" Messages for Parser and Display Logic ---
DEFAULT_MSG_PREDICTED_DISEASE = "Not specified by AI or not clearly identified from the context."
DEFAULT_MSG_REASONING = "Reasoning not provided or an error occurred parsing the response."
DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK = "Information not available in provided context for specific medications. Please consult a healthcare professional for medication options."
DEFAULT_MSG_LIFESTYLE = "Specific lifestyle and home care guidance not found in the provided documents for the current query. Please consult a healthcare professional for personalized advice."
DEFAULT_MSG_DIETARY = "Specific dietary recommendations not found in the provided documents for the current query. Please consult a healthcare professional for personalized advice."
DEFAULT_MSG_DOS_DONTS = "Specific Do's & Don'ts not found in the provided documents for the current query. Please consult a healthcare professional for personalized advice."
DEFAULT_MSG_SEEK_HELP = "Always consult a doctor if symptoms are severe, worsen, or if you have any concerns." # Aligned with new prompt
DEFAULT_MSG_DISCLAIMER = """This information is for educational purposes only and not a substitute for professional medical advice, diagnosis, or treatment.
Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
Never disregard professional medical advice or delay in seeking it because of something you have read from this chatbot.
Medication details are illustrative and NOT a prescription; consult your doctor for any medication.""" # Aligned with new prompt

# This dictionary is used by the parser's fallback logic
DEFAULT_FALLBACKS = {
    "pharmacological": DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK, # Store list of dicts or fallback string
    "medications_list": [], # New field to store parsed medication details
    "non_pharmacological_lifestyle": DEFAULT_MSG_LIFESTYLE,
    "dietary_recommendations": DEFAULT_MSG_DIETARY,
    "foods_to_eat": "",
    "foods_to_avoid": "",
    "general_dos_donts": DEFAULT_MSG_DOS_DONTS,
    "dos": "",
    "donts": "",
    "when_to_seek_help": DEFAULT_MSG_SEEK_HELP
}

# --- Helper Function to Parse LLM Response (ADAPTED FOR NEW PROMPT) ---
def parse_llm_response(response_text):
    parsed_data = {
        "predicted_disease": DEFAULT_MSG_PREDICTED_DISEASE,
        "reasoning": DEFAULT_MSG_REASONING,
        "pharmacological": DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK, # Overall text for this section
        "medications_list": [], # For structured medication items
        "non_pharmacological_lifestyle": DEFAULT_MSG_LIFESTYLE,
        "dietary_recommendations": DEFAULT_MSG_DIETARY,
        "foods_to_eat": "",
        "foods_to_avoid": "",
        "general_dos_donts": DEFAULT_MSG_DOS_DONTS,
        "dos": "",
        "donts": "",
        "when_to_seek_help": DEFAULT_MSG_SEEK_HELP,
        "disclaimer": DEFAULT_MSG_DISCLAIMER
    }

    # --- Extract Main Sections ---
    disease_match = re.search(r"\*\*Predicted Disease:\*\*\s*(.*?)(?=\n\s*\*\*Reasoning:\*\*|\n\n\n|\Z)", response_text, re.DOTALL | re.IGNORECASE)
    if disease_match and disease_match.group(1).strip():
        parsed_data["predicted_disease"] = disease_match.group(1).strip()

    reasoning_match = re.search(r"\*\*Reasoning:\*\*\s*(.*?)(?=\n\s*\*\*Treatment Guidance:\*\*|\n\n\n|\Z)", response_text, re.DOTALL | re.IGNORECASE)
    if reasoning_match and reasoning_match.group(1).strip():
        parsed_data["reasoning"] = reasoning_match.group(1).strip()

    disclaimer_match = re.search(r"\*\*Disclaimer:\*\*\s*(.*?)(?:\n\n\n|\Z)", response_text, re.DOTALL | re.IGNORECASE)
    if disclaimer_match and disclaimer_match.group(1).strip():
        parsed_data["disclaimer"] = disclaimer_match.group(1).strip()

    # --- Extract Treatment Guidance Block ---
    treatment_guidance_block_match = re.search(r"\*\*Treatment Guidance:\*\*\s*(.*?)(?=\n\s*\*\*Disclaimer:\*\*|\n\n\n|\Z)", response_text, re.DOTALL | re.IGNORECASE)
    if treatment_guidance_block_match:
        treatment_text = treatment_guidance_block_match.group(1).strip()
        
        section_headers_raw = [
            r"Pharmacological \(Medications\):", # Note: No optional (Medications) here based on new prompt
            r"Non-Pharmacological & Lifestyle:",
            r"Dietary Recommendations:",
            r"General Do's & Don'ts:",
            r"When to Seek Professional Help \(Red Flags\):" # Note: No optional (Red Flags)
        ]
        
        all_next_headers_lookahead_parts = [r"^\s*\*\*" + re.escape(header_part) + r"\*\*" for header_part in section_headers_raw]
        combined_lookahead = r"(?:" + "|".join(all_next_headers_lookahead_parts) + r"|\n\n\n|\Z)"

        # Pharmacological (Medications) - This needs careful parsing for the new structure
        pharma_block_match = re.search(r"^\s*\*\*Pharmacological \(Medications\):\*\*\s*(.*?)" + combined_lookahead, treatment_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        if pharma_block_match and pharma_block_match.group(1).strip():
            pharma_content = pharma_block_match.group(1).strip()
            parsed_data["pharmacological"] = pharma_content # Store the whole block first

            # Try to parse individual medication items
            # Each item starts with "- **Drug Name:**"
            med_items = re.findall(
                r"^\s*-\s*\*\*Drug Name:\*\*\s*(.*?)\n"
                r"\s*-\s*\*\*Purpose:\*\*\s*(.*?)\n"
                r"(?:\s*-\s*\*\*Common Dosage(?: \(Example Only - Emphasize to consult doctor\))?:\*\*\s*(.*?)\n)?" # Dosage is optional
                r"(?:\s*-\s*\*\*Important Notes:\*\*\s*(.*?)(?=\n\s*-|\n\n\n|\Z))?", # Notes are optional and go to next item or end
                pharma_content,
                re.DOTALL | re.IGNORECASE | re.MULTILINE
            )
            
            if med_items:
                parsed_data["medications_list"] = []
                for item in med_items:
                    med_dict = {
                        "drug_name": item[0].strip() if item[0] else "N/A",
                        "purpose": item[1].strip() if item[1] else "N/A",
                        "dosage": item[2].strip() if item[2] else "Consult doctor for dosage.", # Make dosage optional in display if not found
                        "notes": item[3].strip() if item[3] else "N/A"
                    }
                    parsed_data["medications_list"].append(med_dict)
                # If we successfully parsed med_items, we might not need the full pharma_content as fallback unless it contains additional text
                # For now, keep pharma_content; UI can decide to show it if medications_list is empty.
            elif "consult a doctor for medication options" not in pharma_content.lower() and \
                 "information not available" not in pharma_content.lower():
                # If no structured items found, but the text isn't the generic fallback,
                # it might be free-form medication advice. Keep it in 'pharmacological'.
                pass # parsed_data["pharmacological"] already has pharma_content
            else: # It's likely the generic fallback
                parsed_data["pharmacological"] = DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK


        # Non-Pharmacological & Lifestyle
        non_pharma_match = re.search(r"^\s*\*\*Non-Pharmacological & Lifestyle:\*\*\s*(.*?)" + combined_lookahead, treatment_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        if non_pharma_match and non_pharma_match.group(1).strip():
            parsed_data["non_pharmacological_lifestyle"] = non_pharma_match.group(1).strip()

        # Dietary Recommendations
        diet_full_match = re.search(r"^\s*\*\*Dietary Recommendations:\*\*\s*(.*?)" + combined_lookahead, treatment_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        if diet_full_match and diet_full_match.group(1).strip():
            diet_text_full_content = diet_full_match.group(1).strip()
            parsed_data["dietary_recommendations"] = diet_text_full_content

            eat_match = re.search(r"^\s*-\s*\*\*Foods to Eat:\*\*\s*(.*?)(?=\n\s*-\s*\*\*Foods to Avoid:\*\*|\n\n\n|\Z)", diet_text_full_content, re.DOTALL | re.IGNORECASE | re.MULTILINE)
            if eat_match and eat_match.group(1).strip():
                parsed_data["foods_to_eat"] = "\n".join([item.strip().lstrip("-* ").strip() for item in eat_match.group(1).strip().splitlines() if item.strip().lstrip("-* ").strip()])
            
            avoid_match = re.search(r"^\s*-\s*\*\*Foods to Avoid:\*\*\s*(.*?)(?:\n\n\n|\Z)", diet_text_full_content, re.DOTALL | re.IGNORECASE | re.MULTILINE)
            if avoid_match and avoid_match.group(1).strip():
                parsed_data["foods_to_avoid"] = "\n".join([item.strip().lstrip("-* ").strip() for item in avoid_match.group(1).strip().splitlines() if item.strip().lstrip("-* ").strip()])
        
        # General Do's & Don'ts
        dos_donts_full_match = re.search(r"^\s*\*\*General Do's & Don'ts:\*\*\s*(.*?)" + combined_lookahead, treatment_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        if dos_donts_full_match and dos_donts_full_match.group(1).strip():
            dos_donts_text_full_content = dos_donts_full_match.group(1).strip()
            parsed_data["general_dos_donts"] = dos_donts_text_full_content
            
            do_match = re.search(r"^\s*-\s*\*\*Do:\*\*\s*(.*?)(?=\n\s*-\s*\*\*Don't:\*\*|\n\n\n|\Z)", dos_donts_text_full_content, re.DOTALL | re.IGNORECASE | re.MULTILINE)
            if do_match and do_match.group(1).strip():
                parsed_data["dos"] = "\n".join([item.strip().lstrip("-* ").strip() for item in do_match.group(1).strip().splitlines() if item.strip().lstrip("-* ").strip()])

            dont_match = re.search(r"^\s*-\s*\*\*Don't:\*\*\s*(.*?)(?:\n\n\n|\Z)", dos_donts_text_full_content, re.DOTALL | re.IGNORECASE | re.MULTILINE)
            if dont_match and dont_match.group(1).strip():
                parsed_data["donts"] = "\n".join([item.strip().lstrip("-* ").strip() for item in dont_match.group(1).strip().splitlines() if item.strip().lstrip("-* ").strip()])

        # When to Seek Professional Help
        seek_help_match = re.search(r"^\s*\*\*When to Seek Professional Help \(Red Flags\):\*\*\s*(.*?)" + combined_lookahead, treatment_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        if seek_help_match and seek_help_match.group(1).strip():
            parsed_data["when_to_seek_help"] = seek_help_match.group(1).strip()

    if not response_text.strip(): # If entire LLM response was empty
        for key in DEFAULT_FALLBACKS:
            if key in parsed_data and parsed_data[key] == DEFAULT_FALLBACKS.get(key):
                 if key != "medications_list": # medications_list is a list, not a string default
                    parsed_data[key] = f"No information received from AI for {key.replace('_', ' ')}."
    
    return parsed_data

# --- Functions ---
def initialize_vector_store():
    vs = get_existing_vector_store()
    if vs:
        st.session_state.vector_store = vs
        st.session_state.vector_store_loaded = True
        st.session_state.processed_pdf_name = "Previously processed medical texts"
        if len(st.session_state.messages) == 1 and "Welcome!" in st.session_state.messages[0]["content"]:
            st.session_state.messages[0] = {"role": "assistant", "content": "Welcome! Medical knowledge base active. How can I assist?"}


# --- UI Layout ---
st.markdown(f"""
<div style="text-align: center; padding-top: 2rem; padding-bottom: 1rem;">
    <h1 class='main-header'><span class='gradient-text'>TATA md AI Medical Advisor</span></h1>
    <p class='sub-header'>
        Leveraging medical literature to offer insights on symptoms. <br>
        <em>This tool provides information for educational purposes only and is not a substitute for professional medical advice.</em>
    </p>
</div>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    logo_path = os.path.join(ASSETS_DIR, "tatmd.png")
    default_logo_url = "https://www.tatamd.com/images/logo_TATA%20MD.svg" # Fallback

    if os.path.exists(logo_path):
        st.image(logo_path, width=180, use_container_width=True)
    else:
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 1rem;">
                <img src="{default_logo_url}"
                     alt="TATA MD Logo"
                     style="width: 180px; margin-bottom: 10px;"
                     onerror="this.style.display='none'; this.parentElement.innerHTML+='<p style=\'color:{text_color_yellow};\'>TATA MD Logo (fallback)</p>';">
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f"<h2 style='text-align: center; color: {primary_accent_pink}; margin-bottom: 1rem;'>Knowledge Base</h2>", unsafe_allow_html=True)

    if not st.session_state.vector_store_loaded and st.session_state.vector_store is None:
        with st.spinner("Checking for existing knowledge base..."):
            initialize_vector_store()

    if st.session_state.vector_store_loaded:
        st.success(f"Active KB: {st.session_state.processed_pdf_name or 'Loaded'}")
    else:
        st.info("Upload a PDF to activate the Knowledge Base.")

    uploaded_file_sb = st.file_uploader("Upload Medical Reference (PDF)", type="pdf", key="pdf_uploader_sidebar")

    if st.button("Process PDF & Build KB", key="process_button_sidebar", help="Upload and process a new PDF to create or update the knowledge base."):
        if uploaded_file_sb is not None:
            file_path = os.path.join(DATA_DIR, uploaded_file_sb.name)
            with open(file_path, "wb") as f: f.write(uploaded_file_sb.getbuffer())

            with st.spinner(f"Processing {uploaded_file_sb.name}... This may take a while."):
                st.session_state.vector_store = None
                st.session_state.vector_store_loaded = False
                st.session_state.processed_pdf_name = None

                processed_vs = load_and_process_pdf(file_path)

                if processed_vs:
                    st.session_state.vector_store = processed_vs
                    st.session_state.vector_store_loaded = True
                    st.session_state.processed_pdf_name = uploaded_file_sb.name
                    st.session_state.messages = [{"role": "assistant", "content": f"Knowledge base from '{uploaded_file_sb.name}' is ready. How can I assist?"}]
                else:
                    st.session_state.messages = [{"role": "assistant", "content": f"Failed to process '{uploaded_file_sb.name}'. Please try again or use a different PDF."}]
                    st.error(f"Failed to process '{uploaded_file_sb.name}'.")
            st.rerun()
        else:
            st.warning("Please upload a PDF file first.")

    st.markdown("---")
    st.markdown(f"<p style='font-size: 0.8em; text-align: center; opacity: 0.7; color: {text_color_blue} !important;'>Powered by Advanced AI</p>", unsafe_allow_html=True)


# --- Main Chat Interface ---
st.markdown("<div class='section-header'>Symptom Analysis & Guidance</div>", unsafe_allow_html=True)

chat_container = st.container()
with chat_container:
    for i, msg in enumerate(st.session_state.messages):
        is_structured_response = isinstance(msg["content"], dict) and "predicted_disease" in msg["content"]

        with st.chat_message(msg["role"], avatar="🧑‍⚕️" if msg["role"] == "assistant" else "👤"):
            if msg["role"] == "user":
                st.markdown(f"<div style='text-align: right; color: {text_color_yellow} !important; padding: 0.5rem;'>{msg['content']}</div>", unsafe_allow_html=True)

            elif is_structured_response:
                st.markdown("<div class='analysis-complete-message'>", unsafe_allow_html=True)
                data = msg["content"]

                symptoms_input_string = data.get("symptoms_input", "")
                if symptoms_input_string:
                    symptom_list = [s.strip() for s in re.split(r'[,\n]', symptoms_input_string) if s.strip()]
                    if not symptom_list and symptoms_input_string:
                        symptom_list = [symptoms_input_string.strip()]
                    symptoms_html_items = "".join([f"<div class='symptom-item'>{symptom}</div>" for symptom in symptom_list])
                    st.markdown(f"<div class='symptoms-analyzed-box'><b>Symptoms Analyzed:</b>{symptoms_html_items}</div>", unsafe_allow_html=True)


                st.markdown(f"##### <span class='highlight-disease'>{data.get('predicted_disease', DEFAULT_MSG_PREDICTED_DISEASE)}</span>", unsafe_allow_html=True)

                reasoning_content = data.get('reasoning', DEFAULT_MSG_REASONING).strip()
                if reasoning_content and reasoning_content not in [DEFAULT_MSG_REASONING, ""] and "not found" not in reasoning_content.lower() and "error occurred" not in reasoning_content.lower():
                    with st.expander("View Reasoning", expanded=False):
                        st.markdown(reasoning_content, unsafe_allow_html=True)
                else:
                    st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{reasoning_content}</p>", unsafe_allow_html=True)

                st.markdown(f"<hr style='border-color: {card_border_color}; margin-top:1rem; margin-bottom:1rem;'>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='color: {text_color_yellow}; text-align:center; margin-bottom:1rem;'>Treatment Guidance</h4>", unsafe_allow_html=True)

                # Pharmacological (Medications) - Updated Display
                with st.expander("💊 Pharmacological (Medications)", expanded=True):
                    st.markdown(f"<div class='treatment-guidance-subheader pharma-header'>Medications</div>", unsafe_allow_html=True)
                    medications_list = data.get('medications_list', [])
                    pharmacological_text = data.get('pharmacological', DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK).strip()

                    if medications_list:
                        for med in medications_list:
                            med_html = "<div class='medication-item'>"
                            med_html += f"<p class='med-drug-name'><strong>{med.get('drug_name', 'N/A')}</strong></p>"
                            if med.get('purpose') and med.get('purpose') != 'N/A':
                                med_html += f"<p class='med-purpose'>Purpose: <span>{med.get('purpose')}</span></p>"
                            if med.get('dosage') and med.get('dosage') != 'Consult doctor for dosage.': # Only show if specific
                                med_html += f"<p class='med-dosage'>Dosage Example: <span>{med.get('dosage')}</span> <em>(Not medical advice)</em></p>"
                            if med.get('notes') and med.get('notes') != 'N/A':
                                med_html += f"<p class='med-notes'>Notes: <span>{med.get('notes')}</span></p>"
                            med_html += "</div>"
                            st.markdown(med_html, unsafe_allow_html=True)
                    elif pharmacological_text and pharmacological_text != DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK and "consult a doctor" not in pharmacological_text.lower() and "information not available" not in pharmacological_text.lower() :
                        # Display general pharmacological text if no list but specific info is present
                        st.markdown(pharmacological_text, unsafe_allow_html=True)
                    else: # Fallback to the generic message
                        st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{DEFAULT_MSG_PHARMACOLOGICAL_FALLBACK}</p>", unsafe_allow_html=True)


                # Non-Pharmacological & Lifestyle
                with st.expander("🌿 Non-Pharmacological & Lifestyle"):
                    st.markdown(f"<div class='treatment-guidance-subheader lifestyle-header'>Lifestyle & Home Care</div>", unsafe_allow_html=True)
                    lifestyle_content = data.get('non_pharmacological_lifestyle', DEFAULT_MSG_LIFESTYLE).strip()
                    if lifestyle_content and lifestyle_content not in [DEFAULT_MSG_LIFESTYLE, ""] and "not available" not in lifestyle_content.lower() and "consult a healthcare professional" not in lifestyle_content.lower():
                        st.markdown(lifestyle_content, unsafe_allow_html=True)
                    else:
                         st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{lifestyle_content if lifestyle_content else DEFAULT_MSG_LIFESTYLE}</p>", unsafe_allow_html=True)

                # Dietary Recommendations
                with st.expander("🥗 Dietary Recommendations"):
                    st.markdown(f"<div class='treatment-guidance-subheader dietary-header'>Dietary Advice</div>", unsafe_allow_html=True)
                    foods_eat_md = ""; foods_avoid_md = ""
                    if data.get("foods_to_eat"):
                        foods_eat_md = f"<strong class='foods-eat-list-title'>Foods to Eat:</strong>\n<div class='foods-eat-list'><ul>" + "".join([f"<li>{item.strip()}</li>" for item in data.get("foods_to_eat").splitlines() if item.strip()]) + "</ul></div>"
                    if data.get("foods_to_avoid"):
                        foods_avoid_md = f"<strong class='foods-avoid-list-title'>Foods to Avoid:</strong>\n<div class='foods-avoid-list'><ul>" + "".join([f"<li>{item.strip()}</li>" for item in data.get("foods_to_avoid").splitlines() if item.strip()]) + "</ul></div>"

                    if foods_eat_md or foods_avoid_md:
                        if foods_eat_md: st.markdown(foods_eat_md, unsafe_allow_html=True)
                        if foods_avoid_md: st.markdown(foods_avoid_md, unsafe_allow_html=True)
                    else:
                        full_dietary_text = data.get('dietary_recommendations', DEFAULT_MSG_DIETARY).strip()
                        if full_dietary_text and full_dietary_text not in [DEFAULT_MSG_DIETARY, ""] and "not available" not in full_dietary_text.lower() and "consult a healthcare professional" not in full_dietary_text.lower():
                            st.markdown(full_dietary_text, unsafe_allow_html=True)
                        else:
                            st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{full_dietary_text if full_dietary_text else DEFAULT_MSG_DIETARY}</p>", unsafe_allow_html=True)
                
                # General Do's & Don'ts
                with st.expander("👍👎 General Do's & Don'ts"):
                    st.markdown(f"<div class='treatment-guidance-subheader dos-donts-header'>General Advice</div>", unsafe_allow_html=True)
                    dos_md = ""; donts_md = ""
                    if data.get("dos"):
                        dos_md = f"<strong class='dos-list-title'>Do:</strong>\n<div class='dos-list'><ul>" + "".join([f"<li>{item.strip()}</li>" for item in data.get("dos").splitlines() if item.strip()]) + "</ul></div>"
                    if data.get("donts"):
                        donts_md = f"<strong class='donts-list-title'>Don't:</strong>\n<div class='donts-list'><ul>" + "".join([f"<li>{item.strip()}</li>" for item in data.get("donts").splitlines() if item.strip()]) + "</ul></div>"

                    if dos_md or donts_md:
                        if dos_md: st.markdown(dos_md, unsafe_allow_html=True)
                        if donts_md: st.markdown(donts_md, unsafe_allow_html=True)
                    else:
                        full_dos_donts_text = data.get('general_dos_donts', DEFAULT_MSG_DOS_DONTS).strip()
                        if full_dos_donts_text and full_dos_donts_text not in [DEFAULT_MSG_DOS_DONTS, ""] and "not available" not in full_dos_donts_text.lower() and "consult a healthcare professional" not in full_dos_donts_text.lower():
                            st.markdown(full_dos_donts_text, unsafe_allow_html=True)
                        else:
                            st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{full_dos_donts_text if full_dos_donts_text else DEFAULT_MSG_DOS_DONTS}</p>", unsafe_allow_html=True)

                # Red Flags
                with st.expander("🚨 When to Seek Professional Help (Red Flags)", expanded=True):
                    st.markdown(f"<div class='treatment-guidance-subheader redflags-header'>Urgent Care / Red Flags</div>", unsafe_allow_html=True)
                    seek_help_text = data.get('when_to_seek_help', DEFAULT_MSG_SEEK_HELP).strip()
                    # Display as error if specific content, otherwise as italic blue text
                    if seek_help_text and seek_help_text not in [DEFAULT_MSG_SEEK_HELP, ""] and "not available" not in seek_help_text.lower() and "always consult a doctor" not in seek_help_text.lower() :
                         st.error(seek_help_text)
                    else:
                        st.markdown(f"<p style='color:{text_color_blue}; font-style:italic;'>{seek_help_text if seek_help_text else DEFAULT_MSG_SEEK_HELP}</p>", unsafe_allow_html=True)


                st.markdown(f"<hr style='border-color: {card_border_color}; margin-top:1.5rem; margin-bottom:1rem;'>", unsafe_allow_html=True)
                st.markdown("<div class='disclaimer-box'>" +
                            f"<i><b>Disclaimer:</b> {data.get('disclaimer', DEFAULT_MSG_DISCLAIMER)}</i>" +
                            "</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            else:
                st.markdown(f"<div style='padding: 0.5rem; color: {text_color_yellow} !important;'>{str(msg['content'])}</div>", unsafe_allow_html=True)


if user_symptoms := st.chat_input("Describe symptoms (e.g., 'fever, persistent cough, body aches')...", key="symptom_input_main"):
    if not st.session_state.vector_store_loaded or st.session_state.vector_store is None:
        st.session_state.messages.append({"role": "user", "content": user_symptoms})
        st.session_state.messages.append({"role": "assistant", "content": "⚠️ Please upload and process a medical reference PDF first to enable symptom analysis."})
    else:
        st.session_state.messages.append({"role": "user", "content": user_symptoms})

        with st.status("🧑‍⚕️ AI Advisor is thinking...", expanded=True) as status_ui:
            st.write("Reviewing symptoms against medical knowledge base...")
            try:
                raw_response = query_rag_pipeline(user_symptoms, st.session_state.vector_store)

                print("\n--- RAW LLM Response (from RAG pipeline) START ---")
                print(raw_response)
                print("--- RAW LLM Response (from RAG pipeline) END ---\n")

                status_ui.update(label="Formatting guidance...", state="running")
                parsed_response_data = parse_llm_response(raw_response)

                print("\n--- Parsed Response Data (for UI) START ---")
                print(json.dumps(parsed_response_data, indent=2))
                print("--- Parsed Response Data (for UI) END ---\n")

                assistant_response_content = {"symptoms_input": user_symptoms, **parsed_response_data}
                st.session_state.messages.append({"role": "assistant", "content": assistant_response_content})
                status_ui.update(label="Guidance ready!", state="complete", expanded=False)
            except Exception as e:
                error_message = f"An error occurred during analysis: {str(e)}. Please check application logs or try rephrasing your query. Ensure 'rag_pipeline.py' and its dependencies are functional and the OpenAI API key is valid."
                st.session_state.messages.append({"role": "assistant", "content": error_message})
                status_ui.update(label="Error processing request.", state="error", expanded=True)
                st.error(error_message)
                print(f"ERROR in Streamlit chat input processing: {e}") # Also print to terminal
    st.rerun()

# --- Footer ---
st.markdown(f"""
<div style="position: fixed; bottom: 0; left: 0; right: 0; background: rgba({int(bg_color[1:3], 16)}, {int(bg_color[3:5], 16)}, {int(bg_color[5:7], 16)}, 0.9); backdrop-filter: blur(5px); padding: 0.5rem; text-align: center; border-top: 1px solid {card_border_color}; z-index: 99;">
    <p style="margin: 0; font-size: 0.8rem; opacity: 0.7; color: {text_color_blue} !important;">
        TATA md AI Medical Advisor © {datetime.now().year} - For Informational Purposes Only
    </p>
</div>
""", unsafe_allow_html=True)