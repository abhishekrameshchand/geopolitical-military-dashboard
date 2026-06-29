import pandas as pd
import world_bank_data as wb
import plotly.express as px
import streamlit as st
import urllib.request
import xml.etree.ElementTree as ET
import numpy as np

# Fluid responsive layout engine setup
st.set_page_config(
    page_title="Sovereign Intel Terminal", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STEALTH GRAPHITE & AMBER GOLD CYBER UI STYLING ---
st.markdown("""
    <style>
    /* Premium deep charcoal canvas background */
    [data-testid="stAppViewContainer"], .main {
        background-color: #0A0D14 !important;
        color: #E5E7EB !important;
    }
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* Strict Tab Highlight Overrides Fix */
    button[data-baseweb="tab"] {
        color: #9CA3AF !important;
        background-color: transparent !important;
        border: none !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #F59E0B !important;
        background-color: #111827 !important;
        border-bottom: 3px solid #F59E0B !important;
        border-radius: 6px 6px 0 0 !important;
    }
    
    /* High-Fidelity Tactical Border Cards */
    .tactical-card {
        background: #111827 !important;
        border: 1px solid #1F2937 !important;
        border-left: 4px solid #F59E0B !important;
        border-radius: 8px;
        padding: 22px;
        margin-bottom: 14px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    
    .metric-title {
        color: #9CA3AF;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 700;
    }
    .metric-value {
        color: #FFFFFF;
        font-size: 36px;
        font-weight: 800;
        margin-top: 4px;
        font-family: monospace;
    }
    
    /* Live Broadcast Terminal Wire Cards */
    .wire-card {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 6px;
        padding: 20px;
        margin-bottom: 12px;
    }
    .wire-title {
        color: #F59E0B;
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .wire-desc {
        color: #9CA3AF;
        font-size: 13px;
        line-height: 1.5;
    }
    
    /* Top Terminal Command Bar Layout */
    .terminal-header {
        background: linear-gradient(90deg, #111827 0%, #030712 100%);
        border: 1px solid #1F2937;
        border-radius: 10px;
        padding: 24px;
        margin-bottom: 24px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="terminal-header">
        <h1 style="color:white; margin:0; font-size:26px; font-weight:800; letter-spacing:-0.02em; font-family:monospace;">⚡ SOVEREIGN INTEL // SYSTEM_OS</h1>
        <p style="color:#F59E0B; margin:4px 0 0 0; font-size:12px; font-weight:600; letter-spacing:0.15em; font-family:monospace;">ADVANCED GEOPOLITICS & PREDICTIVE TRAJECTORIES</p>
    </div>
""", unsafe_allow_html=True)

# --- CACHED METRIC DATA SYSTEM ---
@st.cache_data
def get_wb_data(indicator, year):
    try:
        series = wb.get_series(indicator, date=str(year), id_or_value='value')
        df_raw = pd.DataFrame(series).reset_index()
        if df_raw.empty:
            return pd.DataFrame()
        val_col = df_raw.columns[-1]
        df_raw = df_raw.rename(columns={val_col: 'Value'})
        countries = pd.DataFrame(wb.get_countries()).reset_index()
        
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

# Sidebar Configuration Layout
st.sidebar.markdown("### 🎛️ SYSTEM CONTROLS")
selected_year = st.sidebar.slider("Timeline Parameter:", min_value=1990, max_value=2022, value=2022)

# --- MODERNIZED DATA SECTORS TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Budget Profiles", 
    "🚀 Procurement Channels", 
    "🔮 AI Trend Forecasting", 
    "🧠 Policy Dynamics",
    "📰 Live Wire Feed"
])

df_mil = get_wb_data('MS.MIL.XPND.GD.ZS', selected_year)

# Professional dark styling matrix for Plotly
stealth_plotly_layout = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "margin": dict(l=8, r=8, t=40, b=8),
    "font": {"family": "monospace", "size": 11, "color": "#9CA3AF"}
}

