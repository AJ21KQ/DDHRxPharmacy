import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Initialize session state for storing invoice items
if 'invoice_items' not in st.session_state:
    st.session_state.invoice_items = []

# Set up Google Sheets connection
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Pharmacy Products")
products_sheet = sheet.worksheet("Products")  # Assuming 'Products' is the name of the sheet with items
data = products_sheet.get_all_records()
df = pd.DataFrame(data)

# Ensure the price is treated as a float
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

st.title('Pharmacy Invoice Generator')

# Dropdown to select product
product_names = df['Product Name'].unique()
selected_product = st.selectbox('Select Product', product_names)

# Dropdown to select dosage based on selected product
dosages = df[df['Product Name'] == selected_product]['Dosage'].unique()
selected_dosage = st.selectbox('Select Dosage', dosages)

# Filter dataframe for selected product and dosage
filtered_df = df[(df['Product Name'] == selected_product) & (df['Dosage'] == selected_dosage)]

if not filtered_df.empty:
    manufacturer = filtered_df['Manufacturer'].iloc[0]
    price = filtered_df['Price'].iloc[0]  # Assuming price is directly in the DataFrame

    # User inputs the quantity
    quantity = st.number_input('Enter Quantity', min_value=1, value=1, step=1)

    # Calculate total
    total = price * quantity

    # Button to add to invoice
    if st.button('Add to Invoice'):
        st.session_state.invoice_items.append({
            "Product Name": selected_product,
            "Dosage": selected_dosage,
            "Manufacturer": manufacturer,
            "Quantity": quantity,
            "Price": price,
            "Total": total
        })
        st.success(f"Added {quantity} of {selected_product} ({selected_dosage}) to the invoice. Total: ₹{total}")

# Display the current invoice
if st.session_state.invoice_items:
    invoice_df = pd.DataFrame(st.session_state.invoice_items)
    st.write("Invoice Summary", invoice_df)
    grand_total = invoice_df['Total'].sum()
    st.write(f"Grand Total: ₹{grand_total}")

# Print invoice
if st.button('Print Invoice'):
    st.success('Printing to local WiFi printer... (simulated)')

