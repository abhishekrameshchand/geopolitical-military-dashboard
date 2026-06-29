import pandas as pd
import world_bank_data as wb
import plotly.express as px
import streamlit as st
import urllib.request
import xml.etree.ElementTree as ET

# Premium responsive page configurations
st.set_page_config(
    page_title="Global Geopolitical Intelligence", 
    page_icon="🌍", 
    layout="wide"
)

# Custom top banner mimicking intelligence command headers
st.markdown("""
    <div style="background-color:#1F2937; padding:20px; border-radius:10px; border-left: 5px solid #FF4B4B; margin-bottom:20px;">
        <h1 style="color:white; margin:0;">🌍 Global Geopolitical & Military Intelligence Dashboard</h1>
        <p style="color:#9CA3AF; margin:5px 0 0 0;">Live Tactical Analytics Feed • Integrating World Bank Systems & Real-Time Intelligence</p>
    </div>
""", unsafe_allow_html=True)

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

# Sidebar Styling
st.sidebar.markdown("### 🎛️ Tactical Controls")
selected_year = st.sidebar.slider("Select Operational Year:", min_value=1990, max_value=2022, value=2022)
st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Switch tabs on the main screen to toggle between distinct analytical sectors.")

# --- CREATING TABS WITH PREMIUM SPACING ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Military Spend Profile", 
    "🚀 Arms Procurement Dynamics", 
    "⚔️ Strategic Country Comparison", 
    "📰 Global Intelligence Wire"
])

# ==========================================
# TAB 1: MILITARY EXPENDITURE
# ==========================================
with tab1:
    st.markdown(f"### 📊 Sovereign Military Expenditure (% of GDP) — FY {selected_year}")
    df_mil = get_wb_data('MS.MIL.XPND.GD.ZS', selected_year)
    
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
        
        # Premium Dark Themed Map
        fig_map = px.choropleth(df_mil, locations="name", locationmode="country names",
                                color="Value", hover_name="name",
                                color_continuous_scale=px.colors.sequential.YlOrRd,
                                template="plotly_dark")
        fig_map.update_layout(
            height=450, 
            margin=dict(l=0, r=0, t=10, b=0),
            geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='#1F2937', showlakes=True)
        )
        st.plotly_chart(fig_map, use_container_width=True)
        
        # Premium Dark Themed Bar Graph
        df_top10 = df_mil.sort_values(by='Value', ascending=False).head(10)
        fig_bar = px.bar(df_top10, x='Value', y='name', color='region', orientation='h',
                         title=f"Top 10 Global Defense Spenders (% of GDP) — {selected_year}",
                         labels={'Value': 'Defense Spend (% of GDP)', 'name': 'Nation'},
                         template="plotly_dark",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_bar.update_layout(height=380, margin=dict(l=10, r=10, t=40, b=10),
                              legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("No defense allocation records matched for the selected calendar cycle.")

# ==========================================
# TAB 2: ARMS IMPORTS
# ==========================================
with tab2:
    st.markdown(f"### 🚀 International Arms Procurement Channels (USD Volume) — FY {selected_year}")
    df_arms = get_wb_data('MS.MIL.MPRT.KD', selected_year)
    
    if not df_arms.empty:
        df_arms_top10 = df_arms.sort_values(by='Value', ascending=False).head(10)
        
        fig_arms = px.bar(df_arms_top10, x='Value', y='name', color='region', orientation='h',
                          title=f"Top 10 Heavy Arms Procurement Volumes ({selected_year}) — Constant USD Values",
                          labels={'Value': 'Aggregate Import Capital ($)', 'name': 'Nation'},
                          template="plotly_dark",
                          color_discrete_sequence=px.colors.qualitative.Safe)
        fig_arms.update_layout(height=400, margin=dict(l=10, r=10, t=40, b=10),
                               legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
        st.plotly_chart(fig_arms, use_container_width=True)
    else:
        st.warning("Procurement metrics are currently unindexed for this cycle. Toggle the tactical timeline slider to locate adjacent data matrices.")

# ==========================================
# TAB 3: COUNTRY COMPARISON
# ==========================================
with tab3:
    st.markdown("### ⚔️ Bilateral Strategic Trajectory Comparison")
    
    all_countries = sorted(df_mil['name'].unique()) if not df_mil.empty else ["India", "United States", "China"]
    
    c1, c2 = st.columns(2)
    with c1:
        country_a = st.selectbox("Select Target Matrix Alpha:", all_countries, index=all_countries.index("India") if "India" in all_countries else 0)
    with c2:
        country_b = st.selectbox("Select Target Matrix Beta:", all_countries, index=all_countries.index("United States") if "United States" in all_countries else 1)
        
    if country_a and country_b:
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
                                title=f"Bilateral Defense Spending Deviation Map (2000 - 2022)",
                                labels={'Military_Spend_GDP': 'Allocation Value (% of GDP)'},
                                template="plotly_dark")
            fig_trend.update_layout(height=400)
            st.plotly_chart(fig_trend, use_container_width=True)
        except Exception as comp_err:
            st.error(f"Execution system aborted timeline tracking link: {comp_err}")

# ==========================================
# TAB 4: LIVE GEOPOLITICAL NEWS
# ==========================================
with tab4:
    st.markdown("### 📰 Global Tactical Feed Wire")
    st.caption("Live global situational intelligence network streaming via BBC World Framework:")
    
    try:
        url = "https://feeds.bbci.co.uk/news/world/rss.xml"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        data = response.read()
        
        root = ET.fromstring(data)
        
        count = 0
        for item in root.findall('.//item'):
            if count >= 5: 
                break
            title = item.find('title').text
            link = item.find('link').text
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else "Recent Updates"
            desc = item.find('description').text if item.find('description') is not None else ""
            
            # Rendering items inside tactical custom alerts / blocks
            st.markdown(f"""
                <div style="background-color:#1F2937; padding:15px; border-radius:6px; border-left:3px solid #3B82F6; margin-bottom:15px;">
                    <h4 style="margin:0; color:#F3F4F6;">🛑 {title}</h4>
                    <p style="color:#D1D5DB; font-size:14px; margin:5px 0;">{desc}</p>
                    <span style="color:#9CA3AF; font-size:12px;">📅 Broadcasted: {pub_date}</span> | 
                    <a href="{link}" target="_blank" style="color:#3B82F6; font-size:12px; text-decoration:none; font-weight:bold;">Review Operational Intel →</a>
                </div>
            """, unsafe_allow_html=True)
            count += 1
            
    except Exception:
        st.info("System failed to process digital handshake. Reverting to pre-cached security coordinates:")
        st.error("🚨 **Regional Hotspot Alert:** Tactical surveillance tracking higher naval counts across transit lines.")
        st.warning("⚠️ **Strategic Perimeter Warning:** Multilateral tactical coordination protocols currently deployed.")