---
name: session-memory
description: Saves the decisions, insights, and completed tasks from the active chat session into the persistent declarative memory log (~/.agent/memory). 
  Invoked when user says "simpan sesi ini", "record session", "save memory",
  "catat keputusan hari ini", "ingat sesi kita", "buat ringkasan memori".
---

# Session Memory: The Declarative History Keeper

## Kapan Digunakan

- Saat sesi kerja / eksperimen / diskusi hampir selesai dan dirasa produktif.
- Saat user menyuruh agent "simpan sesi ini" agar tidak kehilangan konteks (keputusan/ide).

## Aturan Kompresi (Maximum 10 Lines)

Memori jangka panjang tidak boleh membengkak. Saat di-invoke, kamu HARUS merangkum percakapan saat ini ke format yang ekstrim padat tapi penuh *Semantic Value*:
1. **Built/Fixed:** Apa yang KONKRET dibuat atau diperbaiki di chat ini.
2. **Decisions:** Keputusan *Trade-off* yang diambil dan MENGAPA.
3. **Gotchas:** Pembelajaran (error/hallucination yang dicegah).

## Format Penulisan

Kumpulkan summary di memori kerjamu, lalu jalankan command bash untuk `append` (tambahkan ke ujung file) ke `~/.agent/memory/session-log.md`.

```bash
cat << 'EOF' >> ~/.agent/memory/session-log.md

### Session: YYYY-MM-DD | [Judul Topik yang Bahas]
- **Built**: [e.g. Skill llm-eval-arena]
- **Decisions**: [e.g. Memilih agent-native evaluation over API]
- **Gotchas**: [e.g. Parameter 'weight' GEval adalah halusinasi]

EOF
```

## Secondary Routing (Domain-Specific Context)
Selain master log di atas, jika sesi ini memiliki fokus Domain spesifik, kamu juga DIWAJIBKAN men-copy summary yang sama (di-append) ke salah satu file di folder `~/.agent/memory/topics/`:

*   Jika bahas HFT/Backtest/Data pipeline → append ke `quant-trading.md`
*   Jika bahas System Design/Otomatisasi Agent → append ke `architecture.md`
*   Jika bahas Pembuatan Skill baru → append ke `skills-built.md`

Gunakan bash command `echo` atau `cat` sama seperti di atas.

## Error Handling
- Jika master folder `~/.agent/memory/` belum ada, jalankan `mkdir -p ~/.agent/memory/topics` sebelum append.
- Jika ringkasanmu melebihi 10 baris, PAKSA kompres jadi lebih pendek sebelum di-append.

## Output ke User (Terminal/Chat)
Setelah berhasil *save*, beri tahu user dengan *success message*:
> ✅ Memori sesi berhasil di-compress dan dicatat ke `session-log.md` (dan kategori topik: X). Agent akan mengingat keputusan ini di masa depan!
