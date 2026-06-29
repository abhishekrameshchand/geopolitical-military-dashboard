import pandas as pd
import world_bank_data as wb
import plotly.express as px
import streamlit as st

# 1. Streamlit screen par Title aur Loading message set karna
st.title("Geopolitical & Military Dashboard")
status_text = st.empty()
status_text.write("🔄 World Bank se live data fetch ho raha hai... Isme thoda samay lag sakta hai.")

# 2. World Bank se military expenditure ka data lena (2022 ka data)
mil_series = wb.get_series('MS.MIL.XPND.GD.ZS', date='2022', id_or_value='value')
mil_gdp = mil_series.reset_index()

# 3. Last column ka naam badal kar 'Military_Share_of_GDP' rakhna
value_col = mil_gdp.columns[-1]
mil_gdp = mil_gdp.rename(columns={value_col: 'Military_Share_of_GDP'})

# 4. Deshon ki list aur unke regions load karna
countries = wb.get_countries().reset_index()

# 5. Automatically dhundhna ki kis column me deshon ke naam hain
match_col = None
for col in mil_gdp.columns:
    if str(col).lower() in ['country', 'name']:
        match_col = col
        break

if not match_col:
    match_col = mil_gdp.columns[0]

# 6. Data ko merge aur clean karna
df = pd.merge(countries[['region', 'name']], mil_gdp, left_on='name', right_on=match_col)
df = df.dropna(subset=['Military_Share_of_GDP'])
df = df[df['region'] != 'Aggregates']

# Mobile view ke liye Top 10 deshon ko nikalna (taaki screen par fit aaye)
df_top10 = df.sort_values(by='Military_Share_of_GDP', ascending=False).head(10)

# Loading message ko screen se hatana
status_text.empty()

# 7. Interactive Bar Chart banana
fig = px.bar(df_top10, 
             x='Military_Share_of_GDP', 
             y='name', 
             color='region',
             orientation='h',
             title='Top 10 Countries by Military Expenditure (% of GDP) in 2022',
             labels={'Military_Share_of_GDP': 'Military Spend (% of GDP)', 'name': 'Country'})

# 8. Layout ko Mobile aur Desktop dono ke liye responsive banana
fig.update_layout(
    yaxis={'categoryorder':'total ascending'},
    height=450,  # Mobile screens ke liye perfect height
    margin=dict(l=10, r=10, t=40, b=10),  # Side margins kam kiye taaki phone par katna band ho
    legend=dict(
        orientation="h",  # Regions ke naam graph ke niche horizontal layout me aayenge
        yanchor="bottom",
        y=-0.4,
        xanchor="center",
        x=0.5
    )
)

# 9. Dashboard par graph show karna
st.plotly_chart(fig, use_container_width=True)