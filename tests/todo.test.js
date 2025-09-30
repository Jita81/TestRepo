const request = require('supertest');
const app = require('../backend/server');
const pool = require('../backend/config/database');
const Todo = require('../backend/models/Todo');

describe('Todo API Tests', () => {
    let testTodoId;

    // Setup: Clear database before tests
    beforeAll(async () => {
        await pool.query('DELETE FROM todos');
    });

    // Cleanup: Clear database after tests
    afterAll(async () => {
        await pool.query('DELETE FROM todos');
        await pool.end();
    });

    describe('GET /api/health', () => {
        test('should return health check status', async () => {
            const response = await request(app).get('/api/health');
            
            expect(response.status).toBe(200);
            expect(response.body).toHaveProperty('success', true);
            expect(response.body).toHaveProperty('message', 'Server is running');
        });
    });

    describe('POST /api/todos', () => {
        test('should create a new todo with valid description', async () => {
            const todoData = {
                description: 'Test todo item'
            };

            const response = await request(app)
                .post('/api/todos')
                .send(todoData);

            expect(response.status).toBe(201);
            expect(response.body.success).toBe(true);
            expect(response.body.data).toHaveProperty('id');
            expect(response.body.data.description).toBe(todoData.description);
            expect(response.body.data.completed).toBe(false);
            expect(response.body.data).toHaveProperty('created_at');

            // Save ID for later tests
            testTodoId = response.body.data.id;
        });

        test('should reject empty description', async () => {
            const response = await request(app)
                .post('/api/todos')
                .send({ description: '' });

            expect(response.status).toBe(400);
            expect(response.body.success).toBe(false);
        });

        test('should reject missing description', async () => {
            const response = await request(app)
                .post('/api/todos')
                .send({});

            expect(response.status).toBe(400);
            expect(response.body.success).toBe(false);
        });

        test('should reject description exceeding max length', async () => {
            const longDescription = 'a'.repeat(501);
            const response = await request(app)
                .post('/api/todos')
                .send({ description: longDescription });

            expect(response.status).toBe(400);
            expect(response.body.success).toBe(false);
        });

        test('should handle special characters in description', async () => {
            const specialChars = 'Test <script>alert("xss")</script> & "quotes"';
            const response = await request(app)
                .post('/api/todos')
                .send({ description: specialChars });

            expect(response.status).toBe(201);
            expect(response.body.success).toBe(true);
        });
    });

    describe('GET /api/todos', () => {
        test('should return all todos', async () => {
            const response = await request(app).get('/api/todos');

            expect(response.status).toBe(200);
            expect(response.body.success).toBe(true);
            expect(Array.isArray(response.body.data)).toBe(true);
            expect(response.body.data.length).toBeGreaterThan(0);
            expect(response.body).toHaveProperty('count');
        });

        test('should return todos in descending order by creation date', async () => {
            const response = await request(app).get('/api/todos');
            const todos = response.body.data;

            if (todos.length > 1) {
                const firstDate = new Date(todos[0].created_at);
                const secondDate = new Date(todos[1].created_at);
                expect(firstDate.getTime()).toBeGreaterThanOrEqual(secondDate.getTime());
            }
        });
    });

    describe('GET /api/todos/:id', () => {
        test('should return a specific todo by ID', async () => {
            const response = await request(app).get(`/api/todos/${testTodoId}`);

            expect(response.status).toBe(200);
            expect(response.body.success).toBe(true);
            expect(response.body.data.id).toBe(testTodoId);
        });

        test('should return 404 for non-existent todo', async () => {
            const fakeId = '123e4567-e89b-12d3-a456-426614174000';
            const response = await request(app).get(`/api/todos/${fakeId}`);

            expect(response.status).toBe(404);
            expect(response.body.success).toBe(false);
        });

        test('should return 400 for invalid UUID format', async () => {
            const response = await request(app).get('/api/todos/invalid-id');

            expect(response.status).toBe(400);
            expect(response.body.success).toBe(false);
        });
    });

    describe('PUT /api/todos/:id', () => {
        test('should update todo completion status', async () => {
            const response = await request(app)
                .put(`/api/todos/${testTodoId}`)
                .send({ completed: true });

            expect(response.status).toBe(200);
            expect(response.body.success).toBe(true);
            expect(response.body.data.completed).toBe(true);
        });

        test('should update todo description', async () => {
            const newDescription = 'Updated todo description';
            const response = await request(app)
                .put(`/api/todos/${testTodoId}`)
                .send({ description: newDescription });

            expect(response.status).toBe(200);
            expect(response.body.success).toBe(true);
            expect(response.body.data.description).toBe(newDescription);
        });

        test('should update both description and completed status', async () => {
            const updates = {
                description: 'Another update',
                completed: false
            };
            const response = await request(app)
                .put(`/api/todos/${testTodoId}`)
                .send(updates);

            expect(response.status).toBe(200);
            expect(response.body.success).toBe(true);
            expect(response.body.data.description).toBe(updates.description);
            expect(response.body.data.completed).toBe(updates.completed);
        });

        test('should return 404 for non-existent todo', async () => {
            const fakeId = '123e4567-e89b-12d3-a456-426614174000';
            const response = await request(app)
                .put(`/api/todos/${fakeId}`)
                .send({ completed: true });

            expect(response.status).toBe(404);
            expect(response.body.success).toBe(false);
        });

        test('should reject invalid completion value', async () => {
            const response = await request(app)
                .put(`/api/todos/${testTodoId}`)
                .send({ completed: 'invalid' });

            expect(response.status).toBe(400);
            expect(response.body.success).toBe(false);
        });

        test('should reject empty description update', async () => {
            const response = await request(app)
                .put(`/api/todos/${testTodoId}`)
                .send({ description: '' });

            expect(response.status).toBe(400);
            expect(response.body.success).toBe(false);
        });
    });

    describe('DELETE /api/todos/:id', () => {
        let todoToDelete;

        beforeEach(async () => {
            // Create a todo to delete
            const response = await request(app)
                .post('/api/todos')
                .send({ description: 'Todo to delete' });
            todoToDelete = response.body.data.id;
        });

        test('should delete a todo', async () => {
            const response = await request(app).delete(`/api/todos/${todoToDelete}`);

            expect(response.status).toBe(200);
            expect(response.body.success).toBe(true);

            // Verify it's actually deleted
            const getResponse = await request(app).get(`/api/todos/${todoToDelete}`);
            expect(getResponse.status).toBe(404);
        });

        test('should return 404 when deleting non-existent todo', async () => {
            const fakeId = '123e4567-e89b-12d3-a456-426614174000';
            const response = await request(app).delete(`/api/todos/${fakeId}`);

            expect(response.status).toBe(404);
            expect(response.body.success).toBe(false);
        });
    });

    describe('DELETE /api/todos/completed/all', () => {
        beforeEach(async () => {
            // Create some completed todos
            await request(app).post('/api/todos').send({ description: 'Completed 1' });
            await request(app).post('/api/todos').send({ description: 'Completed 2' });
            
            // Get all todos and mark them as completed
            const todosResponse = await request(app).get('/api/todos');
            const todos = todosResponse.body.data;
            
            for (const todo of todos) {
                await request(app)
                    .put(`/api/todos/${todo.id}`)
                    .send({ completed: true });
            }
        });

        test('should delete all completed todos', async () => {
            const response = await request(app).delete('/api/todos/completed/all');

            expect(response.status).toBe(200);
            expect(response.body.success).toBe(true);
            expect(response.body.count).toBeGreaterThan(0);

            // Verify they're deleted
            const todosResponse = await request(app).get('/api/todos');
            const completedTodos = todosResponse.body.data.filter(t => t.completed);
            expect(completedTodos.length).toBe(0);
        });
    });

    describe('Error Handling', () => {
        test('should handle 404 for unknown routes', async () => {
            const response = await request(app).get('/api/unknown');

            expect(response.status).toBe(404);
            expect(response.body.success).toBe(false);
        });

        test('should handle invalid JSON in request body', async () => {
            const response = await request(app)
                .post('/api/todos')
                .set('Content-Type', 'application/json')
                .send('invalid json');

            expect(response.status).toBe(400);
        });
    });

    describe('Todo Model Tests', () => {
        test('should create a todo using model', async () => {
            const todo = await Todo.create({ description: 'Model test todo' });

            expect(todo).toHaveProperty('id');
            expect(todo.description).toBe('Model test todo');
            expect(todo.completed).toBe(false);
        });

        test('should find all todos using model', async () => {
            const todos = await Todo.findAll();

            expect(Array.isArray(todos)).toBe(true);
        });

        test('should find todo by ID using model', async () => {
            const created = await Todo.create({ description: 'Find by ID test' });
            const found = await Todo.findById(created.id);

            expect(found).toBeTruthy();
            expect(found.id).toBe(created.id);
        });

        test('should update todo using model', async () => {
            const created = await Todo.create({ description: 'Update test' });
            const updated = await Todo.update(created.id, { completed: true });

            expect(updated.completed).toBe(true);
        });

        test('should delete todo using model', async () => {
            const created = await Todo.create({ description: 'Delete test' });
            const deleted = await Todo.delete(created.id);

            expect(deleted).toBe(true);

            const found = await Todo.findById(created.id);
            expect(found).toBeNull();
        });
    });
});