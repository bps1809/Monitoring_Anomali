import streamlit as st
import pandas as pd
import os

# ==============================================================================
# 1. KONFIGURASI HALAMAN UTAMA
# ==============================================================================
st.set_page_config(
    page_title="Monitoring Anomali - BPS Pesawaran",
    page_icon="🔍",
    layout="wide"
)

st.markdown("""
    <style>
    .main-title { font-size: 26px; font-weight: bold; color: #1E3A8A; margin-bottom: 2px; }
    .sub-title { font-size: 15px; color: #4B5563; margin-bottom: 25px; }
    h3 { color: #1E3A8A; font-size: 20px; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 Web Monitoring & Update Anomali Hasil Evaluasi</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Badan Pusat Statistik Kabupaten Pesawaran</div>', unsafe_allow_html=True)
st.write("---")

# ==============================================================================
# 2. MANAJEMEN DATA (BACA & SIMPAN KE EXCEL)
# ==============================================================================
FILE_NAME = "data_anomali.xlsx"

if os.path.exists(FILE_NAME):
    
    # Fungsi membaca data (menggunakan session_state agar perubahan langsung tersimpan di memori web)
    if 'df_anomali' not in st.session_state:
        df = pd.read_excel(FILE_NAME)
        df.columns = df.columns.str.strip()
        
        # Pastikan kolom string tidak rusak formatnya
        kolom_teks = ['No', 'Kecamatan', 'Desa', 'SLS']
        for col in kolom_teks:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        
        # Buat kolom Status jika belum ada
        if 'Status' not in df.columns:
            df['Status'] = 'Belum'
            
        st.session_state.df_anomali = df

    # --------------------------------------------------------------------------
    # BAGIAN A: DASHBOARD METRIK PROGRESS
    # --------------------------------------------------------------------------
    df_kerja = st.session_state.df_anomali
    
    total_kasus = len(df_kerja)
    sudah_diperbaiki = len(df_kerja[df_kerja['Status'] == 'Sudah'])
    belum_diperbaiki = total_kasus - sudah_diperbaiki
    persen_progress = (sudah_diperbaiki / total_kasus * 100) if total_kasus > 0 else 0
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📌 Total Kasus Anomali", f"{total_kasus} Temuan")
    m2.metric("✅ Berhasil Diperbaiki", f"{sudah_diperbaiki} Kasus")
    m3.metric("❌ Sisa Belum Diperbaiki", f"{belum_diperbaiki} Kasus")
    m4.metric("📈 Progress Penyelesaian", f"{persen_progress:.1f}%")
    
    st.write("---")
    
    # --------------------------------------------------------------------------
    # BAGIAN B: FILTER INTERAKTIF (BERLAKU UNTUK KEDUA TABEL)
    # --------------------------------------------------------------------------
    st.markdown("### 🔍 Filter Wilayah & Petugas")
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        list_kec = ["Semua Kecamatan"] + sorted(df_kerja['Kecamatan'].dropna().unique().tolist())
        pilihan_kec = st.selectbox("Pilih Kecamatan:", list_kec)
        
    with col_f2:
        if pilihan_kec != "Semua Kecamatan":
            df_filtered_kec = df_kerja[df_kerja['Kecamatan'] == pilihan_kec]
            list_desa = ["Semua Desa"] + sorted(df_filtered_kec['Desa'].dropna().unique().tolist())
        else:
            df_filtered_kec = df_kerja.copy()
            list_desa = ["Semua Desa"] + sorted(df_kerja['Desa'].dropna().unique().tolist())
        pilihan_desa = st.selectbox("Pilih Desa/Kelurahan:", list_desa)

    with col_f3:
        search_keyword = st.text_input("Kata Kunci Pencarian (Nama Petugas/SLS/Nama Keluarga):", "")

    # Fungsi untuk menerapkan filter pencarian
    def terapkan_filter(df_target):
        if pilihan_kec != "Semua Kecamatan":
            df_target = df_target[df_target['Kecamatan'] == pilihan_kec]
        if pilihan_desa != "Semua Desa":
            df_target = df_target[df_target['Desa'] == pilihan_desa]
        if search_keyword:
            df_target = df_target[df_target.astype(str).apply(lambda x: x.str.contains(search_keyword, case=False)).any(axis=1)]
        return df_target

    # --------------------------------------------------------------------------
    # BAGIAN C: TABEL 1 - BELUM DIPERBAIKI (BISA DICENTANG)
    # --------------------------------------------------------------------------
    st.write("---")
    st.markdown("### 🟥 DAFTAR ANOMALI YANG BELUM DIPERBAIKI")
    st.caption("Silakan centang pada kolom **'Cek & Tandai'** jika kasus anomali di baris tersebut sudah selesai diperbaiki.")
    
    # Pisahkan data yang berstatus 'Belum'
    df_belum = df_kerja[df_kerja['Status'] != 'Sudah'].copy()
    df_belum_filtered = terapkan_filter(df_belum)
    
    if not df_belum_filtered.empty:
        # Tambahkan kolom checkbox bayangan untuk interaksi pengguna
        df_belum_filtered.insert(0, 'Cek & Tandai', False)
        
        # Tampilkan tabel yang bisa diedit (di-centang)
        edited_df = st.data_editor(
            df_belum_filtered,
            column_config={
                "Cek & Tandai": st.column_config.CheckboxColumn(
                    "Cek & Tandai",
                    help="Centang untuk menandai selesai",
                    default=False,
                ),
                "Status": None # Sembunyikan kolom status asli agar rapi
            },
            disabled=['No', 'Kecamatan', 'Desa', 'SLS', 'Nama Keluarga atau Usaha', 'Jenis Anomali', 'Nama Petugas', 'Nama Pengawas'],
            use_container_width=True,
            key="editor_belum"
        )
        
        # Tombol konfirmasi tindakan pemindahan data & simpan permanen
        if st.button("💾 Simpan Sudah diPerbaiki", type="primary"):
            # Cari baris mana saja yang barusan dicentang oleh user
            baris_dicentang = edited_df[edited_df['Cek & Tandai'] == True]
            
            if not baris_dicentang.empty:
                # Ambil nomor unik ('No' atau kombinasi data asli) untuk diupdate statusnya di database utama
                for idx, row in baris_dicentang.iterrows():
                    nomor_kasus = row['No']
                    st.session_state.df_anomali.loc[st.session_state.df_anomali['No'] == nomor_kasus, 'Status'] = 'Sudah'
                
                # Simpan perubahan langsung ke file Excel fisik komputer
                st.session_state.df_anomali.to_excel(FILE_NAME, index=False)
                st.success("✅ Data berhasil diperbarui dan disimpan ke file excel!")
                st.rerun()
            else:
                st.warning("Belum ada baris data yang Anda centang.")
    else:
        st.info("👌 Tidak ada data anomali yang belum diperbaiki pada filter ini.")

    # --------------------------------------------------------------------------
    # BAGIAN D: TABEL 2 - REKAPAN SUDAH DIPERBAIKI (TURUN KE BAWAH)
    # --------------------------------------------------------------------------
    st.write("---")
    st.markdown("### 🟩 REKAPAN ANOMALI YANG SUDAH DIPERBAIKI")
    
    # Pisahkan data yang berstatus 'Sudah'
    df_sudah = df_kerja[df_kerja['Status'] == 'Sudah'].copy()
    df_sudah_filtered = terapkan_filter(df_sudah)
    
    if not df_sudah_filtered.empty:
        # Reset urutan penomoran tampilan
        df_sudah_filtered = df_sudah_filtered.reset_index(drop=True)
        df_sudah_filtered.index = df_sudah_filtered.index + 1
        
        # Tampilkan tabel statis (Hanya dibaca, tidak bisa dicentang lagi)
        st.dataframe(
            df_sudah_filtered.drop(columns=['Status'], errors='ignore'), 
            use_container_width=True
        )
    else:
        st.info("Kolom ini akan terisi jika sudah ada data yang ditandai selesai di tabel atas.")

else:
    st.error(f"❌ File '{FILE_NAME}' tidak ditemukan di folder aplikasi Anda.")
    st.info("Pastikan file Excel diletakkan dalam satu folder dengan 'app.py' dan diubah namanya menjadi 'data_anomali.xlsx'.")