import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- Streamlit Page Config ---
st.set_page_config(page_title="OpenGradient Leaderboard", layout="wide")

st.title("🏆 OpenGradient Leaderboard")
st.write("Tracking community activity")
st.markdown("**Powered by FME | OpenGradient Community**")

# --- Supabase Connection ---
url = st.secrets["supabase_url"]
key = st.secrets["supabase_key"]
supabase: Client = create_client(url, key)

# --- Role Mapping ---
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

# --- Helper Functions ---
def register_user(username: str):
    supabase.table("users").insert({"username": username}).execute()

def submit_activity(username: str, models: int, xp: int, roles: list):
    # Each submission stores the latest roles
    supabase.table("activities").insert({
        "username": username,
        "models": models,
        "xp": xp,
        "roles": roles
    }).execute()

def get_leaderboard():
    response = supabase.table("activities").select("*").execute()
    df = pd.DataFrame(response.data)
    if not df.empty:
        # Calculate score: models*10 + xp + role bonuses
        def calc_score(row):
            role_bonus = sum(role_points.get(r, 0) for r in row["roles"])
            return (row["models"] * 10) + row["xp"] + role_bonus

        df["score"] = df.apply(calc_score, axis=1)
        leaderboard = df.groupby("username", as_index=False)["score"].sum()
        leaderboard = leaderboard.sort_values("score", ascending=False)
        return leaderboard
    return pd.DataFrame(columns=["username", "score"])

def reset_leaderboard(password: str):
    if password == st.secrets["admin_password"]:
        supabase.table("users").delete().neq("id", 0).execute()
        supabase.table("activities").delete().neq("id", 0).execute()
        st.success("Leaderboard reset successfully!")
    else:
        st.error("Invalid password.")

# --- Streamlit UI ---
menu = st.sidebar.radio("Menu", ["Register", "Submit Activity", "Leaderboard", "Admin Reset"])

if menu == "Register":
    st.subheader("📝 Register Your Discord Username")
    username = st.text_input("Enter your exact Discord username")
    if st.button("Register"):
        if username.strip() == "":
            st.error("❌ Please enter a valid username.")
        else:
            register_user(username)
            st.success(f"{username} registered successfully!")

elif menu == "Submit Activity":
    st.subheader("➕ Submit Your Activity")
    username = st.text_input("Username (must be registered)")
    models = st.number_input("Models Built", 0)
    xp = st.number_input("XP", 0)
    roles = st.multiselect("Discord Roles (select all you have)", discord_roles)
    if st.button("Submit"):
        if username.strip() == "":
            st.error("❌ Please enter a valid username.")
        else:
            submit_activity(username, models, xp, roles)
            st.success("✅ Submitted! Refresh to see leaderboard.")

elif menu == "Leaderboard":
    st.subheader("🥇 Top Performers")
    leaderboard = get_leaderboard()
    if not leaderboard.empty:
        leaderboard.insert(0, "Rank", range(1, len(leaderboard) + 1))
        st.dataframe(leaderboard.reset_index(drop=True), use_container_width=True)
        st.bar_chart(leaderboard.set_index("username")["score"])
    else:
        st.info("No submissions yet. Be the first to add your activity!")

elif menu == "Admin Reset":
    st.subheader("⚠️ Admin Controls")
    password = st.text_input("Enter admin password", type="password")
    if st.button("🚨 Reset Leaderboard & Users"):
        reset_leaderboard(password)


