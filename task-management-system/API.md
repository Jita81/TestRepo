# 📡 API Documentation

Complete API reference for the Task Management System.

## Base URL

```
Development: http://localhost:3000/api
Production: https://api.yourdomain.com/api
```

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

## Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## Rate Limiting

- **Authentication endpoints**: 10 requests per 15 minutes
- **API endpoints**: 100 requests per 15 minutes
- **WebSocket messages**: 60 messages per minute

## Endpoints

---

## Authentication

### Register User

Creates a new user account.

**Endpoint:** `POST /api/auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword123",
  "firstName": "John",
  "lastName": "Doe"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "username": "johndoe",
      "firstName": "John",
      "lastName": "Doe",
      "role": "member"
    },
    "accessToken": "eyJhbGc...",
    "refreshToken": "eyJhbGc..."
  }
}
```

**Errors:**
- `400` - Validation error or duplicate email/username
- `500` - Server error

---

### Login

Authenticates a user and returns tokens.

**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "username": "johndoe",
      "firstName": "John",
      "lastName": "Doe",
      "role": "member",
      "avatarUrl": null
    },
    "accessToken": "eyJhbGc...",
    "refreshToken": "eyJhbGc..."
  }
}
```

**Errors:**
- `401` - Invalid credentials
- `403` - Account disabled

---

### Refresh Token

Gets a new access token using refresh token.

**Endpoint:** `POST /api/auth/refresh`

**Request Body:**
```json
{
  "refreshToken": "eyJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGc...",
    "refreshToken": "eyJhbGc..."
  }
}
```

**Errors:**
- `400` - Refresh token required
- `401` - Invalid or expired refresh token

---

### Get Current User

Gets the authenticated user's profile.

**Endpoint:** `GET /api/auth/me`

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "johndoe",
    "firstName": "John",
    "lastName": "Doe",
    "role": "member",
    "avatarUrl": null,
    "lastSeenAt": "2024-01-01T12:00:00.000Z",
    "createdAt": "2024-01-01T00:00:00.000Z"
  }
}
```

**Errors:**
- `401` - Unauthorized

---

### Logout

Revokes the refresh token.

**Endpoint:** `POST /api/auth/logout`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "refreshToken": "eyJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## Projects

### Get All Projects

Gets all projects the user is a member of.

**Endpoint:** `GET /api/projects`

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Project Name",
      "description": "Project description",
      "owner_id": "uuid",
      "owner_username": "johndoe",
      "status": "active",
      "user_role": "admin",
      "member_count": 5,
      "task_count": 20,
      "completed_task_count": 15,
      "created_at": "2024-01-01T00:00:00.000Z",
      "updated_at": "2024-01-01T12:00:00.000Z"
    }
  ]
}
```

---

### Get Project by ID

Gets a specific project.

**Endpoint:** `GET /api/projects/:id`

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Project Name",
    "description": "Project description",
    "owner_id": "uuid",
    "owner_username": "johndoe",
    "status": "active",
    "member_count": 5,
    "task_count": 20,
    "created_at": "2024-01-01T00:00:00.000Z",
    "updated_at": "2024-01-01T12:00:00.000Z"
  }
}
```

**Errors:**
- `403` - Access denied
- `404` - Project not found

---

### Create Project

Creates a new project.

**Endpoint:** `POST /api/projects`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "New Project",
  "description": "Project description"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "New Project",
    "description": "Project description",
    "owner_id": "uuid",
    "status": "active",
    "created_at": "2024-01-01T00:00:00.000Z",
    "updated_at": "2024-01-01T00:00:00.000Z"
  }
}
```

**Errors:**
- `400` - Validation error

---

### Update Project

Updates a project (admin only).

**Endpoint:** `PUT /api/projects/:id`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "status": "active"
}
```

**Response:** `200 OK`

**Errors:**
- `403` - Access denied (not admin)
- `404` - Project not found

---

### Delete Project

Deletes a project (owner only).

**Endpoint:** `DELETE /api/projects/:id`

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Project deleted successfully"
}
```

**Errors:**
- `403` - Access denied (not owner)
- `404` - Project not found

---

### Get Project Members

Gets all members of a project.

**Endpoint:** `GET /api/projects/:id/members`

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe",
      "avatar_url": null,
      "last_seen_at": "2024-01-01T12:00:00.000Z",
      "project_role": "admin",
      "joined_at": "2024-01-01T00:00:00.000Z"
    }
  ]
}
```

---

### Add Project Member

Adds a member to a project (admin only).

