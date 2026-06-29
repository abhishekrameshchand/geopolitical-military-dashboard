import pandas as pd
import world_bank_data as wb
import plotly.express as px
import streamlit as st
import urllib.request
import xml.etree.ElementTree as ET
import numpy as np

# Responsive page configurations
st.set_page_config(
    page_title="GeoIntel Modern Dashboard", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- MODERN COLORFUL GLASSMORPHISM STYLING ---
st.markdown("""
    <style>
    /* Deep space indigo fluid gradient background */
    [data-testid="stAppViewContainer"], .main {
        background: radial-gradient(circle at 50% 10%, #1E1B4B 0%, #090714 80%) !important;
        color: #F3F4F6 !important;
    }
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* Neon & Gradient Styled Metric Display Cards */
    .metric-card-coral {
        background: linear-gradient(135deg, rgba(254, 242, 242, 0.08) 0%, rgba(220, 38, 38, 0.05) 100%) !important;
        border: 1px solid rgba(239, 68, 68, 0.35) !important;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 12px;
        box-shadow: 0 8px 32px 0 rgba(239, 68, 68, 0.15);
    }
    .metric-card-emerald {
        background: linear-gradient(135deg, rgba(240, 253, 250, 0.08) 0%, rgba(5, 150, 105, 0.05) 100%) !important;
        border: 1px solid rgba(16, 185, 129, 0.35) !important;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 12px;
        box-shadow: 0 8px 32px 0 rgba(16, 185, 129, 0.15);
    }
    .metric-card-cyan {
        background: linear-gradient(135deg, rgba(236, 254, 255, 0.08) 0%, rgba(13, 148, 136, 0.05) 100%) !important;
        border: 1px solid rgba(6, 182, 212, 0.35) !important;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 12px;
        box-shadow: 0 8px 32px 0 rgba(6, 182, 212, 0.15);
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
        font-size: 34px;
        font-weight: 800;
        margin-top: 4px;
    }
    
    /* Sleek News Stream Blocks with Indigo Borders */
    .news-card {
        background: rgba(30, 27, 75, 0.45);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-left: 5px solid #6366F1;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .news-title {
        color: #FFFFFF;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .news-desc {
        color: #D1D5DB;
        font-size: 13px;
        line-height: 1.5;
    }
    .news-link {
        color: #818CF8;
        text-decoration: none;
        font-weight: bold;
    }
    
    /* Premium Cyber Gradient Top App Panel Bar */
    .app-header {
        background: linear-gradient(90deg, #312E81 0%, #1E1B4B 50%, #0F172A 100%);
        border: 1px solid rgba(99, 102, 241, 0.4);
        border-radius: 14px;
        padding: 28px;
        margin-bottom: 26px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    
    /* Elegant Custom Styling for Selection Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(30, 27, 75, 0.4) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        border-radius: 6px 6px 0px 0px;
        padding: 10px 20px !important;
        color: #9CA3AF !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4F46E5 !important;
        color: white !important;
        border-color: #6366F1 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="app-header">
        <h1 style="color:white; margin:0; font-size:32px; font-weight:900; letter-spacing:-0.03em; background: linear-gradient(to right, #FFFFFF, #818CF8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">⚡ GEOINTEL COMMAND OS</h1>
        <p style="color:#A5B4FC; margin:6px 0 0 0; font-size:14px; font-weight:500; letter-spacing: 0.05em;">PREMIUM MULTI-DOMAIN VISUALIZATION PLATFORM</p>
    </div>
""", unsafe_allow_html=True)

# --- CACHED DATA FETCHING ---
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

# Sidebar Control
st.sidebar.markdown("### 🎛️ Operational Settings")
selected_year = st.sidebar.slider("Timeline Control:", min_value=1990, max_value=2022, value=2022)

# --- CREATING SECTOR TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Defense Budgets", 
    "🚀 Arms Flows", 
    "⚔️ AI Trajectories", 
    "🧠 Strategic Trade-offs",
    "📰 Intel Terminal"
])

df_mil = get_wb_data('MS.MIL.XPND.GD.ZS', selected_year)

# Plotly layout optimized for colorful high contrast
vibrant_layout = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "margin": dict(l=10, r=10, t=40, b=10),
    "font": {"family": "sans-serif", "size": 12, "color": "#E5E7EB"}
}

