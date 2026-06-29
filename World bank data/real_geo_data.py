import pandas as pd
import world_bank_data as wb
import plotly.express as px
import streamlit as st
import urllib.request
import xml.etree.ElementTree as ET
import numpy as np

# System Configuration
st.set_page_config(
    page_title="Command Center", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- OBSIDIAN & CRIMSON RED (MILITARY COMMAND) STYLING ---
st.markdown("""
    <style>
    /* Matte Obsidian Background (Zinc 950) */
    [data-testid="stAppViewContainer"], .main {
        background-color: #09090B !important;
        color: #FAFAFA !important;
    }
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* Sleek Tab Navigation */
    button[data-baseweb="tab"] {
        color: #A1A1AA !important;
        background-color: transparent !important;
        border: none !important;
        padding: 12px 24px !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #E11D48 !important; /* Crimson Red */
        background-color: #18181B !important;
        border-bottom: 2px solid #E11D48 !important;
    }
    
    /* Gunmetal Metric Cards */
    .metric-card {
        background: #18181B !important; /* Zinc 900 */
        border: 1px solid #27272A !important; /* Zinc 800 */
        border-left: 4px solid #E11D48 !important; /* Crimson Accent */
        border-radius: 6px;
        padding: 24px;
        margin-bottom: 16px;
    }
    
    .metric-title {
        color: #A1A1AA;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        font-weight: 600;
    }
    .metric-value {
        color: #FAFAFA;
        font-size: 38px;
        font-weight: 700;
        margin-top: 4px;
        font-family: 'Courier New', Courier, monospace;
    }
    .metric-subtitle {
        color: #71717A;
        font-size: 12px;
        margin-top: 4px;
        font-weight: 500;
    }
    
    /* Top Header Panel */
    .app-header {
        background: #18181B;
        border-bottom: 1px solid #27272A;
        padding: 24px 32px;
        margin: -40px -32px 24px -32px;
    }
    
    /* News Wire Cards */
    .wire-card {
        background: #18181B;
        border: 1px solid #27272A;
        border-radius: 6px;
        padding: 20px;
        margin-bottom: 12px;
        transition: border-color 0.2s ease;
    }
    .wire-card:hover {
        border-color: #E11D48;
    }
    .wire-title {
        color: #FAFAFA;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .wire-desc {
        color: #A1A1AA;
        font-size: 14px;
        line-height: 1.5;
    }
    </style>
""", unsafe_allow_html=True)

# Main Header
st.markdown("""
    <div class="app-header">
        <h1 style="color:#FAFAFA; margin:0; font-size:24px; font-weight:700; letter-spacing:0.05em; text-transform:uppercase;">
            <span style="color:#E11D48;">♦</span> Strategic Command Interface
        </h1>
        <p style="color:#A1A1AA; margin:4px 0 0 24px; font-size:13px; font-family:monospace;">GLOBAL DEFENSE & MACRO-ECONOMIC TELEMETRY</p>
    </div>
""", unsafe_allow_html=True)

# --- CACHED DATA FETCHING ---
@st.cache_data
def get_wb_data(indicator, year):
    try:
        series = wb.get_series(indicator, date=str(year), id_or_value='value')
        df_raw = pd.DataFrame(series).reset_index()
        if df_raw.empty: return pd.DataFrame()
        val_col = df_raw.columns[-1]
        df_raw = df_raw.rename(columns={val_col: 'Value'})
        countries = pd.DataFrame(wb.get_countries()).reset_index()
        
        match_col = None
        for col in df_raw.columns:
            if str(col).lower() in ['country', 'name']:
                match_col = col; break
        if not match_col: match_col = df_raw.columns[0]
            
        merged = pd.merge(countries[['region', 'name']], df_raw, left_on='name', right_on=match_col)
        merged = merged.dropna(subset=['Value'])
        merged = merged[merged['region'] != 'Aggregates']
        return merged
    except:
        return pd.DataFrame()

# Sidebar Configuration Layout
st.sidebar.markdown("### 🎛️ PARAMETERS")
selected_year = st.sidebar.slider("Fiscal Year:", min_value=1990, max_value=2022, value=2022)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Global Allocation", 
    "Procurement", 
    "AI Projections", 
    "Risk Matrix",
    "Live Feed"
])

df_mil = get_wb_data('MS.MIL.XPND.GD.ZS', selected_year)

# Ultra-clean plotting style
command_plotly_layout = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "margin": dict(l=0, r=0, t=30, b=0),
    "font": {"family": "sans-serif", "size": 12, "color": "#A1A1AA"}
}

