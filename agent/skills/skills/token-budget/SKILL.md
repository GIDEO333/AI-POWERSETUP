---
name: token-budget
description: Hitung dan analisis token overhead dari seluruh stack (MCP, skills, workflows). Bandingkan efisiensi dengan dan tanpa aggregasi. Token budget, context window usage, MCP overhead, context efficiency, cost analysis.
category: Meta
---

# Token Budget — Stack Efficiency Analyzer

## Kapan Digunakan

- User ingin tahu berapa token yang dipakai stack saat ini
- User baru menambah MCP, skill, atau workflow baru dan mau cek dampaknya
- User ingin membandingkan efisiensi: dengan vs tanpa aggregasi
- User mau memastikan stack masih scalable

## Steps

### 1. Hitung MCP Tool Overhead

Untuk setiap MCP server yang terdaftar, hitung estimasi token dari tool definitions:

```
Token per tool ≈ nama (5) + deskripsi (15-30) + inputSchema (30-100)
Rata-rata: ~50-150 token per tool, tergantung jumlah parameter
```

Scan `mcp_config.json` dan hitung jumlah tools per server.

### 2. Hitung Skills Overhead

- Dengan skills-search: overhead TETAP ~80 token (1 tool definition saja)
- Tanpa skills-search: overhead = jumlah_skill × ~100-300 token

Cek jumlah skill saat ini:
```bash
python3 -c "import json; d=json.load(open('agent/skills/skills-index.json')); print(f'{len(d)} skills')"
```

### 3. Hitung Workflow Overhead

- Workflow definitions di system context ≈ 50 token per workflow
- Cek jumlah: `ls ~/.agent/workflows/*.md | wc -l`

### 4. Bandingkan: Dengan vs Tanpa Aggregasi

Buat tabel perbandingan:

```
                          TANPA AGGREGASI     DENGAN AGGREGASI
MCP tools (langsung)      N tools × ~100      Switchboard: ~200 token
Skills (dalam context)    N skills × ~300     skills-search: ~180 token  
Workflows                 sama                sama
────────────────────────────────────────────────────────
TOTAL                     ???? token          ???? token
Penghematan               -                   ????%
```

### 5. Hitung Persentase dari Context Window

```
Context Window:             202,000 token (GLM-4.7)
Total overhead stack:       ???? token
Persentase:                 ????%
Sisa tersedia:              ???? token
```

## Output Format

Output harus berisi:
1. Tabel breakdown per komponen (MCP, skills, workflows)
2. Perbandingan dengan vs tanpa aggregasi
3. Persentase dari context window
4. Estimasi total per sesi (× jumlah prompt)
5. Rekomendasi: apakah stack masih efisien atau perlu optimasi
