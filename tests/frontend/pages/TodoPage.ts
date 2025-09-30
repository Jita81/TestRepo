import { Page, Locator, expect } from '@playwright/test';

/**
 * Page Object Model for Todo List Application
 * Provides methods to interact with the todo list UI
 */
export class TodoPage {
  readonly page: Page;
  readonly taskInput: Locator;
  readonly addButton: Locator;
  readonly taskList: Locator;
  readonly taskCounter: Locator;
  readonly inputFeedback: Locator;
  readonly emptyState: Locator;
  readonly appHeader: Locator;

  constructor(page: Page) {
    this.page = page;
    this.taskInput = page.locator('#task-input');
    this.addButton = page.locator('.btn-add');
    this.taskList = page.locator('#task-list');
    this.taskCounter = page.locator('#counter-text');
    this.inputFeedback = page.locator('#input-feedback');
    this.emptyState = page.locator('#empty-state');
    this.appHeader = page.locator('.app-header');
  }

  /**
   * Navigate to the todo list application
   */
  async goto() {
    await this.page.goto('/');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Add a new task
   * @param taskText - The text of the task to add
   */
  async addTask(taskText: string) {
    await this.taskInput.fill(taskText);
    await this.addButton.click();
  }

  /**
   * Add a task by pressing Enter key
   * @param taskText - The text of the task to add
   */
  async addTaskWithEnter(taskText: string) {
    await this.taskInput.fill(taskText);
    await this.taskInput.press('Enter');
  }

  /**
   * Get all task items
   */
  async getTaskItems() {
    return this.taskList.locator('.task-item').all();
  }

  /**
   * Get task item by index (0-based)
   */
  getTaskItem(index: number) {
    return this.taskList.locator('.task-item').nth(index);
  }

  /**
   * Get task item by text content
   */
  getTaskByText(text: string) {
    return this.taskList.locator('.task-item', { hasText: text });
  }

  /**
   * Complete/uncomplete a task by index
   */
  async toggleTaskCompletion(index: number) {
    const task = this.getTaskItem(index);
    await task.locator('.btn-complete').click();
  }

  /**
   * Delete a task by index
   */
  async deleteTask(index: number) {
    const task = this.getTaskItem(index);
    await task.locator('.btn-delete').click();
    // Wait for delete animation
    await this.page.waitForTimeout(350);
  }

  /**
   * Delete a task by text
   */
  async deleteTaskByText(text: string) {
    const task = this.getTaskByText(text);
    await task.locator('.btn-delete').click();
    // Wait for delete animation
    await this.page.waitForTimeout(350);
  }

  /**
   * Check if a task is marked as completed
   */
  async isTaskCompleted(index: number): Promise<boolean> {
    const task = this.getTaskItem(index);
    const classList = await task.getAttribute('class');
    return classList?.includes('completed') ?? false;
  }

  /**
   * Get the number of tasks
   */
  async getTaskCount(): Promise<number> {
    const tasks = await this.getTaskItems();
    return tasks.length;
  }

  /**
   * Get task text by index
   */
  async getTaskText(index: number): Promise<string> {
    const task = this.getTaskItem(index);
    const textElement = task.locator('.task-text');
    return await textElement.textContent() || '';
  }

  /**
   * Get the counter text
   */
  async getCounterText(): Promise<string> {
    return await this.taskCounter.textContent() || '';
  }

  /**
   * Get feedback message
   */
  async getFeedbackMessage(): Promise<string> {
    return await this.inputFeedback.textContent() || '';
  }

  /**
   * Get feedback type (error, success, warning)
   */
  async getFeedbackType(): Promise<string> {
    const classList = await this.inputFeedback.getAttribute('class');
    if (classList?.includes('error')) return 'error';
    if (classList?.includes('success')) return 'success';
    if (classList?.includes('warning')) return 'warning';
    return '';
  }

  /**
   * Check if empty state is visible
   */
  async isEmptyStateVisible(): Promise<boolean> {
    const classList = await this.emptyState.getAttribute('class');
    return classList?.includes('visible') ?? false;
  }

  /**
   * Clear the input field
   */
  async clearInput() {
    await this.taskInput.clear();
  }

  /**
   * Press Escape to clear input
   */
  async pressEscape() {
    await this.taskInput.press('Escape');
  }

  /**
   * Focus input with keyboard shortcut (Ctrl+K / Cmd+K)
   */
  async focusInputWithShortcut() {
    await this.page.keyboard.press('Control+k');
  }

  /**
   * Clear completed tasks with keyboard shortcut
   */
  async clearCompletedWithShortcut() {
    await this.page.keyboard.press('Control+Shift+C');
  }

  /**
   * Get input value
   */
  async getInputValue(): Promise<string> {
    return await this.taskInput.inputValue();
  }

  /**
   * Clear localStorage
   */
  async clearLocalStorage() {
    await this.page.evaluate(() => localStorage.clear());
  }

  /**
   * Get tasks from localStorage
   */
  async getTasksFromStorage(): Promise<any[]> {
    return await this.page.evaluate(() => {
      const data = localStorage.getItem('todo_tasks');
      return data ? JSON.parse(data) : [];
    });
  }

  /**
   * Set tasks in localStorage
   */
  async setTasksInStorage(tasks: any[]) {
    await this.page.evaluate((tasksData) => {
      localStorage.setItem('todo_tasks', JSON.stringify(tasksData));
    }, tasks);
  }

  /**
   * Reload the page
   */
  async reload() {
    await this.page.reload();
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Wait for feedback message to appear
   */
  async waitForFeedback(timeout: number = 3000) {
    await this.inputFeedback.waitFor({ state: 'visible', timeout });
  }

  /**
   * Check if element is focused
   */
  async isInputFocused(): Promise<boolean> {
    return await this.taskInput.evaluate((el) => el === document.activeElement);
  }
}