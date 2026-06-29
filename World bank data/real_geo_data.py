import pandas as pd
import world_bank_data as wb
import plotly.express as px
import streamlit as st
import urllib.request
import xml.etree.ElementTree as ET
import numpy as np

# Injecting Global CSS for CSS-Grid styling, dynamic font-scaling, and clean dark borders
st.set_page_config(
    page_title="GeoIntel Dashboard", 
    page_icon="🌍", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* Global Background and UI Polish */
    [data-testid="stAppViewContainer"] {
        background-color: #0B0F17;
        color: #F3F4F6;
    }
    [data-testid="stHeader"] {
        background: transparent;
    }
    
    /* Responsive Metric Card Containers */
    .metric-card {
        background: linear-gradient(135deg, #161D2A 0%, #111823 100%);
        border: 1px solid #243046;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        border-color: #3B82F6;
        transform: translateY(-2px);
    }
    .metric-title {
        color: #9CA3AF;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    .metric-value {
        color: #FFFFFF;
        font-size: 24px;
        font-weight: 700;
        margin-top: 4px;
    }
    .metric-delta {
        font-size: 13px;
        font-weight: 500;
        margin-top: 2px;
    }
    
    /* Modern News Stream Block Formatting */
    .news-card {
        background-color: #111723;
        border-left: 4px solid #3B82F6;
        border-radius: 0 10px 10px 0;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .news-title {
        color: #E5E7EB;
        font-size: 16px;
        font-weight: 600;
        margin: 0 0 6px 0;
        line-height: 1.4;
    }
    .news-desc {
        color: #9CA3AF;
        font-size: 13px;
        line-height: 1.5;
        margin: 0 0 10px 0;
    }
    .news-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 11px;
        color: #6B7280;
    }
    .news-link {
        color: #3B82F6;
        text-decoration: none;
        font-weight: 600;
    }
    .news-link:hover {
        text-decoration: underline;
    }
    
    /* Native App Bar Top Header Style */
    .app-header {
        background: radial-gradient(circle at top left, #1E2640 0%, #0F1424 100%);
        border: 1px solid #253154;
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 24px;
    }
    </style>
""", unsafe_allow_html=True)

# Clean, responsive application structural heading
st.markdown("""
    <div class="app-header">
        <h1 style="color:white; margin:0; font-size:28px; font-weight:800; letter-spacing:-0.025em;">GEOINTEL COMMAND</h1>
        <p style="color:#A0AEC0; margin:6px 0 0 0; font-size:14px;">Strategic Sovereign Risk Indices & Forecast Pipelines</p>
    </div>
""", unsafe_allow_html=True)

# --- CACHED COMPACT WORLD BANK RETRIEVAL DATA SYSTEM ---
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

# Sidebar Optimization
st.sidebar.markdown("### 🎛️ Operational Parameters")
selected_year = st.sidebar.slider("Timeline Horizon:", min_value=1990, max_value=2022, value=2022)

# --- MODERN STYLED COMPACT TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Defense Budgets", 
    "🚀 Arms Flow", 
    "⚔️ AI Projections", 
    "🧠 Policy Dilemmas",
    "📰 Intel Wire"
])

# Prefetch Primary Military Dataset
df_mil = get_wb_data('MS.MIL.XPND.GD.ZS', selected_year)

# Common layout parameters optimized for clean mobile viewports
mobile_plotly_layout = {
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
    if not df_mil.empty:
        top_country = df_mil.sort_values(by='Value', ascending=False).iloc[0]
        global_mean = df_mil['Value'].mean()
        
        # Grid Array rendering natively across columns
        m_col1, m_col2, m_col3 = st.columns([1, 1, 1])
        with m_col1:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-title">Peak Allocation</div>
                <div class="metric-value">{top_country['Value']:.1f}%</div>
                <div class="metric-delta" style="color:#FF4B4B;">▲ {top_country['name']}</div>
            </div>""", unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-title">Global Mean</div>
                <div class="metric-value">{global_mean:.2f}%</div>
                <div class="metric-delta" style="color:#3B82F6;">📊 System Baseline</div>
            </div>""", unsafe_allow_html=True)
        with m_col3:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-title">Nations Indexed</div>
                <div class="metric-value">{len(df_mil)}</div>
                <div class="metric-delta" style="color:#10B981;">✓ Live Verified</div>
            </div>""", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Responsive spatial choropleth chart configuration
        fig_map = px.choropleth(df_mil, locations="name", locationmode="country names",
                                color="Value", hover_name="name",
                                color_continuous_scale=px.colors.sequential.YlOrRd)
        fig_map.update_layout(**mobile_plotly_layout)
        fig_map.update_layout(height=320, geo=dict(bgcolor='rgba(0,0,0,0)', showframe=False, showcoastlines=True))
        st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
        
        # Horizontally scaled ranking bar chart configuration
        df_top10 = df_mil.sort_values(by='Value', ascending=False).head(10)
        fig_bar = px.bar(df_top10, x='Value', y='name', color='region', orientation='h',
                         labels={'Value': 'Spend (% GDP)', 'name': ''})
        fig_bar.update_layout(**mobile_plotly_layout)
        fig_bar.update_layout(height=340, showlegend=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("Database contains no reporting entities for this year's index.")

# ==========================================
# TAB 2: ARMS INTERACTION MATRIX
# ==========================================
with tab2:
    df_arms = get_wb_data('MS.MIL.MPRT.KD', selected_year)
    if not df_arms.empty:
        df_arms_top10 = df_arms.sort_values(by='Value', ascending=False).head(10)
        fig_arms = px.bar(df_arms_top10, x='Value', y='name', color='region', orientation='h',
                          labels={'Value': 'Import Capital Volume ($)', 'name': ''})
        fig_arms.update_layout(**mobile_plotly_layout)
        fig_arms.update_layout(height=360, showlegend=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_arms, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("No dynamic arms imports indices are recorded for this calendar cycle.")

# ==========================================
# TAB 3: REGRESSION FORECAST MODEL
# ==========================================
with tab3:
    all_countries = sorted(df_mil['name'].unique()) if not df_mil.empty else ["India", "United States", "China"]
    c1, c2 = st.columns(2)
    with c1:
        country_a = st.selectbox("Entity Alpha:", all_countries, index=all_countries.index("India") if "India" in all_countries else 0)
    with c2:
        country_b = st.selectbox("Entity Beta:", all_countries, index=all_countries.index("United States") if "United States" in all_countries else 1)
        
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
                                    labels={'Spend': 'Allocation Trend (% GDP)'})
                fig_trend.update_layout(**mobile_plotly_layout)
                fig_trend.update_layout(height=340, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
                st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
        except Exception as e:
            st.error(f"Algorithmic modeling run disrupted: {e}")

# ==========================================
# TAB 4: SOCIO-ECONOMIC MATRIX
# ==========================================
with tab4:
    df_edu = get_wb_data('SE.XPD.TOTL.GB.ZS', selected_year)
    if not df_mil.empty and not df_edu.empty:
        df_tradeoff = pd.merge(df_mil[['name', 'Value', 'region']], df_edu[['name', 'Value']], on='name', suffixes=('_Mil', '_Edu'))
        df_tradeoff = df_tradeoff.rename(columns={'Value_Mil': 'Military Burden (% GDP)', 'Value_Edu': 'Education Investment (% Budget)'})
        
        fig_scatter = px.scatter(df_tradeoff, x='Military Burden (% GDP)', y='Education Investment (% Budget)',
                                 color='region', hover_name='name')
        fig_scatter.update_layout(**mobile_plotly_layout)
        fig_scatter.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("Insufficient overlapping reporting indices to map data parameters.")

# ==========================================
# TAB 5: COMPACT REAL-TIME INTEL WIRE
# ==========================================
with tab5:
    try:
        url = "https://feeds.bbci.co.uk/news/world/rss.xml"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        root = ET.fromstring(response.read())
        
        count = 0
        for item in root.findall('.//item'):
            if count >= 6: 
                break
            title = item.find('title').text
            link = item.find('link').text
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else "Recent Updates"
            desc = item.find('description').text if item.find('description') is not None else ""
            
            # Formatting shorter pubDates to look clean on mobile screens
            clean_date = " ".join(pub_date.split()[:4]) if pub_date else "Recent"
            
            st.markdown(f"""
                <div class="news-card">
                    <div class="news-title">🛑 {title}</div>
                    <div class="news-desc">{desc}</div>
                    <div class="news-meta">
                        <span>📅 Broadcasted: {clean_date}</span>
                        <a class="news-link" href="{link}" target="_blank">Review Operational Intel →</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            count += 1
    except Exception:
        st.info("System failed to execute direct handshake. Security stream is offline.")