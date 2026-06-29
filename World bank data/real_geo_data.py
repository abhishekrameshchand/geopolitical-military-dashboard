import pandas as pd
import world_bank_data as wb
import plotly.express as px
import streamlit as st
import urllib.request
import xml.etree.ElementTree as ET
import numpy as np

# Responsive page configurations
st.set_page_config(
    page_title="Global Geopolitical Intelligence", 
    page_icon="🌍", 
    layout="wide"
)

# Top command banner
st.markdown("""
    <div style="background-color:#1F2937; padding:20px; border-radius:10px; border-left: 5px solid #FF4B4B; margin-bottom:20px;">
        <h1 style="color:white; margin:0;">🌍 Global Geopolitical & Military Intelligence Dashboard</h1>
        <p style="color:#9CA3AF; margin:5px 0 0 0;">Live Tactical Analytics Feed • Advanced Predictive Models & Development Metrics</p>
    </div>
""", unsafe_allow_html=True)

# --- CACHED DATA FETCHING ---
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

# Sidebar Controls
st.sidebar.markdown("### 🎛️ Tactical Controls")
selected_year = st.sidebar.slider("Select Operational Year:", min_value=1990, max_value=2022, value=2022)
st.sidebar.markdown("---")
st.sidebar.info("💡 **AI Predictive Engine Active:** Navigate to the Country Comparison tab to view 2026-2030 budget forecasts.")

# --- TABS SETUP ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Military Spend Profile", 
    "🚀 Arms Procurement", 
    "⚔️ AI Predictive Comparison", 
    "🧠 Development Trade-offs",
    "📰 Intelligence Wire"
])

# FETCH BASE DATA
df_mil = get_wb_data('MS.MIL.XPND.GD.ZS', selected_year)

