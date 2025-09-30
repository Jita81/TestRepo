import { test as base } from '@playwright/test';
import { TodoPage } from '../pages/TodoPage';
import tasksData from './tasks.json';

/**
 * Custom fixtures for Todo List tests
 * Provides TodoPage and test data
 */
type TodoFixtures = {
  todoPage: TodoPage;
  sampleTasks: any[];
  edgeCases: any;
  bulkTasks: any[];
};

export const test = base.extend<TodoFixtures>({
  /**
   * TodoPage fixture - automatically navigates to the app
   */
  todoPage: async ({ page }, use) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    await todoPage.clearLocalStorage();
    await todoPage.reload();
    await use(todoPage);
  },

  /**
   * Sample tasks fixture
   */
  sampleTasks: async ({}, use) => {
    await use(tasksData.sampleTasks);
  },

  /**
   * Edge cases fixture
   */
  edgeCases: async ({}, use) => {
    await use(tasksData.edgeCases);
  },

  /**
   * Bulk tasks fixture
   */
  bulkTasks: async ({}, use) => {
    await use(tasksData.bulkTasks);
  },
});

export { expect } from '@playwright/test';