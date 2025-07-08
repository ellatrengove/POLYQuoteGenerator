import streamlit as st
from fpdf import FPDF
from io import BytesIO
from datetime import datetime
import requests
from PIL import Image

# Services list
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

# Header
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

# Inputs
sales_rep = st.text_input("Sales Rep Name")
poly_rep = st.selectbox("POLY Rep Name", ["Ella Trengove", "Lee Wallwork"])
campaign = st.text_input("Client & Campaign Name")
discount_percent = st.number_input("Discount % (off total)", 0.0, 100.0, 0.0, step=0.1)
notes_input = st.text_area("Notes")

st.markdown("---")

# Service state
if "service_rows" not in st.session_state:
    st.session_state.service_rows = []

def add_service():
    st.session_state.service_rows.append({"service": services[0][0], "price": float(services[0][1]), "qty": 1})

def remove_service(idx):
    st.session_state.service_rows.pop(idx)

if st.button("Add Service"):
    add_service()

# Service list editing
for i, row in enumerate(st.session_state.service_rows):
    cols = st.columns([4, 2, 2, 1])
    with cols[0]:
        options = [s[0] for s in services] + ["Custom (Enter Below)"]
        selected = st.selectbox(
            f"Service {i+1}",
            options,
            index=options.index(row["service"]) if row["service"] in options else len(options) - 1,
            key=f"service_{i}"
        )

        if selected == "Custom (Enter Below)":
            custom_desc = st.text_input(f"Custom Service {i+1}", value=row.get("custom_desc", ""), key=f"custom_desc_{i}")
            custom_price = st.number_input(
                f"Custom Price {i+1}",
                min_value=0.0,
                value=float(row.get("price", 0.0)),
                step=10.0,
                key=f"custom_price_{i}"
            )
            service_name = custom_desc
            price = custom_price
        else:
            service_name = selected
            price = float(dict(services)[service_name])

    with cols[1]:
        st.write(f"${price:,.2f}")
    with cols[2]:
        qty = st.number_input(f"Qty {i+1}", min_value=0, value=row["qty"], step=1, key=f"qty_{i}")
    with cols[3]:
        if st.button("Remove", key=f"remove_{i}"):
            remove_service(i)
            st.experimental_rerun()

    st.session_state.service_rows[i]["service"] = service_name
    st.session_state.service_rows[i]["price"] = price
    st.session_state.service_rows[i]["qty"] = qty
    if selected == "Custom (Enter Below)":
        st.session_state.service_rows[i]["custom_desc"] = custom_desc

# Totals
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
    pdf.add_font("CenturyGothic", "", "GOTHIC.TTF", uni=True)
    pdf.add_font("CenturyGothic", "B", "GOTHICB.TTF", uni=True)

    logo_url = "https://lh5.googleusercontent.com/proxy/IbV2YLQngNX15Du4cR7kJMTJqw4FxFAyEEXqajLlHPXjqMvFVtCQhcOeBvyO0x1UjlKWD6i8YmOBZO8xqqj2algzalD_zN-IOlFlvf2e-gNspwRv18uRwybHDRI"
    img = Image.open(BytesIO(requests.get(logo_url).content))
    img_path = "/tmp/logo.png"
    img.save(img_path)
    pdf.image(img_path, x=10, y=8, w=40)
    pdf.image(img_path, x=160, y=8, w=30)

    pdf.set_font("CenturyGothic", "B", 14)
    pdf.ln(30)
    pdf.cell(0, 10, "POLY Creative Quote", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%A, %d %B %Y')}", ln=True)
    pdf.cell(0, 10, "Quote #: 275", ln=True)
    pdf.cell(0, 10, f"Sales Rep: {sales_rep}", ln=True)
    pdf.cell(0, 10, f"POLY Rep: {poly_rep}", ln=True)
    pdf.cell(0, 10, f"Client & Campaign: {campaign}", ln=True)
    pdf.ln(10)

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

    pdf.ln(5)
    pdf.cell(140, 8, "Subtotal", border=0)
    pdf.cell(40, 8, f"${subtotal:,.2f}", border=0, align="R")
    pdf.ln()
    pdf.cell(140, 8, "Discount", border=0)
    pdf.cell(40, 8, f"-${discount_amount:,.2f}", border=0, align="R")
    pdf.ln()
    pdf.cell(140, 8, "Total (ex GST)", border=0)
    pdf.cell(40, 8, f"${total:,.2f}", border=0, align="R")
    pdf.ln(10)

    pdf.set_font("CenturyGothic", "I", 10)
    pdf.multi_cell(0, 8, f"Notes:\n{notes_input if notes_input else ' '}", border=0)

    return BytesIO(pdf.output(dest='S').encode('latin1'))

# Download
if st.button("Download PDF"):
    if not st.session_state.service_rows:
        st.warning("Please add at least one service before downloading.")
    else:
        pdf_data = create_pdf()
        st.download_button("Download POLY Quote PDF", data=pdf_data, file_name="POLY_Quote.pdf", mime="application/pdf")
