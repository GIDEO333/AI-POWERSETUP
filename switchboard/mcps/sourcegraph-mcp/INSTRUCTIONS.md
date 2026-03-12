# Sourcegraph MCP — Agent Instructions

## When to USE this tool
- Refactoring besar: perlu tahu "bagaimana project besar lain melakukannya"
- Mengimplementasikan library baru yang belum familiar
- Debugging edge case yang sangat spesifik, butuh bukti dari codebase lain
- Mencari contoh pattern tertentu di repo terkenal (e.g., "how does Next.js handle X")

## When NOT to use
- Sudah tahu cara implementasinya → langsung coding
- Searching di project lokal → pakai `grep_search` atau `find_by_name`
- Query terlalu umum (e.g., "sort array") → hasilnya tidak berguna

## Anti-Bloat Rules (WAJIB DIPATUHI)
1. SELALU gunakan query spesifik dengan `repo:` filter
2. Hasil SUDAH dibatasi otomatis ke 5 matches oleh bridge
3. Baca file satu-per-satu, JANGAN minta seluruh repo
4. Jika 0 results, perbaiki query, JANGAN ulangi query yang sama
5. Maksimal 3 panggilan search per sesi kerja

## Query Examples
❌ `search_code("useEffect")`
✅ `search_code("useEffect cleanup WebSocket disconnect repo:vercel/next.js")`

❌ `search_code("database connection")`
✅ `search_code("pg.Pool idleTimeoutMillis repo:expressjs/express")`
