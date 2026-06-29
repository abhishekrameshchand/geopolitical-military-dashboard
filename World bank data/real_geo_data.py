import pandas as pd
import world_bank_data as wb
import plotly.express as px
import streamlit as st

# Page Configuration (Mobile aur Desktop dono ke liye wide layout)
st.set_page_config(page_title="Geopolitical Dashboard", layout="wide")

st.title("🌍 Geopolitical & Military Expenditure Dashboard")
st.markdown("World Bank ke live data par aadharit deshon ka sainik kharch (% of GDP)")

# Sidebar me filters lagana
st.sidebar.header("🎛️ Dashboards Filters")

# 1. Year Selection Filter (1990 se 2022)
selected_year = st.sidebar.slider("Saal chune (Select Year):", min_value=1990, max_value=2022, value=2022)

status_text = st.empty()
status_text.write(f"🔄 World Bank se saal {selected_year} ka data fetch ho raha hai...")

try:
    # Data Fetching
    mil_series = wb.get_series('MS.MIL.XPND.GD.ZS', date=str(selected_year), id_or_value='value')
    mil_gdp = mil_series.reset_index()
    
    value_col = mil_gdp.columns[-1]
    mil_gdp = mil_gdp.rename(columns={value_col: 'Military_Share_of_GDP'})
    
    countries = wb.get_countries().reset_index()
    
    match_col = None
    for col in mil_gdp.columns:
        if str(col).lower() in ['country', 'name']:
            match_col = col
            break
    if not match_col:
        match_col = mil_gdp.columns[0]
        
    df = pd.merge(countries[['region', 'name', 'iso2Code']], mil_gdp, left_on='name', right_on=match_col)
    df = df.dropna(subset=['Military_Share_of_GDP'])
    df = df[df['region'] != 'Aggregates']
    
    status_text.empty() # Loading message hatayein

    # --- FEATURE 1: TOP METRICS CARDS ---
    top_country = df.sort_values(by='Military_Share_of_GDP', ascending=False).iloc[0]
    global_avg = df['Military_Share_of_GDP'].mean()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Highest Spender", f"{top_country['name']}", f"{top_country['Military_Share_of_GDP']:.2f}% GDP")
    col2.metric("Global Average Spend", f"{global_avg:.2f}% of GDP")
    col3.metric("Total Countries Data", f"{len(df)}")
    
    st.markdown("---")

    # --- FEATURE 2: INTERACTIVE MAP VIEW ---
    st.subheader(f"🗺️ Global Military Expenditure Map ({selected_year})")
    fig_map = px.choropleth(df, 
                            locations="name", 
                            locationmode="country names",
                            color="Military_Share_of_GDP",
                            hover_name="name",
                            color_continuous_scale=px.colors.sequential.Plasma,
                            labels={'Military_Share_of_GDP':'% of GDP'})
    fig_map.update_layout(height=400, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

    # --- FEATURE 3: TOP 10 BAR CHART ---
    st.subheader(f"📊 Top 10 Countries by Military Spend ({selected_year})")
    df_top10 = df.sort_values(by='Military_Share_of_GDP', ascending=False).head(10)
    
    fig_bar = px.bar(df_top10, 
                     x='Military_Share_of_GDP', 
                     y='name', 
                     color='region',
                     orientation='h',
                     labels={'Military_Share_of_GDP': 'Spend (% of GDP)', 'name': 'Country'})
    
    fig_bar.update_layout(
        yaxis={'categoryorder':'total ascending'},
        height=350,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

except Exception as e:
    st.error(f"Data load karne me dikkat aayi: {e}")