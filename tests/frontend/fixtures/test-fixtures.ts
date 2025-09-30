import { test as base, expect } from '@playwright/test';
import { TodoPage } from '../pages/TodoPage';
import todosData from './todos.json';

/**
 * Test fixture types
 */
type TodoFixtures = {
  todoPage: TodoPage;
  sampleTasks: any[];
  edgeCaseTasks: any[];
  bulkTasks: any[];
};

/**
 * Extended Playwright test with custom fixtures
 */
export const test = base.extend<TodoFixtures>({
  /**
   * TodoPage fixture - automatically creates page object
   */
  todoPage: async ({ page }, use) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    // Clear storage before each test
    await todoPage.clearStorage();
    await use(todoPage);
  },
  
  /**
   * Sample tasks fixture
   */
  sampleTasks: async ({}, use) => {
    await use(todosData.sampleTasks);
  },
  
  /**
   * Edge case tasks fixture
   */
  edgeCaseTasks: async ({}, use) => {
    await use(todosData.edgeCaseTasks);
  },
  
  /**
   * Bulk tasks fixture
   */
  bulkTasks: async ({}, use) => {
    await use(todosData.bulkTasks);
  },
});

export { expect };