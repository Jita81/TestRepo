import { Page, Locator, expect } from '@playwright/test';

/**
 * Page Object Model for Todo List Application
 * Encapsulates page interactions and element selectors
 */
export class TodoPage {
  readonly page: Page;
  
  // Input elements
  readonly taskInput: Locator;
  readonly addButton: Locator;
  readonly taskForm: Locator;
  
  // Display elements
  readonly taskList: Locator;
  readonly emptyState: Locator;
  readonly taskCounter: Locator;
  readonly inputFeedback: Locator;
  
  // Header elements
  readonly header: Locator;
  readonly subtitle: Locator;
  
  constructor(page: Page) {
    this.page = page;
    
    // Input elements
    this.taskInput = page.locator('#task-input');
    this.addButton = page.locator('.btn-add');
    this.taskForm = page.locator('#task-form');
    
    // Display elements
    this.taskList = page.locator('#task-list');
    this.emptyState = page.locator('#empty-state');
    this.taskCounter = page.locator('#counter-text');
    this.inputFeedback = page.locator('#input-feedback');
    
    // Header elements
    this.header = page.locator('h1');
    this.subtitle = page.locator('.app-subtitle');
  }
  
  /**
   * Navigate to the todo app
   */
  async goto() {
    await this.page.goto('/');
    await this.page.waitForLoadState('networkidle');
  }
  
  /**
   * Add a new task using the input field and button
   */
  async addTask(taskText: string) {
    await this.taskInput.fill(taskText);
    await this.addButton.click();
  }
  
  /**
   * Add a new task using Enter key
   */
  async addTaskWithEnter(taskText: string) {
    await this.taskInput.fill(taskText);
    await this.taskInput.press('Enter');
  }
  
  /**
   * Get all task items on the page
   */
  getTaskItems(): Locator {
    return this.page.locator('.task-item');
  }
  
  /**
   * Get a specific task item by its text content
   */
  getTaskByText(taskText: string): Locator {
    return this.page.locator('.task-item', { hasText: taskText });
  }
  
  /**
   * Get task item by index (0-based)
   */
  getTaskByIndex(index: number): Locator {
    return this.getTaskItems().nth(index);
  }
  
  /**
   * Complete a task by its text
   */
  async completeTask(taskText: string) {
    const task = this.getTaskByText(taskText);
    await task.locator('.btn-complete').click();
  }
  
  /**
   * Complete a task by index
   */
  async completeTaskByIndex(index: number) {
    const task = this.getTaskByIndex(index);
    await task.locator('.btn-complete').click();
  }
  
  /**
   * Delete a task by its text
   */
  async deleteTask(taskText: string) {
    const task = this.getTaskByText(taskText);
    await task.locator('.btn-delete').click();
    // Wait for deletion animation
    await this.page.waitForTimeout(350);
  }
  
  /**
   * Delete a task by index
   */
  async deleteTaskByIndex(index: number) {
    const task = this.getTaskByIndex(index);
    await task.locator('.btn-delete').click();
    // Wait for deletion animation
    await this.page.waitForTimeout(350);
  }
  
  /**
   * Get the count of tasks
   */
  async getTaskCount(): Promise<number> {
    return await this.getTaskItems().count();
  }
  
  /**
   * Get the count of completed tasks
   */
  async getCompletedTaskCount(): Promise<number> {
    return await this.page.locator('.task-item.completed').count();
  }
  
  /**
   * Check if empty state is visible
   */
  async isEmptyStateVisible(): Promise<boolean> {
    return await this.emptyState.isVisible();
  }
  
  /**
   * Get the counter text
   */
  async getCounterText(): Promise<string> {
    return await this.taskCounter.textContent() || '';
  }
  
  /**
   * Get the feedback message
   */
  async getFeedbackMessage(): Promise<string> {
    return await this.inputFeedback.textContent() || '';
  }
  
  /**
   * Check if a task is completed
   */
  async isTaskCompleted(taskText: string): Promise<boolean> {
    const task = this.getTaskByText(taskText);
    const classes = await task.getAttribute('class') || '';
    return classes.includes('completed');
  }
  
  /**
   * Clear input field using Escape key
   */
  async clearInputWithEscape() {
    await this.taskInput.press('Escape');
  }
  
  /**
   * Focus input using keyboard shortcut (Ctrl/Cmd + K)
   */
  async focusInputWithShortcut() {
    await this.page.keyboard.press('Control+k');
  }
  
  /**
   * Clear completed tasks using keyboard shortcut (Ctrl/Cmd + Shift + C)
   */
  async clearCompletedTasksWithShortcut() {
    await this.page.keyboard.press('Control+Shift+C');
  }
  
  /**
   * Clear localStorage to reset the app state
   */
  async clearStorage() {
    await this.page.evaluate(() => {
      localStorage.clear();
    });
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
   * Wait for task to appear in the list
   */
  async waitForTask(taskText: string) {
    await this.getTaskByText(taskText).waitFor({ state: 'visible' });
  }
  
  /**
   * Get all visible task texts
   */
  async getAllTaskTexts(): Promise<string[]> {
    const tasks = await this.getTaskItems().all();
    const texts: string[] = [];
    
    for (const task of tasks) {
      const text = await task.locator('.task-text').textContent();
      if (text) texts.push(text);
    }
    
    return texts;
  }
  
  /**
   * Check if input is focused
   */
  async isInputFocused(): Promise<boolean> {
    return await this.taskInput.evaluate((el) => el === document.activeElement);
  }
  
  /**
   * Fill input without triggering add
   */
  async fillInput(text: string) {
    await this.taskInput.fill(text);
  }
  
  /**
   * Get input value
   */
  async getInputValue(): Promise<string> {
    return await this.taskInput.inputValue();
  }
}