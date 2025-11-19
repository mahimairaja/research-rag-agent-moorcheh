css = """
    <style>
    [data-testid=\"stTextInput\"] input[type=\"text\"] {
        background-color: #111111 !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 8px !important;
        box-sizing: border-box !important;
        height: 42px !important;
        line-height: 42px !important; /* centers text vertically */
        padding: 0 14px !important; /* no vertical padding */
        font-size: 1rem !important;
        vertical-align: middle !important;
        -webkit-appearance: none !important;
        appearance: none !important;
        caret-color: #ffffff !important;
        transition: box-shadow 0.2s ease, border-color 0.2s ease;
    }
    [data-testid="stTextInput"] input[type="text"]::placeholder { color: rgba(255,255,255,0.6) !important; }
    [data-testid=\"stTextInput\"] input[type=\"text\"]:focus {
        outline: none !important;
        border-color: #0078D4 !important;
        box-shadow: 0 0 0 2px rgba(0,120,212,0.45) !important;
        background-color: #111111 !important;
    }
    /* Center the built-in Streamlit widget instruction inside the input */
    [data-testid="stTextInput"] > div { position: relative !important; }
    [data-testid="stTextInput"] [data-testid="stWidgetInstructions"] {
        position: absolute !important;
        right: 12px !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        margin: 0 !important;
        padding: 0 !important;
        font-size: 0.85rem !important;
        color: rgba(255,255,255,0.65) !important;
        pointer-events: none !important;
    }
    </style>
    """
