import streamlit as st
import pandas as pd
import world_bank_data as wb
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Global Military Expenditure Dashboard", layout="wide")

# App Header
st.title("🌐 Interactive Geopolitical Intelligence Map & Dashboard")
st.markdown("---")

# 2. Sidebar Filters
st.sidebar.header("Analysis Filters")
selected_year = st.sidebar.selectbox("Select Year:", ['2022', '2021', '2020', '2019', '2018'])

region_options = ['All Regions', 'Europe & Central Asia', 'Middle East & North Africa', 'East Asia & Pacific', 'Sub-Saharan Africa', 'South Asia', 'Latin America & Caribbean']
selected_region = st.sidebar.selectbox("Select Region:", region_options)

top_n = st.sidebar.slider("Number of Countries for Bar Chart:", min_value=5, max_value=50, value=15)

# 3. Data Fetching Function (Ab hum ISO-3 code bhi reset_index me layenge)
@st.cache_data
def fetch_data(year):
    mil_series = wb.get_series('MS.MIL.XPND.GD.ZS', date=year, id_or_value='value')
    mil_gdp = mil_series.reset_index()
    
    value_col = mil_gdp.columns[-1]
    mil_gdp = mil_gdp.rename(columns={value_col: 'Military_Share_of_GDP'})
    
    # Countries list with ISO codes (Country ID)
    countries = wb.get_countries().reset_index()
    
    # Merge using country name
    df = pd.merge(countries[['id', 'region', 'name']], mil_gdp, left_on='name', right_on=mil_gdp.columns[0])
    
    df = df.dropna(subset=['Military_Share_of_GDP'])
    df = df[df['region'] != 'Aggregates']
    return df

# Loading State
with st.spinner('Fetching live data from World Bank...'):
    df_clean = fetch_data(selected_year)

# Filter Region for analysis
if selected_region != 'All Regions':
    df_filtered = df_clean[df_clean['region'] == selected_region]
    title_suffix = f"in {selected_region} ({selected_year})"
else:
    df_filtered = df_clean
    title_suffix = f"Globally ({selected_year})"

df_top = df_filtered.sort_values(by='Military_Share_of_GDP', ascending=False).head(top_n)

# 4. Dynamic KPI Metrics
if not df_top.empty:
    highest_country = df_top.iloc[0]['name']
    highest_value = df_top.iloc[0]['Military_Share_of_GDP']
    avg_spending = df_filtered['Military_Share_of_GDP'].mean()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Selected View", value=selected_region)
    with col2:
        st.metric(label="Highest Spender", value=f"{highest_value:.2f}%", delta=highest_country)
    with col3:
        st.metric(label="Average Spending", value=f"{avg_spending:.2f}%")
else:
    st.warning("No data available for this selection.")

st.markdown("---")

# 5. NEW FEATURE: Global Choropleth Map
st.subheader(f"🗺️ Global Heatmap: Military Spending as % of GDP ({selected_year})")
st.markdown("*Tip: Hover over countries to see exact values. Missing data countries will appear blank/grey.*")

# Plotly World Map Code
fig_map = px.choropleth(df_clean, # Pure data pass karenge taaki map hamesha poori duniya ka dikhe
                        locations="id", # ISO 3-letter code column
                        color="Military_Share_of_GDP",
                        hover_name="name",
                        color_continuous_scale=px.colors.sequential.Plasma,
                        labels={'Military_Share_of_GDP': 'Spend % of GDP'})

fig_map.update_layout(
    height=500,
    margin=dict(l=10, r=10, t=10, b=10)
)

st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# 6. Bar Chart Layout
st.subheader(f"📊 Top {top_n} Nations Breakdown {title_suffix}")
if not df_top.empty:
    fig_bar = px.bar(df_top, 
                     x='Military_Share_of_GDP', 
                     y='name', 
                     color='region',
                     orientation='h',
                     labels={'Military_Share_of_GDP': 'Military Expenditure (% of GDP)', 'name': 'Country'},
                     color_discrete_sequence=px.colors.qualitative.Safe)

    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=500)
    st.plotly_chart(fig_bar, use_container_width=True)

# 7. Data Explorer
if st.checkbox("Show Comprehensive Data Table"):
    st.dataframe(df_top[['name', 'region', 'Military_Share_of_GDP']].reset_index(drop=True), use_container_width=True)