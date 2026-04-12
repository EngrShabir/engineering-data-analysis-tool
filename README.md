# ⚙️ Engineering Data Analysis Dashboard

A professional data analysis dashboard built for engineers. Upload any structured dataset (CSV or Excel) and instantly get statistics, interactive charts, automated insights, and a downloadable PDF report — all in a clean dark industrial UI.

---

## 🚀 Features

### 📂 File Support
- Upload **CSV** or **Excel** (.xlsx, .xls) files
- Works with any structured dataset — no fixed column names required

### 🧹 Data Cleaning
- Drop rows with null values
- Fill null values using **Mean** or **Median**
- Remove duplicate rows
- Cleaning summary shown in sidebar after each operation

### 📊 Dataset Preview
- Adjustable row slider — preview 5 to full dataset length
- Live update as you drag

### 📈 Statistical Analysis
- Select any numeric columns to analyse
- Computes: **Mean, Median, Max, Min, Standard Deviation, Skewness**
- Color-gradient table for quick visual scanning

### 📉 Interactive Visualizations (5 chart types)
| Chart | Description |
|-------|-------------|
| 📈 Line Chart | Track any columns over index or sample_id |
| 📊 Histogram | Distribution of values with adjustable bins |
| 📦 Box Plot | Spread, median, and outliers at a glance |
| 🔥 Correlation Heatmap | Relationships between all numeric columns |
| 🔵 Scatter Plot | X vs Y with OLS trendline and optional color grouping |

- All charts are **interactive** (zoom, pan, hover)
- All charts are **downloadable** with one click (Plotly toolbar)

### 🤖 Automated Insights Engine
Automatically detects and flags:
- ⚠️ High or moderate variation (Coefficient of Variation)
- 🔴 Probable outliers (IQR method)
- 📈 Increasing or 📉 decreasing trends (linear regression)
- 🔗 Strong correlations between column pairs (r ≥ 0.85)

### 📄 PDF Report Download
- Auto-generated professional PDF report
- Includes: dataset info, statistical summary table, all insights, data preview
- Timestamped filename for easy archiving

---

## 🛠️ Tech Stack

| Library | Purpose |
|---------|---------|
| Streamlit | Web dashboard framework |
| Pandas | Data loading and processing |
| NumPy | Numerical computations |
| Plotly Express | Interactive charts |
| ReportLab | PDF report generation |
| Statsmodels | OLS trendline for scatter plot |

---

## ▶️ How to Run Locally

```bash
pip install streamlit pandas numpy plotly reportlab statsmodels openpyxl
streamlit run app.py
```
## 📁 Sample Dataset

A sample file `data100.csv` is included in this repo to test the dashboard immediately.

| Column | Description |
|--------|-------------|
| sample_id | Sample number (1–100) |
| temperature | Temperature readings (°C) |
| pressure | Pressure values (bar) |
| stress | Stress measurements (MPa) |
| strain | Strain values (dimensionless) |

The file intentionally contains a few **null values** to let you test the data cleaning features (drop nulls / fill with mean or median).


🔗 **Live Demo:** https://engineering-data-analysis-tool-q7pp3mas5z9msrvjgndlub.streamlit.app/
---

## 👨‍💻 Author

**Shabir Ahmad**
- GitHub: [@EngrShabir](https://github.com/EngrShabir)
- LinkedIn: [Shabir Ahmad](https://www.linkedin.com/in/shabir-ahmad-0886b0342/)
