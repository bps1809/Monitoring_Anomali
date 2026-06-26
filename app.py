import streamlit as st
import pandas as pd

# ==============================================================================
# 1. KONFIGURASI HALAMAN UTAMA
# ==============================================================================
st.set_page_config(
    page_title="Monitoring Anomali Susenas & Seruti - BPS Pesawaran",
    page_icon="🔍",
    layout="wide"
)

# Custom Styling menggunakan CSS internal Streamlit agar visual rapi & profesional
st.markdown("""
    <style>
    .main-title { font-size: 28px; font-weight: bold; color: #1E3A8A; margin-bottom: 2px; }
    .sub-title { font-size: 16px; color: #4B5563; margin-bottom: 25px; }
    .card-label { font-size: 14px; color: #6B7280; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 Web Monitoring Anomali SUSENAS & SERUTI 2026</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Badan Pusat Statistik Kabupaten Pesawaran</div>', unsafe_allow_html=True)
st.write("---")

# ==============================================================================
# 2. SIDEBAR - UNTUK UNGGAH FILE EXCEL
# ==============================================================================
st.sidebar.header("📁 Menu Unggah Data")
uploaded_file = st.sidebar.file_uploader(
    "Unggah File Excel Isian Anomali (Format .xlsx / .xls)", 
    type=["xlsx", "xls"]
)

# Petunjuk penggunaan di sidebar
st.sidebar.write("---")
st.sidebar.markdown("""
**💡 Cara Penggunaan:**
1. Unduh rekapan anomali dari sistem Provinsi/Pusat.
2. Tambahkan satu kolom bernama **Status** di bagian paling kanan Excel Anda jika ingin melacak progress (Isi dengan: *Belum Diperbaiki*, *Sudah Diperbaiki*, atau *Sesuai Lapangan*).
3. Unggah filenya ke aplikasi ini.
""")

# ==============================================================================
# 3. PROSES DATA & LOGIKA UTAMA APLIKASI
# ==============================================================================
if uploaded_file is not None:
    
    # Fungsi membaca dan membersihkan data (menggunakan cache agar loading cepat)
    @st.cache_data
    def load_data(file):
        # Membaca excel
        df = pd.read_excel(file)
        
        # Membersihkan nama kolom (menghilangkan spasi tak sengaja)
        df.columns = df.columns.str.strip()
        
        # Konversi kolom kode-kodean dan ID menjadi Text/String agar tidak rusak/pembulatan angka
        kolom_teks = ['IdNUS', 'Kode Prov', 'Kode Kab/Kota', 'Kode Kec', 'Kode Desa', 'Kode BS', 'No']
        for col in kolom_teks:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        
        # Cek ketersediaan kolom 'Status' untuk tracking pengerjaan, jika tidak ada dibuat otomatis
        if 'Status' not in df.columns:
            # Contoh logika deteksi: jika di kolom 'Batasan Masalah' mengandung kata tertentu atau kita set default
            df['Status'] = 'Belum Diperbaiki'
            
        return df

    # Memuat data dari file excel yang diupload
    df_raw = load_data(uploaded_file)
    
    # --------------------------------------------------------------------------
    # BAGIAN A: SUMMARY DASHBOARD (METRIK / KPI CARD)
    # --------------------------------------------------------------------------
    total_kasus = len(df_raw)
    
    # Menghitung progress penyelesaian berdasarkan teks di kolom Status
    sudah_diperbaiki = len(df_raw[df_raw['Status'].str.contains('Sudah|Sesuai|Clean', case=False, na=False)])
    belum_diperbaiki = total_kasus - sudah_diperbaiki
    persen_progress = (sudah_diperbaiki / total_kasus * 100) if total_kasus > 0 else 0
    
    # Tampilan Baris Metrik Ringkasan Atas
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📌 Total Temuan Anomali", f"{total_kasus} Kasus")
    m2.metric("✅ Sudah Clear / Sesuai", f"{sudah_diperbaiki} Kasus")
    m3.metric("❌ Belum Diperbaiki", f"{belum_diperbaiki} Kasus")
    m4.metric("📈 Progress Kabupaten", f"{persen_progress:.1f}%")
    
    st.write("---")
    
    # --------------------------------------------------------------------------
    # BAGIAN B: FILTERING DATA INTERAKTIF
    # --------------------------------------------------------------------------
    st.markdown("### 🔍 Filter & Pencarian Data Masalah")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    # Filter 1: Kecamatan (Hanya mendeteksi data yang ada di Excel)
    with col_f1:
        if 'Kode Kec' in df_raw.columns:
            list_kec = ["Semua Kecamatan"] + sorted(df_raw['Kode Kec'].unique().tolist())
            pilihan_kec = st.selectbox("Filter Kecamatan:", list_kec)
        else:
            pilihan_kec = "Semua Kecamatan"
            st.warning("Kolom 'Kode Kec' tidak ditemukan di Excel.")
            
    # Filter 2: Desa (Otomatis menyesuaikan dengan Kecamatan yang dipilih di atas)
    with col_f2:
        if 'Kode Desa' in df_raw.columns:
            if pilihan_kec != "Semua Kecamatan":
                df_filtered_kec = df_raw[df_raw['Kode Kec'] == pilihan_kec]
                list_desa = ["Semua Desa"] + sorted(df_filtered_kec['Kode Desa'].unique().tolist())
            else:
                df_filtered_kec = df_raw.copy()
                list_desa = ["Semua Desa"] + sorted(df_raw['Kode Desa'].unique().tolist())
                
            pilihan_desa = st.selectbox("Filter Desa/Kelurahan:", list_desa)
        else:
            pilihan_desa = "Semua Desa"
            df_filtered_kec = df_raw.copy()
            st.warning("Kolom 'Kode Desa' tidak ditemukan di Excel.")

    # Terapkan hasil filter wilayah ke dataframe kerja
    df_final = df_filtered_kec.copy()
    if pilihan_desa != "Semua Desa":
        df_final = df_final[df_final['Kode Desa'] == pilihan_desa]
        
    # Filter 3: Pencarian Pintar Global (Ketik Nama Petugas/PML, Isian Masalah, dsb)
    with col_f3:
        search_keyword = st.text_input("Pencarian Kata Kunci (Nama Petugas / IDNUS / Masalah):", "")
        
    if search_keyword:
        # Melakukan pencarian string di semua kolom secara fleksibel
        df_final = df_final[
            df_final.astype(str).apply(lambda x: x.str.contains(search_keyword, case=False)).any(axis=1)
        ]

    # Menata ulang nomor urut (Index) tabel di web agar rapi dari angka 1
    df_final = df_final.reset_index(drop=True)
    df_final.index = df_final.index + 1
    df_final.index.name = "No"

    # --------------------------------------------------------------------------
    # BAGIAN C: DATA TABLE & DOWNLOAD ACTION
    # --------------------------------------------------------------------------
    st.write("---")
    
    # Header Info Hasil Filter
    st.markdown(f"📊 **Daftar Rincian Anomali Terfilter ({len(df_final)} Baris Data):**")
    
    # Menampilkan Spreadsheet Interaktif di Web
    st.dataframe(df_final, use_container_width=True)
    
    # Fitur Download: Mengonversi data terfilter ke CSV agar bisa dikerjakan petugas lapangan
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv_output = convert_df_to_csv(df_final)
    
    st.download_button(
        label="📥 Download Hasil Filter ke Excel (.csv)",
        data=csv_output,
        file_name=f"Anomali_Pesawaran_{pilihan_kec}_{pilihan_desa}.csv",
        mime='text/csv',
    )

else:
    # Tampilan default (Landing Page) saat user pertama kali membuka web dan belum ada file di-upload
    st.info("💡 Silakan unggah file Excel daftar anomali Susenas/Seruti melalui menu upload di sebelah kiri (sidebar) untuk memunculkan dashboard.")
    
    # Contoh Panduan Template Kolom Excel
    st.markdown("""
    ### 📝 Panduan Kolom Input Excel
    Aplikasi ini didesain agar langsung kompatibel dengan format unduhan aplikasi BPS. Pastikan file Anda memuat kolom-kolom berikut agar sistem pencarian berjalan sempurna:
    * **IdNUS** (Berisi ID Baris/Identitas Unik)
    * **Nama Anomali** (Nama kategori error/rule validasi)
    * **Kode Kec** & **Kode Desa** (Identitas wilayah tingkat kecamatan & desa)
    * **Batasan Masalah / Isi NUS** (Rincian penjelasan anomali)
    * **Nama Petugas** / **Nama Pengawas** *(Jika ada, untuk memudahkan petugas menyaring namanya sendiri)*
    """)