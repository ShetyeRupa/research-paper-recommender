"""
Research Paper Recommender - Streamlit Web App
Complete version with flagging, persistence, and responsible AI features
"""
import streamlit as st
import pandas as pd
from recommender import PaperRecommender, create_sample_papers
from pdf_processor import PDFProcessor
import tempfile
import os
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Paper Recommender",
    page_icon="📚",
    layout="wide"
)

# Title
st.title("📚 Research Paper Recommender")
st.markdown("""
    *An AI-powered system that helps researchers find the most relevant papers 
    from their library based on what they are writing.*
""")

# ============================================================================
# PERSISTENT LIBRARY STORAGE
# ============================================================================

LIBRARY_FILE = "user_library.json"
FLAGGED_FILE = "flagged_papers.json"
CITATIONS_FILE = "my_citations.json"

def save_library():
    """Save current library to disk"""
    if st.session_state.recommender.papers:
        papers_to_save = []
        for paper in st.session_state.recommender.papers:
            paper_copy = paper.copy()
            paper_copy.pop('embedding', None) if 'embedding' in paper_copy else None
            papers_to_save.append(paper_copy)
        
        with open(LIBRARY_FILE, 'w') as f:
            json.dump(papers_to_save, f, indent=2)

def load_library():
    """Load library from disk"""
    if os.path.exists(LIBRARY_FILE):
        try:
            with open(LIBRARY_FILE, 'r') as f:
                papers = json.load(f)
                if papers:
                    st.session_state.recommender.add_papers(papers)
                    st.session_state.papers_loaded = True
                    return len(papers)
        except Exception as e:
            print(f"Error loading library: {e}")
    return 0

def save_flagged_papers():
    """Save flagged papers to disk"""
    if st.session_state.flagged_papers:
        with open(FLAGGED_FILE, 'w') as f:
            json.dump(st.session_state.flagged_papers, f, indent=2)

