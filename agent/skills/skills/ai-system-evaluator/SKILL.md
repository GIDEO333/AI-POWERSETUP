---
name: ai-system-evaluator
description: Pedoman prosedural untuk mengevaluasi luaran teknis, kohesi komunikasi antar agen, dan penemuan bottleneck pada kerangka kerja kolaborasi mesin.
category: QA
---

# AI System Evaluator (The QA Auditor)

## Tujuan
Membekali Anda (sebagai entitas pengawas makro) metode evaluasi objektif yang merdeka dari ranah satu spesifik bahasa pemograman, guna membedah tingkat keberhasilan desain arsitektur Multi-Agent.

## Kapan Menggunakan
Saat Anda diminta *"Coba evaluasi performa kerja bot-bot ini, cari kurangnya di mana?"*

## Metodologi Skoring Komponen (Obyektif)

Jangan menilai *output* hanya dari "Apakah kodenya jalan di browser atau tidak" atau "Apakah tesnya hijau". Nilai proses perjalanan komputasinya menggunakan metrik berikut:

### 1. Kohesi Rencana vs Eksekusi
- **Bahan Uji:** Bandingkan file `architecture_plan.md` buatan Arsitek VS hasil *Diff Files* buatan Eksekutor.
- **Paramater Gagal:** Si Eksekutor berasumsi melakukan tambahan fungsional (menulis modul ekstra) yang tidak diamanatkan dalam perintah dokumen Rencana Arsitektur.

### 2. Akurasi Handoff & Isolasi Tugas
- **Bahan Uji:** Tinjau riwayat eksekusi *QA Tester* vs *Worker*.
- **Parameter Gagal:** Jika agen The Worker kepergok menjalankan skrip uji-coba (*Test Framework*) secara sembunyi-sembunyi yang semestinya ranah pekerjaan ekslusif The QA Tester. Ini mengindikasikan kelonggaran *Constraint System Prompt* agen tersebut.

### 3. Fault Tolerance & Ketahanan Kritis
- **Bahan Uji:** Apakah ada perlindungan *Hard Timeout*? Jika si Worker panik, apakah ia mati dan menyandera memori laptop host (*zombie*), atau mati elegan dengan riwayat jejak pesan?
- **Parameter Gagal:** Mengandalkan loop interogatif pada konfigurasi *Headless*. Mengindikasikan "Overengineering" bash ketika penanganan kesalahan tidak diinjeksi secara vertikal ke otak AI agennya sendiri.

## The Output Format
Sajikan temuan Anda dalam blok evaluasi ringkas:
**"Nama Komponen Evaluasi" | Nilai (V/X/O) | Catatan Teknikal Analitis**
Akhiri selalu audit dengan satu rekomendasi "The Missing Link" (satu teknik/tools paling *impactful* yang absen di keseluruhan sistem).