**Endpoint:** `POST /api/projects/:id/members`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "userId": "uuid",
  "role": "member"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Member added successfully"
}
```

**Errors:**
- `400` - User already a member
- `403` - Access denied (not admin)
- `404` - User not found

---

## Tasks

### Get Project Tasks

Gets all tasks for a project with optional filters.

**Endpoint:** `GET /api/tasks/project/:projectId`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `status` (optional) - Filter by status (todo, in_progress, review, done, blocked)
- `assignedTo` (optional) - Filter by assigned user ID
- `priority` (optional) - Filter by priority (low, medium, high, urgent)

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "project_id": "uuid",
      "title": "Task title",
      "description": "Task description",
      "status": "todo",
      "priority": "medium",
      "assigned_to": "uuid",
      "created_by": "uuid",
      "due_date": "2024-01-10T00:00:00.000Z",
      "completed_at": null,
      "position": 0,
      "created_by_username": "johndoe",
      "created_by_avatar": null,
      "assigned_to_username": "janedoe",
      "assigned_to_avatar": null,
      "comment_count": 3,
      "created_at": "2024-01-01T00:00:00.000Z",
      "updated_at": "2024-01-01T12:00:00.000Z"
    }
  ]
}
```

---

### Get Task by ID

Gets a specific task.

**Endpoint:** `GET /api/tasks/:id`

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`

**Errors:**
- `403` - Access denied
- `404` - Task not found

---

### Get My Tasks

Gets tasks assigned to the current user.

**Endpoint:** `GET /api/tasks/assigned/me`

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`

---

### Create Task

Creates a new task.

**Endpoint:** `POST /api/tasks`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "projectId": "uuid",
  "title": "New task",
  "description": "Task description",
  "status": "todo",
  "priority": "medium",
  "assignedTo": "uuid",
  "dueDate": "2024-01-10T00:00:00.000Z"
}
```

**Response:** `201 Created`

**Errors:**
- `400` - Validation error
- `403` - Access denied to project

---

### Update Task

Updates a task.

**Endpoint:** `PUT /api/tasks/:id`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Updated title",
  "status": "in_progress",
  "priority": "high",
  "assignedTo": "uuid",
  "dueDate": "2024-01-15T00:00:00.000Z"
}
```

**Response:** `200 OK`

**Errors:**
- `403` - Access denied
- `404` - Task not found

---

### Delete Task

Deletes a task.

**Endpoint:** `DELETE /api/tasks/:id`

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```

**Errors:**
- `403` - Access denied (not creator or admin)
- `404` - Task not found

---

### Get Task Statistics

Gets task statistics for a project.

**Endpoint:** `GET /api/tasks/project/:projectId/statistics`

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "total": 50,
    "todo": 15,
    "in_progress": 10,
    "review": 5,
    "done": 18,
    "blocked": 2,
    "urgent": 3,
    "high": 12,
    "overdue": 4
  }
}
```

---

## Comments

### Get Task Comments

Gets all comments for a task.

**Endpoint:** `GET /api/comments/task/:taskId`

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "task_id": "uuid",
      "user_id": "uuid",
      "content": "Comment text",
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe",
      "avatar_url": null,
      "created_at": "2024-01-01T12:00:00.000Z",
      "updated_at": "2024-01-01T12:00:00.000Z"
    }
  ]
}
```

---

### Create Comment

Creates a comment on a task.

**Endpoint:** `POST /api/comments`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "taskId": "uuid",
  "content": "Comment text"
}
```

**Response:** `201 Created`

**Errors:**
- `403` - Access denied to task's project

---

### Update Comment

Updates a comment (owner only).

**Endpoint:** `PUT /api/comments/:id`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "content": "Updated comment text"
}
```

**Response:** `200 OK`

**Errors:**
- `403` - Access denied (not owner)
- `404` - Comment not found

---

### Delete Comment

Deletes a comment (owner only).

**Endpoint:** `DELETE /api/comments/:id`

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Comment deleted successfully"
}
```

**Errors:**
- `403` - Access denied (not owner)
- `404` - Comment not found

---

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `AUTHENTICATION_REQUIRED` | Missing or invalid token |
| `ACCESS_DENIED` | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | Resource not found |
| `DUPLICATE_VALUE` | Unique constraint violation |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INVALID_CREDENTIALS` | Invalid email or password |
| `TOKEN_EXPIRED` | JWT token expired |
| `INVALID_TOKEN` | JWT token invalid |
| `ACCOUNT_DISABLED` | User account is disabled |

---

## WebSocket Events

See [README.md](./README.md#-websocket-events) for complete WebSocket documentation.

---

For support, open an issue on GitHub or contact support@example.com.
