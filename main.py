import streamlit as st
import inspect
import os

st.set_page_config(layout="wide")
st.title("Request + Auth Introspection")

# -------------------------
# Request / headers (SAFE)
# -------------------------
headers = {}
attrs = {}

try:
    ctx = st.context
    if ctx:
        headers = dict(ctx.headers or {})
        for name in dir(ctx):
            if name.startswith("_"):
                continue
            try:
                val = getattr(ctx, name)
                if inspect.isfunction(val) or inspect.ismethod(val):
                    continue
                attrs[name] = str(val)
            except Exception as e:
                attrs[name] = f"<error: {e}>"
except Exception as e:
    st.error(f"Context error: {e}")

# -------------------------
# Display raw info
# -------------------------
st.header("Raw request headers")
st.json(headers)

st.header("Context attributes")
st.json(attrs)

# -------------------------
# Auth resolution
# -------------------------
st.header("Auth resolution")

auth_source = None
user_identity = None

iap_email = headers.get("X-Goog-Authenticated-User-Email")
iap_user_id = headers.get("X-Goog-Authenticated-User-ID")

if iap_email:
    auth_source = "IAP"
    user_identity = {"email": iap_email, "user_id": iap_user_id}

elif "user" in st.query_params:
    auth_source = "query_param"
    user_identity = {"email": st.query_params.get("user"), "user_id": None}

elif os.getenv("DEV_USER"):
    auth_source = "env_var"
    user_identity = {"email": os.getenv("DEV_USER"), "user_id": None}

else:
    auth_source = "anonymous"
    user_identity = {"email": "anonymous", "user_id": None}

st.subheader("Resolved identity")
st.write(user_identity)
st.write("Auth source:", auth_source)

if auth_source == "anonymous":
    st.warning(
        "No authenticated identity detected. "
        "This is expected locally, but NOT behind IAP."
    )
else:
    st.success(f"Authenticated via {auth_source}")
