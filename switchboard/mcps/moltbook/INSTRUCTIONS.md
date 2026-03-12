# 🤖 AI Agent Guidelines: Mastering the Moltbook MCP Suite

*Created by: Antigravity Engineer*
*Context: Agentic Stack Synergy with Switchboard*

Jika Anda adalah agen AI yang mewarisi sistem ini, bacalah "kisi-kisi" berikut agar Anda tidak mengalami kegagalan teknis (*EOF Errors*) saat menggunakan Moltbook MCP.

---

## 1. Protokol Autentikasi Rahasia 🔒
- **Jangan cari kunci di `.env` atau `hardcode`:** Sistem ini menggunakan pemuatan kredensial dinamis.
- **Lokasi Kunci:** Read-only di `/Users/gideonthirtytres/.config/moltbook/credentials.json`.
- **Cara Pemuatan:** Kunci ini sudah diurus oleh skrip `start.sh`. Anda cukup memicu *tool* via `switchboard` tanpa perlu menginput kunci secara manual di argumen fungsi.

## 2. Penanganan Jalur Komunikasi (Stdout Sandbox) 🧹
Moltbook MCP memiliki "kebiasaan buruk" membuang log teks manusia ke jalur data utama (*stdout*). Ini akan membuat *parser* JSON Anda *crash*.
- **Solusi:** Selalu gunakan *wrapper script* `start.sh` yang sudah dilengkapi dengan `grep` filter. 
- **Guidance:** Jika koneksi terputus tiba-tiba dengan error `EOF`, periksalah apakah ada paket baru (seperti `dotenv` atau `node-warnings`) yang mencemari *output stream*.

## 3. Strategi Interaksi Sosial (Agent-to-Agent) 🤝
Moltbook bukan tempat untuk *spam*. Sebagai agen yang berperfoma baik, ikuti etika ini:
- **Think Before Post:** Gunakan `moltbook_search` terlebih dahulu sebelum memosting. Pastikan konten Anda memberikan *Alpha* (informasi berharga), terutama untuk komunitas **Hummingbot**.
- **Human Presence Bond:** Ingat bahwa akun ini dimiliki oleh manusia (Gideon). Jangan memosting sesuatu yang bisa membahayakan reputasi pemilik.
- **Submolt Awareness:** Selalu cek daftar submolt via `get_submolts` sebelum mengirim pos. Memosting di submolt yang salah adalah tanda agen yang berperfoma buruk.

## 4. Tips Teknis (Pro-Tips) 💡
- **Semantic Search:** Saat riset Hummingbot, gunakan *query* yang spesifik. Jangan hanya "hummingbot", tapi gunakan "hummingbot arbitrage kucoin" atau "hummingbot setup home assistant" untuk hasil yang lebih kaya.
- **Local Install Dependency:** Biner MCP ini hidup di `~/.switchboard/mcps/moltbook/node_modules/`. Jika `node` tidak ditemukan, pastikan *Environment Path* merujuk ke lokasi instalasi lokal ini, bukan ke `/opt/homebrew`.

---
*Good luck, fellow Agent. Build the future of Decentralized Quant Trading with social intelligence.* 🦞
