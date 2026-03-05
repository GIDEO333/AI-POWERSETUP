---
name: database-query
description: Write, optimize, and debug SQL queries and ORM calls. Use when the user needs to fetch data, design schema, or fix slow queries.
category: Dev
---

# Database Query

## Common SQL Patterns

### Aggregation
```sql
SELECT category, COUNT(*) as total, AVG(price) as avg_price
FROM products
WHERE active = true
GROUP BY category
HAVING COUNT(*) > 10
ORDER BY total DESC;
```

### Joins
```sql
-- Get users with their latest order
SELECT u.id, u.name, o.created_at as last_order
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.id = (
    SELECT id FROM orders 
    WHERE user_id = u.id 
    ORDER BY created_at DESC LIMIT 1
);
```

### Upsert (PostgreSQL)
```sql
INSERT INTO settings (user_id, key, value)
VALUES ($1, $2, $3)
ON CONFLICT (user_id, key)
DO UPDATE SET value = EXCLUDED.value;
```

## Query Optimization Checklist

- [ ] Is there an index on the WHERE/JOIN columns?
- [ ] Use `EXPLAIN ANALYZE` to see query plan
- [ ] Avoid `SELECT *` — select only needed columns
- [ ] Avoid N+1: use JOINs or `IN` clauses instead of loops
- [ ] Use pagination (`LIMIT`/`OFFSET` or cursor-based)

## Schema Design Principles

- Use `id` (auto-increment or UUID) as primary key
- Always add `created_at`, `updated_at` timestamps
- Foreign keys should have indexes
- Normalize to 3NF unless performance requires denormalization
