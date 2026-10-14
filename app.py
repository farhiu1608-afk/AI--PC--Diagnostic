import platform
import shutil
import socket
import psutil
import streamlit as st
from ai_logic import analyze_with_ai

# =========================================================
# CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="AI PC Health Monitor",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="collapsed", 
)


# Load CSS & HTML Helper
def load_css(file_name):
  try:
    with open(file_name, encoding="utf-8") as f:
      st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
  except FileNotFoundError:
    pass


def load_html(file_name):
  try:
    with open(file_name, encoding="utf-8") as f:
      return f.read()
  except FileNotFoundError:
    return f"<h3>Error: File {file_name} tidak ditemukan!</h3>"


load_css("style.css")

# =========================================================
#  CUSTOM NAVBAR HTML 
# =========================================================
st.markdown(
    """
    <div class="fContainer">
      <nav class="wrapper">
      <div class="brand">
        <div class="first">AI PC</div>
        <div class="last">Health Monitor</div>
      </div>
      <ul class="navigation">
          <li class="navbar li"><a href="?page=home">Home</a></li>
          <li><a href="?page=about">About</a></li>
          <li><a href="?page=diagnostic">Diagnostic</a></li>
      </ul>
      </nav>
    </div>
""",
    unsafe_allow_html=True,
)

# Mengambil status halaman dari URL (Query Parameters)
query_params = st.query_params
active_page = query_params.get("page", "home",)  # Default-nya ke halaman 'home'

# =========================================================
# LOGIKA PEMILIHAN HALAMAN BERDASARKAN NAVBAR
# =========================================================

if active_page == "home":
  # Membaca file home.html
  st.markdown(load_html("home.html"), unsafe_allow_html=True)

elif active_page == "diagnostic":
  # Ambil data hardware asli komputer
  cpu_usage = psutil.cpu_percent(interval=1)
  ram = psutil.virtual_memory()
  ram_usage = ram.percent
  ram_total = ram.total / (1024**3)
  ram_available = ram.available / (1024**3)

  disk = shutil.disk_usage("/")
  disk_total = disk.total / (1024**3)
  disk_used = disk.used / (1024**3)
  disk_percent = (disk.used / disk.total) * 100

  computer_name = socket.gethostname()
  system_name = platform.system()
  system_version = platform.version()
  processor = platform.processor()

  # Baca kerangka dari diagnostic.html lalu format datanya
  diag_template = load_html("diagnostic.html")
  rendered_html = diag_template.format(
      cpu_val=f"{cpu_usage:.1f}%",
      ram_val=f"{ram_usage:.1f}%",
      disk_val=f"{disk_percent:.1f}%",
  )
  st.markdown(rendered_html, unsafe_allow_html=True)

  # Progress bar tambahan
  col_l, col_r = st.columns(2)
  with col_l:
    st.write(f"**CPU Usage Detail:** {cpu_usage:.1f}%")
    st.progress(min(cpu_usage / 100, 1.0))
    st.write(f"**RAM Usage:** {ram_usage:.1f}% ({ram_total:.2f} GB Total)")
    st.progress(min(ram_usage / 100, 1.0))

  with col_r:
    st.write(f"**Disk Usage:** {disk_percent:.1f}%")
    st.progress(min(disk_percent / 100, 1.0))
    st.write(
        f"**Disk Free:** {(disk_total - disk_used):.2f} GB dari"
        f" {disk_total:.2f} GB"
    )

  # Tombol AI Diagnostic
  st.markdown("---")
  if st.button("🔍 ANALYZE PC WITH AI", use_container_width=True):
    with st.spinner("🤖 AI sedang menganalisis kondisi PC..."):
      ai_result, error = analyze_with_ai(
          computer_name,
          system_name,
          processor,
          cpu_usage,
          ram_usage,
          ram_total,
          ram_available,
          disk_percent,
          disk_total,
          disk_used,
      )

      if error:
        st.error("Gagal terhubung ke Ollama.")
        st.code(error)
      else:
        st.markdown(
            """
                <div class="ai-box">
                    <div class="ai-title">🤖 AI Diagnosis Result</div>
                </div>
                """,
            unsafe_allow_html=True,
        )
        st.markdown(ai_result)

elif active_page == "about":
  # Membaca file about.html
  st.markdown(load_html("about.html"), unsafe_allow_html=True)
