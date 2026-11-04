import hashlib
import json
import time
import pandas as pd
import streamlit as st

st.set_page_config(page_title="RWA Tokenization Lab", page_icon="🏢", layout="wide")

# State Initialization
if "asset" not in st.session_state:
    st.session_state.asset = {
        "name": "Asia Pacific University Block C",
        "symbol": "APUBC",
        "appraised_value": 200000.00,
        "total_supply": 200000,
        "token_price": 1.00,
        "deed_hash": hashlib.sha256(b"Deed_ID_99482_Univ_District").hexdigest()
    }

if "wallets" not in st.session_state:
    st.session_state.wallets = {
        "Issuer (Treasury)": {"balance_tokens": 200000, "cash_usd": 0.0, "kyc_verified": True},
        "Student Wallet A (Alice)": {"balance_tokens": 0, "cash_usd": 10000.0, "kyc_verified": True},
        "Student Wallet B (Bob)": {"balance_tokens": 0, "cash_usd": 5000.0, "kyc_verified": False},
        "Investor C (Charlie)": {"balance_tokens": 0, "cash_usd": 25000.0, "kyc_verified": True}
    }

if "audit_log" not in st.session_state:
    st.session_state.audit_log = []

# Header
st.title("🏢 Real World Asset (RWA) Tokenization Simulator")
st.caption("Educational sandbox showing physical asset tokenization, whitelisting, and dividend distribution.")

st.divider()

# Asset Overview
col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("1. Off-Chain Asset Registry")
    st.write(f"**Asset Name:** {st.session_state.asset['name']}")
    st.write(f"**Valuation:** ${st.session_state.asset['appraised_value']:,.2f}")
    st.write(f"**Off-Chain Deed Hash (SHA-256):** `{st.session_state.asset['deed_hash'][:16]}...`")

with col2:
    st.subheader("2. On-Chain Token Parameters")
    st.write(f"**Token Symbol:** {st.session_state.asset['symbol']}")
    st.write(f"**Total Minted Supply:** {st.session_state.asset['total_supply']:,} tokens")
    st.write(f"**Initial Price:** ${st.session_state.asset['token_price']:.2f} / token")

st.divider()

# Trading Section
st.subheader("3. Primary Market Token Purchase")
selected_user = st.selectbox("Select Wallet to Act As:", list(st.session_state.wallets.keys()))
current_user = st.session_state.wallets[selected_user]

u_col1, u_col2, u_col3 = st.columns(3)
u_col1.metric("Token Balance", f"{current_user['balance_tokens']:,} {st.session_state.asset['symbol']}")
u_col2.metric("Available USD", f"${current_user['cash_usd']:,.2f}")
u_col3.metric("KYC Status", "Verified" if current_user['kyc_verified'] else "Not Verified")

if selected_user != "Issuer (Treasury)":
    tokens_to_buy = st.number_input("Amount of Tokens to Purchase:", min_value=1, max_value=50000, value=1000)
    cost = tokens_to_buy * st.session_state.asset["token_price"]

    if st.button("Execute Token Purchase"):
        if not current_user["kyc_verified"]:
            st.error("Transaction Reverted: Address is not KYC whitelisted (RWA Compliance Constraint).")
        elif current_user["cash_usd"] < cost:
            st.error("Transaction Reverted: Insufficient USD funds.")
        elif st.session_state.wallets["Issuer (Treasury)"]["balance_tokens"] < tokens_to_buy:
            st.error("Transaction Reverted: Insufficient treasury supply.")
        else:
            current_user["cash_usd"] -= cost
            current_user["balance_tokens"] += tokens_to_buy
            st.session_state.wallets["Issuer (Treasury)"]["balance_tokens"] -= tokens_to_buy
            st.session_state.wallets["Issuer (Treasury)"]["cash_usd"] += cost

            st.session_state.audit_log.append({
                "Timestamp": time.strftime("%H:%M:%S"),
                "Action": "Token Buy",
                "Buyer": selected_user,
                "Tokens": tokens_to_buy,
                "Amount Paid ($)": cost
            })
            st.success(f"Successfully purchased {tokens_to_buy:,} tokens for ${cost:,.2f}!")
            st.rerun()

st.divider()

# Yield Distribution
st.subheader("4. Automated Rental Yield Payout")
monthly_rent = st.number_input("Simulated Monthly Rent Collected ($):", min_value=100, max_value=50000, value=2000)

if st.button("Distribute Rental Yield"):
    total_circulating = sum(w["balance_tokens"] for name, w in st.session_state.wallets.items() if name != "Issuer (Treasury)")

    if total_circulating == 0:
        st.warning("No tokens are held by investors yet.")
    else:
        for name, wallet in st.session_state.wallets.items():
            if name != "Issuer (Treasury)" and wallet["balance_tokens"] > 0:
                share = wallet["balance_tokens"] / total_circulating
                payout = monthly_rent * share
                wallet["cash_usd"] += payout

        st.session_state.audit_log.append({
            "Timestamp": time.strftime("%H:%M:%S"),
            "Action": "Yield Payout",
            "Buyer": "N/A",
            "Tokens": total_circulating,
            "Amount Paid ($)": monthly_rent
        })
        st.success(f"Distributed ${monthly_rent:,.2f} across circulating tokens!")
        st.rerun()

st.divider()

# Cap Table
st.subheader("5. Cap Table & Audit Trail")
cap_data = [{
    "Holder": name,
    "Token Balance": wallet["balance_tokens"],
    "Ownership %": f"{(wallet['balance_tokens'] / st.session_state.asset['total_supply']) * 100:.2f}%",
    "USD Balance": f"${wallet['cash_usd']:,.2f}",
    "KYC Status": "Passed" if wallet["kyc_verified"] else "Pending"
} for name, wallet in st.session_state.wallets.items()]

st.dataframe(pd.DataFrame(cap_data), use_container_width=True)
if st.session_state.audit_log:
    st.dataframe(pd.DataFrame(st.session_state.audit_log), use_container_width=True)
