"""Browser demo for Product Review Frequency Analysis."""

from collections import Counter
from datetime import datetime
from pathlib import Path
import csv
import io

import streamlit as st


st.set_page_config(page_title="Product Review Frequency Analysis", page_icon="📊", layout="wide")

st.title("📊 Product Review Frequency Analysis")
st.caption("Student ID: 24691A3219 · Big Data Analytics · Hadoop MapReduce project demo")
st.info(
    "This dashboard demonstrates the same review-frequency measures as the Hadoop job. "
    "The browser demo processes the selected CSV in the app; the Hadoop Streaming mapper "
    "and reducer remain the distributed batch implementation."
)

uploaded = st.file_uploader("Upload a review CSV", type=["csv"])
if uploaded is None:
    sample_path = Path(__file__).parent / "data" / "sample_reviews.csv"
    raw_text = sample_path.read_text(encoding="utf-8-sig")
    st.caption("Showing the included sample dataset. Upload your own CSV to analyze it.")
else:
    raw_text = uploaded.getvalue().decode("utf-8-sig")

required = {"review_id", "product_id", "category", "review_date", "rating"}
reader = csv.DictReader(io.StringIO(raw_text))
headers = {name.strip() for name in (reader.fieldnames or [])}
if not required.issubset(headers):
    st.error("CSV needs these columns: review_id, product_id, category, review_date, rating")
    st.stop()

date_formats = ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%d-%m-%Y")
counts = {"Month": Counter(), "Product": Counter(), "Category": Counter()}
valid_rows = 0
invalid_rows = 0

for row in reader:
    product = (row.get("product_id") or "").strip()
    category = (row.get("category") or "").strip()
    date_text = (row.get("review_date") or "").strip()
    parsed_date = None
    for date_format in date_formats:
        try:
            parsed_date = datetime.strptime(date_text, date_format)
            break
        except ValueError:
            continue
    if not product or not category or parsed_date is None:
        invalid_rows += 1
        continue
    valid_rows += 1
    counts["Month"][parsed_date.strftime("%Y-%m")] += 1
    counts["Product"][product] += 1
    counts["Category"][category] += 1

if valid_rows == 0:
    st.warning("No valid review rows found. Check product_id, category, and review_date values.")
    st.stop()

left, middle, right = st.columns(3)
left.metric("Valid reviews", valid_rows)
middle.metric("Products", len(counts["Product"]))
right.metric("Categories", len(counts["Category"]))
if invalid_rows:
    st.warning(f"Skipped {invalid_rows} row(s) with missing fields or unrecognized dates.")

tab_month, tab_product, tab_category, tab_table = st.tabs(
    ["By month", "By product", "By category", "All counts"]
)
for tab, dimension in (
    (tab_month, "Month"),
    (tab_product, "Product"),
    (tab_category, "Category"),
):
    with tab:
        st.subheader(f"Review count by {dimension.lower()}")
        chart_data = {
            "Group": list(counts[dimension].keys()),
            "Reviews": list(counts[dimension].values()),
        }
        st.bar_chart(chart_data, x="Group", y="Reviews")
        st.dataframe(
            [{"Group": group, "Review count": count} for group, count in counts[dimension].most_common()],
            hide_index=True,
            use_container_width=True,
        )

with tab_table:
    rows = [
        {"Dimension": dimension.upper(), "Group": group, "Review count": count}
        for dimension, groups in counts.items()
        for group, count in sorted(groups.items())
    ]
    st.dataframe(rows, hide_index=True, use_container_width=True)
    st.download_button(
        "Download frequency results as CSV",
        data="dimension,group,review_count\n" + "\n".join(
            f'{row["Dimension"]},{row["Group"]},{row["Review count"]}' for row in rows
        ),
        file_name="review_frequency_results.csv",
        mime="text/csv",
    )

st.markdown("---")
st.subheader("How the Big Data workflow works")
st.markdown(
    "1. **HDFS** stores the CSV input.  2. The **Mapper** emits a count of 1 for each "
    "month, product, and category.  3. Hadoop groups matching keys.  4. The **Reducer** "
    "adds the counts.  5. Hadoop writes the aggregate output back to HDFS."
)
st.caption("The sample file is for demonstration. Use an appropriate Hadoop cluster for large datasets.")
