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

# ---------------- COLORFUL UI CSS ----------------
st.markdown("""
<style>

/* Main Background */
.stApp {
    background: linear-gradient(
        135deg,
        #667eea 0%,
        #764ba2 25%,
        #6B8DD6 50%,
        #8E37D7 75%,
        #4A00E0 100%
    );
    background-attachment: fixed;
    color: white;
}

/* Main Title */
.main-title {
    font-size: 54px;
    font-weight: 800;
    text-align: center;
    color: white;
    margin-top: 10px;
    text-shadow: 2px 2px 15px rgba(0,0,0,0.4);
}

/* Subtitle */
.sub-title {
    text-align: center;
    color: #f1f5f9;
    font-size: 22px;
    margin-bottom: 30px;
}

/* Cards */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.15);
    padding: 20px;
    border-radius: 24px;
    backdrop-filter: blur(14px);
    box-shadow: 0px 8px 25px rgba(0,0,0,0.25);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(
        to right,
        #ff6a00,
        #ee0979
    );
    color: white;
    border-radius: 14px;
    border: none;
    padding: 12px 28px;
    font-size: 16px;
    font-weight: bold;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0px 0px 15px rgba(255,255,255,0.4);
}

/* Input Boxes */
.stTextInput > div > div > input {
    border-radius: 14px;
}

/* Chat Messages */
.stChatMessage {
    background: rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 10px;
}

/* Headers */
h1, h2, h3 {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown(
    '<div class="main-title">🤖 AI SQL Data Analyst Platform</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">AI SQL Queries • Smart Dashboards • Business Insights • Visualizations</div>',
    unsafe_allow_html=True
)

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

    pdf.cell(
        200,
        10,
        txt="AI SQL Data Analyst Report",
        ln=True
    )

    pdf.multi_cell(
        0,
        10,
        summary_text
    )

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

    numeric_cols = df.select_dtypes(
        include=['number']
    ).columns

    # ---------------- TABS ----------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard",
        "💬 AI Chat",
        "📈 Visualizations",
        "📄 Reports"
    ])

    # =========================================================
    # DASHBOARD TAB
    # =========================================================
    with tab1:

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
            st.metric("❌ Missing", missing_values)

        with m4:
            st.metric("🔁 Duplicates", duplicate_rows)

        # ---------------- KPI DASHBOARD ----------------
        st.markdown("## 🚀 AI KPI Dashboard")

        k1, k2, k3 = st.columns(3)

        if len(numeric_cols) > 0:

            with k1:
                st.metric(
                    "📈 Highest Value",
                    round(df[numeric_cols[0]].max(), 2)
                )

            with k2:
                st.metric(
                    "📉 Lowest Value",
                    round(df[numeric_cols[0]].min(), 2)
                )

            with k3:
                st.metric(
                    "📊 Average Value",
                    round(df[numeric_cols[0]].mean(), 2)
                )

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

        # ---------------- DATA CLEANING ----------------
        st.markdown("## 🧹 AI Data Cleaning")

        if st.button("Clean Dataset"):

            before_rows = df.shape[0]

            df = df.drop_duplicates()

            df = df.fillna(0)

            after_rows = df.shape[0]

            st.balloons()

            st.success(
                f"Dataset cleaned successfully. Removed {before_rows - after_rows} duplicate rows."
            )

        # ---------------- SEARCH ----------------
        st.markdown("## 🔍 Search Data")

        search_col = st.selectbox(
            "Select Column",
            df.columns
        )

        search_value = st.text_input(
            "Enter Search Value"
        )

        if search_value:

            filtered_df = df[
                df[search_col].astype(str).str.contains(
                    search_value,
                    case=False,
                    na=False
                )
            ]

            st.dataframe(
                filtered_df,
                use_container_width=True
            )

        # ---------------- INSIGHTS ----------------
        st.markdown("## 📌 AI Business Insights")

        if len(numeric_cols) > 0:

            for col in numeric_cols:

                avg_val = round(df[col].mean(), 2)
                max_val = df[col].max()
                min_val = df[col].min()

                st.success(
                    f"{col}: Average = {avg_val} | Highest = {max_val} | Lowest = {min_val}"
                )

    # =========================================================
    # AI CHAT TAB
    # =========================================================
    with tab2:

        st.markdown("## 💬 AI Data Chat")

        # Suggested Questions
        st.markdown("### 🤖 Suggested Questions")

        suggestions = []

        for col in numeric_cols:
            suggestions.append(f"What is average {col}?")
            suggestions.append(f"What is maximum {col}?")

        suggestions = suggestions[:6]

        cols = st.columns(3)

        for i, suggestion in enumerate(suggestions):

            with cols[i % 3]:

                if st.button(
                    suggestion,
                    key=f"suggestion_{i}"
                ):
                    st.session_state["auto_question"] = suggestion

        # Display Chat
        for msg in st.session_state.messages:

            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        question = st.chat_input(
            "Ask questions about your data..."
        )

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

                    sql_query = response.split(
                        "SQL:"
                    )[1].split(
                        "Answer:"
                    )[0].strip()

                    final_answer = response.split(
                        "Answer:"
                    )[1].strip()

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

    # =========================================================
    # VISUALIZATION TAB
    # =========================================================
    with tab3:

        st.markdown("## 📈 Smart Visualizations")

        if len(numeric_cols) > 0:

            x_axis = st.selectbox(
                "Select X-axis",
                df.columns
            )

            y_axis = st.selectbox(
                "Select Y-axis",
                numeric_cols
            )

            chart_type = st.selectbox(
                "Chart Type",
                [
                    "Line",
                    "Bar",
                    "Scatter",
                    "Histogram",
                    "Pie"
                ]
            )

            if st.button("Generate Visualization"):

                if chart_type == "Line":

                    fig = px.line(
                        df,
                        x=x_axis,
                        y=y_axis
                    )

                elif chart_type == "Bar":

                    fig = px.bar(
                        df,
                        x=x_axis,
                        y=y_axis
                    )

                elif chart_type == "Scatter":

                    fig = px.scatter(
                        df,
                        x=x_axis,
                        y=y_axis
                    )

                elif chart_type == "Pie":

                    fig = px.pie(
                        df,
                        names=x_axis,
                        values=y_axis
                    )

                else:

                    fig = px.histogram(
                        df,
                        x=y_axis
                    )

                st.plotly_chart(
                    fig,
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
                    color_continuous_scale="Turbo"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            except Exception:

                st.warning(
                    "⚠️ Could not generate heatmap"
                )

    # =========================================================
    # REPORT TAB
    # =========================================================
    with tab4:

        st.markdown("## 📄 Download Reports")

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

        # ---------------- DOWNLOAD CSV ----------------
        csv = df.to_csv(index=False).encode('utf-8')

        st.download_button(
            "⬇ Download CSV",
            csv,
            "cleaned_data.csv",
            "text/csv"
        )

else:

    st.info("👆 Upload a CSV file to start AI analysis")