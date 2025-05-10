# # medical_rag_chatbot/rag_pipeline.py

# import os
# from dotenv import load_dotenv

# from langchain_community.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain_community.vectorstores import Chroma
# from langchain_community.tools import DuckDuckGoSearchRun
# from langchain.chains import LLMChain

# from utils import get_qa_prompt_template # Import from utils.py

# # Load environment variables (for OpenAI API key)
# load_dotenv()

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# if not OPENAI_API_KEY:
#     raise ValueError("OPENAI_API_KEY not found in .env file or environment variables.")

# # --- Global Variables ---
# CHROMA_DB_PATH = "./chroma_db"
# BOOK_COLLECTION_NAME = "medical_book_collection"
# EMBEDDING_MODEL = OpenAIEmbeddings(model="text-embedding-3-small") # Cheaper and often good enough
# LLM_MODEL = ChatOpenAI(temperature=0.2, model_name="gpt-3.5-turbo") # Or "gpt-4" for higher quality

# # --- Ingestion Pipeline ---
# def load_and_process_pdf(pdf_file_path):
#     """
#     Loads a PDF, splits it into chunks, creates embeddings, and stores them in ChromaDB.
#     Returns the Chroma vector store.
#     """
#     print(f"Loading PDF from: {pdf_file_path}")
#     loader = PyPDFLoader(pdf_file_path)
#     documents = loader.load()

#     if not documents:
#         print("No documents loaded from PDF. Check PDF content and path.")
#         return None

#     print(f"Loaded {len(documents)} pages initially.")

#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,  # Adjust as needed
#         chunk_overlap=200   # Adjust as needed
#     )
#     split_docs = text_splitter.split_documents(documents)
#     print(f"Split into {len(split_docs)} chunks.")

#     if not split_docs:
#         print("No text chunks created after splitting. Check PDF content.")
#         return None

#     # Create or load Chroma vector store
#     # We will delete the old collection if it exists to ensure fresh data for the uploaded book
#     # For a production system, you might want a more sophisticated update strategy.
#     vector_store = Chroma.from_documents(
#         documents=split_docs,
#         embedding=EMBEDDING_MODEL,
#         collection_name=BOOK_COLLECTION_NAME,
#         persist_directory=CHROMA_DB_PATH
#     )
#     vector_store.persist()
#     print(f"Successfully created and persisted vector store with {vector_store._collection.count()} documents.")
#     return vector_store

# def get_existing_vector_store():
#     """
#     Loads an existing Chroma vector store if it exists.
#     """
#     if os.path.exists(CHROMA_DB_PATH) and any(os.scandir(CHROMA_DB_PATH)): # Check if directory exists and is not empty
#         try:
#             print(f"Loading existing vector store from: {CHROMA_DB_PATH}")
#             vector_store = Chroma(
#                 persist_directory=CHROMA_DB_PATH,
#                 embedding_function=EMBEDDING_MODEL,
#                 collection_name=BOOK_COLLECTION_NAME
#             )
#             if vector_store._collection.count() > 0:
#                  print(f"Successfully loaded vector store with {vector_store._collection.count()} documents.")
#                  return vector_store
#             else:
#                 print("Found Chroma DB directory, but collection is empty or not found.")
#                 return None
#         except Exception as e:
#             print(f"Error loading existing vector store: {e}")
#             # Potentially delete corrupted DB if it fails to load
#             # import shutil
#             # shutil.rmtree(CHROMA_DB_PATH, ignore_errors=True)
#             # print("Cleared potentially corrupted Chroma DB directory.")
#             return None
#     else:
#         print("No existing vector store found.")
#         return None

# # --- Query Pipeline ---
# def query_rag_pipeline(symptoms_query: str, vector_store: Chroma):
#     """
#     Queries the RAG pipeline with user symptoms.
#     1. Retrieves relevant chunks from the book (ChromaDB).
#     2. Performs a DuckDuckGo search for additional context.
#     3. Combines context and query for the LLM.
#     """
#     if not vector_store:
#         return "Error: Knowledge base (vector store) is not loaded. Please upload and process a book first."

