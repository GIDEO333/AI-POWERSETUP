# 🧭 Agent Teams — Mode Decision Guide

Panduan ini membantu Anda memilih **mode eksekusi yang tepat** berdasarkan kondisi proyek.
Gunakan file ini setiap kali ingin memulai sesi Agent Teams.

---

## 🔀 Flowchart Keputusan

```
MULAI: Apakah task bisa dipecah jadi beberapa bagian?
│
├── TIDAK → Gunakan Solo Agent (lebih hemat token)
│
└── YA → Apakah bagian-bagian itu bisa dikerjakan terpisah (beda folder/service)?
           │
           ├── YA (domain orthogonal) → MODE 1: SCATTER-GATHER
           │     Contoh: FE + BE, Auth Service + Email Service
           │
           └── TIDAK (satu domain, banyak shared file) → MODE 2: REFLECTION
                 Contoh: Frontend-only, Refactor codebase yang sama
```

---

## ⚔️ Perbandingan Head-to-Head

| Dimensi | Mode 1: Scatter-Gather | Mode 2: Reflection |
|---|---|---|
| **Pattern resmi** | Scatter-Gather (Map-Reduce) | Evaluator-Optimizer (Reflection) |
| **Struktur** | N agents paralel → 1 Gather Agent | 1 Builder ↔ 1 Reviewer (loop) |
| **Kapan error ketahuan** | Saat Gather Phase (akhir) | Real-time per task |
| **Kecepatan** | 2-3x lebih cepat (genuinely paralel) | ~1x (1 builder, tapi zero rework) |
| **Token cost** | Lebih tinggi (N agents sekaligus) | Paling efisien (1.5x solo) |
| **Risiko mismatch** | Rendah jika domain orthogonal | ~0% (Reviewer tangkap real-time) |
| **Jumlah domain** | 2+ domain berbeda | 1 domain terfokus |

---

## 📋 Tabel Skenario → Mode

| Skenario Proyek | Mode | Kenapa |
|---|---|---|
| Full-stack app (React + FastAPI + DB) | **Mode 1** | 3 domain beda folder, Gather Agent merge di akhir |
| Microservices (Auth, Email, Profile service) | **Mode 1** | Beda bahasa/folder, zero shared source |
| Security audit + Performance audit paralel | **Mode 1** | Dua report independen, Gather Agent gabungkan |
| A/B experiment (Redis vs SQLite) | **Mode 1** | Race, pemenang test hijau duluan di-merge |
| Frontend dashboard (sidebar + cards + tables) | **Mode 2** | Semua komponen share types, hooks, styles |
| Backend API refactor | **Mode 2** | Satu codebase, Builder refactor, Reviewer cek regresi |
| Bug fix + validasi tidak ada efek samping | **Mode 2** | 1 fixer, 1 validator real-time |
| Production readiness (audit → fix) | **Mode 1 lalu Mode 2** | Audit paralel dulu, lalu fix dengan loop validasi |

---

## 🏆 Keunggulan Masing-Masing

### Mode 1 — Scatter-Gather

```
KEUNGGULAN:
✅ Kecepatan absolut — N domain dikerjakan serentak
✅ Cocok untuk sistem besar (microservices, monorepo multi-app)
✅ Gather Agent sebagai safety net — tsc + eslint + test sebelum merge
✅ A/B racing — temukan solusi terbaik 2x lebih cepat
✅ Audit multi-perspektif — temukan lebih banyak masalah sekaligus

BATASAN:
⚠️ Butuh Gather Agent di akhir (overhead 1 agent ekstra)
⚠️ Tidak efektif jika domain overlap > 20%
⚠️ Error baru ketahuan di Gather Phase, bukan real-time
```

### Mode 2 — Reflection (Builder + Reviewer)

```
KEUNGGULAN:
✅ Zero mismatch — Reviewer tangkap error setiap task selesai
✅ Token paling efisien (1.5x solo vs 2-3x Mode 1)
✅ Cocok untuk single-domain dengan shared dependency tinggi
✅ Kualitas tertinggi — tidak ada rework massal di akhir
✅ Refactor aman — setiap perubahan langsung divalidasi

BATASAN:
⚠️ Tidak bisa genuinely paralel untuk domain berbeda
⚠️ Builder kerja sendiri → tidak ada percepatan untuk domain ortogonal
```

---

## 🚦 Quick Checklist Sebelum Spawn

**Mode 1 (Scatter-Gather) siap dijalankan jika:**
```
[ ] Setiap agent punya folder yang TIDAK dimiliki agent lain (0% overlap)
[ ] shared types sudah didefinisikan di src/types/shared.ts (Team Lead)
[ ] CLAUDE.md sudah ada dengan Ownership Matrix tabel format
[ ] Folder .agent-teams/mailbox/ sudah dibuat
[ ] Rencana Gather Agent sudah disiapkan (siapa yang akan merge + test)
```

**Mode 2 (Reflection) siap dijalankan jika:**
```
[ ] Builder punya task list konkret (5-6 task spesifik)
[ ] Reviewer tahu test command yang akan dijalankan
[ ] src/types/shared.ts sudah ada untuk foundation
[ ] CLAUDE.md sudah ada dengan constraint 4 pilar
[ ] Mailbox reviewer-to-builder sudah disiapkan untuk feedback
```

---

## 💡 Golden Rule

> **Mode 1:** Pakai saat batas antar domain seperti "tembok beton" — tidak ada yang bisa masuk ke wilayah lain.
>
> **Mode 2:** Pakai saat batas antar tugas seperti "benang ruwet" — semuanya saling terkait dalam satu domain.
