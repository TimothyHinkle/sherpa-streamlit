import streamlit as st
import inspect
import os

st.set_page_config(layout="wide")
st.title("Request + Auth Introspection")

req = st.request
headers = dict(req.headers)

# -------------------------
# 1. Raw request dump
# -------------------------
st.header("Raw request headers")
st.json(headers)

st.header("All request attributes")
attrs = {}
for name in dir(req):
    if name.startswith("_"):
        continue
    try:
        val = getattr(req, name)
        if inspect.isfunction(val) or inspect.ismethod(val):
            continue
        attrs[name] = str(val)
    except Exception as e:
        attrs[name] = f"<error: {e}>"

st.json(attrs)

# -------------------------
# 2. Auth resolution logic
# -------------------------
st.header("Auth resolution")

auth_source = None
user_identity = None

# --- Primary: IAP headers ---
iap_email = headers.get("X-Goog-Authenticated-User-Email")
iap_user_id = headers.get("X-Goog-Authenticated-User-ID")

if iap_email:
    auth_source = "IAP"
    user_identity = {
        "email": iap_email,
        "user_id": iap_user_id,
    }

# --- Fallback 1: query param ---
elif "user" in st.query_params:
    auth_source = "query_param"
    user_identity = {
        "email": st.query_params.get("user"),
        "user_id": None,
    }

# --- Fallback 2: environment variable ---
elif os.getenv("DEV_USER"):
    auth_source = "env_var"
    user_identity = {
        "email": os.getenv("DEV_USER"),
        "user_id": None,
    }

# --- Final fallback: anonymous ---
else:
    auth_source = "anonymous"
    user_identity = {
        "email": "anonymous",
        "user_id": None,
    }

st.subheader("Resolved identity")
st.write(user_identity)
st.write("Auth source:", auth_source)

# -------------------------
# 3. Explicit failure signal
# -------------------------
if auth_source == "anonymous":
    st.warning(
        "No authenticated identity detected. "
        "This is expected locally, but NOT behind IAP."
    )
else:
    st.success(f"Authenticated via {auth_source}")