#     # 1. Retrieve from Vector Store (Book Context)
#     retriever = vector_store.as_retriever(search_kwargs={"k": 3}) # Retrieve top 3 relevant chunks
#     try:
#         book_docs = retriever.get_relevant_documents(symptoms_query)
#         book_context = "\n\n".join([doc.page_content for doc in book_docs])
#         if not book_context:
#             book_context = "No relevant information found in the uploaded book for these symptoms."
#     except Exception as e:
#         print(f"Error retrieving from vector store: {e}")
#         book_context = "Error retrieving information from the book."

#     # 2. Augment with DuckDuckGo Search
#     ddg_search = DuckDuckGoSearchRun()
#     try:
#         web_search_query = f"medical information for symptoms: {symptoms_query}"
#         web_search_results = ddg_search.run(web_search_query)
#         if not web_search_results:
#              web_search_results = "No relevant information found on the web for these symptoms via DuckDuckGo."
#     except Exception as e:
#         print(f"Error during DuckDuckGo search: {e}")
#         web_search_results = "Error performing web search."


#     # 3. Generate Response using LLM with combined context
#     qa_prompt = get_qa_prompt_template()
#     chain = LLMChain(llm=LLM_MODEL, prompt=qa_prompt)

#     response = chain.invoke({
#         "book_context": book_context,
#         "web_search_results": web_search_results,
#         "symptoms": symptoms_query
#     })

#     return response['text'] # LLMChain returns a dict with 'text' key

# if __name__ == '__main__':
#     # --- This is for testing the rag_pipeline.py directly ---
#     print("Testing RAG Pipeline...")

#     # Ensure a dummy PDF exists in data/ for testing
#     DUMMY_PDF_PATH = "data/dummy_medical_book.pdf"
#     if not os.path.exists("data"):
#         os.makedirs("data")
#     if not os.path.exists(DUMMY_PDF_PATH):
#         # Create a very simple PDF for testing if you don't have one
#         # This requires `reportlab` -> add to requirements if you use this
#         try:
#             from reportlab.pdfgen import canvas
#             c = canvas.Canvas(DUMMY_PDF_PATH)
#             c.drawString(100, 750, "Chapter 1: Common Cold")
#             c.drawString(100, 730, "Symptoms: Runny nose, sore throat, cough.")
#             c.drawString(100, 710, "Medication: Rest, fluids, over-the-counter decongestants.")
#             c.drawString(100, 690, "Chapter 2: Flu (Influenza)")
#             c.drawString(100, 670, "Symptoms: Fever, chills, muscle aches, fatigue, cough.")
#             c.drawString(100, 650, "Medication: Antivirals (e.g., Tamiflu), rest, fluids.")
#             c.save()
#             print(f"Created dummy PDF: {DUMMY_PDF_PATH}")
#         except ImportError:
#             print("Please create a dummy PDF named 'dummy_medical_book.pdf' in the 'data/' directory for testing.")
#             print("Or install reportlab: pip install reportlab")
#             exit()

#     # 1. Test Ingestion
#     print("\n--- Testing Ingestion ---")
#     # To ensure a clean test, you might want to clear the chroma_db directory
#     # import shutil
#     # if os.path.exists(CHROMA_DB_PATH):
#     #     shutil.rmtree(CHROMA_DB_PATH)
#     #     print(f"Cleared existing Chroma DB at {CHROMA_DB_PATH}")

#     vs = load_and_process_pdf(DUMMY_PDF_PATH)
#     if vs:
#         print(f"Vector store created/loaded. Documents: {vs._collection.count()}")

#         # 2. Test Querying
#         print("\n--- Testing Query ---")
#         test_symptoms = "fever, muscle aches, fatigue"
#         print(f"Querying with symptoms: {test_symptoms}")
#         response = query_rag_pipeline(test_symptoms, vs)
#         print("\nResponse:")
#         print(response)

#         print("\n--- Testing Query for different symptoms ---")
#         test_symptoms_2 = "runny nose and sore throat"
#         print(f"Querying with symptoms: {test_symptoms_2}")
#         response_2 = query_rag_pipeline(test_symptoms_2, vs)
#         print("\nResponse:")
#         print(response_2)

#     else:
#         print("Failed to create or load vector store during testing.")

