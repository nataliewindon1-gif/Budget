"""Spending tracker web app.

Run with: streamlit run app.py
Then open the URL it prints (usually http://localhost:8501) in your browser.
"""
import io

import pandas as pd
import streamlit as st

from core import CATEGORIES, load_rules, parse_rows, summarize
import csv

st.set_page_config(page_title="Spending Tracker", page_icon="💰")
st.title("💰 Spending Tracker")

uploaded = st.file_uploader("Upload your Capital One CSV export", type="csv")

if not uploaded:
    st.info("Upload a CSV export from Capital One to see your spending summary.")
    st.stop()

categories, tags = load_rules()
text = io.TextIOWrapper(uploaded, encoding="utf-8-sig")
transactions = parse_rows(csv.DictReader(text))
months = summarize(transactions, categories, tags)

if not months:
    st.warning("No transactions found in that file.")
    st.stop()

month_keys = sorted(months.keys(), reverse=True)
selected = st.selectbox("Month", month_keys)
m = months[selected]

col1, col2, col3 = st.columns(3)
col1.metric("Money in", f"${m['money_in']:,.2f}")
col2.metric("Money out", f"${m['money_out']:,.2f}")
col3.metric("Net", f"${m['money_in'] - m['money_out']:,.2f}")

st.subheader("By category")
cat_df = pd.DataFrame({
    "Category": CATEGORIES,
    "Amount": [m["categories"].get(c, 0.0) for c in CATEGORIES],
}).set_index("Category")
st.bar_chart(cat_df)
st.dataframe(cat_df.style.format("${:,.2f}"), use_container_width=True)

if m["tags"]:
    st.subheader("Tags")
    st.caption("Sub-labels within the categories above — don't add to the totals twice.")
    tag_df = pd.DataFrame(
        sorted(m["tags"].items(), key=lambda x: -x[1]),
        columns=["Tag", "Amount"],
    ).set_index("Tag")
    st.dataframe(tag_df.style.format("${:,.2f}"), use_container_width=True)

if m["defaulted"]:
    st.subheader("Landed in Spending/Misc (no rule match)")
    st.caption("Add a keyword to rules.json if any of these should move to a different category.")
    defaulted_df = pd.DataFrame(
        sorted(m["defaulted"], key=lambda x: -x[1]),
        columns=["Description", "Amount"],
    )
    st.dataframe(
        defaulted_df.style.format({"Amount": "${:,.2f}"}),
        use_container_width=True,
        hide_index=True,
    )
