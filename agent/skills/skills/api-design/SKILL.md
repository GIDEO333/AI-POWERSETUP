---
name: api-design
description: Design clean, consistent, and scalable REST APIs or GraphQL schemas. Use when the user is creating a new API endpoint or designing a backend service.
category: Dev
---

# API Design

## REST API Best Practices

### URL Structure
```
GET    /users          → list all users
POST   /users          → create a user
GET    /users/:id      → get one user
PUT    /users/:id      → replace a user
PATCH  /users/:id      → update specific fields
DELETE /users/:id      → delete a user
```

### Response Format
```json
{
  "data": { ... },
  "error": null,
  "meta": { "page": 1, "total": 100 }
}
```

### HTTP Status Codes
| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content (DELETE success) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Unprocessable Entity |
| 500 | Server Error |

## Checklist for New Endpoints

- [ ] Clear, consistent URL naming (nouns, not verbs)
- [ ] Input validation with clear error messages
- [ ] Authentication + authorization checks
- [ ] Pagination for list endpoints
- [ ] Rate limiting consideration
- [ ] Response documented (OpenAPI/Swagger)
- [ ] Error cases handled and return useful messages