#     # 3. Test loading existing vector store
#     print("\n--- Testing Loading Existing Vector Store ---")
#     existing_vs = get_existing_vector_store()
#     if existing_vs:
#         print(f"Successfully loaded existing vector store. Documents: {existing_vs._collection.count()}")
#         test_symptoms_3 = "fever, fatigue"
#         response_3 = query_rag_pipeline(test_symptoms_3, existing_vs)
#         print("\nResponse from loaded store:")
#         print(response_3)
#     else:
#         print("Could not load existing vector store for test.")






# medical_rag_chatbot/rag_pipeline.py

import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.output_parsers import StrOutputParser

# Ensure utils is importable.
from utils import get_qa_prompt_template

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file or environment variables.")

SCRIPT_DIR_RAG = os.path.dirname(os.path.abspath(__file__))
CHROMA_DB_PATH_ABS = os.path.join(SCRIPT_DIR_RAG, "chroma_db")

BOOK_COLLECTION_NAME = "medical_book_collection"
EMBEDDING_MODEL = OpenAIEmbeddings(model="text-embedding-3-small")
LLM_MODEL = ChatOpenAI(temperature=0.1, model_name="gpt-3.5-turbo") # Consider gpt-4-turbo for complex parsing/generation

def load_and_process_pdf(pdf_file_path):
    print(f"Loading PDF from: {pdf_file_path}")
    loader = PyPDFLoader(pdf_file_path)
    documents = loader.load()

    if not documents:
        print("No documents loaded from PDF. Check PDF content and path.")
        return None
    print(f"Loaded {len(documents)} pages initially.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, # Adjust if needed based on PDF content structure
        chunk_overlap=200  # Adjust overlap
    )
    split_docs = text_splitter.split_documents(documents)
    print(f"Split into {len(split_docs)} chunks.")

    if not split_docs:
        print("No text chunks created after splitting. Check PDF content.")
        return None

    print(f"Attempting to create/update vector store at {CHROMA_DB_PATH_ABS}")

    vector_store = None
    # Chroma's add_documents can handle lists directly. Batching is good for very large inputs or specific API limits.
    # For simplicity here, we'll add all documents at once if creating, or in batches if updating an existing store.
    # The existing batching logic is fine.
    chroma_add_batch_size = 512 

    total_docs = len(split_docs)
    for i in range(0, total_docs, chroma_add_batch_size):
        batch_of_langchain_documents = split_docs[i:i + chroma_add_batch_size]
        current_batch_number = i // chroma_add_batch_size + 1
        total_batches = (total_docs + chroma_add_batch_size -1) // chroma_add_batch_size
        
        print(f"Processing Chroma batch {current_batch_number}/{total_batches}: "
              f"{len(batch_of_langchain_documents)} documents.")
        
        if vector_store is None: # If it's the first batch
            vector_store = Chroma.from_documents(
                documents=batch_of_langchain_documents,
                embedding=EMBEDDING_MODEL,
                collection_name=BOOK_COLLECTION_NAME,
                persist_directory=CHROMA_DB_PATH_ABS
            )
            print(f"Initial Chroma batch processed. Vector store initialized.")
        else: # For subsequent batches, add to the existing vector_store object
            vector_store.add_documents(documents=batch_of_langchain_documents)
            print(f"Subsequent Chroma batch processed.")
        
        if vector_store:
            print(f"Current vector store count: {vector_store._collection.count()}")
        else:
            print(f"Error: vector_store is None after processing batch {current_batch_number}")
            return None

    if vector_store:
        print(f"Successfully created/updated vector store with {vector_store._collection.count()} documents.")
    else:
        print("Vector store creation failed.")
    return vector_store