# ==========================================
# TAB 1: DEFENSE BUDGET METRICS & MAP
# ==========================================
with tab1:
    if isinstance(df_mil, pd.DataFrame) and not df_mil.empty:
        top_country = df_mil.sort_values(by='Value', ascending=False).iloc[0]
        global_mean = df_mil['Value'].mean()
        
        m_col1, m_col2, m_col3 = st.columns([1, 1, 1])
        with m_col1:
            st.markdown(f"""<div class="metric-card-coral">
                <div class="metric-title">🔥 Peak Allocation</div>
                <div class="metric-value">{top_country['Value']:.1f}%</div>
                <div style="color:#FCA5A5; font-size:13px; font-weight:600; margin-top:4px;">{top_country['name']}</div>
            </div>""", unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"""<div class="metric-card-emerald">
                <div class="metric-title">⚡ Global Average</div>
                <div class="metric-value">{global_mean:.2f}%</div>
                <div style="color:#6EE7B7; font-size:13px; font-weight:600; margin-top:4px;">System Baseline</div>
            </div>""", unsafe_allow_html=True)
        with m_col3:
            st.markdown(f"""<div class="metric-card-cyan">
                <div class="metric-title">🌐 Active Track</div>
                <div class="metric-value">{len(df_mil)}</div>
                <div style="color:#67E8F9; font-size:13px; font-weight:600; margin-top:4px;">Sovereign Nodes</div>
            </div>""", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # High intensity neon spectrum choropleth
        fig_map = px.choropleth(df_mil, locations="name", locationmode="country names",
                                color="Value", hover_name="name",
                                color_continuous_scale=px.colors.sequential.Electric)
        fig_map.update_layout(**vibrant_layout)
        fig_map.update_layout(height=360, geo=dict(bgcolor='rgba(0,0,0,0)', showframe=False, projection_type="natural earth"))
        st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
        
        # High dynamic horizontal ranks chart
        df_top10 = df_mil.sort_values(by='Value', ascending=False).head(10)
        fig_bar = px.bar(df_top10, x='Value', y='name', color='Value', orientation='h',
                         color_continuous_scale=px.colors.sequential.Plasma,
                         labels={'Value': 'Spend (% GDP)', 'name': ''})
        fig_bar.update_layout(**vibrant_layout)
        fig_bar.update_layout(height=360, coloraxis_showscale=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("No reporting data streams available.")

# ==========================================
# TAB 2: ARMS FLOWS
# ==========================================
with tab2:
    df_arms = get_wb_data('MS.MIL.MPRT.KD', selected_year)
    if isinstance(df_arms, pd.DataFrame) and not df_arms.empty:
        df_arms_top10 = df_arms.sort_values(by='Value', ascending=False).head(10)
        fig_arms = px.bar(df_arms_top10, x='Value', y='name', color='Value', orientation='h',
                          color_continuous_scale=px.colors.sequential.Viridis,
                          labels={'Value': 'Import Capital Volume (USD)', 'name': ''})
        fig_arms.update_layout(**vibrant_layout)
        fig_arms.update_layout(height=380, coloraxis_showscale=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_arms, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("No dynamic arms procurement flows mapped.")

# ==========================================
# TAB 3: AI TRAJECTORIES
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
            df_comp = df_comp[df_comp['Year'] >= 2000]
            
            forecast_data = []
            for country in [country_a, country_b]:
                c_df = df_comp[df_comp[h_c] == country].sort_values('Year')
                if len(c_df) > 3:
                    X = c_df['Year'].values
                    y = c_df['Spend'].values
                    slope, intercept = np.polyfit(X, y, 1)
                    
                    for idx, row in c_df.iterrows():
                        forecast_data.append({'Year': row['Year'], 'Spend': row['Spend'], 'Country': country, 'Type': 'Historical'})
                    for future_year in range(2023, 2031):
                        pred_val = max(0.1, slope * future_year + intercept)
                        forecast_data.append({'Year': future_year, 'Spend': pred_val, 'Country': country, 'Type': 'AI Forecast'})
            
            if forecast_data:
                df_forecast = pd.DataFrame(forecast_data)
                # Neon Blue vs Vivid Hot Fuchsia/Pink lines
                fig_trend = px.line(df_forecast, x='Year', y='Spend', color='Country', line_dash='Type',
                                    color_discrete_sequence=['#38BDF8', '#F43F5E'],
                                    labels={'Spend': 'Allocation Volume (% GDP)'})
                fig_trend.update_layout(**vibrant_layout)
                fig_trend.update_layout(height=360, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
                st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
        except Exception as e:
            st.error(f"Prediction matrix run fault: {e}")

# ==========================================
# TAB 4: STRATEGIC TRADE-OFFS
# ==========================================
with tab4:
    df_edu = get_wb_data('SE.XPD.TOTL.GB.ZS', selected_year)
    if isinstance(df_mil, pd.DataFrame) and not df_mil.empty and isinstance(df_edu, pd.DataFrame) and not df_edu.empty:
        df_tradeoff = pd.merge(df_mil[['name', 'Value', 'region']], df_edu[['name', 'Value']], on='name', suffixes=('_Mil', '_Edu'))
        df_tradeoff = df_tradeoff.rename(columns={'Value_Mil': 'Military Burden (% GDP)', 'Value_Edu': 'Education Investment (% Budget)'})
        
        fig_scatter = px.scatter(df_tradeoff, x='Military Burden (% GDP)', y='Education Investment (% Budget)',
                                 color='region', hover_name='name', size='Military Burden (% GDP)', size_max=15,
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_scatter.update_layout(**vibrant_layout)
        fig_scatter.update_layout(height=380)
        st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("Insufficient overlapping records registered for this specific loop.")

# ==========================================
# TAB 5: REAL-TIME INTEL TERMINAL
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
                <div class="news-card">
                    <div class="news-title">🛑 {title}</div>
                    <div class="news-desc">{desc}</div>
                    <div class="news-meta" style="display: flex; justify-content: space-between; font-size: 11px; margin-top: 8px; color: #9CA3AF;">
                        <span>📅 Broadcasted: {clean_date}</span>
                        <a class="news-link" href="{link}" target="_blank">Review Full Intel →</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            count += 1
    except Exception:
        st.info("Dynamic news feeds stream offline.")