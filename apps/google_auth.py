import streamlit as st
from streamlit.web.server.server import Server

st.set_page_config(layout="wide")
st.title("Raw Request Dump")

ctx = Server.get_current()._get_script_run_ctx()
req = ctx.request if ctx else None

if not req:
    st.error("No request context")
    st.stop()

st.subheader("Headers (raw)")
st.code("\n".join(f"{k}: {v}" for k, v in req.headers.items()))

st.subheader("Cookies (raw)")
st.code(str(req.cookies))

st.subheader("Query Params (raw)")
st.code(str(req.args))

st.subheader("Request Metadata")
st.code(
    f"""
method: {req.method}
url: {req.url}
host: {req.host}
scheme: {req.scheme}
remote_addr: {req.remote_addr}
access_route: {req.access_route}
"""
)

st.subheader("WSGI Environ (everything)")
st.code(
    "\n".join(f"{k}={v}" for k, v in req.environ.items()),
    language="text"
)