def get_existing_vector_store():
    if os.path.exists(CHROMA_DB_PATH_ABS) and any(os.scandir(CHROMA_DB_PATH_ABS)):
        try:
            print(f"Loading existing vector store from: {CHROMA_DB_PATH_ABS}")
            vector_store = Chroma(
                persist_directory=CHROMA_DB_PATH_ABS,
                embedding_function=EMBEDDING_MODEL,
                collection_name=BOOK_COLLECTION_NAME
            )
            if vector_store._collection.count() > 0:
                 print(f"Successfully loaded vector store with {vector_store._collection.count()} documents.")
                 return vector_store
            else:
                print("Found Chroma DB directory, but collection is empty or not found.")
                return None
        except Exception as e:
            print(f"Error loading existing vector store: {e}") # More specific error
            return None
    else:
        print(f"No existing vector store found at {CHROMA_DB_PATH_ABS}.")
        return None


def query_rag_pipeline(symptoms_query: str, vector_store: Chroma):
    if not vector_store:
        return "Error: Knowledge base (vector store) is not loaded. Please upload and process a PDF first."

    retriever = vector_store.as_retriever(search_kwargs={"k": 5}) # Increased k slightly for more context
    try:
        print(f"Retrieving top {retriever.search_kwargs['k']} documents for query: {symptoms_query}")
        book_docs = retriever.invoke(symptoms_query)
        book_context = "\n\n---\n\n".join([f"Source Document {i+1}:\n{doc.page_content}" for i, doc in enumerate(book_docs)]) # Added separator for clarity
        
        print("\n--- Retrieved Book Context (for LLM) START ---")
        print(book_context) 
        print(f"--- Total length of book_context: {len(book_context)} chars ---")
        print("--- Retrieved Book Context (for LLM) END ---\n")

        if not book_context.strip():
            book_context = "No relevant information was found in the uploaded book for the user's symptoms."
            print("WARNING: Book context was empty or only whitespace after retrieval.")
    except Exception as e:
        print(f"Error retrieving from vector store: {e}")
        book_context = "An error occurred while retrieving information from the book."

    ddg_search = DuckDuckGoSearchRun()
    try:
        # Web search query based on symptoms for general advice and potential medication classes if needed
        web_search_query = f"treatment options and advice for managing symptoms: {symptoms_query} (include lifestyle, diet, medication classes, do's and don'ts, when to see a doctor)"
        print(f"Performing Web Search with query: {web_search_query}")
        web_search_results = ddg_search.run(web_search_query)
        if not web_search_results:
             web_search_results = "No specific information found on the web for these symptoms via DuckDuckGo."
        
        print("\n--- Web Search Results (for LLM) START ---") # Changed key for consistency with prompt
        print(web_search_results)
        print(f"--- Total length of web_search_results: {len(web_search_results)} chars ---")
        print("--- Web Search Results (for LLM) END ---\n")

    except Exception as e:
        print(f"Error during DuckDuckGo search: {e}")
        web_search_results = "An error occurred during web search."

    qa_prompt_template_obj = get_qa_prompt_template() # Renamed to avoid conflict
    chain = qa_prompt_template_obj | LLM_MODEL | StrOutputParser()
    
    print("Invoking LLM chain (LCEL)...")
    input_data = {
        "book_context": book_context,
        "web_search_results": web_search_results, # Matches prompt
        "symptoms": symptoms_query
    }
    
    response_content = chain.invoke(input_data)
    print("LLM chain invocation complete.")
    return response_content