def load_flagged_papers():
    """Load flagged papers from disk"""
    if os.path.exists(FLAGGED_FILE):
        try:
            with open(FLAGGED_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_citations():
    """Save cited papers to disk"""
    if st.session_state.my_citations:
        with open(CITATIONS_FILE, 'w') as f:
            json.dump(st.session_state.my_citations, f, indent=2)

def load_citations():
    """Load cited papers from disk"""
    if os.path.exists(CITATIONS_FILE):
        try:
            with open(CITATIONS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if 'recommender' not in st.session_state:
    st.session_state.recommender = PaperRecommender()
if 'papers_loaded' not in st.session_state:
    st.session_state.papers_loaded = False
if 'recommendation_history' not in st.session_state:
    st.session_state.recommendation_history = []
if 'flagged_papers' not in st.session_state:
    st.session_state.flagged_papers = load_flagged_papers()
if 'my_citations' not in st.session_state:
    st.session_state.my_citations = load_citations()
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""
if 'last_recommendations' not in st.session_state:
    st.session_state.last_recommendations = []
# NEW: Flag to prevent duplicate sample paper loading
if 'sample_papers_loaded' not in st.session_state:
    st.session_state.sample_papers_loaded = False

# Try to load saved library on startup
if not st.session_state.papers_loaded:
    num_loaded = load_library()
    if num_loaded > 0:
        st.success(f"📚 Loaded {num_loaded} papers from your saved library")
        st.session_state.sample_papers_loaded = True  # Mark as loaded if library exists

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.header("📁 Your Paper Library")
    
    # Option to load sample papers - FIXED to prevent duplicate loading
    if st.button("📚 Load Sample Papers", use_container_width=True):
        if not st.session_state.sample_papers_loaded:
            with st.spinner("Loading sample papers..."):
                sample_papers = create_sample_papers()
                st.session_state.recommender.add_papers(sample_papers)
                st.session_state.papers_loaded = True
                st.session_state.sample_papers_loaded = True
                save_library()
                st.success(f"Loaded {len(sample_papers)} sample papers")
                st.rerun()
        else:
            st.info("Sample papers already loaded! Click 'Clear Library' if you want to reload.")
    
    st.divider()
    
    # Upload PDF files
    st.subheader("📄 Upload Your Own Papers")
    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload research papers to build your personalized library"
    )
    
    if uploaded_files:
        pdf_processor = PDFProcessor()
        new_papers = []
        
        for file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(file.getvalue())
                tmp_path = tmp_file.name
            
            with st.spinner(f"Processing {file.name}..."):
                paper_data = pdf_processor.process_paper(tmp_path)
                if paper_data:
                    paper_data["title"] = file.name.replace('.pdf', '').replace('_', ' ').title()
                    new_papers.append(paper_data)
            
            os.unlink(tmp_path)
        
        if new_papers:
            st.session_state.recommender.add_papers(new_papers)
            st.session_state.papers_loaded = True
            save_library()
            st.success(f"Added {len(new_papers)} new papers")
            st.rerun()
    
    st.divider()
    
    # Library stats
    if st.session_state.papers_loaded:
        st.subheader("📊 Library Stats")
        st.metric("Papers in Library", len(st.session_state.recommender.papers))
        
        # Show flagged count
        if st.session_state.flagged_papers:
            st.metric("Flagged for Review", len(st.session_state.flagged_papers))
        
        # Show citations count
        if st.session_state.my_citations:
            st.metric("Papers Cited", len(st.session_state.my_citations))
    
    # Export citations button
    if st.session_state.my_citations:
        st.divider()
        citations_text = "\n".join([f"- {c['title']} ({c['year']})" for c in st.session_state.my_citations])
        st.download_button(
            label="📋 Export Citations",
            data=citations_text,
            file_name=f"my_citations_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    st.divider()
    
    # Clear library button - FIXED to reset sample_papers_loaded flag
    if st.button("🗑️ Clear Library", use_container_width=True):
        st.session_state.recommender.clear()
        st.session_state.papers_loaded = False
        st.session_state.recommendation_history = []
        st.session_state.flagged_papers = []
        st.session_state.my_citations = []
        st.session_state.last_recommendations = []
        st.session_state.sample_papers_loaded = False  # Reset sample flag
        if os.path.exists(LIBRARY_FILE):
            os.remove(LIBRARY_FILE)
        if os.path.exists(FLAGGED_FILE):
            os.remove(FLAGGED_FILE)
        if os.path.exists(CITATIONS_FILE):
            os.remove(CITATIONS_FILE)
        st.success("Library cleared!")
        st.rerun()

# ============================================================================
# MAIN AREA - TWO COLUMNS
# ============================================================================

col1, col2 = st.columns([1, 1])

with col1:
    st.header("✍️ Your Writing")
    st.markdown("*Paste the section you are currently writing*")
    
    query_text = st.text_area(
        "Write your paragraph here:",
        placeholder="Example: Recent advances in attention mechanisms have transformed natural language processing. The Transformer architecture, introduced by Vaswani et al. (2017), replaced recurrent networks with self-attention...",
        height=200
    )
    
    col_rec1, col_rec2 = st.columns(2)
    with col_rec1:
        top_k = st.selectbox("Number of recommendations", [3, 5, 10], index=1)
    with col_rec2:
        min_score = st.slider(
            "Minimum relevance score", 
            0.0, 1.0, 0.3, 0.05,
            help="Papers below this score will not be shown. Lower = more results, less accurate."
        )
    
    if st.button("🔍 Find Relevant Papers", type="primary", use_container_width=True):
        if not st.session_state.papers_loaded:
            st.error("Please load some papers first (click 'Load Sample Papers')")
        elif not query_text.strip():
            st.error("Please enter your writing to search for relevant papers")
        else:
            with st.spinner("Searching for relevant papers using semantic similarity..."):
                recommendations = st.session_state.recommender.recommend(
                    query_text, 
                    top_k=top_k, 
                    min_score=min_score
                )
                
                if recommendations:
                    st.session_state.recommendation_history = recommendations
                    st.session_state.last_recommendations = recommendations
                    st.session_state.last_query = query_text
                    st.success(f"Found {len(recommendations)} relevant papers")
                    
                    # SILENT FAILURE MITIGATION - Check if top score is low
                    if recommendations and recommendations[0]['similarity_score'] < 0.5:
                        st.warning("⚠️ **No strong matches found (confidence < 0.5).** Try different keywords or search manually. AI works best with specific technical terms.")
                else:
                    st.warning(f"⚠️ **No papers found above {min_score} relevance threshold.** Try:\n- Lowering the minimum score\n- Using more specific technical terms\n- Adding more papers to your library")
                    st.session_state.recommendation_history = []

with col2:
    st.header("📖 Recommended Papers")
    st.markdown("*Ranked by semantic similarity to your writing*")
    
    # DOMAIN DRIFT WARNING (shown when using new/specific terminology)
    if query_text and len(query_text) > 20:
        new_terms = ["RAG", "LoRA", "QLoRA", "GPT-4", "Gemma", "Mistral", "Claude"]
        found_new_terms = [term for term in new_terms if term.lower() in query_text.lower()]
        if found_new_terms:
            st.info(f"💡 **Note:** Terms like {', '.join(found_new_terms)} are recent. Our embeddings may not fully capture them yet. Try adding synonyms or manual keywords if needed.")
    
    if st.session_state.recommendation_history:
        for i, paper in enumerate(st.session_state.recommendation_history, 1):
            # Determine color based on relevance
            if paper['similarity_score'] >= 0.7:
                color = "🟢"
                score_status = "Strong match"
            elif paper['similarity_score'] >= 0.5:
                color = "🟡"
                score_status = "Good match"
            else:
                color = "🟠"
                score_status = "Weak match - verify carefully"
            
            with st.container():
                st.markdown(f"### {color} {i}. {paper['title']}")
                
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.markdown(f"**Authors:** {paper['authors']}")
                    st.markdown(f"**Year:** {paper['year']}")
                with col_b:
                    st.markdown(f"**Similarity:** {paper['similarity_score']:.0%}")
                    st.markdown(f"**{score_status}**")
                
                with st.expander("📄 View Abstract"):
                    st.write(paper['abstract'])
                
                # Buttons row
                col_cite, col_flag, _ = st.columns([1, 1, 3])
                
                # Cite button (Human-in-the-loop)
                with col_cite:
                    if st.button(f"📝 Cite", key=f"cite_{i}"):
                        citation_entry = {
                            "title": paper['title'],
                            "authors": paper['authors'],
                            "year": paper['year'],
                            "similarity": paper['similarity_score'],
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        # Avoid duplicates
                        if not any(c['title'] == paper['title'] for c in st.session_state.my_citations):
                            st.session_state.my_citations.append(citation_entry)
                            save_citations()
                            st.success(f"✅ Added to your citations: {paper['title']}")
                        else:
                            st.info(f"📌 Already in your citations: {paper['title']}")
                
                # Flag button (User feedback for bad recommendations)
                with col_flag:
                    if st.button(f"🚩 Flag", key=f"flag_{i}"):
                        # Check if already flagged
                        already_flagged = False
                        for f in st.session_state.flagged_papers:
                            if isinstance(f, dict) and f.get('title') == paper['title']:
                                already_flagged = True
                                break
                        if not already_flagged:
                            st.session_state.flagged_papers.append({
                                "title": paper['title'],
                                "reason": "User flagged as irrelevant",
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "query_context": st.session_state.last_query[:200] if st.session_state.last_query else ""
                            })
                            save_flagged_papers()
                            st.warning(f"🚩 Flagged: {paper['title']}. Thanks for helping us improve!")
                        else:
                            st.info(f"Already flagged this paper")
                
                st.divider()
    else:
        if st.session_state.papers_loaded:
            st.info("Enter your writing above and click 'Find Relevant Papers' to see recommendations.")
        else:
            st.warning("No papers in library. Click 'Load Sample Papers' or upload your own PDFs to get started.")
    
    # Show flagged papers summary if any
    if st.session_state.flagged_papers:
        with st.expander("🚩 Flagged Papers (for review)"):
            for flagged in st.session_state.flagged_papers:
                if isinstance(flagged, dict):
                    st.write(f"- {flagged['title']} (flagged on {flagged['timestamp']})")

# ============================================================================
# HUMAN-IN-THE-LOOP REMINDER & RESPONSIBLE AI SECTION
# ============================================================================

st.divider()
with st.container():
    st.markdown("""
    ### 👩‍💻 Human-in-the-Loop Design & Responsible AI
    
    | Feature | Status | Description |
    |:---|:---|:---|
    | Similarity scores displayed | ✅ Active | Every recommendation shows 0-100% match |
    | Confidence threshold filter | ✅ Active | Papers below min_score are hidden |
    | User decides which papers to cite | ✅ Active | You click "Cite" to approve each paper |
    | Flag bad recommendations | ✅ Active | Click "Flag" to report irrelevant results |
    | Silent failure mitigation | ✅ Active | Shows warning when confidence < 0.5 |
    | Domain drift warning | ✅ Active | Detects recent terminology |
    | Export citations | ✅ Active | Download your cited papers as text file |
    
    > ⚠️ **Remember:** AI recommendations are suggestions. Always verify papers before citing them in your research.
    > 
    > 💡 **Tip:** If you're not finding what you need, try:
    > - Using more specific technical keywords
    > - Lowering the minimum relevance score (slider above)
    > - Uploading more papers to your library
    """)

# Display current citations summary
if st.session_state.my_citations:
    with st.expander(f"📋 My Citations ({len(st.session_state.my_citations)} papers)"):
        for cited in st.session_state.my_citations:
            st.write(f"- {cited['title']} ({cited['year']}) - Cited on {cited['timestamp']}")