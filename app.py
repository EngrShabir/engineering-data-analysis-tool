"""
Engineering Data Analysis Dashboard
Author  : Shabir Ahmad (EngrShabir)
GitHub  : https://github.com/EngrShabir
Purpose : Professional data analysis tool for engineering datasets
Run     : streamlit run app.py
"""

import io
import warnings
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Engineering Data Dashboard",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS  (industrial / dark-steel theme)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
}

/* dark background */
.stApp { background-color: #0d1117; color: #c9d1d9; }

/* sidebar */
[data-testid="stSidebar"] {
    background: #161b22;
    border-right: 1px solid #21262d;
}
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }

/* metric cards */
[data-testid="metric-container"] {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 12px 16px;
}
[data-testid="metric-container"] label { color: #8b949e !important; font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #58a6ff !important; font-family: 'Share Tech Mono', monospace; font-size: 1.6rem; }

/* section headers */
.section-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #58a6ff;
    border-left: 3px solid #58a6ff;
    padding-left: 10px;
    margin: 24px 0 12px 0;
}

/* insight cards */
.insight-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-left: 4px solid;
    border-radius: 6px;
    padding: 12px 16px;
    margin-bottom: 10px;
    font-size: 0.9rem;
    line-height: 1.5;
}
.insight-warning  { border-left-color: #d29922; }
.insight-danger   { border-left-color: #f85149; }
.insight-success  { border-left-color: #3fb950; }
.insight-info     { border-left-color: #58a6ff; }

/* dataframe */
[data-testid="stDataFrame"] { border: 1px solid #21262d; border-radius: 6px; }

/* buttons */
.stButton>button, .stDownloadButton>button {
    background: #21262d;
    border: 1px solid #30363d;
    color: #c9d1d9;
    border-radius: 6px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.05em;
    transition: all .2s;
}
.stButton>button:hover, .stDownloadButton>button:hover {
    border-color: #58a6ff;
    color: #58a6ff;
    background: #0d1117;
}

/* hero banner */
.hero {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 60%, #0d1117 100%);
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 32px 40px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #58a6ff, #3fb950, #d29922);
}
.hero h1 {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.8rem;
    color: #e6edf3;
    margin: 0 0 4px 0;
}
.hero p { color: #8b949e; font-size: 0.95rem; margin: 0; }

/* select / multiselect */
[data-testid="stSelectbox"] > div, [data-testid="stMultiSelect"] > div {
    background: #161b22 !important;
    border-color: #30363d !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPER  ─  load file
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_file(uploaded) -> pd.DataFrame:
    name = uploaded.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded)
    elif name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded)
    else:
        raise ValueError("Unsupported file type.")


# ─────────────────────────────────────────────
# HELPER  ─  statistics table
# ─────────────────────────────────────────────
def compute_stats(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    rows = []
    for col in cols:
        s = df[col]
        rows.append({
            "Column": col,
            "Mean":   round(s.mean(), 4),
            "Median": round(s.median(), 4),
            "Max":    round(s.max(), 4),
            "Min":    round(s.min(), 4),
            "Std":    round(s.std(), 4),
            "Skew":   round(s.skew(), 4),
        })
    return pd.DataFrame(rows).set_index("Column")


# ─────────────────────────────────────────────
# HELPER  ─  auto insights
# ─────────────────────────────────────────────
def generate_insights(df: pd.DataFrame, num_cols: list) -> list:
    """Return a list of (level, message) tuples."""
    insights = []

    for col in num_cols:
        s = df[col]
        mean, std = s.mean(), s.std()
        cv = (std / mean * 100) if mean != 0 else 0

        # High variation
        if cv > 40:
            insights.append(("warning",
                             f"⚠️ <b>{col}</b> has very high variation (CV = {cv:.1f}%). "
                             "Results may be unstable or contain mixed populations."))
        elif cv > 20:
            insights.append(("info",
                             f"ℹ️ <b>{col}</b> shows moderate variation (CV = {cv:.1f}%)."))

        # Outliers  (IQR method)
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        outliers = ((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).sum()
        if outliers > 0:
            insights.append(("danger",
                             f"🔴 <b>{col}</b> has <b>{outliers}</b> probable outlier(s) "
                             f"(IQR method: [{q1 - 1.5*iqr:.3f}, {q3 + 1.5*iqr:.3f}])."))

        # Trend detection (simple linear fit)
        x = np.arange(len(s))
        if len(x) >= 3:
            slope = np.polyfit(x, s.values, 1)[0]
            rel_slope = slope / (mean if mean != 0 else 1) * 100
            if rel_slope > 5:
                insights.append(("success",
                                 f"📈 <b>{col}</b> shows an increasing trend "
                                 f"(+{rel_slope:.1f}% per step on average)."))
            elif rel_slope < -5:
                insights.append(("warning",
                                 f"📉 <b>{col}</b> shows a decreasing trend "
                                 f"({rel_slope:.1f}% per step on average)."))

    # Correlation
    if len(num_cols) >= 2:
        corr = df[num_cols].corr()
        for i in range(len(num_cols)):
            for j in range(i + 1, len(num_cols)):
                val = corr.iloc[i, j]
                if abs(val) >= 0.85:
                    direction = "positive" if val > 0 else "negative"
                    insights.append(("info",
                                     f"🔗 Strong {direction} correlation between "
                                     f"<b>{num_cols[i]}</b> and <b>{num_cols[j]}</b> "
                                     f"(r = {val:.3f})."))

    if not insights:
        insights.append(
            ("success", "✅ No major anomalies detected. Dataset looks clean."))

    return insights


# ─────────────────────────────────────────────
# HELPER  ─  PDF report
# ─────────────────────────────────────────────
def build_pdf(filename: str, df: pd.DataFrame, stats: pd.DataFrame,
              insights: list, num_cols: list) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("title",
                                 parent=styles["Title"],
                                 fontSize=18,
                                 textColor=colors.HexColor("#1a73e8"),
                                 spaceAfter=4)

    sub_style = ParagraphStyle("sub",
                               parent=styles["Normal"],
                               fontSize=9,
                               textColor=colors.grey,
                               spaceAfter=12)

    h2_style = ParagraphStyle("h2",
                              parent=styles["Heading2"],
                              fontSize=12,
                              textColor=colors.HexColor("#1a73e8"),
                              spaceBefore=16,
                              spaceAfter=6)

    body_style = ParagraphStyle("body",
                                parent=styles["Normal"],
                                fontSize=9,
                                leading=14)

    elements = []

    # Title
    elements.append(Paragraph("Engineering Data Analysis Report", title_style))
    elements.append(Paragraph(
        f"Dataset: <b>{filename}</b> &nbsp;|&nbsp; "
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} &nbsp;|&nbsp; "
        f"Rows: {len(df)} &nbsp;|&nbsp; Columns: {len(df.columns)}",
        sub_style))
    elements.append(HRFlowable(width="100%", thickness=1,
                               color=colors.HexColor("#1a73e8"), spaceAfter=12))

    # Stats table
    elements.append(Paragraph("Statistical Summary", h2_style))
    tdata = [["Column", "Mean", "Median", "Max", "Min", "Std", "Skew"]]
    for col in stats.index:
        row = stats.loc[col]
        tdata.append([col] + [str(row[c])
                     for c in ["Mean", "Median", "Max", "Min", "Std", "Skew"]])

    t = Table(tdata, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a73e8")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTSIZE",   (0, 0), (-1, -1), 8),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#f4f8ff")]),
        ("ALIGN",      (1, 0), (-1, -1), "CENTER"),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t)

    # Insights
    elements.append(Paragraph("Automated Insights", h2_style))
    level_map = {"warning": "🟡", "danger": "🔴", "success": "🟢", "info": "🔵"}
    for level, msg in insights:
        clean = msg.replace("<b>", "").replace("</b>", "")
        prefix = level_map.get(level, "•")
        elements.append(Paragraph(f"{prefix} {clean}", body_style))
        elements.append(Spacer(1, 4))

    # Data sample
    elements.append(Paragraph("Dataset Preview (first 20 rows)", h2_style))
    preview = df.head(20)
    hdr = list(preview.columns)
    pdata = [hdr] + preview.values.tolist()
    pt = Table(pdata, repeatRows=1)
    pt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#444444")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTSIZE",   (0, 0), (-1, -1), 7),
        ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#f7f7f7")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(pt)

    doc.build(elements)
    return buf.getvalue()


# ─────────────────────────────────────────────
# PLOTLY THEME
# ─────────────────────────────────────────────
PLOTLY_TEMPLATE = "plotly_dark"
ACCENT = "#58a6ff"


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-header">Data Source</div>',
                unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Upload CSV or Excel", type=["csv", "xlsx", "xls"])

    st.markdown('<div class="section-header">Data Cleaning</div>',
                unsafe_allow_html=True)
    drop_null = st.checkbox("Drop rows with null values")
    fill_null = st.checkbox("Fill null values")
    fill_method = None
    if fill_null:
        fill_method = st.selectbox("Fill method", ["Mean", "Median"])
    drop_dups = st.checkbox("Remove duplicate rows")

    st.markdown('<div class="section-header">About</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<span style="font-size:0.8rem;color:#8b949e;">'
        '⚙️ Built by <a href="https://github.com/EngrShabir" '
        'style="color:#58a6ff;">Shabir Ahmad</a></span>',
        unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>⚙ Engineering Data Dashboard</h1>
  <p>Upload any structured dataset — get instant statistics, charts, and automated insights.</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN LOGIC
# ─────────────────────────────────────────────
if uploaded is None:
    st.info("👈  Upload a CSV or Excel file from the sidebar to get started.")
    st.stop()

# Load
with st.spinner("Loading dataset…"):
    try:
        df_raw = load_file(uploaded)
    except Exception as e:
        st.error(f"Could not read file: {e}")
        st.stop()

# Cleaning
df = df_raw.copy()
cleaning_log = []

nulls_before = df.isnull().sum().sum()
dups_before = df.duplicated().sum()

if drop_null:
    before = len(df)
    df = df.dropna()
    removed = before - len(df)
    cleaning_log.append(f"🗑️ Dropped **{removed}** rows with null values.")

if fill_null and fill_method:
    num_cols_all = df.select_dtypes(include="number").columns
    for col in num_cols_all:
        val = df[col].mean() if fill_method == "Mean" else df[col].median()
        df[col].fillna(val, inplace=True)
    cleaning_log.append(
        f"✏️ Filled **{int(nulls_before)}** null values using **{fill_method}**.")

if drop_dups:
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    cleaning_log.append(f"♻️ Removed **{removed}** duplicate rows.")

if cleaning_log:
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Cleaning Summary**")
    for log in cleaning_log:
        st.sidebar.markdown(log)
else:
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<span style='color:#8b949e;font-size:0.8rem;'>No cleaning applied.</span>", unsafe_allow_html=True)

num_cols = df.select_dtypes(include="number").columns.tolist()

# ── TOP METRICS ──────────────────────────────
m1, m2, m3, m4 = st.columns(4)
m1.metric("Rows",     f"{len(df):,}")
m2.metric("Columns",  len(df.columns))
m3.metric("Numeric",  len(num_cols))
m4.metric("Nulls",    int(df.isnull().sum().sum()))

# ── PREVIEW ──────────────────────────────────
st.markdown('<div class="section-header">Dataset Preview</div>',
            unsafe_allow_html=True)
preview_rows = st.slider("Rows to preview", min_value=5, max_value=len(df), value=min(50, len(df)), step=5)
st.dataframe(df.head(preview_rows), use_container_width=True)

if not num_cols:
    st.warning(
        "No numeric columns found. Please upload a dataset with numeric data.")
    st.stop()

# ── STATISTICS ───────────────────────────────
st.markdown('<div class="section-header">Statistical Analysis</div>',
            unsafe_allow_html=True)
sel_cols = st.multiselect("Select columns to analyse",
                          num_cols, default=num_cols[:min(4, len(num_cols))])

if sel_cols:
    valid_cols = [c for c in sel_cols if c in num_cols]
    if valid_cols:
        stats_df = compute_stats(df, valid_cols)
        st.dataframe(stats_df.style.format("{:.4f}").background_gradient(cmap="Blues", axis=None),
                     use_container_width=True)
    else:
        st.warning("Selected columns must be numeric.")

# ── VISUALIZATIONS ───────────────────────────
st.markdown('<div class="section-header">Visualizations</div>',
            unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Line Chart", "📊 Histogram", "📦 Box Plot", "🔥 Correlation Heatmap", "🔵 Scatter Plot"])

# Determine x axis (sample_id preferred)
x_col = "sample_id" if "sample_id" in df.columns else (
    df.columns[0] if len(df.columns) > 0 else "index")

with tab1:
    line_cols = st.multiselect(
        "Columns", num_cols, default=num_cols[:1], key="line_col")
    if line_cols:
        fig_line = px.line(df, x=x_col, y=line_cols, markers=True,
                           template=PLOTLY_TEMPLATE)
        fig_line.update_traces(line_width=2, marker_size=6)
        fig_line.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
                               font_color="#c9d1d9", title=f"Selected columns over {x_col}")
        st.plotly_chart(fig_line, use_container_width=True)

with tab2:
    hist_cols = st.multiselect(
        "Columns", num_cols, default=num_cols[:1], key="hist_col")
    bins = st.slider("Bins", 5, 80, 20)
    if hist_cols:
        for hcol in hist_cols:
            fig_hist = px.histogram(df, x=hcol, nbins=bins,
                                    template=PLOTLY_TEMPLATE,
                                    color_discrete_sequence=["#3fb950"],
                                    title=f"Distribution of {hcol}")
            fig_hist.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
                                   font_color="#c9d1d9", bargap=0.05)
            st.plotly_chart(fig_hist, use_container_width=True)

with tab3:
    box_cols = st.multiselect(
        "Columns", num_cols, default=num_cols[:min(3, len(num_cols))], key="box_cols")
    if box_cols:
        fig_box = px.box(df, y=box_cols, template=PLOTLY_TEMPLATE,
                         color_discrete_sequence=px.colors.qualitative.Set2)
        fig_box.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
                              font_color="#c9d1d9")
        st.plotly_chart(fig_box, use_container_width=True)

with tab4:
    if len(num_cols) >= 2:
        corr = df[num_cols].corr()
        fig_heat = go.Figure(go.Heatmap(
            z=corr.values, x=corr.columns, y=corr.index,
            colorscale="RdBu_r", zmid=0,
            text=corr.round(2).values, texttemplate="%{text}",
            hovertemplate="%{x} vs %{y}: %{z:.3f}<extra></extra>"
        ))
        fig_heat.update_layout(
            template=PLOTLY_TEMPLATE, paper_bgcolor="#0d1117",
            plot_bgcolor="#161b22", font_color="#c9d1d9",
            title="Correlation Matrix")
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Need at least 2 numeric columns for correlation heatmap.")

with tab5:
    if len(num_cols) >= 2:
        sc_col1, sc_col2 = st.columns(2)
        with sc_col1:
            x_scatter = st.selectbox("X axis", num_cols, index=0, key="sc_x")
        with sc_col2:
            y_scatter = st.selectbox("Y axis", num_cols, index=1, key="sc_y")
        color_col = None
        cat_cols = df.select_dtypes(exclude="number").columns.tolist()
        if cat_cols:
            color_col = st.selectbox("Color by (optional)", ["None"] + cat_cols, key="sc_color")
            color_col = None if color_col == "None" else color_col
        fig_scatter = px.scatter(
            df, x=x_scatter, y=y_scatter,
            color=color_col,
            trendline="ols",
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=px.colors.qualitative.Set2,
            title=f"{y_scatter} vs {x_scatter}"
        )
        fig_scatter.update_traces(marker=dict(size=8, opacity=0.8))
        fig_scatter.update_layout(
            paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
            font_color="#c9d1d9"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Need at least 2 numeric columns for scatter plot.")

# ── INSIGHTS ─────────────────────────────────
st.markdown('<div class="section-header">Automated Insights</div>',
            unsafe_allow_html=True)

insights = generate_insights(df, num_cols)
for level, msg in insights:
    st.markdown(
        f'<div class="insight-card insight-{level}">{msg}</div>',
        unsafe_allow_html=True)

# ── PDF REPORT ───────────────────────────────
st.markdown('<div class="section-header">Download Report</div>',
            unsafe_allow_html=True)

if sel_cols:
    stats_for_pdf = compute_stats(df, sel_cols)
else:
    stats_for_pdf = compute_stats(df, num_cols)

with st.spinner("Building PDF…"):
    pdf_bytes = build_pdf(uploaded.name, df, stats_for_pdf, insights, num_cols)

st.download_button(
    label="⬇ Download PDF Report",
    data=pdf_bytes,
    file_name=f"engineering_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
    mime="application/pdf",
)
