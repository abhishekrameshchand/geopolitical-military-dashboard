import pandas as pd
import world_bank_data as wb
import plotly.express as px

print("World Bank se live data fetch ho raha hai... Isme thoda samay lag sakta hai.")

# 1. World Bank se military expenditure ka data lena
mil_series = wb.get_series('MS.MIL.XPND.GD.ZS', date='2022', id_or_value='value')
mil_gdp = mil_series.reset_index()

# Debugging ke liye terminal me columns print karte hain
print("Humne mil_gdp me ye columns paye:", list(mil_gdp.columns))

# 2. Sabse aakhri column ka naam badal kar 'Military_Share_of_GDP' rakhna
# Kyunki value hamesha aakhri column me hi hoti hai
value_col = mil_gdp.columns[-1]
mil_gdp = mil_gdp.rename(columns={value_col: 'Military_Share_of_GDP'})

# 3. Deshon ki list aur unke regions load karna
countries = wb.get_countries().reset_index()

# 4. Automatically dhundhna ki kis column me deshon ke naam hain
match_col = None
for col in mil_gdp.columns:
    if str(col).lower() in ['country', 'name']:
        match_col = col
        break

# Agar 'country' naam ka column nahi mila, toh pehle column ko hi use kar lenge
if not match_col:
    match_col = mil_gdp.columns[0]

print(f"Dono tables ko '{match_col}' column ke basis par merge kiya ja raha hai...")

# 5. Data ko safe tarike se merge karna
df = pd.merge(countries[['region', 'name']], mil_gdp, left_on='name', right_on=match_col)

# 6. Data clean karna (Missing values hatana)
df = df.dropna(subset=['Military_Share_of_GDP'])
df = df[df['region'] != 'Aggregates']

# Top 20 deshon ko nikalna
df_top20 = df.sort_values(by='Military_Share_of_GDP', ascending=False).head(20)

print("Data process ho gaya. Ab graph save ho raha hai...")

# 7. Interactive Bar Chart banana
fig = px.bar(df_top20, 
             x='Military_Share_of_GDP', 
             y='name', 
             color='region',
             orientation='h',
             title='Top 20 Countries by Military Expenditure (% of GDP) in 2022',
             labels={'Military_Share_of_GDP': 'Military Spend (% of GDP)', 'name': 'Country'})

fig.update_layout(yaxis={'categoryorder':'total ascending'})

# HTML file me save karna
fig.write_html("real_military_graph.html")
print("Done! 'real_military_graph.html' ab tayar hai.")