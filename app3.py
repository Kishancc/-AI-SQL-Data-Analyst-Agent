import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from fpdf import FPDF

from langchain_groq import ChatGroq

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI SQL Data Analyst",
    page_icon="🤖",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "query_history" not in st.session_state:
    st.session_state.query_history = []

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Settings")

groq_api_key = st.sidebar.text_input(
    "Enter Groq API Key",
    type="password"
)

model_option = st.sidebar.selectbox(
    "Select AI Model",
    [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]
)

theme_mode = st.sidebar.radio(
    "Theme",
    ["Dark", "Light"]
)

# ---------------- THEME CSS ----------------
if theme_mode == "Dark":

    st.markdown("""
    <style>

    .stApp {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        color: white;
    }

    .main-title {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        color: white;
        margin-top: 10px;
    }

    .sub-title {
        text-align: center;
        color: #cbd5e1;
        font-size: 20px;
        margin-bottom: 30px;
    }

    [data-testid="metric-container"] {
        background: rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 15px;
    }

    section[data-testid="stSidebar"] {
        background: rgba(255,255,255,0.05);
    }

    .stButton > button {
        background: linear-gradient(to right, #3b82f6, #8b5cf6);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 10px 25px;
        font-size: 16px;
        font-weight: bold;
    }

    </style>
    """, unsafe_allow_html=True)

else:

    st.markdown("""
    <style>

    .stApp {
        background: white;
        color: black;
    }

    .main-title {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        color: black;
        margin-top: 10px;
    }

    .sub-title {
        text-align: center;
        color: #475569;
        font-size: 20px;
        margin-bottom: 30px;
    }

    </style>
    """, unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown(
    '<div class="main-title">🤖 AI SQL Data Analyst Platform</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">AI SQL Queries • Business Insights • Smart Visualizations</div>',
    unsafe_allow_html=True
)

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "📂 Upload CSV File",
    type=["csv"]
)

# ---------------- PDF FUNCTION ----------------
def generate_pdf(summary_text):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="AI SQL Data Analyst Report", ln=True)

    pdf.multi_cell(0, 10, summary_text)

    pdf.output("report.pdf")