# ==========================================
# TAB 1: DEFENSE BUDGET METRICS & SPATIAL MAPS
# ==========================================
with tab1:
    if isinstance(df_mil, pd.DataFrame) and not df_mil.empty:
        top_country = df_mil.sort_values(by='Value', ascending=False).iloc[0]
        global_mean = df_mil['Value'].mean()
        
        # Operational Info Blocks array
        m_col1, m_col2, m_col3 = st.columns([1, 1, 1])
        with m_col1:
            st.markdown(f"""<div class="tactical-card">
                <div class="metric-title">MAX ALLOCATION</div>
                <div class="metric-value">{top_country['Value']:.2f}%</div>
                <div style="color:#E5E7EB; font-size:12px; margin-top:4px; font-weight:600;">{top_country['name']}</div>
            </div>""", unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"""<div class="tactical-card" style="border-left-color: #10B981 !important;">
                <div class="metric-title">SYSTEM MEAN</div>
                <div class="metric-value">{global_mean:.2f}%</div>
                <div style="color:#E5E7EB; font-size:12px; margin-top:4px; font-weight:600;">Global Baseline GDP</div>
            </div>""", unsafe_allow_html=True)
        with m_col3:
            st.markdown(f"""<div class="tactical-card" style="border-left-color: #06B6D4 !important;">
                <div class="metric-title">NODES CAPTURED</div>
                <div class="metric-value">{len(df_mil)}</div>
                <div style="color:#E5E7EB; font-size:12px; margin-top:4px; font-weight:600;">Verified Sovereignties</div>
            </div>""", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # High contrast tactical orange map scale
        fig_map = px.choropleth(df_mil, locations="name", locationmode="country names",
                                color="Value", hover_name="name",
                                color_continuous_scale=px.colors.sequential.Sunsetdark)
        fig_map.update_layout(**stealth_plotly_layout)
        fig_map.update_layout(height=340, geo=dict(bgcolor='rgba(0,0,0,0)', showframe=False))
        st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
        
        # NEW FEATURE ADDED: Regional Distribution Donut Chart
        st.markdown("### 🍩 Continental Allocation Share")
        df_region = df_mil.groupby('region')['Value'].mean().reset_index()
        fig_donut = px.pie(df_region, values='Value', names='region', hole=0.4,
                           color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_donut.update_layout(**stealth_plotly_layout)
        fig_donut.update_layout(height=300)
        st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("No reporting entities found.")

# ==========================================
# TAB 2: PROCUREMENT CHANNELS
# ==========================================
with tab2:
    df_arms = get_wb_data('MS.MIL.MPRT.KD', selected_year)
    if isinstance(df_arms, pd.DataFrame) and not df_arms.empty:
        df_arms_top10 = df_arms.sort_values(by='Value', ascending=False).head(10)
        fig_arms = px.bar(df_arms_top10, x='Value', y='name', color='Value', orientation='h',
                          color_continuous_scale=px.colors.sequential.Onyx,
                          labels={'Value': 'Import Volume (Constant USD)', 'name': ''})
        fig_arms.update_layout(**stealth_plotly_layout)
        fig_arms.update_layout(height=360, coloraxis_showscale=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_arms, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("No arms trade records mapped.")

# ==========================================
# TAB 3: AI TREND FORECASTING MATRIX (UPGRADED LOGIC)
# ==========================================
with tab3:
    if isinstance(df_mil, pd.DataFrame) and not df_mil.empty:
        all_countries = sorted(df_mil['name'].unique())
    else:
        all_countries = ["India", "United States", "China"]
        
    c1, c2 = st.columns(2)
    with c1:
        country_a = st.selectbox("Select Target Nation Alpha:", all_countries, index=0)
    with c2:
        country_b = st.selectbox("Select Target Nation Beta:", all_countries, index=min(1, len(all_countries)-1))
        
    if country_a and country_b:
        try:
            hist_series = wb.get_series('MS.MIL.XPND.GD.ZS', id_or_value='value')
            hist_df = pd.DataFrame(hist_series).reset_index()
            h_val = hist_df.columns[-1]
            h_c = hist_df.columns[0]
            
            df_comp = hist_df[hist_df[h_c].isin([country_a, country_b])].dropna()
            df_comp = df_comp.rename(columns={h_val: 'Spend', 'date': 'Year'})
            df_comp['Year'] = df_comp['Year'].astype(int)
            # Filter to modern timeframe for cleaner polynomial accuracy
            df_comp = df_comp[df_comp['Year'] >= 2005]
            
            forecast_data = []
            for country in [country_a, country_b]:
                c_df = df_comp[df_comp[h_c] == country].sort_values('Year')
                if len(c_df) > 4:
                    X = c_df['Year'].values
                    y = c_df['Spend'].values
                    
                    # UPGRADED LOGIC: Polynomial Fit (Degree 2) to capture variance curves instead of flat lines
                    poly_coefficients = np.polyfit(X, y, 2)
                    poly_model = np.poly1d(poly_coefficients)
                    
                    for idx, row in c_df.iterrows():
                        forecast_data.append({'Year': row['Year'], 'Spend': row['Spend'], 'Country': country, 'Type': 'Historical'})
                    
                    # Dynamic curve plotting through 2030
                    for future_year in range(2023, 2031):
                        pred_val = max(0.05, poly_model(future_year))
                        forecast_data.append({'Year': future_year, 'Spend': pred_val, 'Country': country, 'Type': 'AI Curved Forecast'})
            
            if forecast_data:
                df_forecast = pd.DataFrame(forecast_data)
                # Tactical Gold vs Clean Mint Green tracking lines
                fig_trend = px.line(df_forecast, x='Year', y='Spend', color='Country', line_dash='Type',
                                    color_discrete_sequence=['#F59E0B', '#10B981'],
                                    labels={'Spend': 'Allocation Volume (% GDP)'})
                fig_trend.update_layout(**stealth_plotly_layout)
                fig_trend.update_layout(height=360, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
                st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
        except Exception as e:
            st.error(f"Prediction matrix processing fault: {e}")

# ==========================================
# TAB 4: POLICY DILEMMAS
# ==========================================
with tab4:
    df_edu = get_wb_data('SE.XPD.TOTL.GB.ZS', selected_year)
    if isinstance(df_mil, pd.DataFrame) and not df_mil.empty and isinstance(df_edu, pd.DataFrame) and not df_edu.empty:
        df_tradeoff = pd.merge(df_mil[['name', 'Value', 'region']], df_edu[['name', 'Value']], on='name', suffixes=('_Mil', '_Edu'))
        df_tradeoff = df_tradeoff.rename(columns={'Value_Mil': 'Military Burden (% GDP)', 'Value_Edu': 'Education Investment (% Budget)'})
        
        fig_scatter = px.scatter(df_tradeoff, x='Military Burden (% GDP)', y='Education Investment (% Budget)',
                                 color='region', hover_name='name', size='Military Burden (% GDP)', size_max=12,
                                 color_discrete_sequence=px.colors.qualitative.Set2)
        fig_scatter.update_layout(**stealth_plotly_layout)
        fig_scatter.update_layout(height=380)
        st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("Insufficient overlapping records registered.")

# ==========================================
# TAB 5: LIVE WIRE FEED TERMINAL
# ==========================================
with tab5:
    try:
        url = "https://feeds.bbci.co.uk/news/world/rss.xml"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        root = ET.fromstring(response.read())
        
        count = 0
        for item in root.findall('.//item'):
            if count >= 6: break
            title = item.find('title').text
            link = item.find('link').text
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else "Recent Updates"
            desc = item.find('description').text if item.find('description') is not None else ""
            clean_date = " ".join(pub_date.split()[:4]) if pub_date else "Recent"
            
            st.markdown(f"""
                <div class="wire-card">
                    <div class="wire-title">⌧ {title}</div>
                    <div class="wire-desc">{desc}</div>
                    <div style="display: flex; justify-content: space-between; font-size: 11px; margin-top: 10px; color: #6B7280; font-family: monospace;">
                        <span>TIMESTAMP: {clean_date}</span>
                        <a href="{link}" target="_blank" style="color: #F59E0B; text-decoration: none; font-weight: bold;">OPEN DATA LOG →</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            count += 1
    except Exception:
        st.info("Dynamic news terminal pipeline offline.")