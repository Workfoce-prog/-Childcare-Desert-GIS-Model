
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Childcare Desert GIS Model", layout="wide")

st.title("Childcare Desert GIS Model")
st.caption("Division fit: Assistant Commissioner: Early Childhood / Child Care Services Division")

DATA_PATH = "data/sample_data.csv"

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


def norm(series, reverse=False):
    s = pd.to_numeric(series, errors="coerce")
    if s.max() == s.min():
        out = pd.Series([50]*len(s))
    else:
        out = 100 * (s - s.min()) / (s.max() - s.min())
    if reverse:
        out = 100 - out
    return out.fillna(50)

def band_good(score):
    if score >= 75: return "Strong"
    if score >= 50: return "Moderate"
    return "Needs Support"

def band_risk(score):
    if score >= 75: return "Red"
    if score >= 50: return "Amber"
    return "Green"


df = load_data()

df["Childcare_Desert_Score"] = (
    0.45*norm(df["childcare_slots_per_100_children"], reverse=True) +
    0.35*norm(df["licensed_provider_count"], reverse=True) +
    0.20*norm(df["poverty_rate"])
).round(1)
df["Desert_Risk_Band"] = df["Childcare_Desert_Score"].apply(band_risk)
score_col = "Childcare_Desert_Score"
band_col = "Desert_Risk_Band"
display_cols = ["youth_id","county","zip_code",score_col,band_col,"childcare_slots_per_100_children","licensed_provider_count","poverty_rate"]


with st.sidebar:
    st.header("Filters")
    selected_counties = st.multiselect("County", sorted(df["county"].unique()), default=sorted(df["county"].unique()))
    selected_band = st.multiselect("Band", sorted(df[band_col].unique()), default=sorted(df[band_col].unique()))

dff = df[(df["county"].isin(selected_counties)) & (df[band_col].isin(selected_band))]

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Average Score", f"{dff[score_col].mean():.1f}")
with c2:
    st.metric("Records", f"{len(dff):,}")
with c3:
    priority = dff[dff[band_col].isin(["Red","Needs Support"])]
    st.metric("Priority Records", f"{len(priority):,}")

st.subheader("Purpose")
st.write("Identifies ZIP codes/counties where childcare supply is limited relative to need. Production version can connect to tract shapefiles, provider licensing records, and GIS coordinates.")

county_summary = dff.groupby("county", as_index=False)[score_col].mean().sort_values(score_col, ascending=False)

st.subheader("County Summary")
chart = alt.Chart(county_summary).mark_bar().encode(
    x=alt.X("county:N", sort="-y"),
    y=alt.Y(f"{score_col}:Q"),
    tooltip=["county", score_col]
).properties(height=350)
st.altair_chart(chart, use_container_width=True)

st.subheader("Individual-Level Results")
st.dataframe(dff[display_cols].sort_values(score_col, ascending=False), use_container_width=True, height=420)

st.subheader("Recommended Actions")
if "Childcare Desert GIS Model" == "Child Opportunity Index":
    st.write("Use low-score areas to target early childhood supports, food security partnerships, attendance supports, and family stabilization resources.")
elif "Childcare Desert GIS Model" == "Childcare Desert GIS Model":
    st.write("Use high-risk ZIP codes/counties to prioritize childcare provider recruitment, licensing support, transportation solutions, and subsidy access.")
elif "Childcare Desert GIS Model" == "Youth Workforce Stability Predictor":
    st.write("Use low-score youth groups to target paid work-based learning, transportation support, mentoring, training enrollment, and employer partnerships.")
elif "Childcare Desert GIS Model" == "Child Support Compliance Sustainability Model":
    st.write("Use low sustainability scores for early supportive intervention, payment plan review, employment referrals, and arrears management—not punitive automation.")
elif "Childcare Desert GIS Model" == "Housing + School Mobility Risk Model":
    st.write("Use high-risk records to coordinate school stability, McKinney-Vento supports, transportation, shelter access, and family housing stabilization.")
else:
    st.write("Use high transition-risk records to coordinate youth services, mentorship, employment/training, housing support, and cross-system case coordination.")

st.download_button("Download scored CSV", dff.to_csv(index=False), "02_childcare_desert_gis_model_early_childhood_scored.csv", "text/csv")
