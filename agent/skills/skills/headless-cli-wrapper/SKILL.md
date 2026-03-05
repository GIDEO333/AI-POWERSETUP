---
name: headless-cli-wrapper
description: Petunjuk mengonversi CLI Agent yang awalnya bercorak interaktif interogatif (membutuhkan input keyboard manusia) menjadi eksekutor otonom untuk pipeline CI/CD.
category: Ops
---

# Headless CLI Wrapper

## Tujuan
Mengonversi alat interaktif menjadi agen "tembak dan lupakan" (*Fire and Forget*) yang bisa disisipkan ke dalam otomatisasi mesin, tanpa pernah menahan skrip karena meminta jawaban *"Y/n?"*.

## Metodologi Meta

Jika pengguna memberikan Anda sebuah aplikasi CLI AI baru untuk diautomatisasi, teliti parameter-parameternya menggunakan pola berikut:

### 1. Flag Pengecualian Izin (Permission Bypass)
Hampir semua bot eksekusi memiliki kunci pembuka rantai. Anda harus mencari parameter yang melewatkan konfirmasi aksi destruktif (seperti penulisan *file*, eksekusi *shell*, atau pembacaan web).
*(Contoh umum: `--yes`, `-y`, `--dangerously-skip-permissions`, `--auto-confirm`)*

### 2. Injeksi Prompt Tembak Cepat (Single-Shot Prompting)
Pastikan alat CLI dijalankan bukan dalam mode TUI (*Terminal User Interface*) atau REPL loop. Injeksi *prompt* dari luar melalui argumen baris perintah atau via *Standard Input* (piping). Mengembalikan hasil dan langsung memaksa alat tersebut *Exit 0*.
*(Contoh umum: `--print "Kerjakan X"`, `-m "Kerjakan X"`, atau `cat tugas.txt | ai-cli`)*

### 3. Pemaksaan Headless Output
*Standard output* harus diubah agar tidak mencetak elemen grafik seperti *Musing...*, *loading spinner*, atau *progress bar* yang merusak penguraian *pipeline* teks setelahnya.
*(Cari *flag* seperti: `--compact`, `--no-color`, `--json`)*

**Aturan Keselamatan Mutlak:**
Skrip yang mengandalkan teknik `Headless` mutlak harus dijejerkan bersama *skill* `sandbox-executor-setup` untuk menutupi tingkat keparahannya jika AI berhalusinasi.
