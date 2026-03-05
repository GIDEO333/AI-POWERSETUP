---
name: meta-levelup
description: Elevates a domain-specific solution, script, or workflow into a language-agnostic, universal "Meta-Skill". Extracts core architectural principles from isolated examples.
category: Meta
---

# Meta-Levelup (Abstraction Skill)

## Kapan Digunakan
Ketika *user* memiliki solusi spesifik (misal: *script* Bash untuk menghandle *error* React) dan meminta Anda: *"Jadikan ini meta"*, *"Bawa ke level arsitektur"*, *"Generalisir solusi ini"*, atau *"Abstraksikan agar bisa dipakai di semua framework"*.

## Prinsip "Meta-Leveling"
Proses memisahkan **Implementasi Teknis (How)** dari **Prinsip Arsitektural (Why & What)**. Sebuah Meta-Skill tidak peduli bahasa pemograman apa yang dipakai, ia hanya peduli pada **Pola Desain (Design Pattern)** dan **Batasan Logis (Logical Constraints)**.

## Langkah-Langkah Eksekusi (The Meta-Levelup Process)

### Step 1: Dekonstruksi Spesifik (Deconstruct)
Identifikasi elemen yang mengikat solusi pada satu spesifik *domain/framework*.
- *Kasus:* "Hentikan `npm run dev` agar terminal tidak lag." 
- *Lock-in Element:* `npm run dev`, ekosistem Node.js.

### Step 2: Ekstraksi Pola Inti (Extract Core Pattern)
Apa sebenarnya klasifikasi ilmiah (Ilmu Komputer) dari masalah dan elemen spesifik tersebut?
- *Abstraksi Masalah:* Proses komputasi yang bersifat *non-terminating* (daemon/server) menahan iterasi skrip otomatisasi.

### Step 3: Generalisasi Terminologi (Generalize)
Ubah leksikon sempit menjadi bahasa Arsitektur Sistem tingkat perusahaan.
- Jangan gunakan: `Terminal`, `Bash`, `React`, `Python`.
- Gunakan: `Execution Agent`, `Host Supervisor`, `State Machine`, `Sandboxed Sub-Process`, `Deterministic Termination Guard`.

### Step 4: Rumuskan Prasyarat Agnostik (Agnostic Contract)
Buat "Kontrak Arsitektur". Meta-Skill harus merumuskan solusi hanya berdasarkan prinsip logika.
- *Meta Solution:* "Implementasikan *Time-Bound Supervisor Policy* pada tingkat *Host OS*. Jika sebuah *Sub-Process* melebihi ambang batas komputasi, *Host* memutusnya secara asinkron."

## Format Output ke Pengguna
Bila skill ini dipicu, agen WAJIB mengembalikan *output* dengan kerangka berikut:
1. **The Paradigm Shift:** Penjelasan singkat perubahan sudut pandang (Sempit -> Luas).
2. **Spatial Hierarchy Diagram (Mermaid):** Diagram yang memetakan bagaimana Prinsip Meta menurun menjadi beberapa kemungkinan implementasi di berbagai bahasa.
3. **The Universal Blueprint:** Konsep operasional standar yang bersih dari istilah/nama aplikasi spesifik.
