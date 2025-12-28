import streamlit as st
import os
import importlib
import time
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx

# Set page config before any Streamlit command
st.set_page_config(layout="wide")

# Initialize last_interaction in session state
if "last_interaction" not in st.session_state:
    st.session_state.last_interaction = time.time()

# Removed the timeout window logic and reload button
# Reverted to the previous implementation of runtime limit enforcement

def enforce_runtime_limit():
    def shutdown_timer():
        while True:
            if "last_interaction" in st.session_state:
                time_since_last_interaction = time.time() - st.session_state.last_interaction
                if time_since_last_interaction > 60*20:  # 20 minutes timeout
                    os._exit(0)  # Forcefully exit the script
            time.sleep(1)

    shutdown_thread = threading.Thread(target=shutdown_timer, daemon=True)
    add_script_run_ctx(shutdown_thread)
    shutdown_thread.start()

# Start the runtime limit enforcement
enforce_runtime_limit()

# Update last interaction timestamp on every app rerun
st.session_state.last_interaction = time.time()

# Sidebar navigation for app selection
APP_DIR = "apps"
DEFAULT_APP = "google_auth.py"

st.sidebar.title("Select an App")
app_files = [f for f in os.listdir(APP_DIR) if f.endswith(".py")]

if not app_files:
    st.sidebar.write("No apps found in the directory.")
else:
    app_display_names = [f.replace("_", " ").replace(".py", "").title() for f in app_files]

    if DEFAULT_APP in app_files:
        default_index = app_files.index(DEFAULT_APP)
    else:
        default_index = 0

    selected_display_name = st.sidebar.selectbox("Choose an app", app_display_names, index=default_index)
    selected_app_file = app_files[app_display_names.index(selected_display_name)]

    # Append application name to URL
    app_name_for_url = selected_app_file.replace(".py", "")
    st.query_params["app"] = app_name_for_url  # Corrected usage here

    app_module = importlib.import_module(f"{APP_DIR}.{selected_app_file[:-3]}")
    if hasattr(app_module, "run"):
        app_module.run()
    else:
        st.write(f"The selected app '{selected_display_name}' does not have a 'run()' function.")
