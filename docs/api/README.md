# API Documentation

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.yourdomain.com`

## API Versions

- **v1**: `/api/v1` - Current stable version
- **v2**: `/api/v2` - Future version (if needed)

## Authentication

### JWT Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

### Getting a Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

## Standard Response Format

### Success Response

```json
{
  "success": true,
  "data": { ... },
  "message": "Optional success message",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  },
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### Paginated Response

```json
{
  "success": true,
  "data": {
    "items": [...],
    "meta": {
      "page": 1,
      "page_size": 20,
      "total_items": 100,
      "total_pages": 5,
      "has_next": true,
      "has_previous": false
    }
  }
}
```

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 500 | Internal Server Error |

## Error Codes

| Code | Description |
|------|-------------|
| `BAD_REQUEST` | Invalid request |
| `UNAUTHORIZED` | Authentication required |
| `FORBIDDEN` | Access denied |
| `NOT_FOUND` | Resource not found |
| `CONFLICT` | Resource conflict |
| `VALIDATION_ERROR` | Input validation failed |
| `DOMAIN_VALIDATION_ERROR` | Business rule violation |
| `DATABASE_ERROR` | Database operation failed |

## Pagination

All list endpoints support pagination:

**Query Parameters:**
- `page` (integer, default: 1) - Page number
- `page_size` (integer, default: 20, max: 100) - Items per page

**Example:**
```
GET /api/v1/users?page=2&page_size=50
```

## Filtering and Sorting

**Filtering:**
```
GET /api/v1/users?is_active=true&role=admin
```

**Sorting:**
```
GET /api/v1/users?sort=created_at&order=desc
```

## Rate Limiting

- **Authenticated**: 1000 requests per hour
- **Anonymous**: 100 requests per hour

Headers returned with each request:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640000000
```

## API Endpoints

### User Management

#### Create User
```http
POST /api/v1/users
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Get User
```http
GET /api/v1/users/{user_id}
```

#### Update User
```http
PUT /api/v1/users/{user_id}
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith"
}
```

#### Delete User
```http
DELETE /api/v1/users/{user_id}
```

#### List Users
```http
GET /api/v1/users?page=1&page_size=20
```

### File Management

#### Upload File
```http
POST /api/v1/files
Content-Type: multipart/form-data

file: <binary>
description: "File description"
is_public: false
```

#### Get File
```http
GET /api/v1/files/{file_id}
```

#### Download File
```http
GET /api/v1/files/{file_id}/download
```

#### Delete File
```http
DELETE /api/v1/files/{file_id}
```

#### List Files
```http
GET /api/v1/files?page=1&page_size=20
```

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "contexts": ["user_management", "file_management", "jobs"]
}
```

## OpenAPI Documentation

Interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json