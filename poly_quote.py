import streamlit as st
from fpdf import FPDF
from io import BytesIO
from datetime import datetime
import requests
from PIL import Image
import os

# Services list: name and price ex GST
services = [
    ("Animated Artwork Development", 4270),
    ("Animating Artwork Only", 2074),
    ("Static Artwork Development", 3538),
    ("Animated Resizing (Different Orientation)", 854),
    ("Animated Resizing (Same Orientation)", 732),
    ("Static Resizes (Same Orientation)", 306),
    ("Static Resizes (Different Orientation)", 408),
]

st.set_page_config(page_title="POLY Creative Quote", layout="wide")

# Title and header with logo and date
col1, col2 = st.columns([1, 3])
with col1:
    st.image(
        "https://lh5.googleusercontent.com/proxy/IbV2YLQngNX15Du4cR7kJMTJqw4FxFAyEEXqajLlHPXjqMvFVtCQhcOeBvyO0x1UjlKWD6i8YmOBZO8xqqj2algzalD_zN-IOlFlvf2e-gNspwRv18uRwybHDRI",
        width=120,
    )
with col2:
    st.markdown(f"**Date:** {datetime.now().strftime('%A, %d %B %Y')}")
    st.markdown("**Quote #:** 275")

st.markdown("---")

# Input fields
sales_rep = st.text_input("Sales Rep Name")
poly_rep = st.selectbox("POLY Rep Name", ["Ella Trengove", "Lee Wallwork"])
campaign = st.text_input("Client & Campaign Name")
discount_percent = st.number_input("Discount % (off total)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
notes_input = st.text_area("Notes")

st.markdown("---")

# Session state to store services table
if "service_rows" not in st.session_state:
    st.session_state.service_rows = []

def add_service():
    st.session_state.service_rows.append({"service": services[0][0], "price": services[0][1], "qty": 1})

def remove_service(idx):
    st.session_state.service_rows.pop(idx)

# Add service button
if st.button("Add Service"):
    add_service()

# Services table editing
for i, row in enumerate(st.session_state.service_rows):
    cols = st.columns([4, 2, 2, 1])
    with cols[0]:
        service_name = st.selectbox(
            f"Service {i+1}",
            [s[0] for s in services],
            index=[s[0] for s in services].index(row["service"]),
            key=f"service_{i}"
        )
    with cols[1]:
        price = dict(services)[service_name]
        st.write(f"${price:,.2f}")
    with cols[2]:
        qty = st.number_input(f"Qty {i+1}", min_value=0, value=row["qty"], step=1, key=f"qty_{i}")
    with cols[3]:
        if st.button("Remove", key=f"remove_{i}"):
            remove_service(i)
            st.experimental_rerun()

    # Update values in session state
    st.session_state.service_rows[i]["service"] = service_name
    st.session_state.service_rows[i]["price"] = price
    st.session_state.service_rows[i]["qty"] = qty

# Calculate totals
subtotal = sum(row["price"] * row["qty"] for row in st.session_state.service_rows)
discount_amount = subtotal * (discount_percent / 100)
total = subtotal - discount_amount

st.markdown("---")
st.write(f"**Subtotal:** ${subtotal:,.2f}")
st.write(f"**Discount:** -${discount_amount:,.2f}")
st.write(f"**Total (ex GST):** ${total:,.2f}")

# PDF generation
def create_pdf():
    pdf = FPDF()
    pdf.add_page()

    # Register fonts
    pdf.add_font("CenturyGothic", "", "GOTHIC.TTF", uni=True)
    pdf.add_font("CenturyGothic", "B", "GOTHICB.TTF", uni=True)

    # POLY logo (top right)
    logo_url = "https://lh5.googleusercontent.com/proxy/IbV2YLQngNX15Du4cR7kJMTJqw4FxFAyEEXqajLlHPXjqMvFVtCQhcOeBvyO0x1UjlKWD6i8YmOBZO8xqqj2algzalD_zN-IOlFlvf2e-gNspwRv18uRwybHDRI"
    response = requests.get(logo_url)
    img = Image.open(BytesIO(response.content))
    img_path = "/tmp/poly_logo.png"
    img.save(img_path)
    pdf.image(img_path, x=160, y=8, w=30)

    pdf.set_xy(10, 15)
    pdf.set_font("CenturyGothic", "B", 14)
    pdf.cell(0, 10, "POLY Creative Quote", ln=True)

    pdf.set_font("CenturyGothic", "", 10)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%A, %d %B %Y')}", ln=True)
    pdf.cell(0, 8, "Quote #: 275", ln=True)
    pdf.ln(5)
    pdf.cell(0, 8, f"Sales Rep: {sales_rep}", ln=True)
    pdf.cell(0, 8, f"POLY Rep: {poly_rep}", ln=True)
    pdf.cell(0, 8, f"Client & Campaign: {campaign}", ln=True)
    pdf.ln(8)

    # Table header
    pdf.set_font("CenturyGothic", "B", 10)
    pdf.cell(90, 8, "Service", border=0)
    pdf.cell(30, 8, "Unit Price", border=0, align="R")
    pdf.cell(20, 8, "Qty", border=0, align="R")
    pdf.cell(40, 8, "Line Total", border=0, align="R")
    pdf.ln()

    # Table rows
    pdf.set_font("CenturyGothic", "", 10)
    for row in st.session_state.service_rows:
        line_total = row["price"] * row["qty"]
        pdf.cell(90, 8, row["service"], border=0)
        pdf.cell(30, 8, f"${row['price']:,.2f}", border=0, align="R")
        pdf.cell(20, 8, str(row["qty"]), border=0, align="R")
        pdf.cell(40, 8, f"${line_total:,.2f}", border=0, align="R")
        pdf.ln()

    pdf.ln(4)

    # Totals
    pdf.cell(140, 8, "Subtotal", border=0)
    pdf.cell(40, 8, f"${subtotal:,.2f}", border=0, align="R")
    pdf.ln()
    pdf.cell(140, 8, "Discount", border=0)
    pdf.cell(40, 8, f"-${discount_amount:,.2f}", border=0, align="R")
    pdf.ln()
    pdf.cell(140, 8, "Total (ex GST)", border=0)
    pdf.cell(40, 8, f"${total:,.2f}", border=0, align="R")
    pdf.ln(10)

    # Notes
    pdf.set_font("CenturyGothic", "I", 10)
    pdf.multi_cell(0, 8, f"Notes:\n{notes_input if notes_input else ' '}", border=0)

    # Output PDF
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_bytes)

if st.button("Download PDF"):
    if not st.session_state.service_rows:
        st.warning("Please add at least one service before downloading.")
    else:
        pdf_data = create_pdf()
        st.download_button(
            label="Download POLY Quote PDF",
            data=pdf_data,
            file_name="POLY_Quote.pdf",
            mime="application/pdf"
        )
