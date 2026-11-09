import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import io
import re
import json

st.set_page_config(page_title="ፈጣን ድለላ", layout="wide")

##### CSS
st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #fef08a 0%, #f1f5f9 100%); }
        [data-testid="stHeader"] { background-color: #ffffff !important; }
        [data-testid="stHeader"] *, [data-testid="stHeader"] svg { color: #1e293b !important; fill: #1e293b !important; }
        html, body, [data-testid="stWidgetLabel"] p, .stMarkdown p, p, li, span {
            font-size: 22px !important; font-weight: 500 !important; color: #1e293b !important;
        }
        [data-testid="stFileUploader"] div, [data-testid="stFileUploaderDropzone"] {
            background-color: #ffffff !important; color: #1e293b !important; border: 2px dashed #cbd5e1 !important;
        }
        [data-testid="stFileUploaderDropzone"] p, [data-testid="stFileUploaderDropzone"] span { color: #1e293b !important; }
        div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input {
            background-color: #ffffff !important; color: #1e293b !important; border: 1px solid #cbd5e1 !important;
        }
        [data-testid="stDataFrame"] div, [data-testid="stDataFrame"] table, [data-testid="stDataFrame"] th, [data-testid="stDataFrame"] td {
            background-color: #ffffff !important; color: #1e293b !important;
        }
        [data-testid="stSidebar"] { background-color: #ffffff !important; background: #ffffff !important; }
        [data-testid="stSidebar"] .stRadio label p { color: #1e293b !important; font-size: 18px !important; font-weight: 700 !important; }
        div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #1e293b !important; border: 1px solid #cbd5e1 !important; }
        div[data-baseweb="popover"] ul, div[data-baseweb="popover"] li { background-color: #ffffff !important; color: #1e293b !important; }
        .stTabs [data-baseweb="tab"] p { color: #1e3a8a !important; font-size: 21px !important; font-weight: bold !important; }
        .stTabs [aria-selected="true"] p { color: #ffffff !important; }
        .worker-card {
            background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);
            border-radius: 20px; padding: 26px; box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.05);
            border-left: 6px solid #3b82f6; margin-bottom: 30px;
        }
        div[data-testid="stCheckbox"] {
            background-color: #f0fdf4 !important; padding: 14px 24px !important; border-radius: 12px !important;
            border: 2px solid #22c55e !important; box-shadow: 0 4px 6px rgba(34, 197, 94, 0.15) !important;
            margin: 15px 0 !important; width: fit-content !important;
        }
        div[data-testid="stCheckbox"] label p { font-size: 21px !important; font-weight: 800 !important; color: #15803d !important; }
        input, select, textarea { font-size: 22px !important; color: #1e293b !important; background-color: #ffffff !important; }
        .stForm { background: #ffffff !important; border-radius: 20px !important; padding: 35px !important; border: 1px solid #cbd5e1 !important; }
        .stImage > img { border-radius: 15px !important; }
        div.stFormSubmitButton > button, div.stButton > button[key^="submit_"] {
            background-color: #16a34a !important; color: white !important; border-radius: 12px !important;
            border: none !important; padding: 14px 32px !important; font-weight: 800 !important; font-size: 20px !important;
        }
        div.stButton > button[key^="del_"], div.stButton > button[key^="delorder_"] { background-color: #dc2626 !important; color: white !important; font-size: 16px !important; }
        div.stButton > button:not([key^="del_"]):not([key^="delorder_"]):not([key^="submit_"]):not([data-testid="baseButton-secondaryFormSubmit"]) { background-color: #2563eb !important; color: white !important; }

        /* 🔠 ትልቅ የጽሁፍ መጠኖች */
        h1, h1 * { font-size: 42px !important; font-weight: 800 !important; color: #1e3a8a !important; }
        h2, h2 *, h3, h3 * { font-size: 30px !important; font-weight: 700 !important; color: #1e293b !important; }
        [data-testid="stWidgetLabel"] p { font-size: 23px !important; font-weight: 700 !important; }
        div[role="radiogroup"] label p { font-size: 22px !important; font-weight: 700 !important; }
        div[data-baseweb="select"] * { font-size: 22px !important; }
        div[data-baseweb="popover"] li, div[data-baseweb="popover"] li * { font-size: 22px !important; }
        div.stButton > button p, div.stFormSubmitButton > button p { font-size: 22px !important; font-weight: 800 !important; }
        [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { font-size: 20px !important; }
        [data-testid="stAlert"] p { font-size: 22px !important; }

        /* "Press Enter to submit form" የሚለውን ጽሁፍ ደብቅ */
        [data-testid="InputInstructions"], div[data-testid="InputInstructions"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS applicants (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone TEXT NOT NULL, job_type TEXT NOT NULL, experience TEXT, photo BLOB)')
    cursor.execute('CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, employer_name TEXT NOT NULL, employer_phone TEXT NOT NULL, applicant_id INTEGER, applicant_name TEXT, status TEXT DEFAULT "አዲስ ጥያቄ")')
    conn.commit()
    conn.close()

init_db()

def load_data():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    df = pd.read_sql_query("SELECT * FROM applicants", conn)
    conn.close()
    return df

def load_orders():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    df = pd.read_sql_query("SELECT * FROM orders", conn)
    conn.close()
    return df

def update_order_status(order_id, new_status):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
    conn.commit()
    conn.close()

def delete_applicant(applicant_id):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM applicants WHERE id = ?', (applicant_id,))
    conn.commit()
    conn.close()

def delete_order(order_id):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    conn.commit()
    conn.close()

# ✍️ የመሙያ ሳጥኖች ስሞች (እዚህ ብቻ ይቀየራሉ፣ የመከልከያው ስክሪፕት ራሱ ይከተላቸዋል)
LABEL_NAME = "ሙሉ ስም"
LABEL_PHONE = "ስልክ ቁጥር:"
LABEL_EMP_NAME = "የእርስዎ ስም:"
LABEL_EMP_PHONE = "የእርስዎ ስልክ:"
LABEL_EXPERIENCE = "የስራ ልምድ:"

def name_has_digit(text):
    return any(ch in "0123456789" for ch in text)

def format_experience(value):
    # ቁጥር ብቻ ከሆነ "አመት" ይጨምራል፤ ቀድሞ በጽሁፍ የተመዘገበ ልምድ እንዳለ ይታያል
    text = "" if value is None or (isinstance(value, float) and pd.isna(value)) else str(value).strip()
    if not text:
        return "—"
    return f"{text} አመት" if text.isdigit() else text

def phone_is_valid(text):
    # ቁጥሮች ብቻ (መጀመሪያ ላይ + ይፈቀዳል)፣ ከ 9 እስከ 13 አሃዝ
    return re.fullmatch(r"\+?[0-9]{9,13}", text) is not None

GUARD_JS = """
<script>
(function () {
  const CFG = __CFG__;
  const PWin = window.parent;
  const pdoc = PWin.document;
  const token = String(Math.random());

  function setValue(el, value) {
    const setter = Object.getOwnPropertyDescriptor(PWin.HTMLInputElement.prototype, 'value').set;
    setter.call(el, value);
    el.dispatchEvent(new PWin.Event('input', { bubbles: true }));
  }

  function clean(kind, value) {
    if (kind === 'phone') {
      return value.replace(/[^0-9+]/g, '').replace(/(?!^)\\+/g, '');
    }
    if (kind === 'number') {
      return value.replace(/[^0-9]/g, '');
    }
    return value.replace(/[0-9]/g, '');
  }

  function guard(el, kind) {
    const handler = function (e) {
      if (e && e.isComposing) return;
      const cleaned = clean(kind, el.value);
      if (cleaned !== el.value) {
        const removed = el.value.length - cleaned.length;
        const pos = Math.max(0, (el.selectionStart || 0) - removed);
        setValue(el, cleaned);
        try { el.setSelectionRange(pos, pos); } catch (err) {}
      }
    };
    el.addEventListener('input', handler);
    el.addEventListener('compositionend', handler);
  }

  function scan() {
    pdoc.querySelectorAll('input').forEach(function (el) {
      if (el.dataset.guardToken === token) return;
      const label = el.getAttribute('aria-label') || '';
      let kind = null;
      if (CFG.names.indexOf(label) !== -1) kind = 'name';
      else if (CFG.phones.indexOf(label) !== -1) kind = 'phone';
      else if (CFG.numbers.indexOf(label) !== -1) kind = 'number';
      if (!kind) return;
      el.dataset.guardToken = token;
      if (kind === 'phone') el.setAttribute('inputmode', 'tel');
      if (kind === 'number') el.setAttribute('inputmode', 'numeric');
      guard(el, kind);
    });
  }

  scan();
  new MutationObserver(scan).observe(pdoc.body, { childList: true, subtree: true });
})();
</script>
"""

def enable_input_guard():
    # ስም ሳጥን ውስጥ ቁጥር፣ ስልክ ሳጥን ውስጥ ፊደል ሲጻፍ ወዲያውኑ ያጠፋል
    cfg = json.dumps({"names": [LABEL_NAME, LABEL_EMP_NAME], "phones": [LABEL_PHONE, LABEL_EMP_PHONE], "numbers": [LABEL_EXPERIENCE]}, ensure_ascii=False)
    html = GUARD_JS.replace("__CFG__", cfg).strip()
    try:
        if hasattr(st, "iframe"):          # አዲስ የ Streamlit ስሪቶች
            st.iframe(html, height=1)
        else:                              # የድሮ ስሪቶች
            import streamlit.components.v1 as components
            components.html(html, height=0)
    except Exception:
        pass  # ስክሪፕቱ ባይሰራም ከታች ያለው የማረጋገጫ ፍተሻ ይሰራል

st.title("ፈጣን ድለላ")
enable_input_guard()

###### menu
page = st.radio("Menu", ["የሰራተኛ መመዝገቢያ", "ዝግጁ የሆኑ ሰራተኞች ዝርዝር", "Admin Only"], horizontal=True)

if page == "የሰራተኛ መመዝገቢያ":
    st.subheader("ከቤትዎ ሆነው በቀላሉ ይመዝግቡ")
    reg_n = st.session_state.get("reg_n", 0)
    if st.session_state.pop("reg_ok", False):
        st.success("ማመልከቻዎ ደርሶናል! በቅርቡ እናሳውቅወታለን")
    with st.form("registration_form"):
        name = st.text_input(LABEL_NAME, key=f"reg_name_{reg_n}")
        phone = st.text_input(LABEL_PHONE, max_chars=13, key=f"reg_phone_{reg_n}")
        job_type = st.selectbox("የስራ አይነት:", ["የቡና ባለሙያ", "ወጥ ቤት", "ፅዳት", "ሌላ"], key=f"reg_job_{reg_n}")
        experience = st.text_input(LABEL_EXPERIENCE, max_chars=2, key=f"reg_exp_{reg_n}")
        uploaded_file = st.file_uploader("ፎቶዎን ይጫኑ (ግዴታ):", type=["jpg", "jpeg", "png"], key=f"reg_photo_{reg_n}")
        submit_button = st.form_submit_button("ይጫኑ")
        if submit_button:
            phone_clean = phone.replace(" ", "")
            if not (name.strip() and phone_clean and uploaded_file):
                st.error("እባክዎ ሙሉ ስም፣ ስልክ ቁጥር እና ፎቶ ያስገቡ።")
            elif name_has_digit(name):
                st.error("በስም ውስጥ ቁጥር መጻፍ አይቻልም።")
            elif not phone_is_valid(phone_clean):
                st.error("ስልክ ቁጥር ቁጥሮችን ብቻ መያዝ አለበት (ለምሳሌ 0912345678)።")
            elif experience.strip() and re.fullmatch(r"[0-9]{1,2}", experience.strip()) is None:
                st.error("የስራ ልምድ ቁጥር ብቻ መሆን አለበት (በአመት፣ ለምሳሌ 3)።")
            else:
                photo_bytes = uploaded_file.read()
                conn = sqlite3.connect('database.db', check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute('INSERT INTO applicants (name, phone, job_type, experience, photo) VALUES (?, ?, ?, ?, ?)', (name.strip(), phone_clean, job_type, experience.strip(), photo_bytes))
                conn.commit()
                conn.close()
                st.session_state["reg_n"] = reg_n + 1
                st.session_state["reg_ok"] = True
                st.rerun()

elif page == "ዝግጁ የሆኑ ሰራተኞች ዝርዝር":
    st.subheader("የሚፈልጉትን ሰራተኛ ይምረጡ")
    df = load_data()
    if not df.empty:
        job_filter = st.selectbox("የስራ አይነት ይምረጡ:", ["ሁሉም"] + list(df["job_type"].unique()))
        filtered_df = df if job_filter == "ሁሉም" else df[df["job_type"] == job_filter]
        for index, row in filtered_df.iterrows():
            st.markdown('<div class="worker-card">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if row['photo']:
                    st.image(Image.open(io.BytesIO(row['photo'])), width=150, caption=f"ኮድ BDR-{row['id']}")
                else:
                    st.write("❌ ፎቶ የለም")
            with col2:
                badge_color = "#ea580c" if row['job_type'] in ("የቡና ባለሙያ", "የቡና አፍዪ") else ("#16a34a" if row['job_type'] == "ወጥ ቤት" else "#7c3aed")
                st.subheader(f"ስም: {row['name']}")
                st.markdown(f"<p style='font-size:16px;'>💼 <b>የስራ ዘርፍ:</b> <span style='background-color:{badge_color}; color:#ffffff; padding:4px 10px; border-radius:12px; font-weight:600;'>{row['job_type']}</span></p>", unsafe_allow_html=True)
                st.write(f"📜 **የስራ ልምድ:** {format_experience(row['experience'])}")
                show_form = st.checkbox(f"ይህንን ሰራተኛ መቅጠር እፈልጋለሁ", key=f"check_{row['id']}")
                if show_form:
                    rid = int(row['id'])
                    ord_n = st.session_state.get(f"ord_n_{rid}", 0)
                    if st.session_state.pop(f"ord_ok_{rid}", False):
                        st.success("ጥያቄዎ ደርሶናል! በቅርቡ እናሳውቅዎታለን")
                    with st.form(f"order_form_{rid}"):
                        emp_name = st.text_input(LABEL_EMP_NAME, key=f"emp_name_{rid}_{ord_n}")
                        emp_phone = st.text_input(LABEL_EMP_PHONE, max_chars=13, key=f"emp_phone_{rid}_{ord_n}")
                        submit_order = st.form_submit_button("ላክ")
                        if submit_order:
                            emp_phone_clean = emp_phone.replace(" ", "")
                            if not (emp_name.strip() and emp_phone_clean):
                                st.error("እባክዎ ስምዎን እና ስልክዎን ያስገቡ።")
                            elif name_has_digit(emp_name):
                                st.error("በስም ውስጥ ቁጥር መጻፍ አይቻልም።")
                            elif not phone_is_valid(emp_phone_clean):
                                st.error("ስልክ ቁጥር ቁጥሮችን ብቻ መያዝ አለበት (ለምሳሌ 0912345678)።")
                            else:
                                conn = sqlite3.connect('database.db', check_same_thread=False)
                                cursor = conn.cursor()
                                cursor.execute('INSERT INTO orders (employer_name, employer_phone, applicant_id, applicant_name) VALUES (?, ?, ?, ?)', (emp_name.strip(), emp_phone_clean, rid, row['name']))
                                conn.commit()
                                conn.close()
                                st.session_state[f"ord_n_{rid}"] = ord_n + 1
                                st.session_state[f"ord_ok_{rid}"] = True
                                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

elif page == "Admin Only":
    st.subheader("የአስተዳዳሪ መቆጣጠሪያ")
    password = st.text_input("Password ያስገቡ፦", type="password")
    if password == "123":
        tab1, tab2 = st.tabs(["የተመዘገቡ ሰራተኞች", "የመጡ የቅጥር ጥያቄዎች"])
        with tab1:
            df_admin = load_data()
            if not df_admin.empty:
                for index, row in df_admin.iterrows():
                    st.markdown('<div class="worker-card">', unsafe_allow_html=True)
                    st.markdown(f"**BDR-{row['id']}** | **ስም:** {row['name']} | 📞 **ስልክ:** {row['phone']} | 💼 **ስራ:** {row['job_type']}")
                    if st.button("❌ ይህንን ሰራተኛ አጥፋ", key=f"del_{row['id']}"):
                        delete_applicant(row['id'])
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            else: st.info("እስካሁን ምንም ሰራተኛ አልተመዘገበም።")
        with tab2:
            orders_df = load_orders()
            if not orders_df.empty:
                status_options = ["አዲስ ጥያቄ", "በሂደት ላይ", "ተጠናቋል"]
                for index, row in orders_df.iterrows():
                    order_id = int(row['id'])
                    st.markdown('<div class="worker-card">', unsafe_allow_html=True)
                    st.markdown(f"**ጥያቄ #{order_id}** | 🏢 **ቀጣሪ:** {row['employer_name']} | 📞 **ስልክ:** {row['employer_phone']}")
                    st.markdown(f"👤 **የተጠየቀው ሰራተኛ:** {row['applicant_name']} (BDR-{row['applicant_id']})")
                    st.markdown(f"**አሁን ያለበት ሁኔታ:** {row['status']}")
                    current_status = row['status'] if row['status'] in status_options else status_options[0]
                    new_status = st.selectbox("ሁኔታ ቀይር:", status_options, index=status_options.index(current_status), key=f"status_{order_id}")
                    col_save, col_del = st.columns(2)
                    with col_save:
                        if st.button("ሁኔታውን አስቀምጥ", key=f"save_{order_id}"):
                            update_order_status(order_id, new_status)
                            st.rerun()
                    with col_del:
                        if st.button("❌ ጥያቄውን አጥፋ", key=f"delorder_{order_id}"):
                            delete_order(order_id)
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("እስካሁን ምንም የቅጥር ጥያቄ አልመጣም።")
    elif password:
        st.error("❌ Password የተሳሳተ ነው።")
