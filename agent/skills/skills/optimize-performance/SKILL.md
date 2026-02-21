---
name: optimize-performance
description: Identify and fix performance bottlenecks including slow API response times, high latency, sluggish code, aplikasi lemot, lambat, database slowness, high CPU/memory usage, or timeouts. Use when something is slow or needs speed optimization.
---

# Optimize Performance

## Profiling First — Never Guess

### Python
```bash
python -m cProfile -s cumtime your_script.py
# or use py-spy for live profiling:
pip install py-spy && py-spy top --pid <PID>
```

### Node.js
```bash
node --prof app.js
node --prof-process isolate-*.log
```

### Browser (Frontend)
- Open DevTools → Performance tab → Record → Stop → Analyze flame chart

## Common Bottlenecks & Fixes

### Backend
| Problem | Fix |
|---------|-----|
| N+1 queries | Use JOIN or batch fetch (e.g., `select_related` in Django) |
| Missing DB index | `CREATE INDEX ON table(column)` |
| Repeated expensive computation | Cache result (Redis / in-memory) |
| Large payload response | Paginate, use field selection |
| Blocking I/O in async code | Use `asyncio` / non-blocking libraries |

### Frontend
| Problem | Fix |
|---------|-----|
| Large bundle size | Code-split with dynamic imports |
| Unnecessary re-renders | `useMemo`, `useCallback`, `React.memo` |
| Unoptimized images | Use WebP, lazy loading, `next/image` |
| Waterfall requests | Parallel fetch with `Promise.all` |

## Rule of Thumb

1. **Measure** — Get a baseline before changing anything
2. **Profile** — Find the actual hot path
3. **Fix the biggest bottleneck first**
4. **Measure again** — Confirm improvement
5. **Don't over-optimize** — Premature optimization is the root of all evil
