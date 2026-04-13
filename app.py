import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Finance Analyzer",
    page_icon="💹",
    layout="wide"
)

# ── Theme CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Grotesk:wght@400;500;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background-color: #0a0a0a;
    color: #f0f0f0;
  }
  .main { background-color: #0a0a0a; }
  .block-container { padding: 2rem 2.5rem; }

  h1 {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3rem;
    letter-spacing: 3px;
    color: #E24B4A;
    margin-bottom: 0;
  }
  h2, h3 {
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 2px;
    color: #f0f0f0;
  }

  .metric-card {
    background: #141414;
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 12px;
  }
  .metric-card.accent { border-color: #A32D2D; background: #1a0a0a; }
  .metric-label {
    font-size: 11px;
    color: #888;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 4px;
  }
  .metric-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2rem;
    letter-spacing: 1px;
  }
  .pos { color: #4ade80; }
  .neg { color: #E24B4A; }
  .red { color: #E24B4A; }

  .section-label {
    font-size: 10px;
    color: #666;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    border-bottom: 1px solid #1c1c1c;
    padding-bottom: 6px;
    margin-bottom: 14px;
    margin-top: 8px;
  }

  .stSelectbox > div, .stMultiSelect > div { background: #141414; }
  div[data-testid="stSidebar"] { background: #0d0d0d; border-right: 1px solid #1c1c1c; }

  .outlier-row {
    background: #141414;
    border-left: 3px solid #E24B4A;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .outlier-desc { font-size: 13px; font-weight: 500; }
  .outlier-meta { font-size: 11px; color: #888; margin-top: 2px; }
  .outlier-amt { font-size: 15px; font-weight: 600; color: #E24B4A; }
</style>
""", unsafe_allow_html=True)

# ── Matplotlib dark theme ─────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#141414",
    "axes.facecolor":   "#141414",
    "axes.edgecolor":   "#2a2a2a",
    "axes.labelcolor":  "#888888",
    "xtick.color":      "#666666",
    "ytick.color":      "#666666",
    "text.color":       "#f0f0f0",
    "grid.color":       "#1c1c1c",
    "grid.linestyle":   "--",
    "font.family":      "sans-serif",
    "font.size":        10,
})

RED    = "#E24B4A"
GREEN  = "#4ade80"
MUTED  = "#888888"
BORDER = "#2a2a2a"

# ── Load data ─────────────────────────────────────────────────
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df["date"]  = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M")
    return df

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2>Finance Analyzer</h2>", unsafe_allow_html=True)
    st.markdown("---")

    uploaded = st.file_uploader("Upload transactions.csv", type="csv")
    if uploaded:
        df = load_data(uploaded)
        months = sorted(df["month"].unique().astype(str))
        selected_months = st.multiselect(
            "Filter by month",
            options=months,
            default=months,
            placeholder="All months"
        )
        categories = sorted(df["category"].unique())
        selected_cats = st.multiselect(
            "Filter by category",
            options=categories,
            default=categories,
            placeholder="All categories"
        )
    st.markdown("---")
    st.markdown("<p style='font-size:11px;color:#444;'>Built with Pandas · Matplotlib · Streamlit</p>", unsafe_allow_html=True)

# ── Main ──────────────────────────────────────────────────────
st.markdown("<h1>Finance Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#666;font-size:13px;letter-spacing:1px;margin-top:-8px;margin-bottom:24px'>PERSONAL FINANCIAL REPORT</p>", unsafe_allow_html=True)

if not uploaded:
    st.markdown("""
    <div style='background:#141414;border:1px dashed #2a2a2a;border-radius:12px;padding:48px;text-align:center;'>
        <p style='font-size:32px;font-family:Bebas Neue,sans-serif;letter-spacing:2px;color:#E24B4A;margin-bottom:8px'>Upload your CSV</p>
        <p style='color:#666;font-size:13px'>Use the sidebar to upload your transactions.csv file</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Filter data ───────────────────────────────────────────────
mask = (df["month"].astype(str).isin(selected_months)) & (df["category"].isin(selected_cats))
filtered = df[mask]

income_df  = filtered[filtered["type"] == "income"]
expense_df = filtered[filtered["type"] == "expense"]

total_income  = income_df["amount"].sum()
total_expense = expense_df["amount"].sum()
balance       = total_income - total_expense
savings_rate  = (balance / total_income * 100) if total_income > 0 else 0

# ── Metric cards ──────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

def metric_card(col, label, value, color_class, accent=False):
    col.markdown(f"""
    <div class="metric-card {'accent' if accent else ''}">
        <div class="metric-label">{label}</div>
        <div class="metric-value {color_class}">{value}</div>
    </div>
    """, unsafe_allow_html=True)

metric_card(c1, "Total Income",   f"{total_income:,.0f}",  "pos")
metric_card(c2, "Total Expenses", f"{total_expense:,.0f}", "red")
metric_card(c3, "Net Balance",    f"{balance:+,.0f}",      "pos" if balance >= 0 else "neg", accent=True)
metric_card(c4, "Savings Rate",   f"{savings_rate:.1f}%",  "pos" if savings_rate >= 20 else "red")

st.markdown("---")

# ── Row 1: Monthly bar + Category bar ─────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("<div class='section-label'>Monthly income vs expenses</div>", unsafe_allow_html=True)
    monthly = filtered.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0)
    if "income" not in monthly.columns:  monthly["income"] = 0
    if "expense" not in monthly.columns: monthly["expense"] = 0
    monthly["balance"] = monthly["income"] - monthly["expense"]

    fig, ax = plt.subplots(figsize=(6, 3.2))
    x = np.arange(len(monthly))
    w = 0.38
    ax.bar(x - w/2, monthly["income"],  w, color=GREEN, label="Income",  zorder=3)
    ax.bar(x + w/2, monthly["expense"], w, color=RED,   label="Expenses", zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels([str(m)[5:] for m in monthly.index], rotation=45, ha="right", fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v/1000:.0f}k"))
    ax.grid(axis="y", zorder=0)
    ax.legend(framealpha=0, labelcolor="#aaa", fontsize=9)
    ax.spines[["top","right","left","bottom"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col_right:
    st.markdown("<div class='section-label'>Spending by category</div>", unsafe_allow_html=True)
    by_cat = expense_df.groupby("category")["amount"].sum().sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(6, 3.2))
    colors = [RED if i == len(by_cat)-1 else "#3a3a3a" for i in range(len(by_cat))]
    bars = ax.barh(by_cat.index, by_cat.values, color=colors, zorder=3)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v/1000:.0f}k"))
    ax.grid(axis="x", zorder=0)
    ax.spines[["top","right","left","bottom"]].set_visible(False)
    for bar, val in zip(bars, by_cat.values):
        ax.text(val + 50, bar.get_y() + bar.get_height()/2,
                f"{val:,.0f}", va="center", fontsize=8, color="#aaa")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ── Row 2: Balance trend + Pie ─────────────────────────────────
col_l2, col_r2 = st.columns([2, 1])

with col_l2:
    st.markdown("<div class='section-label'>Net balance trend</div>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(7, 2.8))
    bal = monthly["balance"]
    colors_pts = [GREEN if v >= 0 else RED for v in bal]
    ax.plot(range(len(bal)), bal.values, color=RED, linewidth=2, zorder=3)
    ax.scatter(range(len(bal)), bal.values, color=colors_pts, s=40, zorder=4)
    ax.axhline(0, color=BORDER, linewidth=1, linestyle="--")
    ax.fill_between(range(len(bal)), bal.values, 0,
                    where=[v >= 0 for v in bal], color=GREEN, alpha=0.08)
    ax.fill_between(range(len(bal)), bal.values, 0,
                    where=[v < 0 for v in bal], color=RED, alpha=0.08)
    ax.set_xticks(range(len(bal)))
    ax.set_xticklabels([str(m)[5:] for m in bal.index], fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v/1000:.0f}k"))
    ax.grid(axis="y", zorder=0)
    ax.spines[["top","right","left","bottom"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col_r2:
    st.markdown("<div class='section-label'>Income vs expenses</div>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(3, 2.8))
    ax.pie(
        [total_income, total_expense],
        labels=["Income", "Expenses"],
        colors=[GREEN, RED],
        autopct="%1.1f%%",
        startangle=90,
        textprops={"color": "#aaa", "fontsize": 10},
        wedgeprops={"linewidth": 0}
    )
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ── Outliers ──────────────────────────────────────────────────
st.markdown("---")
st.markdown("<div class='section-label'>Unusual transactions (outliers)</div>", unsafe_allow_html=True)

mean_exp = expense_df["amount"].mean()
std_exp  = expense_df["amount"].std()
outliers = expense_df[expense_df["amount"] > mean_exp + 1.8 * std_exp].sort_values("amount", ascending=False).head(6)

if outliers.empty:
    st.markdown("<p style='color:#666;font-size:13px'>No outliers detected in selected range.</p>", unsafe_allow_html=True)
else:
    cols = st.columns(3)
    for i, (_, row) in enumerate(outliers.iterrows()):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="outlier-row">
                <div>
                    <div class="outlier-desc">{row['description']}</div>
                    <div class="outlier-meta">{row['category']} · {str(row['date'])[:10]}</div>
                </div>
                <div class="outlier-amt">{row['amount']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

# ── Top 5 biggest expenses ─────────────────────────────────────
st.markdown("---")
st.markdown("<div class='section-label'>Top 5 biggest expenses</div>", unsafe_allow_html=True)
top5 = expense_df.nlargest(5, "amount")[["date","category","description","amount"]]
top5["date"] = top5["date"].dt.strftime("%Y-%m-%d")
top5["amount"] = top5["amount"].map("{:,.2f}".format)
top5.columns = ["Date", "Category", "Description", "Amount"]
st.dataframe(
    top5,
    use_container_width=True,
    hide_index=True,
)

# ── Rolling average ────────────────────────────────────────────
st.markdown("---")
st.markdown("<div class='section-label'>3-month rolling average spend</div>", unsafe_allow_html=True)
monthly_exp = filtered[filtered["type"]=="expense"].groupby("month")["amount"].sum()
rolling     = monthly_exp.rolling(3).mean().dropna()

if not rolling.empty:
    fig, ax = plt.subplots(figsize=(10, 2.5))
    ax.plot(range(len(monthly_exp)), monthly_exp.values, color=BORDER, linewidth=1.5, label="Monthly", zorder=2)
    offset = len(monthly_exp) - len(rolling)
    ax.plot(range(offset, offset+len(rolling)), rolling.values, color=RED, linewidth=2.5, label="3-mo avg", zorder=3)
    ax.set_xticks(range(len(monthly_exp)))
    ax.set_xticklabels([str(m)[5:] for m in monthly_exp.index], fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v/1000:.0f}k"))
    ax.grid(axis="y", zorder=0)
    ax.legend(framealpha=0, labelcolor="#aaa", fontsize=9)
    ax.spines[["top","right","left","bottom"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
else:
    st.markdown("<p style='color:#666;font-size:13px'>Need at least 3 months of data for rolling average.</p>", unsafe_allow_html=True)
