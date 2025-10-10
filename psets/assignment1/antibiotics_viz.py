import pandas as pd
import altair as alt
import os


df = pd.read_csv("data/antibiotics-1.csv")
df.columns = (df.columns
              .str.strip()
              .str.replace(r'[\s\-]+', '_', regex=True)
              .str.replace('[^0-9a-zA-Z_]', '', regex=True)
              .str.lower())

long = df.melt(
    id_vars=["bacteria", "gram_staining"],
    value_vars=["penicilin", "streptomycin", "neomycin"],
    var_name="antibiotic",
    value_name="mic"
).dropna(subset=["mic"])


long["mic"] = pd.to_numeric(long["mic"], errors="coerce")
long = long[long["mic"] > 0]

# Order antibiotics by median MIC
antibiotic_order = (long.groupby("antibiotic")["mic"]
                    .median()
                    .sort_values()
                    .index
                    .tolist())

y_axis = alt.Y(
    "mic:Q",
    title="Minimum Inhibitory Concentration (MIC)",
    scale=alt.Scale(type="log", domain=[1e-3, 1e3]),
    axis=alt.Axis(values=[1e-3, 1e-2, 1e-1, 1, 10, 100, 1000],
                  format=".1e",  # or "e" for scientific notation
                  )
)

points = (
    alt.Chart(long)
    .transform_calculate(jitter="(random()-0.5)*8")
    .mark_circle(size=20, opacity=0.2)
    .encode(
        x=alt.X("antibiotic:N", sort=antibiotic_order, title="Antibiotic"),
        xOffset=alt.X("gram_staining:N", title=None),
        y=y_axis,
        color=alt.Color("gram_staining:N", title="Gram Stain"),
        tooltip=["bacteria", "antibiotic", "mic", "gram_staining"]
    )
)

boxes = (
    alt.Chart(long)
    .mark_boxplot(size=30)
    .encode(
        x=alt.X("antibiotic:N", sort=antibiotic_order, title="Antibiotic"),
        xOffset=alt.X("gram_staining:N", title=None),
        y=y_axis,
        color=alt.Color("gram_staining:N", title="Gram Stain")
    )
)


final_chart = (points + boxes).properties(
    width=500,
    height=350,
    title="MIC by Antibiotic and Gram Stain (log scale)"
).configure_axis(
    grid=True,
    gridColor='lightgray',
    gridOpacity=0.3
).configure_view(
    strokeWidth=0
)

final_chart.save("antibiotics_single_chart.svg")
os.system("rsvg-convert -f pdf -o antibiotics_single_chart.pdf antibiotics_single_chart.svg")