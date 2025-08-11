import os
import math
from typing import List

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

try:
    from PIL import Image, ImageOps
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

st.set_page_config(
    page_title="Bank Customer Segmentation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------
# Theme & Palettes
# ----------------------------
PRIMARY = "#4b6cb7"
PRIMARY_2 = "#182848"

# General cluster palette for bars/heatmaps/treemap (kept distinct)
CLUSTER_PALETTE = {
    0: "#9467bd",  # purple
    1: "#f4a261",  # orange
    2: "#2a9d8f",  # teal
    3: "#e63946",  # red
    4: "#6a4c93",
    5: "#8a5a44",
}

# For Segment Positioning (bubble chart) — avoid blues entirely for clarity
BUBBLE_PALETTE = [
    "#e63946",  # red
    "#f77f00",  # orange
    "#2a9d8f",  # teal
    "#6a4c93",  # violet
    "#ffbe0b",  # amber
    "#264653",  # dark teal
]

# ----------------------------
# Data Loading
# ----------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "top_kpis.csv")

@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        st.error("Data file not found. Place 'top_kpis.csv' next to app.py.")
        st.stop()
    return pd.read_csv(path)

df = load_csv(CSV_PATH)

# ----------------------------
# Header
# ----------------------------
    st.markdown(
        "<div style='width:100%; display:flex; justify-content:center; margin-top:6px; margin-bottom:10px;'>"
        "<h1 style='margin:0; white-space:nowrap;'>🇮🇳 Bank Customer Segmentation Dashboard</h1>"
        "</div>",
        unsafe_allow_html=True,
    )


# ----------------------------
# Banner (auto, no uploader)
# ----------------------------
# We will look for a local image to render as a banner. Recommended size ~1400x350.
BANNER_CANDIDATES = [
    "India_map.png", "india_map.png", "india.png", "banner.png", "map.png"
]
_banner_path = next((p for p in BANNER_CANDIDATES if os.path.exists(p)), None)
if _banner_path:
    if PIL_AVAILABLE:
        try:
            img = Image.open(_banner_path).convert("RGB")
            # Fit to 1400x350 (crop if needed) for a sleek banner strip
            target_size = (1400, 350)
            img_fit = ImageOps.fit(img, target_size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            st.image(img_fit, use_container_width=True)
        except Exception:
            st.image(_banner_path, use_container_width=True)
    else:
        st.image(_banner_path, use_container_width=True)

# ----------------------------
# Load Data
# ----------------------------

required_cols = [
    "CustLocation", "Cluster", "CustomerCount",
    "AvgAge", "AvgRecency", "AvgFrequency", "AvgAvgMonetary", "AvgTotalMonetary"
]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

num_cols = [c for c in df.columns if c not in ["CustLocation", "Cluster"]]
for c in num_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

all_cities: List[str] = sorted(df["CustLocation"].dropna().unique().tolist())
all_clusters: List[int] = sorted(df["Cluster"].dropna().unique().tolist())

# ----------------------------
# Sidebar Filters & Controls
# ----------------------------
st.sidebar.markdown("### 🔎 Filters")
city_sel = st.sidebar.multiselect("City (multi)", options=all_cities, default=all_cities)
cluster_sel = st.sidebar.multiselect("Segment (Cluster)", options=all_clusters, default=all_clusters)

st.sidebar.markdown("---")
topn_on = st.sidebar.checkbox("Limit to Top‑N cities by customer count", value=False)
if topn_on:
    topn = st.sidebar.slider("Top‑N", min_value=3, max_value=max(3, len(all_cities)), value=10)
else:
    topn = None

st.sidebar.markdown("### 📄 Display: City Pagination")
page_size = st.sidebar.slider("Cities per page", 5, 15, 10)
show_all = st.sidebar.checkbox("Show all cities (override pagination)", value=False)

# Base filtered frame
fdf_base = df[df["CustLocation"].isin(city_sel) & df["Cluster"].isin(cluster_sel)].copy()
if topn:
    city_totals_all = (
        fdf_base.groupby("CustLocation")["CustomerCount"].sum().sort_values(ascending=False)
    )
    keep_cities = city_totals_all.head(topn).index.tolist()
    fdf_base = fdf_base[fdf_base["CustLocation"].isin(keep_cities)]

if show_all:
    fdf = fdf_base.copy()
    current_cities = sorted(fdf["CustLocation"].unique().tolist())
else:
    candidate_cities = sorted(fdf_base["CustLocation"].unique().tolist())
    total_pages = max(1, math.ceil(len(candidate_cities) / page_size))
    page = st.sidebar.number_input("City page", min_value=1, max_value=total_pages, value=1, step=1)
    start = (page - 1) * page_size
    end = start + page_size
    current_cities = candidate_cities[start:end]
    fdf = fdf_base[fdf_base["CustLocation"].isin(current_cities)].copy()

# ----------------------------
# KPI Row
# ----------------------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Customers", f"{int(df['CustomerCount'].sum()):,}")
with col2:
    st.metric("Cities", df["CustLocation"].nunique())
with col3:
    st.metric("Segments", df["Cluster"].nunique())
with col4:
    weighted_spend = (df["AvgTotalMonetary"] * df["CustomerCount"]).sum() / df["CustomerCount"].sum()
    st.metric("Avg Spend per Customer", f"{weighted_spend:,.2f}")

st.markdown("---")

# ----------------------------
# Tabs (Executive Summary first)
# ----------------------------
summary_tab, overview_tab, city_tab, segment_tab, details_tab = st.tabs([
    "Executive Summary",
    "Overview",
    "City Deep‑Dive",
    "Segment Explorer",
    "Data & Notes",
])

# ----------------------------
# Executive Summary (polished; reads file if present)
# ----------------------------
with summary_tab:
    st.subheader("Key Takeaways")
    # Try to read user's interpretations if provided
    interp_path = "cluster_interpretations.txt"
    if os.path.exists(interp_path):
        with open(interp_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        st.markdown(text)
    else:
        # Fallback curated summary
        st.markdown(
            """
            - **Cluster 2 = High‑Value Spenders:** Highest average total spend across major cities; ideal for premium offers, upgrades, and retention.
            - **Cluster 3 = Largest Base:** Biggest share of customers in most metros → prioritize broad re‑engagement and loyalty uplift.
            - **Consistency Across Cities:** Cluster spending patterns are stable across locations, enabling national, cluster‑led strategies.
            - **Tier‑2 Opportunity:** Cities with balanced mixes (e.g., NOIDA, FARIDABAD, KOLKATA, PUNE) are strong pilots for localized promotions.

            **Strategic Actions**
            1) Focus **Cluster 2** on exclusive financial products and concierge‑style services.  
            2) Launch reactivation and cross‑sell campaigns for **Cluster 3** to move them up the value ladder.  
            3) Maintain a **cluster‑first playbook** with city overlays rather than city‑only targeting.  
            4) Test **regional playbooks** in second‑tier cities to capture emerging growth.
            """
        )

# ----------------------------
# Overview Tab
# ----------------------------
with overview_tab:
    lcol, rcol = st.columns([1.2, 1])

    with lcol:
        pivot = (
            fdf.pivot_table(index="CustLocation", columns="Cluster", values="CustomerCount", aggfunc="sum", fill_value=0)
            .reset_index()
        )
        pivot_long = pivot.melt(id_vars="CustLocation", var_name="Cluster", value_name="CustomerCount")
        fig_bar = px.bar(
            pivot_long,
            x="CustLocation",
            y="CustomerCount",
            color="Cluster",
            color_discrete_map=CLUSTER_PALETTE,
            barmode="stack",
            title=f"Customer Distribution by City & Segment — {len(current_cities)} cities (page view)",
        )
        fig_bar.update_layout(legend_title_text="Cluster", xaxis_title="City", yaxis_title="Customers", bargap=0.15)
        st.plotly_chart(fig_bar, use_container_width=True)

    with rcol:
        heat = (
            fdf.pivot_table(index="CustLocation", columns="Cluster", values="AvgTotalMonetary", aggfunc="mean")
            .fillna(0)
        )
        fig_heat = px.imshow(
            heat,
            labels=dict(color="Avg Total Monetary"),
            aspect="auto",
            title="Avg Total Monetary — Heatmap",
            color_continuous_scale="Tealrose",
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    treemap_df = fdf.groupby(["CustLocation", "Cluster"], as_index=False)["CustomerCount"].sum()
    fig_tree = px.treemap(
        treemap_df,
        path=["CustLocation", "Cluster"],
        values="CustomerCount",
        color="Cluster",
        color_discrete_map=CLUSTER_PALETTE,
        title="Customer Mix Treemap",
    )
    st.plotly_chart(fig_tree, use_container_width=True)

    st.markdown("#### Insight Highlights")
    city_lead = treemap_df.groupby("CustLocation")["CustomerCount"].sum().sort_values(ascending=False).head(3)
    seg_mix = fdf.groupby("Cluster")["CustomerCount"].sum().sort_values(ascending=False)
    lead_city_txt = ", ".join([f"{c} ({v:,})" for c, v in city_lead.items()]) if not city_lead.empty else "N/A"
    lead_seg_txt = ", ".join([f"Cluster {int(k)} ({int(v):,})" for k, v in seg_mix.items()]) if not seg_mix.empty else "N/A"
    st.info(
        f"Top cities by customers: **{lead_city_txt}**. Leading segments: **{lead_seg_txt}**. "
        "Use the sidebar to page through cities or show all.")

# ----------------------------
# City Deep‑Dive Tab
# ----------------------------
with city_tab:
    c1, c2 = st.columns([1, 1])

    with c1:
        city_totals = fdf.groupby("CustLocation")["CustomerCount"].sum().reset_index().sort_values("CustomerCount", ascending=False)
        fig_ct = px.bar(
            city_totals,
            x="CustLocation",
            y="CustomerCount",
            title="Total Customers by City",
        )
        st.plotly_chart(fig_ct, use_container_width=True)

    with c2:
        metric_cols = ["AvgFrequency", "AvgTotalMonetary", "AvgRecency"]
        city_profile = (
            fdf.groupby("CustLocation")[metric_cols].mean().reset_index()
        )
        prof_norm = city_profile.copy()
        for c in metric_cols:
            rng = prof_norm[c].max() - prof_norm[c].min()
            prof_norm[c] = 0.5 if rng == 0 else (prof_norm[c] - prof_norm[c].min()) / rng
        default_choices = prof_norm.sort_values("AvgTotalMonetary", ascending=False)["CustLocation"].head(3).tolist()
        pick = st.multiselect("Compare up to 4 cities", prof_norm["CustLocation"].tolist(), default=default_choices, max_selections=4)
        pick = pick if pick else default_choices
        categories = ["Freq (norm)", "Spend (norm)", "Recency (norm)"]
        prof_plot = prof_norm.rename(columns={
            "AvgFrequency": categories[0],
            "AvgTotalMonetary": categories[1],
            "AvgRecency": categories[2],
        })
        fig_radar = go.Figure()
        for city in pick:
            row = prof_plot[prof_plot["CustLocation"] == city][categories].iloc[0].tolist()
            row.append(row[0])
            fig_radar.add_trace(go.Scatterpolar(r=row, theta=categories + [categories[0]], fill='toself', name=city, opacity=0.5))
        fig_radar.update_layout(title="City Profile — Normalized Metrics", polar=dict(radialaxis=dict(visible=True, range=[0,1])), showlegend=True)
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("### Segment Mix & Averages per City")
    col_a, col_b = st.columns(2)

    with col_a:
        mix = (
            fdf.groupby(["CustLocation", "Cluster"], as_index=False)["CustomerCount"].sum()
        )
        fig_mix = px.bar(
            mix, x="CustLocation", y="CustomerCount", color="Cluster",
            color_discrete_map=CLUSTER_PALETTE, barmode="group",
            title="Segment Mix by City (Customers)",
        )
        st.plotly_chart(fig_mix, use_container_width=True)

    with col_b:
        avg_metrics = (
            fdf.groupby("CustLocation", as_index=False)[["AvgAge", "AvgFrequency", "AvgTotalMonetary", "AvgRecency"]].mean()
        )
        fig_metrics = px.line(
            avg_metrics.melt(id_vars="CustLocation", var_name="Metric", value_name="Value"),
            x="CustLocation", y="Value", color="Metric", markers=True,
            title="Average Metrics by City",
        )
        st.plotly_chart(fig_metrics, use_container_width=True)

# ----------------------------
# Segment Explorer Tab
# ----------------------------
with segment_tab:
    st.markdown("#### Segment Profiles (All Cities in Current Page/Selection)")

    seg_summary = (
        fdf.groupby("Cluster")[[
            "CustomerCount", "AvgAge", "AvgFrequency", "AvgTotalMonetary", "AvgRecency"
        ]].agg({
            "CustomerCount": "sum",
            "AvgAge": "mean",
            "AvgFrequency": "mean",
            "AvgTotalMonetary": "mean",
            "AvgRecency": "mean",
        }).round(2).reset_index()
    )

    st.dataframe(seg_summary, use_container_width=True)

    fig_bubble = px.scatter(
        seg_summary,
        x="AvgFrequency", y="AvgTotalMonetary", size="CustomerCount", color="Cluster",
        color_discrete_sequence=BUBBLE_PALETTE, size_max=64,
        hover_data={"AvgAge": True, "AvgRecency": True, "CustomerCount": ":,"},
        title="Segment Positioning (Frequency vs. Spend)",
    )
    fig_bubble.update_traces(marker=dict(line=dict(width=1, color="white")))
    st.plotly_chart(fig_bubble, use_container_width=True)

    st.markdown("#### Strategy Suggestions")
    recs = []
    if not seg_summary.empty:
        med_spend = seg_summary["AvgTotalMonetary"].median()
        med_freq = seg_summary["AvgFrequency"].median()
        for _, row in seg_summary.sort_values("AvgTotalMonetary", ascending=False).iterrows():
            cid = int(row["Cluster"]) if not math.isnan(row["Cluster"]) else row["Cluster"]
            if row["AvgTotalMonetary"] >= med_spend and row["AvgFrequency"] >= med_freq:
                recs.append(f"**Cluster {cid}**: Premium offers & loyalty — high spend and activity.")
            elif row["AvgTotalMonetary"] >= med_spend:
                recs.append(f"**Cluster {cid}**: Value‑add bundles to sustain high spend.")
            elif row["AvgFrequency"] >= med_freq:
                recs.append(f"**Cluster {cid}**: Cross‑sell bundles — frequent but mid spend.")
            else:
                recs.append(f"**Cluster {cid}**: Re‑engagement & onboarding nudges — build activity.")

    st.markdown("\n".join([f"- {r}" for r in recs]) or "No segments in current filter.")


# ----------------------------
# Data & Notes Tab
# ----------------------------
with details_tab:
    st.markdown("#### Filtered Data Preview")
    st.dataframe(fdf.sort_values(["CustLocation", "Cluster"]).reset_index(drop=True), use_container_width=True)

    csv = fdf.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download filtered data (CSV)", data=csv, file_name="filtered_top_kpis.csv", mime="text/csv")

    st.markdown("---")
    st.markdown(
        """
        **Banner sizing**  
        Recommended banner size: **1400×350 px** (or 2800×700 for HiDPI). The app auto‑fits/crops to this aspect.

        **How pagination works**  
        • Use **Cities per page** and **City page** in the sidebar to flip between city groups (e.g., first 10 vs. next 10).  
        • Toggle **Show all cities** to view every city in one go.  
        • Top‑N (by CustomerCount) can be combined with pagination.

        **Metric Glossary**  
        • **CustomerCount** — number of customers in a City×Segment cell.  
        • **AvgFrequency** — average transaction frequency.  
        • **AvgTotalMonetary** — average total monetary value per customer.  
        • **AvgRecency** — days since last activity (lower is more recent).  
        • **AvgAge** — average customer age.
        """
    )

# ----------------------------
# Footer
# ----------------------------
st.markdown(
    """
    <div style="text-align:center; opacity:0.7; font-size:0.9rem; padding: 10px 0 0 0;">
        Built with Streamlit by Abibat Oki
    </div>
    """,
    unsafe_allow_html=True,
)
