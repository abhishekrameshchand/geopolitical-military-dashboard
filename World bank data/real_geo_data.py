import pandas as pd
import world_bank_data as wb
import plotly.express as px
import streamlit as st  # <-- Streamlit ko import kiya

# Streamlit ki screen par title aur loading message dikhana
st.title("Geopolitical & Military Dashboard")
status_text = st.empty()
status_text.write("🔄 World Bank se live data fetch ho raha hai... Isme thoda samay lag sakta hai.")

# 1. Data lena
mil_series = wb.get_series('MS.MIL.XPND.GD.ZS', date='2022', id_or_value='value')
mil_gdp = mil_series.reset_index()

# 2. Column rename karna
value_col = mil_gdp.columns[-1]
mil_gdp = mil_gdp.rename(columns={value_col: 'Military_Share_of_GDP'})

# 3. Countries load karna
countries = wb.get_countries().reset_index()

# 4. Column match karna
match_col = None
for col in mil_gdp.columns:
    if str(col).lower() in ['country', 'name']:
        match_col = col
        break

if not match_col:
    match_col = mil_gdp.columns[0]

# 5. Merge karna
df = pd.merge(countries[['region', 'name']], mil_gdp, left_on='name', right_on=match_col)

# 6. Clean karna
df = df.dropna(subset=['Military_Share_of_GDP'])
df = df[df['region'] != 'Aggregates']
df_top20 = df.sort_values(by='Military_Share_of_GDP', ascending=False).head(20)

# Loading message hata kar graph dikhana
status_text.empty()

# 7. Interactive Bar Chart banana
fig = px.bar(df_top20, 
             x='Military_Share_of_GDP', 
             y='name', 
             color='region',
             orientation='h',
             title='Top 20 Countries by Military Expenditure (% of GDP) in 2022',
             labels={'Military_Share_of_GDP': 'Military Spend (% of GDP)', 'name': 'Country'})

fig.update_layout(yaxis={'categoryorder':'total ascending'})

# HTML file me save karne ke sath-sath Streamlit par graph show karna
st.plotly_chart(fig, use_container_width=True)