# ---------------- MAIN APP ----------------
if uploaded_file:

    try:
        df = pd.read_csv(uploaded_file)

    except Exception:
        st.error("❌ Could not read CSV file")
        st.stop()

    # ---------------- SQLITE ----------------
    conn = sqlite3.connect("data.db")

    df.to_sql(
        "data_table",
        conn,
        if_exists="replace",
        index=False
    )

    # ---------------- DATASET INSIGHTS ----------------
    st.markdown("## 📌 Dataset Insights")

    total_rows = df.shape[0]
    total_columns = df.shape[1]
    missing_values = int(df.isnull().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric("📄 Rows", total_rows)

    with m2:
        st.metric("📊 Columns", total_columns)

    with m3:
        st.metric("❌ Missing Values", missing_values)

    with m4:
        st.metric("🔁 Duplicate Rows", duplicate_rows)

    # ---------------- PREVIEW ----------------
    left, right = st.columns(2)

    with left:

        st.markdown("## 📊 Data Preview")

        st.dataframe(
            df.head(20),
            use_container_width=True
        )

    with right:

        st.markdown("## 🧠 Schema")

        schema_df = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str)
        })

        st.dataframe(
            schema_df,
            use_container_width=True
        )

    # ---------------- SUGGESTED QUESTIONS ----------------
    st.markdown("## 🤖 Suggested Questions")

    numeric_cols = df.select_dtypes(include=['number']).columns

    suggestions = []

    for col in numeric_cols:
        suggestions.append(f"What is average {col}?")
        suggestions.append(f"What is maximum {col}?")

    suggestions = suggestions[:6]

    cols = st.columns(3)

    for i, suggestion in enumerate(suggestions):

        with cols[i % 3]:

            if st.button(suggestion):
                st.session_state["auto_question"] = suggestion

    # ---------------- STATISTICS ----------------
    if len(numeric_cols) > 0:

        st.markdown("## 📈 Statistical Summary")

        st.dataframe(
            df.describe(),
            use_container_width=True
        )

    # ---------------- HEATMAP ----------------
    if len(numeric_cols) >= 2:

        st.markdown("## 🔥 Correlation Heatmap")

        try:

            corr_matrix = df[numeric_cols].corr()

            corr_matrix = corr_matrix.fillna(0)

            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="Blues"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        except Exception:

            st.warning(
                "⚠️ Could not generate heatmap"
            )

    # ---------------- BUSINESS INSIGHTS ----------------
    st.markdown("## 📌 Business Insights")

    if len(numeric_cols) > 0:

        for col in numeric_cols:

            avg_val = round(df[col].mean(), 2)
            max_val = df[col].max()
            min_val = df[col].min()

            st.success(
                f"{col}: Average = {avg_val} | Highest = {max_val} | Lowest = {min_val}"
            )

    # ---------------- PDF REPORT ----------------
    st.markdown("## 📄 Download Report")

    if st.button("Generate PDF Report"):

        report_text = f"""
Rows: {total_rows}
Columns: {total_columns}
Missing Values: {missing_values}
Duplicate Rows: {duplicate_rows}
"""

        generate_pdf(report_text)

        with open("report.pdf", "rb") as f:

            st.download_button(
                label="⬇ Download PDF",
                data=f,
                file_name="AI_Report.pdf",
                mime="application/pdf"
            )

    # ---------------- CHAT UI ----------------
    st.markdown("## 💬 AI Data Chat")

    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Ask questions about your data...")

    if st.session_state.get("auto_question"):
        question = st.session_state["auto_question"]
        st.session_state["auto_question"] = None

    if question and groq_api_key:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        try:

            llm = ChatGroq(
                groq_api_key=groq_api_key,
                model_name=model_option
            )

            prompt = f"""
You are an expert SQL analyst.

Database: SQLite
Table Name: data_table

Columns:
{', '.join(df.columns)}

User Question:
{question}

Instructions:
1. Generate valid SQLite query
2. Then give answer

STRICT FORMAT:

SQL:
<query>

Answer:
<answer>
"""

            response = llm.invoke(prompt).content

            sql_query = ""
            final_answer = response

            if "SQL:" in response and "Answer:" in response:

                sql_query = response.split("SQL:")[1].split("Answer:")[0].strip()

                final_answer = response.split("Answer:")[1].strip()

            ai_response = (
                f"### 🧠 SQL Query\n\n"
                f"```sql\n{sql_query}\n```\n\n"
                f"### ✅ Answer\n\n"
                f"{final_answer}"
            )

            st.session_state.messages.append({
                "role": "assistant",
                "content": ai_response
            })

            st.session_state.query_history.append({
                "question": question,
                "sql": sql_query
            })

            with st.chat_message("assistant"):

                st.markdown(ai_response)

                try:

                    if sql_query.lower().startswith("select"):

                        result_df = pd.read_sql_query(
                            sql_query,
                            conn
                        )

                        st.dataframe(
                            result_df,
                            use_container_width=True
                        )

                        # SMART CHARTS
                        if not result_df.empty:

                            result_numeric = result_df.select_dtypes(
                                include=['number']
                            ).columns

                            result_object = result_df.select_dtypes(
                                include=['object']
                            ).columns

                            if len(result_object) >= 1 and len(result_numeric) >= 1:

                                fig = px.bar(
                                    result_df,
                                    x=result_object[0],
                                    y=result_numeric[0],
                                    title='Auto Generated Chart'
                                )

                                st.plotly_chart(
                                    fig,
                                    use_container_width=True
                                )

                            elif len(result_numeric) >= 2:

                                fig = px.scatter(
                                    result_df,
                                    x=result_numeric[0],
                                    y=result_numeric[1],
                                    title='Auto Scatter Plot'
                                )

                                st.plotly_chart(
                                    fig,
                                    use_container_width=True
                                )

                except Exception:

                    st.warning(
                        "⚠️ SQL execution failed"
                    )

        except Exception as e:

            st.error(str(e))

    elif question and not groq_api_key:

        st.warning(
            "⚠️ Please enter Groq API Key"
        )

    # ---------------- QUERY HISTORY ----------------
    st.markdown("## 🕘 Query History")

    for item in st.session_state.query_history:

        st.markdown(f"### ❓ {item['question']}")

        st.code(item['sql'], language='sql')

else:

    st.info("👆 Upload a CSV file to start AI analysis")