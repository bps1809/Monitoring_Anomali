import streamlit as st
import pandas as pd
import os

# ==============================================================================
# 1. KONFIGURASI HALAMAN UTAMA & SIDEBAR
# ==============================================================================
st.set_page_config(
    page_title="Monitoring Anomali - BPS Pesawaran",
    page_icon="📊",
    layout="wide"
)

# Custom CSS untuk mempercantik komponen visual & tata letak (Layout)
st.markdown("""
    <style>
    /* Styling Judul Utama */
    .main-title { font-size: 32px; font-weight: 800; color: #1E3A8A; margin-bottom: 2px; }
    .sub-title { font-size: 16px; color: #6B7280; margin-bottom: 20px; font-weight: 400; }
    
    /* Styling Sub-Header Section Tabel */
    .section-header-belum { font-size: 20px; font-weight: 700; color: #DC2626; border-left: 5px solid #DC2626; padding-left: 10px; margin-bottom: 15px; }
    .section-header-sudah { font-size: 20px; font-weight: 700; color: #16A34A; border-left: 5px solid #16A34A; padding-left: 10px; margin-bottom: 15px; }
    
    /* Box Panduan di Sidebar */
    .sidebar-guide-box { background-color: #F8FAFC; padding: 12px; border-radius: 8px; border: 1px solid #E2E8F0; margin-top: 10px; }
    .sidebar-guide-title { font-weight: bold; color: #0F172A; margin-bottom: 8px; font-size: 14px; }
    .sidebar-step { margin-left: 15px; padding-left: 0px; line-height: 1.5; font-size: 13px; color: #334155; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. STRUKTUR SIDEBAR (PETUNJUK PEMAKAIAN PINDAH KE SINI)
# ==============================================================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/2/28/Logo_BPS.svg", width=70)
    st.markdown("### 📋 Menu Navigasi")
    st.write("---")
    
    st.markdown("#### 💡 CARA PENGGUNAAN")
    st.markdown("""
    <div class="sidebar-guide-box">
        <div class="sidebar-guide-title">📢 Langkah Update Progress:</div>
        <ol class="sidebar-step">
            <li><b>Filter Data:</b><br>Pilih Kecamatan, Desa, atau langsung ketik nama Anda pada kolom pencarian petugas.</li>
            <li style="margin-top: 8px;"><b>Periksa Isian:</b><br>Lihat rincian daftar kesalahan data Anda pada tabel berwarna <span style="color:#DC2626; font-weight:bold;">Merah</span>.</li>
            <li style="margin-top: 8px;"><b>Tandai Selesai:</b><br>Jika dokumen sudah clean, <b>beri centang (✔️)</b> pada kolom paling kiri (<b>Cek & Tandai</b>).</li>
            <li style="margin-top: 8px;"><b>Simpan Tempat:</b><br>Klik tombol merah <b>"💾 Simpan Perubahan"</b> di bawah tabel untuk menyimpan ke Excel dan memindahkan baris ke tabel hijau.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    st.caption("⚙️ **BPS Kabupaten Pesawaran**\nMonitoring Evaluasi Lokal v2.0")

# ==============================================================================
# 3. KONTEN HALAMAN UTAMA (DASHBOARD UTAMA)
# ==============================================================================
st.markdown('<div class="main-title">📊 Web Monitoring & Update Anomali</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Badan Pusat Statistik Kabupaten Pesawaran</div>', unsafe_allow_html=True)

# ==============================================================================
# 4. MANAJEMEN DATA EXCEL LOKAL
# ==============================================================================
FILE_NAME = "data_anomali.xlsx"

if os.path.exists(FILE_NAME):
    
    # Ambil data ke session state web agar tidak hilang saat refresh halaman
    if 'df_anomali' not in st.session_state:
        df = pd.read_excel(FILE_NAME)
        df.columns = df.columns.str.strip()
        
        # Penyeragaman data ID/Kode agar tidak berubah format (.0)
        kolom_teks = ['No', 'Kecamatan', 'Desa', 'SLS']
        for col in kolom_teks:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        
        # Buat kolom Status pelacakan otomatis jika belum ada di Excel induk
        if 'Status' not in df.columns:
            df['Status'] = 'Belum'
            
        st.session_state.df_anomali = df

    df_kerja = st.session_state.df_anomali

    # --------------------------------------------------------------------------
    # 5. DASHBOARD METRIK CAPAIAN (KPI CARDS)
    # --------------------------------------------------------------------------
    total_kasus = len(df_kerja)
    sudah_diperbaiki = len(df_kerja[df_kerja['Status'] == 'Sudah'])
    belum_diperbaiki = total_kasus - sudah_diperbaiki
    persen_progress = (sudah_diperbaiki / total_kasus * 100) if total_kasus > 0 else 0
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📌 Total Kasus Anomali", f"{total_kasus} Kasus")
    m2.metric("✅ Berhasil Diperbaiki", f"{sudah_diperbaiki} Kasus")
    m3.metric("❌ Sisa Belum Diperbaiki", f"{belum_diperbaiki} Kasus")
    m4.metric("📈 Progress Penyelesaian", f"{persen_progress:.1f}%")
    
    st.write("---")
    
    # --------------------------------------------------------------------------
    # 6. PANEL FILTER DATA SEJAJAR 3 KOLOM
    # --------------------------------------------------------------------------
    st.markdown("### 🔍 Filter Wilayah & Nama Petugas")
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        list_kec = ["Semua Kecamatan"] + sorted(df_kerja['Kecamatan'].dropna().unique().tolist())
        pilihan_kec = st.selectbox("📍 Pilih Kecamatan:", list_kec)
        
    with col_f2:
        if pilihan_kec != "Semua Kecamatan":
            df_filtered_kec = df_kerja[df_kerja['Kecamatan'] == pilihan_kec]
            list_desa = ["Semua Desa"] + sorted(df_filtered_kec['Desa'].dropna().unique().tolist())
        else:
            df_filtered_kec = df_kerja.copy()
            list_desa = ["Semua Desa"] + sorted(df_kerja['Desa'].dropna().unique().tolist())
        pilihan_desa = st.selectbox("🏢 Pilih Desa/Kelurahan:", list_desa)

    with col_f3:
        search_keyword = st.text_input("👤 Cari Nama Petugas / SLS / Kategori:", "")

    def jalankan_filter(df_target):
        if pilihan_kec != "Semua Kecamatan":
            df_target = df_target[df_target['Kecamatan'] == pilihan_kec]
        if pilihan_desa != "Semua Desa":
            df_target = df_target[df_target['Desa'] == pilihan_desa]
        if search_keyword:
            df_target = df_target[df_target.astype(str).apply(lambda x: x.str.contains(search_keyword, case=False)).any(axis=1)]
        return df_target

    # --------------------------------------------------------------------------
    # 7. TABEL 1 - DAFTAR BELUM DIPERBAIKI (RUANG EDIT INTERAKTIF)
    # --------------------------------------------------------------------------
    st.write("---")
    st.markdown('<div class="section-header-belum">🟥 DAFTAR ANOMALI YANG BELUM DIPERBAIKI</div>', unsafe_allow_html=True)
    
    df_belum = df_kerja[df_kerja['Status'] != 'Sudah'].copy()
    df_belum_filtered = jalankan_filter(df_belum)
    
    if not df_belum_filtered.empty:
        # Masukkan kolom checkbox isian di depan tabel web
        df_belum_filtered.insert(0, 'Cek & Tandai', False)
        
        edited_df = st.data_editor(
            df_belum_filtered,
            column_config={
                "Cek & Tandai": st.column_config.CheckboxColumn(
                    "Cek & Tandai",
                    help="Centang jika baris data kesalahan ini sudah selesai Anda perbaiki",
                    default=False,
                ),
                "Status": None  # Sembunyikan kolom status asli
            },
            disabled=['No', 'Kecamatan', 'Desa', 'SLS', 'Nama Keluarga atau Usaha', 'Jenis Anomali', 'Nama Petugas', 'Nama Pengawas'],
            use_container_width=True,
            key="tabel_editor_lokal"
        )
        
        # Tombol Kirim Perubahan
        if st.button("💾 Simpan Perubahan & Pindahkan ke Tabel Bawah", type="primary"):
            baris_dicentang = edited_df[edited_df['Cek & Tandai'] == True]
            
            if not baris_dicentang.empty:
                try:
                    # Ambil No referensi index untuk diubah statusnya di database utama memory
                    for idx, row in baris_dicentang.iterrows():
                        id_kasus = row['No']
                        st.session_state.df_anomali.loc[st.session_state.df_anomali['No'] == id_kasus, 'Status'] = 'Sudah'
                    
                    # Tulis permanen ke file Excel komputer induk
                    st.session_state.df_anomali.to_excel(FILE_NAME, index=False)
                    st.success("🎉 Berhasil! Perubahan tersimpan permanen ke file Excel.")
                    st.rerun()
                    
                except PermissionError:
                    st.error("⚠️ GAGAL MENYIMPAN: File Excel sedang dikunci atau dibuka di program lain!")
                    st.warning("👉 Silakan **TUTUP / CLOSE** file `data_anomali.xlsx` dari aplikasi Microsoft Excel Anda terlebih dahulu, lalu klik kembali tombol simpan di atas.")
            else:
                st.info("💡 Pemberitahuan: Belum ada data yang Anda centang.")
    else:
        st.success("✨ Sempurna! Semua data anomali pada filter wilayah ini sudah diselesaikan.")

    # --------------------------------------------------------------------------
    # 8. TABEL 2 - REKAPAN DATA SELESAI (SUDAH DIPERBAIKI)
    # --------------------------------------------------------------------------
    st.write("---")
    st.markdown('<div class="section-header-sudah">🟩 REKAPAN ANOMALI YANG SUDAH DIPERBAIKI</div>', unsafe_allow_html=True)
    
    df_sudah = df_kerja[df_kerja['Status'] == 'Sudah'].copy()
    df_sudah_filtered = jalankan_filter(df_sudah)
    
    if not df_sudah_filtered.empty:
        # Reset penomoran tampilan
        df_sudah_filtered = df_sudah_filtered.reset_index(drop=True)
        df_sudah_filtered.index = df_sudah_filtered.index + 1
        
        st.dataframe(
            df_sudah_filtered.drop(columns=['Status'], errors='ignore'), 
            use_container_width=True
        )
    else:
        st.info("💡 Catatan: Belum ada daftar kasus yang selesai diperbaiki pada kombinasi filter ini.")

else:
    st.error(f"❌ File '{FILE_NAME}' tidak ditemukan di folder aplikasi Anda.")
    st.info("Pastikan file Excel diletakkan dalam satu folder dengan 'app.py' dan diubah namanya menjadi 'data_anomali.xlsx'.")