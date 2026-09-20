import streamlit as st
from api_client import api_client, API_BASE_URL

# Page Config
st.set_page_config(
    page_title="ITI Document Assistant - معهد تكنولوجيا المعلومات",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .source-box {
        background-color: #F8FAFC;
        border-left: 4px solid #0284C7;
        padding: 0.8rem;
        margin-top: 0.5rem;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    .citation-badge {
        background-color: #E0F2FE;
        color: #0369A1;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/color/96/graduation-cap.png", width=70)
    st.title("ITI Assistant Setup")
    st.markdown(f"**Backend Endpoint:**\n`{API_BASE_URL}`")
    
    # Health status check button
    if st.button("🔌 Test Backend Connection"):
        health = api_client.check_health()
        if health["success"]:
            st.success("✅ Backend Online & Reachable!")
            st.json(health["data"])
        else:
            st.error(f"❌ Connection Failed:\n{health['error']}")
            
    st.divider()
    st.markdown("### ⚙️ Search Settings")
    top_k = st.slider("Top-K Chunks to Retrieve", min_value=1, max_value=8, value=3)
    
    st.divider()
    st.markdown("### 💡 Sample ITI Questions")
    sample_questions = [
        "What is the ITI 9-Month Professional Training Program?",
        "What are the admission requirements for ITI grants?",
        "What is the Intensive Code Camp (ICC) and how long does it last?",
        "Where are ITI branches and Creativa Hubs located?",
        "Which entrance exams are required during ITI selection?",
        "What is the minimum mandatory attendance percentage for ITI students?"
    ]
    for q in sample_questions:
        if st.button(q, use_container_width=True):
            st.session_state["user_input_query"] = q

# Main UI
st.markdown('<div class="main-header">🎓 ITI RAG Document Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Ask questions about Information Technology Institute (ITI - معهد تكنولوجيا المعلومات) programs, admission requirements, tracks, and Creativa branches.</div>', unsafe_allow_html=True)

# Session state initialization for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to the Information Technology Institute (ITI) RAG Assistant! How can I help you regarding ITI programs, admission criteria, or governorate branches?", "sources": []}
    ]

# Render prior chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            st.markdown("**Cited Sources:**")
            sources_html = "".join([f'<span class="citation-badge">📄 {src}</span>' for src in message["sources"]])
            st.markdown(f'<div style="margin-top: 0.3rem;">{sources_html}</div>', unsafe_allow_html=True)

# Chat Input Handler
input_query = st.chat_input("Ask a question about ITI (e.g., 9-Month program, Creativa hubs, admission tests)...")

# Handle sample button click selection
if "user_input_query" in st.session_state and st.session_state["user_input_query"]:
    prompt = st.session_state.pop("user_input_query")
else:
    prompt = input_query

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔎 Searching ITI vector database & synthesizing grounded answer..."):
            res = api_client.query(question=prompt, top_k=top_k)
            
        if res["success"]:
            data = res["data"]
            answer = data.get("answer", "No answer generated.")
            sources = data.get("sources", [])
            retrieved_chunks = data.get("retrieved_chunks", [])
            
            st.markdown(answer)
            
            if sources:
                st.markdown("**Cited Sources:**")
                sources_html = "".join([f'<span class="citation-badge">📄 {src}</span>' for src in sources])
                st.markdown(f'<div style="margin-top: 0.3rem;">{sources_html}</div>', unsafe_allow_html=True)
                
            if retrieved_chunks:
                with st.expander("📚 View Retrieved Context Chunks"):
                    for idx, chunk in enumerate(retrieved_chunks, 1):
                        st.markdown(f"**Chunk {idx}** | Source: `{chunk.get('source')}` | Relevance Score: `{chunk.get('score', 'N/A')}`")
                        st.info(chunk.get("content", ""))
                        
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })
        else:
            error_msg = res["error"]
            st.error(f"⚠️ {error_msg}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ Error: {error_msg}",
                "sources": []
            })