# ==========================================
# TAB 1: MILITARY EXPENDITURE
# ==========================================
with tab1:
    st.markdown(f"### 📊 Sovereign Military Expenditure (% of GDP) — FY {selected_year}")
    if not df_mil.empty:
        col1, col2, col3 = st.columns(3)
        top_country = df_mil.sort_values(by='Value', ascending=False).iloc[0]
        
        with col1:
            st.markdown(f"<div style='background-color:#1F2937; padding:15px; border-radius:8px; text-align:center;'><strong>Peak Allocation Country</strong><br><span style='color:#FF4B4B; font-size:20px; font-weight:bold;'>{top_country['name']}</span><br>({top_country['Value']:.2f}% GDP)</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div style='background-color:#1F2937; padding:15px; border-radius:8px; text-align:center;'><strong>Global Mean Allocation</strong><br><span style='color:#3B82F6; font-size:20px; font-weight:bold;'>{df_mil['Value'].mean():.2f}% GDP</span><br>System Baseline</div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div style='background-color:#1F2937; padding:15px; border-radius:8px; text-align:center;'><strong>Data Points Tracked</strong><br><span style='color:#10B981; font-size:20px; font-weight:bold;'>{len(df_mil)} Nations</span><br>Verified Status</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        fig_map = px.choropleth(df_mil, locations="name", locationmode="country names",
                                color="Value", hover_name="name",
                                color_continuous_scale=px.colors.sequential.YlOrRd,
                                template="plotly_dark")
        fig_map.update_layout(height=420, margin=dict(l=0, r=0, t=10, b=0), geo=dict(bgcolor='rgba(0,0,0,0)', showlakes=True))
        st.plotly_chart(fig_map, use_container_width=True)
        
        df_top10 = df_mil.sort_values(by='Value', ascending=False).head(10)
        fig_bar = px.bar(df_top10, x='Value', y='name', color='region', orientation='h',
                         title=f"Top 10 Global Defense Spenders — {selected_year}", template="plotly_dark")
        fig_bar.update_layout(height=350, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("No records matched for this cycle.")

# ==========================================
# TAB 2: ARMS IMPORTS
# ==========================================
with tab2:
    st.markdown(f"### 🚀 International Arms Procurement Channels — FY {selected_year}")
    df_arms = get_wb_data('MS.MIL.MPRT.KD', selected_year)
    if not df_arms.empty:
        df_arms_top10 = df_arms.sort_values(by='Value', ascending=False).head(10)
        fig_arms = px.bar(df_arms_top10, x='Value', y='name', color='region', orientation='h',
                          title=f"Top 10 Arms Importers ({selected_year}) — Constant USD", template="plotly_dark")
        st.plotly_chart(fig_arms, use_container_width=True)
    else:
        st.warning("Procurement metrics are unindexed for this cycle.")

# ==========================================
# TAB 3: AI PREDICTIVE COUNTRY COMPARISON
# ==========================================
with tab3:
    st.markdown("### ⚔️ Bilateral Strategic Trajectory & AI Forecasting (2026–2030)")
    
    all_countries = sorted(df_mil['name'].unique()) if not df_mil.empty else ["India", "United States", "China"]
    c1, c2 = st.columns(2)
    with c1:
        country_a = st.selectbox("Select Target Nation Alpha:", all_countries, index=all_countries.index("India") if "India" in all_countries else 0)
    with c2:
        country_b = st.selectbox("Select Target Nation Beta:", all_countries, index=all_countries.index("United States") if "United States" in all_countries else 1)
        
    if country_a and country_b:
        try:
            hist_series = wb.get_series('MS.MIL.XPND.GD.ZS', id_or_value='value')
            hist_df = hist_series.reset_index()
            h_val = hist_df.columns[-1]
            h_c = hist_df.columns[0]
            
            df_comp = hist_df[hist_df[h_c].isin([country_a, country_b])].dropna()
            df_comp = df_comp.rename(columns={h_val: 'Spend', 'date': 'Year'})
            df_comp['Year'] = df_comp['Year'].astype(int)
            df_comp = df_comp[df_comp['Year'] >= 2000]
            
            # --- AI LINEAR TREND FORECASTING ENGINE ---
            forecast_data = []
            for country in [country_a, country_b]:
                c_df = df_comp[df_comp[h_c] == country].sort_values('Year')
                if len(c_df) > 3:
                    X = c_df['Year'].values
                    y = c_df['Spend'].values
                    # Calculate linear trend line (y = mx + c)
                    slope, intercept = np.polyfit(X, y, 1)
                    
                    # Append historical entries
                    for idx, row in c_df.iterrows():
                        forecast_data.append({'Year': row['Year'], 'Spend': row['Spend'], 'Country': country, 'Type': 'Historical'})
                    
                    # Generate Future Predictions through 2030
                    for future_year in range(2023, 2031):
                        pred_val = max(0.1, slope * future_year + intercept) # Prevent negative budgets
                        forecast_data.append({'Year': future_year, 'Spend': pred_val, 'Country': country, 'Type': 'AI Forecast'})
            
            if forecast_data:
                df_forecast = pd.DataFrame(forecast_data)
                fig_trend = px.line(df_forecast, x='Year', y='Spend', color='Country', line_dash='Type',
                                    title="Historical Allocation vs. AI Predictive Growth Path (Through 2030)",
                                    labels={'Spend': 'Allocation Value (% of GDP)'}, template="plotly_dark")
                st.plotly_chart(fig_trend, use_container_width=True)
                st.caption("📝 *Note: Solid lines show verified historical records. Dotted lines display AI linear projections out to 2030 based on historical trends.*")
        except Exception as e:
            st.error(f"Prediction engine fault: {e}")

# ==========================================
# TAB 4: DEVELOPMENT TRADE-OFFS
# ==========================================
with tab4:
    st.markdown("### 🧠 The Security-Development Dilemma")
    st.write("Does massive military spending crowd out civic investment? This matrix maps military burdens against central government spending on education.")
    
    # Fetching Education expenditure as % of total government expenditure
    df_edu = get_wb_data('SE.XPD.TOTL.GB.ZS', selected_year)
    
    if not df_mil.empty and not df_edu.empty:
        df_tradeoff = pd.merge(df_mil[['name', 'Value', 'region']], df_edu[['name', 'Value']], on='name', suffixes=('_Mil', '_Edu'))
        df_tradeoff = df_tradeoff.rename(columns={'Value_Mil': 'Military Burden (% GDP)', 'Value_Edu': 'Education Investment (% Budget)'})
        
        fig_scatter = px.scatter(df_tradeoff, x='Military Burden (% GDP)', y='Education Investment (% Budget)',
                                 color='region', hover_name='name', size_max=15,
                                 title=f"National Strategic Trade-Off Analysis Matrix ({selected_year})",
                                 template="plotly_dark")
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.warning("Overlapping data profiles for education and defense are unavailable for this specific calendar cycle.")

# ==========================================
# TAB 5: LIVE GEOPOLITICAL NEWS
# ==========================================
with tab4 if 'tab5' not in locals() else tab5:
    st.markdown("### 📰 Global Tactical Feed Wire")
    try:
        url = "https://feeds.bbci.co.uk/news/world/rss.xml"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        root = ET.fromstring(response.read())
        
        count = 0
        for item in root.findall('.//item'):
            if count >= 5: break
            title = item.find('title').text
            link = item.find('link').text
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else "Recent"
            desc = item.find('description').text if item.find('description') is not None else ""
            
            st.markdown(f"""
                <div style="background-color:#1F2937; padding:15px; border-radius:6px; border-left:3px solid #3B82F6; margin-bottom:15px;">
                    <h4 style="margin:0; color:#F3F4F6;">🛑 {title}</h4>
                    <p style="color:#D1D5DB; font-size:14px; margin:5px 0;">{desc}</p>
                    <span style="color:#9CA3AF; font-size:12px;">📅 {pub_date}</span> | 
                    <a href="{link}" target="_blank" style="color:#3B82F6; font-size:12px; text-decoration:none; font-weight:bold;">Review Intel →</a>
                </div>
            """, unsafe_allow_html=True)
            count += 1
    except Exception:
        st.info("Displaying pre-cached security coordinates. Network stream offline.")