# ==========================================
# TAB 1: DEFENSE BUDGET METRICS & MAP
# ==========================================
with tab1:
    if isinstance(df_mil, pd.DataFrame) and not df_mil.empty:
        top_country = df_mil.sort_values(by='Value', ascending=False).iloc[0]
        global_mean = df_mil['Value'].mean()
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-title">Primary Spender</div>
                <div class="metric-value">{top_country['Value']:.2f}%</div>
                <div class="metric-subtitle">{top_country['name']}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="metric-card" style="border-left-color: #3F3F46 !important;">
                <div class="metric-title">System Average</div>
                <div class="metric-value">{global_mean:.2f}%</div>
                <div class="metric-subtitle">Global Mean GDP</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="metric-card" style="border-left-color: #3F3F46 !important;">
                <div class="metric-title">Active Nodes</div>
                <div class="metric-value">{len(df_mil)}</div>
                <div class="metric-subtitle">Nations Tracked</div>
            </div>""", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Red heatmap style for military theme
        fig_map = px.choropleth(df_mil, locations="name", locationmode="country names",
                                color="Value", hover_name="name",
                                color_continuous_scale=px.colors.sequential.Reds)
        fig_map.update_layout(**command_plotly_layout)
        fig_map.update_layout(height=400, geo=dict(bgcolor='rgba(0,0,0,0)', showframe=False))
        st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
        
    else:
        st.warning("No data found.")

# ==========================================
# TAB 2: PROCUREMENT CHANNELS
# ==========================================
with tab2:
    df_arms = get_wb_data('MS.MIL.MPRT.KD', selected_year)
    if isinstance(df_arms, pd.DataFrame) and not df_arms.empty:
        df_arms_top10 = df_arms.sort_values(by='Value', ascending=False).head(10)
        fig_arms = px.bar(df_arms_top10, x='Value', y='name', orientation='h',
                          color_discrete_sequence=['#E11D48'],
                          labels={'Value': 'Import Volume', 'name': ''})
        fig_arms.update_layout(**command_plotly_layout)
        fig_arms.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10), yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_arms, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("No arms trade records mapped.")

# ==========================================
# TAB 3: AI TREND FORECASTING MATRIX
# ==========================================
with tab3:
    if isinstance(df_mil, pd.DataFrame) and not df_mil.empty:
        all_countries = sorted(df_mil['name'].unique())
    else:
        all_countries = ["India", "United States", "China"]
        
    col_a, col_b = st.columns(2)
    with col_a:
        country_a = st.selectbox("Entity 1:", all_countries, index=0)
    with col_b:
        country_b = st.selectbox("Entity 2:", all_countries, index=min(1, len(all_countries)-1))
        
    if country_a and country_b:
        try:
            hist_series = wb.get_series('MS.MIL.XPND.GD.ZS', id_or_value='value')
            hist_df = pd.DataFrame(hist_series).reset_index()
            h_val = hist_df.columns[-1]
            h_c = hist_df.columns[0]
            
            df_comp = hist_df[hist_df[h_c].isin([country_a, country_b])].dropna()
            df_comp = df_comp.rename(columns={h_val: 'Spend', 'date': 'Year'})
            df_comp['Year'] = df_comp['Year'].astype(int)
            df_comp = df_comp[df_comp['Year'] >= 2005]
            
            forecast_data = []
            for country in [country_a, country_b]:
                c_df = df_comp[df_comp[h_c] == country].sort_values('Year')
                if len(c_df) > 4:
                    X = c_df['Year'].values
                    y = c_df['Spend'].values
                    poly_model = np.poly1d(np.polyfit(X, y, 2))
                    
                    for idx, row in c_df.iterrows():
                        forecast_data.append({'Year': row['Year'], 'Spend': row['Spend'], 'Country': country, 'Type': 'Historic'})
                    for future_year in range(2023, 2031):
                        forecast_data.append({'Year': future_year, 'Spend': max(0.05, poly_model(future_year)), 'Country': country, 'Type': 'Forecast'})
            
            if forecast_data:
                df_forecast = pd.DataFrame(forecast_data)
                fig_trend = px.line(df_forecast, x='Year', y='Spend', color='Country', line_dash='Type',
                                    color_discrete_sequence=['#E11D48', '#71717A'],
                                    labels={'Spend': 'Allocation Volume (% GDP)'})
                fig_trend.update_layout(**command_plotly_layout)
                fig_trend.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
                st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
        except Exception as e:
            st.error(f"Error: {e}")

# ==========================================
# TAB 4: RISK MATRIX
# ==========================================
with tab4:
    df_edu = get_wb_data('SE.XPD.TOTL.GB.ZS', selected_year)
    if isinstance(df_mil, pd.DataFrame) and not df_mil.empty and isinstance(df_edu, pd.DataFrame) and not df_edu.empty:
        df_tradeoff = pd.merge(df_mil[['name', 'Value', 'region']], df_edu[['name', 'Value']], on='name', suffixes=('_Mil', '_Edu'))
        df_tradeoff = df_tradeoff.rename(columns={'Value_Mil': 'Military Burden', 'Value_Edu': 'Education Investment'})
        
        fig_scatter = px.scatter(df_tradeoff, x='Military Burden', y='Education Investment',
                                 color='region', hover_name='name', size='Military Burden', size_max=12,
                                 color_discrete_sequence=px.colors.qualitative.Set1)
        fig_scatter.update_layout(**command_plotly_layout)
        fig_scatter.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("Insufficient data.")

# ==========================================
# TAB 5: LIVE FEED
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
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else "Recent"
            desc = item.find('description').text if item.find('description') is not None else ""
            clean_date = " ".join(pub_date.split()[:4]) if pub_date else "Recent"
            
            st.markdown(f"""
                <div class="wire-card">
                    <div class="wire-title">{title}</div>
                    <div class="wire-desc">{desc}</div>
                    <div style="display: flex; justify-content: space-between; font-size: 11px; margin-top: 12px; color: #71717A;">
                        <span>{clean_date}</span>
                        <a href="{link}" target="_blank" style="color: #E11D48; text-decoration: none; font-weight: 600;">READ DISPATCH →</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            count += 1
    except Exception:
        st.info("Feed offline.")