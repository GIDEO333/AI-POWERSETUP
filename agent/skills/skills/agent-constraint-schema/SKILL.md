---
name: agent-constraint-schema
description: Teknik perancangan arsitektur profil JSON cerdas yang mengekang AI dengan batasan token, pelarangan bash mandek, dan injeksi mesin status putus asa (Escalation Break).
category: AI-Orchestration
---

# Agent Constraint Schema Design

## Tujuan
Mengekang keliaran model dasar (LLM) di dalam lingkungan eksekusi bebas dengan menyuntikkan dokumen instruksi level sistem (biasanya file konfigurasi berformat JSON/YAML/XML) yang merinci larangan fatal secara absolut.

## Konsep "The Strict Envelope"
Ketika merancang "Otak Pekerja" (profil konfigurasi agen kustom), gunakan prinsip **Meta-Prompt berbasis TypeScript Schema** atau XML untuk menanamkan kepatuhan logis yang tidak dapat dinegosiasikan oleh model.

### 4 Pilar Wajib (Bisa diterapkan di Prompt System AI manapun):

1. **Anti-Bleeding Reasoning**
   Pangkas pikiran *rambling*/mengigau dari LLM.
   *Contoh implementasi meta:* "Anda dibatasi maksimal 3 kalimat saat menjelaskan tindakan Anda (*chain of thought*). Lebih dari itu dianggap sebagai kegagalan sistematis."

2. **The Execution First Directive**
   Gunakan instruksi negasi absolut untuk mematikan sifat "Sok Tahu" dari AI *coding*.
   *Contoh meta:* "Penggunaan placeholder code seperti `// TODO: Implement logic` adalah KEHARAMAN MUTLAK. Konteks yang hilang tidak boleh ditebak, Anda harus menggunakan alat baca *filesystem*."

3. **Anti-Hanging Logic (Larangan Konstan)**
   Mencegah agen menjebak terminal dalam *infinite stream* dengan melarang keras pembukaan server.
   *Contoh meta:* "MENJALANKAN PERINTAH NON-TERMINATING (server web, *daemon* OS, *auto-watch build*) ADALAH LARANGAN KERAS. Seluruh komando sistem WAJIB mengembalikan kode *Exit 0* secara instan."

4. **Klausa Menyerah Dini (The Escalate Rule)**
   Tutup lubang *infinite-retry loop* di mana AI terus-menerus mencoba teknik *brute force* yang memecahkan kesalahan sintaks tanpa arah.
   *Contoh meta:* "Sistem ini merawat mesin hitung kegagalan. Jika kompilasi kode yang Anda buat gagal lebih dari 3 kali berturut-turut, ANDA WAJIB berhenti seketika, menghentikan seluruh upaya perbaikan otomatis, dan mencetak kalimat 'ESCALATION REQUIRED'."