if __name__ == '__main__':
    # Your existing __main__ test block can be kept or adapted.
    # Ensure to test with symptoms that might trigger the detailed medication format.
    print("Testing RAG Pipeline with new prompt structure...")
    SCRIPT_DIR_RAG_MAIN = os.path.dirname(os.path.abspath(__file__))
    dummy_data_dir = os.path.join(SCRIPT_DIR_RAG_MAIN, "data")
    DUMMY_PDF_PATH = os.path.join(dummy_data_dir, "dummy_test_book_v3_meds.pdf")

    current_y_pos_for_test_pdf = 780
    def add_line_to_test_pdf(pdf_canvas_obj, text, indent=0):
        global current_y_pos_for_test_pdf
        pdf_canvas_obj.drawString(72 + indent, current_y_pos_for_test_pdf, text)
        current_y_pos_for_test_pdf -= 15
        if current_y_pos_for_test_pdf < 50:
            pdf_canvas_obj.showPage()
            pdf_canvas_obj.setFont("Helvetica", 10)
            current_y_pos_for_test_pdf = 780

    if not os.path.exists(dummy_data_dir): os.makedirs(dummy_data_dir)

    # Create a PDF specifically designed to test the new prompt logic for medications
    if True: # Always recreate for this test
        try:
            from reportlab.pdfgen import canvas
            pdf_canvas = canvas.Canvas(DUMMY_PDF_PATH)
            pdf_canvas.setFont("Helvetica", 10)
            current_y_pos_for_test_pdf = 780

            add_line_to_test_pdf(pdf_canvas, "Chapter: Common Cold & Flu")
            add_line_to_test_pdf(pdf_canvas, "Symptoms: Fever, cough, sore throat, runny nose, body aches, fatigue.", 10)
            add_line_to_test_pdf(pdf_canvas, "Pharmacological Information:", 10)
            add_line_to_test_pdf(pdf_canvas, "  - Drug Name: Acetaminophen (e.g., Tylenol)", 20)
            add_line_to_test_pdf(pdf_canvas, "    Purpose: Reduces fever and relieves minor aches and pains.", 30)
            add_line_to_test_pdf(pdf_canvas, "    Common Dosage (Example Only - Emphasize to consult doctor): Adults: 325-650 mg every 4-6 hours as needed. Max 3000-4000mg/day.", 30)
            add_line_to_test_pdf(pdf_canvas, "    Important Notes: Do not exceed maximum daily dose. Check other medications for acetaminophen.", 30)
            add_line_to_test_pdf(pdf_canvas, "  - Drug Name: Ibuprofen (e.g., Advil, Motrin)", 20)
            add_line_to_test_pdf(pdf_canvas, "    Purpose: Reduces fever, pain, and inflammation.", 30)
            add_line_to_test_pdf(pdf_canvas, "    Common Dosage (Example Only - Emphasize to consult doctor): Adults: 200-400 mg every 4-6 hours as needed. Max 1200mg/day (OTC).", 30)
            add_line_to_test_pdf(pdf_canvas, "    Important Notes: Take with food to reduce stomach upset. Not for everyone (check contraindications).", 30)
            add_line_to_test_pdf(pdf_canvas, "  - Drug Name: Guaifenesin (e.g., Mucinex)", 20)
            add_line_to_test_pdf(pdf_canvas, "    Purpose: Expectorant, helps loosen phlegm.", 30)
            add_line_to_test_pdf(pdf_canvas, "    Common Dosage (Example Only - Emphasize to consult doctor): Follow product labeling.", 30)
            add_line_to_test_pdf(pdf_canvas, "    Important Notes: Drink plenty of water.", 30)
            add_line_to_test_pdf(pdf_canvas, "Lifestyle: Rest, hydration.", 10)
            add_line_to_test_pdf(pdf_canvas, "Diet: Soups, fluids. Avoid alcohol.", 10)
            add_line_to_test_pdf(pdf_canvas, "Do: Wash hands. Don't: Smoke.", 10)
            add_line_to_test_pdf(pdf_canvas, "Red Flags: Difficulty breathing, high persistent fever.", 10)
            
            pdf_canvas.save()
            print(f"Created DUMMY TEST PDF with detailed meds: {DUMMY_PDF_PATH}")
        except ImportError: exit("ReportLab not found. Please install it: pip install reportlab")
        except Exception as e: exit(f"Error creating dummy PDF: {e}")

    if os.path.exists(CHROMA_DB_PATH_ABS): # Delete DB for this specific test run
        import shutil
        print(f"Deleting existing Chroma DB for fresh test: {CHROMA_DB_PATH_ABS}")
        shutil.rmtree(CHROMA_DB_PATH_ABS)
        
    test_vs = load_and_process_pdf(DUMMY_PDF_PATH)
    if test_vs:
        print(f"Vector store created/loaded for DUMMY TEST PDF. Documents: {test_vs._collection.count()}")
        
        symptoms = "fever, cough, body aches" 
        print(f"\nQuerying for symptoms: {symptoms}")
        response_text = query_rag_pipeline(symptoms, test_vs)
        print("\nLLM Response Text (should include detailed meds if parsed from book):")
        print(response_text)
    else:
        print("Failed to create or load vector store during DUMMY TEST PDF testing.")