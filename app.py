import streamlit as st
import pandas as pd
import json
import os

# Page setup
st.set_page_config(page_title="OpenGradient Leaderboard", layout="wide")

st.title("🏆 OpenGradient Leaderboard")
st.write("Tracking community activity")
st.markdown("**Powered by FME | OpenGradient Community**")

# -------------------------------
# Reset Function
# -------------------------------
def reset_data():
    with open("users.json", "w") as f:
        json.dump([], f)
    with open("data.json", "w") as f:
        json.dump([], f)
    st.success("✅ Leaderboard and registrations have been reset!")

# Refresh button (safe for all users)
if st.button("🔄 Refresh Leaderboard"):
    st.success("Leaderboard refreshed!")

# Admin-only reset (requires password)
st.subheader("⚠️ Admin Controls")
admin_pass = st.text_input("Enter admin password to unlock reset", type="password")
if admin_pass == "opengradient2026":  # <-- change this to your secret
    if st.button("🚨 Reset Leaderboard & Users"):
        reset_data()

# -------------------------------
# Role Mapping
# -------------------------------
role_points = {
    "OG": 200,
    "The supreme Quant": 180,
    "Elite Quant": 160,
    "Master Quant": 140,
    "Senior Quant": 120,
    "Quant Associate": 100,
    "Quant Apprentice": 80,
    "Quantling": 60,
    "Quant Catalyst": 50,
    "Quotent Creators": 50,
    "Developer": 50,
    "Research": 50
}
discord_roles = list(role_points.keys())

# -------------------------------
# Load registered users
# -------------------------------
try:
    with open("users.json", "r") as f:
        valid_users = json.load(f)
except:
    valid_users = []

# -------------------------------
# Registration Section
# -------------------------------
st.subheader("📝 Register Your Discord Username")

reg_name = st.text_input("Enter your exact Discord username")
if st.button("Register"):
    if reg_name.strip() == "":
        st.error("❌ Please enter a valid username.")
    elif reg_name in valid_users:
        st.warning("⚠️ Already registered.")
    else:
        valid_users.append(reg_name)
        with open("users.json", "w") as f:
            json.dump(valid_users, f, indent=4)
        st.success("✅ Registered successfully!")

# -------------------------------
# View Registered Users
# -------------------------------
st.subheader("👥 View Registered Users")
if valid_users:
    st.write(f"Total registered users: **{len(valid_users)}**")
    st.dataframe(pd.DataFrame(valid_users, columns=["Registered User"]), use_container_width=True)
else:
    st.info("No users registered yet.")

# -------------------------------
# Submission Section
# -------------------------------
st.subheader("➕ Submit Your Activity")

try:
    with open("data.json", "r") as f:
        data = json.load(f)
except:
    data = []

name = st.text_input("Username (must be registered)")
models = st.number_input("Models Built", 0)
discord = st.multiselect("Discord Roles (select all you have)", discord_roles)
xp = st.number_input("XP", 0)

if st.button("Submit"):
    if name not in valid_users:
        st.error("❌ Username not recognized. Please register first.")
    else:
        new_entry = {
            "User": name,
            "Models": models,
            "Discord": discord if isinstance(discord, list) else [discord],
            "XP": xp
        }
        data.append(new_entry)
        with open("data.json", "w") as f:
            json.dump(data, f, indent=4)
        st.success("✅ Submitted! Refresh to see leaderboard.")

# -------------------------------
# Leaderboard Section
# -------------------------------
df = pd.DataFrame(data)

if not df.empty:
    def fix_roles(x):
        if isinstance(x, list):
            return x
        elif isinstance(x, str):
            return [x]
        else:
            return []

    df["Discord"] = df["Discord"].apply(fix_roles)

    df["Score"] = df.apply(
        lambda row: (row["Models"] * 10) + row["XP"] + sum(role_points.get(r, 0) for r in row["Discord"]),
        axis=1
    )

    df = df.sort_values(by="Score", ascending=False)
    df.insert(0, "Rank", range(1, len(df) + 1))
    df["Discord"] = df["Discord"].apply(lambda roles: ", ".join(roles))

    st.subheader("🥇 Top Performers")
    top3 = df.head(3)
    cols = st.columns(3)
    for i, row in enumerate(top3.itertuples(), start=1):
        cols[i-1].metric(label=f"#{i} {row.User}", value=row.Score)

    st.subheader("📊 Full Leaderboard")
    st.dataframe(df.reset_index(drop=True), use_container_width=True)

    st.subheader("📈 Score Breakdown")
    st.bar_chart(df.set_index("User")["Score"])
    st.subheader("📈 Models vs XP")
    st.scatter_chart(df, x="Models", y="XP", size="Score", color="User")

else:
    st.info("No submissions yet. Be the first to add your activity!")


