import pandas as pd
import world_bank_data as wb
import plotly.express as px
import streamlit as st
import urllib.request
import xml.etree.ElementTree as ET
import numpy as np

# Responsive page configurations
st.set_page_config(
    page_title="GeoIntel Dashboard", 
    page_icon="🌍", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CLEAN INDUSTRIAL SAAS STYLING ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main {
        background-color: #0E131F !important;
        color: #F3F4F6 !important;
    }
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    .metric-card {
        background: #161F30 !important;
        border: 1px solid #23324D !important;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    .metric-title {
        color: #9CA3AF;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
    }
    .metric-value {
        color: #FFFFFF;
        font-size: 32px;
        font-weight: 800;
        margin-top: 4px;
    }
    .metric-delta {
        font-size: 13px;
        font-weight: 600;
        margin-top: 6px;
    }
    .news-card {
        background: #161F30;
        border: 1px solid #23324D;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 14px;
    }
    .news-title {
        color: #FFFFFF;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .news-desc {
        color: #9CA3AF;
        font-size: 13px;
        line-height: 1.5;
        margin-bottom: 12px;
    }
    .news-link {
        color: #3B82F6;
        text-decoration: none;
        font-weight: bold;
        font-size: 13px;
    }
    .app-header {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 10px;
        padding: 24px;
        margin-bottom: 24px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="app-header">
        <h1 style="color:white; margin:0; font-size:28px; font-weight:800; letter-spacing:-0.02em;">🌍 GEOINTEL COMMAND</h1>
        <p style="color:#9CA3AF; margin:4px 0 0 0; font-size:14px; font-weight:400;">Strategic Sovereign Risk Indices & Forecast Pipelines</p>
    </div>
""", unsafe_allow_html=True)

# --- SAFE DATA FETCHING ENGINE ---
@st.cache_data
def get_wb_data(indicator, year):
    try:
        series = wb.get_series(indicator, date=str(year), id_or_value='value')
        df_raw = pd.DataFrame(series).reset_index()
        
        # Safe column tracking to prevent AttributeError
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

# Sidebar Setup
st.sidebar.markdown("### 🎛️ Parameters")
selected_year = st.sidebar.slider("Timeline Horizon:", min_value=1990, max_value=2022, value=2022)

# --- CREATING SECTOR TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Defense Budgets", 
    "🚀 Arms Flow", 
    "⚔️ AI Projections", 
    "🧠 Policy Dilemmas",
    "📰 Intel Wire"
])

df_mil = get_wb_data('MS.MIL.XPND.GD.ZS', selected_year)

clean_plotly_layout = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "margin": dict(l=8, r=8, t=35, b=8),
    "font": {"family": "sans-serif", "size": 11}
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
            st.markdown(f"""<div class="metric-card">
                <div class="metric-title">Peak Allocation</div>
                <div class="metric-value">{top_country['Value']:.1f}%</div>
                <div class="metric-delta" style="color:#EF4444;">▲ {top_country['name']}</div>
            </div>""", unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-title">Global Mean</div>
                <div class="metric-value">{global_mean:.2f}%</div>
                <div class="metric-delta" style="color:#10B981;">Baseline Center</div>
            </div>""", unsafe_allow_html=True)
        with m_col3:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-title">Nations Indexed</div>
                <div class="metric-value">{len(df_mil)}</div>
                <div class="metric-delta" style="color:#3B82F6;">Verified Entities</div>
            </div>""", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        fig_map = px.choropleth(df_mil, locations="name", locationmode="country names",
                                color="Value", hover_name="name",
                                color_continuous_scale=px.colors.sequential.Cividis)
        fig_map.update_layout(**clean_plotly_layout)
        fig_map.update_layout(height=340, geo=dict(bgcolor='rgba(0,0,0,0)', showframe=False))
        st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
        
        df_top10 = df_mil.sort_values(by='Value', ascending=False).head(10)
        fig_bar = px.bar(df_top10, x='Value', y='name', color='region', orientation='h',
                         color_discrete_sequence=px.colors.qualitative.Muted,
                         labels={'Value': 'Spend (% GDP)', 'name': ''})
        fig_bar.update_layout(**clean_plotly_layout)
        fig_bar.update_layout(height=340, showlegend=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("No reporting entities found.")

# ==========================================
# TAB 2: ARMS FLOW
# ==========================================
with tab2:
    df_arms = get_wb_data('MS.MIL.MPRT.KD', selected_year)
    if isinstance(df_arms, pd.DataFrame) and not df_arms.empty:
        df_arms_top10 = df_arms.sort_values(by='Value', ascending=False).head(10)
        fig_arms = px.bar(df_arms_top10, x='Value', y='name', color='region', orientation='h',
                          color_discrete_sequence=px.colors.qualitative.Muted,
                          labels={'Value': 'Import Volume ($)', 'name': ''})
        fig_arms.update_layout(**clean_plotly_layout)
        fig_arms.update_layout(height=360, showlegend=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_arms, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("No arms flow records found for this year.")

# ==========================================
# TAB 3: AI PROJECTIONS
# ==========================================
with tab3:
    if isinstance(df_mil, pd.DataFrame) and not df_mil.empty:
        all_countries = sorted(df_mil['name'].unique())
    else:
        all_countries = ["India", "United States", "China"]
        
    c1, c2 = st.columns(2)
    with c1:
        country_a = st.selectbox("Entity Alpha:", all_countries, index=0)
    with c2:
        country_b = st.selectbox("Entity Beta:", all_countries, index=min(1, len(all_countries)-1))
        
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
                fig_trend = px.line(df_forecast, x='Year', y='Spend', color='Country', line_dash='Type',
                                    color_discrete_sequence=['#3B82F6', '#EF4444'],
                                    labels={'Spend': 'Allocation Trend (% GDP)'})
                fig_trend.update_layout(**clean_plotly_layout)
                fig_trend.update_layout(height=340, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
                st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
        except Exception as e:
            st.error(f"Prediction engine fault: {e}")

# ==========================================
# TAB 4: POLICY DILEMMAS
# ==========================================
with tab4:
    df_edu = get_wb_data('SE.XPD.TOTL.GB.ZS', selected_year)
    if isinstance(df_mil, pd.DataFrame) and not df_mil.empty and isinstance(df_edu, pd.DataFrame) and not df_edu.empty:
        df_tradeoff = pd.merge(df_mil[['name', 'Value', 'region']], df_edu[['name', 'Value']], on='name', suffixes=('_Mil', '_Edu'))
        df_tradeoff = df_tradeoff.rename(columns={'Value_Mil': 'Military Burden (% GDP)', 'Value_Edu': 'Education Investment (% Budget)'})
        
        fig_scatter = px.scatter(df_tradeoff, x='Military Burden (% GDP)', y='Education Investment (% Budget)',
                                 color='region', hover_name='name')
        fig_scatter.update_layout(**clean_plotly_layout)
        fig_scatter.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("Insufficient structural records overlapping for this timeline window.")

# ==========================================
# TAB 5: INTEL WIRE
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
                    <div class="news-meta">
                        <span>📅 {clean_date}</span>
                        <a class="news-link" href="{link}" target="_blank">Review Intel →</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            count += 1
    except Exception:
        st.info("System feed is offline.")