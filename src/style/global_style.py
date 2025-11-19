css = """
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.5rem;
}
.sub-header {
    font-size: 1.1rem;
    color: #ffffff;
    font-weight: 700;
    margin-bottom: 2rem;
}
.answer-card {
    background: #252526; /* fallback for old browsers */
    background: -webkit-linear-gradient(to right, #005A9E, #0078D4, #005A9E); /* Chrome 10-25, Safari 5.1-6 */
    background: linear-gradient(to right, #005A9E, #0078D4, #005A9E); /* Modern browsers */
    padding: 1.5rem;
    border-radius: 10px;
    color: white;
    margin: 1rem 0;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.answer-title {
    font-size: 1.3rem;
    font-weight: 600;
    margin-bottom: 1rem;
}
.citation-item {
    background: rgba(255, 255, 255, 0.06);
    padding: 0.9rem 1rem;
    border-radius: 8px;
    margin: 0.6rem 0;
    border-left: 4px solid #0078D4; /* Azure blue accent */
    color: #ffffff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
    transition: background 0.2s ease, transform 0.1s ease;
}
.citation-item:hover {
    background: rgba(255, 255, 255, 0.10);
    transform: translateY(-1px);
}
.citation-item strong {
    color: #ffffff;
}
.citation-item small {
    color: rgba(255, 255, 255, 0.75);
}
.stButton>button {
    width: 100%;
    background: #0078D4; /* Azure blue fallback */
    background: -webkit-linear-gradient(to right, #005A9E, #0078D4, #00BCF2); /* Chrome 10-25, Safari 5.1-6 */
    background: linear-gradient(to right, #005A9E, #0078D4, #00BCF2); /* Modern browsers */
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 5px;
    padding: 0.35rem 0.9rem;
}
.stButton>button:hover {
    background: #005A9E; /* Azure dark blue fallback */
    background: -webkit-linear-gradient(to left, #005A9E, #0078D4, #00BCF2);
    background: linear-gradient(to left, #005A9E, #0078D4, #00BCF2);
}
/* Sidebar buttons: force bold label (affects '📚 Index Documents') */
[data-testid="stSidebar"] .stButton>button,
[data-testid="stSidebar"] .stButton>button * {
    font-weight: 800 !important;
}
/* Main area buttons: force bold label (affects '🔍 Search & Generate Answer') */
[data-testid="stAppViewContainer"] .stButton>button,
[data-testid="stAppViewContainer"] .stButton>button * {
    font-weight: 800 !important;
}
/* Main area search button sizing and inline text */
[data-testid="stAppViewContainer"] .stButton>button {
    height: 40px !important;           /* fixed height for consistent centering */
    min-height: 40px !important;
    padding: 0 1rem !important;        /* no vertical padding */
    font-size: 0.95rem !important;     /* align with slider row */
    line-height: 40px !important;      /* match height for perfect vertical centering */
    white-space: nowrap !important;    /* keep text on one line */
    display: grid !important;   /* enable grid centering */
    align-items: center !important;    /* vertical centering */
    justify-content: center !important;/* horizontal centering */
    text-align: center !important;     /* ensure text is centered */
    gap: 0 !important;                 /* no internal gaps */
    transform: translateY(-0.5px) !important; /* subtle optical nudge up */
}
[data-testid="stAppViewContainer"] .stButton { margin: 0 !important; width: 100% !important; }
[data-testid="stAppViewContainer"] .stButton>button * {
    margin: 0 !important;              /* remove inner element margins */
    line-height: inherit !important;   /* match parent for vertical centering */
    display: inline-block !important;  /* consistent vertical metrics */
}
/* Global dark background and text color */
[data-testid="stAppViewContainer"] {
    background-color: #1E1E1E !important;
    color: #ffffff !important;
}
[data-testid="stSidebar"] {
    background-color: #2D2D30 !important;
    color: #ffffff !important;
}
/* Top Streamlit header bar */
header[data-testid="stHeader"] {
    background: #1E1E1E !important;
    color: #ffffff !important;
    border-bottom: 1px solid #0078D4 !important;
}
header[data-testid="stHeader"] * {
    color: #ffffff !important;
}
/* Style the main question text input */
[data-testid="stTextInput"] input[type="text"] {
    background-color: rgba(255, 255, 255, 0.08) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    border-radius: 10px !important;
    padding: 0.75rem 1rem !important;
    height: 46px !important;
    font-size: 0.98rem !important;
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.35);
    transition: box-shadow 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}
[data-testid="stTextInput"] input[type="text"]::placeholder {
    color: rgba(255, 255, 255, 0.65) !important;
}
[data-testid="stTextInput"] input[type="text"]:focus {
    outline: none !important;
    border-color: #0078D4 !important;
    box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.6), inset 0 1px 2px rgba(0,0,0,0.35) !important;
    background-color: rgba(255, 255, 255, 0.10) !important;
}
/* Make the sidebar metric value (Indexed Documents number) bold and slightly larger */
[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    font-weight: 800 !important;
    font-size: 1rem !important;
    line-height: 1.2 !important;
}
/* Make only the sidebar file uploader label bold */
[data-testid="stSidebar"] [data-testid="stFileUploader"] label {
    font-weight: 700 !important;
}
</style>
"""
