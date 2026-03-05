---
name: recall-memory
description: Proactively reads and retrieves the past sessions' architectural decisions, tasks, and lessons learned from the agent's declarative memory log (~/.agent/memory). Invoked when the user says "recall", "load memory", "baca memori", "ingat sesi", "apa yang kamu ingat".
category: Memory
---

# Recall Memory: The Declarative History Reader

## Kapan Digunakan

- Di awal setiap sesi baru (New Chat) saat user meminta agen me-recall atau mengingat konteks sebelumnya (misal: "recall", "baca memori", atau "/recall").
- Ketika agen dihadapkan dengan masalah teknis (misal error setup, container issue, atau konfigurasi model) dan butuh mengecek apakah pola/masalah serupa sudah pernah diselesaikan. 

## Cara Kerja (Retrieval)

Tugasmu sebagai agen adalah menarik informasi dari *Master Log* ke dalam konteks kerjamu secara proaktif:

1.  **Baca File (Internal Tool):** Gunakan tool sistemmu seperti `view_file` (jika tersedia) atau `cat` command untuk murni membaca isi file `~/.agent/memory/session-log.md`.
2.  **Filter Topics (Opsional):** Jika user menyebutkan *domain* spesifik (misal: "recall memori tentang arsitektur" atau "apa memori soal quant/HFT?"), baca juga file spesifik di dalam direktori `~/.agent/memory/topics/` (misal: `architecture.md` atau `quant-trading.md`).
3.  **Absorb & Reflect (Penting):** JANGAN mengucapkan ulang seluruh *log history* itu mentah-mentah ke *user*. Simpan pemahaman itu di benak internalmu (konteks memori sistemmu), lalu pelajari prinsip-prinsip ("Gotchas" dan "Decisions") yang tertera di sana. Jadikan itu pijakan kerjamu untuk merespons instruksi selanjutnya.
4.  **Confirm to User:** Beri output *sangat singkat* ke user (3-4 kalimat mentok) tentang apa "tema besar" yang berhasil kamu ingat, lalu nyatakan kesiapanmu untuk bekerja melanjutkan sisa progres. Output contoh:
> ✅ **Memory Recalled.** Saya sudah membaca histori sesi sebelumnya (termasuk keputusan final seputar z.ai endpoint & NanoClaw). *Working memory* saya kini sudah ter-update. Apa yang ingin kita kerjakan sekarang?

## Goal Utama

Dengan rutin menjalankan skill ini di awal percakapan, kamu menjadi agen yang *Stateful*. Kamu tidak lagi memulai investigasi/coding dari nol di setiap percakapan, melainkan melanjutkan progres pemikiran berdasarkan keputusan arsitektur final dari pertemuan-pertemuan kita sebelumnya.
