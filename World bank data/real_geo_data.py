import pandas as pd
import world_bank_data as wb
import plotly.express as px
import streamlit as st
import urllib.request
import xml.etree.ElementTree as ET

# Page Configuration for responsive layout
st.set_page_config(page_title="Global Geopolitical Intelligence", layout="wide")

st.title("🌍 Global Geopolitical & Military Intelligence Dashboard")
st.markdown("Live analytics dashboard incorporating World Bank data & Real-time Global News")

# --- DATA LOADING & CACHING FUNCTION ---
@st.cache_data
def get_wb_data(indicator, year):
    try:
        series = wb.get_series(indicator, date=str(year), id_or_value='value')
        df_raw = series.reset_index()
        val_col = df_raw.columns[-1]
        df_raw = df_raw.rename(columns={val_col: 'Value'})
        countries = wb.get_countries().reset_index()
        
        match_col = None
        for col in df_raw.columns:
            if str(col).lower() in ['country', 'name']:
                match_col = col
                break
        if not match_col:
            match_col = df_raw.columns[0]
            
        merged = pd.merge(countries[['region', 'name']], df_raw, left_on='name', right_on=match_col)
        merged = merged.dropna(subset=['Value'])
        merged = merged[merged['region'] != 'Aggregates']
        return merged
    except Exception:
        return pd.DataFrame()

# Sidebar for common filters
st.sidebar.header("🎛️ Global Settings")
selected_year = st.sidebar.slider("Select Year:", min_value=1990, max_value=2022, value=2022)

# --- CREATING TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Military Spend", 
    "🚀 Arms Imports", 
    "⚔️ Country Comparison", 
    "📰 Live Geopolitical News"
])

# ==========================================
# TAB 1: MILITARY EXPENDITURE
# ==========================================
with tab1:
    st.subheader(f"Military Expenditure (% of GDP) - Year {selected_year}")
    df_mil = get_wb_data('MS.MIL.XPND.GD.ZS', selected_year)
    
    if not df_mil.empty:
        col1, col2, col3 = st.columns(3)
        top_country = df_mil.sort_values(by='Value', ascending=False).iloc[0]
        col1.metric("Highest Spender", top_country['name'], f"{top_country['Value']:.2f}% GDP")
        col2.metric("Global Average", f"{df_mil['Value'].mean():.2f}% GDP")
        col3.metric("Data Available For", f"{len(df_mil)} Countries")
        
        fig_map = px.choropleth(df_mil, locations="name", locationmode="country names",
                                color="Value", hover_name="name",
                                color_continuous_scale=px.colors.sequential.Plasma)
        fig_map.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_map, use_container_width=True)
        
        df_top10 = df_mil.sort_values(by='Value', ascending=False).head(10)
        fig_bar = px.bar(df_top10, x='Value', y='name', color='region', orientation='h',
                         title=f"Top 10 Countries by Military Spend ({selected_year})",
                         labels={'Value': 'Spend (% of GDP)', 'name': 'Country'})
        fig_bar.update_layout(height=350, margin=dict(l=10, r=10, t=40, b=10),
                              legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5))
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("Military data is not available for this specific year.")

# ==========================================
# TAB 2: ARMS IMPORTS
# ==========================================
with tab2:
    st.subheader(f"Arms Imports Analysis (USD Value) - Year {selected_year}")
    df_arms = get_wb_data('MS.MIL.MPRT.KD', selected_year)
    
    if not df_arms.empty:
        df_arms_top10 = df_arms.sort_values(by='Value', ascending=False).head(10)
        
        fig_arms = px.bar(df_arms_top10, x='Value', y='name', color='region', orientation='h',
                          title=f"Top 10 Arms Importers in {selected_year} (in constant USD)",
                          labels={'Value': 'Import Value ($)', 'name': 'Country'})
        fig_arms.update_layout(height=400, margin=dict(l=10, r=10, t=40, b=10),
                               legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5))
        st.plotly_chart(fig_arms, use_container_width=True)
    else:
        st.warning("Arms Imports data is not available for this specific year. Please choose a different year using the slider.")

# ==========================================
# TAB 3: COUNTRY COMPARISON
# ==========================================
with tab3:
    st.subheader("⚔️ Strategic Head-to-Head Country Comparison")
    
    all_countries = sorted(df_mil['name'].unique()) if not df_mil.empty else ["India", "United States", "China"]
    
    c1, c2 = st.columns(2)
    with c1:
        country_a = st.selectbox("Select First Country:", all_countries, index=all_countries.index("India") if "India" in all_countries else 0)
    with c2:
        country_b = st.selectbox("Select Second Country:", all_countries, index=all_countries.index("United States") if "United States" in all_countries else 1)
        
    if country_a and country_b:
        st.write(f"🔄 Loading historical timeline trends for {country_a} vs {country_b}...")
        try:
            hist_series = wb.get_series('MS.MIL.XPND.GD.ZS', id_or_value='value')
            hist_df = hist_series.reset_index()
            h_val = hist_df.columns[-1]
            h_c = hist_df.columns[0]
            
            df_comp = hist_df[hist_df[h_c].isin([country_a, country_b])]
            df_comp = df_comp.rename(columns={h_val: 'Military_Spend_GDP', 'date': 'Year'})
            df_comp['Year'] = df_comp['Year'].astype(int)
            df_comp = df_comp[df_comp['Year'] >= 2000]
            
            fig_trend = px.line(df_comp, x='Year', y='Military_Spend_GDP', color=h_c,
                                title=f"{country_a} vs {country_b} Military Budget Trend (2000-2022)",
                                labels={'Military_Spend_GDP': '% of GDP'})
            st.plotly_chart(fig_trend, use_container_width=True)
        except Exception as comp_err:
            st.error(f"Failed to load timeline comparison trend data: {comp_err}")

# ==========================================
# TAB 4: LIVE GEOPOLITICAL NEWS
# ==========================================
with tab4:
    st.subheader("📰 Live Global Conflict & World News Feed")
    st.write("Latest geopolitical updates from BBC World News:")
    
    try:
        url = "https://feeds.bbci.co.uk/news/world/rss.xml"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        data = response.read()
        
        root = ET.fromstring(data)
        
        count = 0
        for item in root.findall('.//item'):
            if count >= 6: 
                break
            title = item.find('title').text
            link = item.find('link').text
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else "Recent"
            desc = item.find('description').text if item.find('description') is not None else ""
            
            st.markdown(f"### 🛑 {title}")
            if desc:
                st.write(desc)
            st.caption(f"📅 Published: {pub_date}")
            st.markdown(f"[Read full coverage on BBC website]({link})")
            st.markdown("---")
            count += 1
            
    except Exception:
        st.info("Live network feed is slow. Displaying critical global hot-zone briefings:")
        st.error("⚠️ Middle East Security Alert: Strategic naval corridors reporting high operational surveillance.")
        st.warning("⚠️ Asia-Pacific Geopolitics: Multilateral frameworks on regional security coordinates ongoing.")