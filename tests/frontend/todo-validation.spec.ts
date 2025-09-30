import { test, expect } from './fixtures/todoFixtures';

/**
 * Input Validation and Edge Cases Tests
 * Tests validation, error handling, and edge cases
 */

test.describe('Input Validation', () => {
  
  test('should not add an empty task', async ({ todoPage, edgeCases }) => {
    await todoPage.taskInput.fill(edgeCases.emptyTask);
    await todoPage.addButton.click();
    
    // No task should be added
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(0);
    
    // Error feedback should be shown
    const feedbackMessage = await todoPage.getFeedbackMessage();
    expect(feedbackMessage).toContain('cannot be empty');
    
    const feedbackType = await todoPage.getFeedbackType();
    expect(feedbackType).toBe('error');
  });

  test('should not add a task with only whitespace', async ({ todoPage, edgeCases }) => {
    await todoPage.taskInput.fill(edgeCases.whitespaceTask);
    await todoPage.addButton.click();
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(0);
    
    const feedbackMessage = await todoPage.getFeedbackMessage();
    expect(feedbackMessage).toContain('cannot be empty');
  });

  test('should accept task at maximum length (280 characters)', async ({ todoPage, edgeCases }) => {
    const maxLengthTask = edgeCases.maxLengthTask;
    expect(maxLengthTask.length).toBe(280);
    
    await todoPage.taskInput.fill(maxLengthTask);
    await todoPage.addButton.click();
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
  });

  test('should not accept task exceeding maximum length', async ({ todoPage, edgeCases }) => {
    const tooLongTask = edgeCases.tooLongTask;
    expect(tooLongTask.length).toBeGreaterThan(280);
    
    await todoPage.taskInput.fill(tooLongTask);
    await todoPage.addButton.click();
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(0);
    
    const feedbackMessage = await todoPage.getFeedbackMessage();
    expect(feedbackMessage).toContain('cannot exceed 280 characters');
  });

  test('should show warning when approaching character limit', async ({ todoPage, edgeCases }) => {
    const nearMaxTask = edgeCases.nearMaxLength;
    
    await todoPage.taskInput.fill(nearMaxTask);
    
    // Wait for debounced input validation
    await todoPage.page.waitForTimeout(400);
    
    const feedbackMessage = await todoPage.getFeedbackMessage();
    expect(feedbackMessage).toContain('characters remaining');
    
    const feedbackType = await todoPage.getFeedbackType();
    expect(feedbackType).toBe('warning');
  });

  test('should sanitize HTML/script tags to prevent XSS', async ({ todoPage, edgeCases }) => {
    const maliciousTask = edgeCases.specialChars;
    
    await todoPage.addTask(maliciousTask);
    
    const taskText = await todoPage.getTaskText(0);
    
    // Script tags should be escaped
    expect(taskText).not.toContain('<script>');
    expect(taskText).toContain('&lt;script&gt;');
  });

  test('should accept tasks with emoji', async ({ todoPage, edgeCases }) => {
    const emojiTask = edgeCases.emoji;
    
    await todoPage.addTask(emojiTask);
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
    
    const taskText = await todoPage.getTaskText(0);
    expect(taskText).toContain('🎉');
    expect(taskText).toContain('✅');
  });

  test('should accept tasks with unicode characters', async ({ todoPage, edgeCases }) => {
    const unicodeTask = edgeCases.unicode;
    
    await todoPage.addTask(unicodeTask);
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
    
    const taskText = await todoPage.getTaskText(0);
    expect(taskText).toContain('français');
    expect(taskText).toContain('é');
  });

  test('should accept single character task', async ({ todoPage, edgeCases }) => {
    const singleChar = edgeCases.singleChar;
    
    await todoPage.addTask(singleChar);
    
    const taskCount = await todoPage.getTaskCount();
    expect(taskCount).toBe(1);
    
    const taskText = await todoPage.getTaskText(0);
    expect(taskText).toBe('A');
  });

  test('should trim whitespace from task input', async ({ todoPage }) => {
    await todoPage.addTask('   Task with spaces   ');
    
    const taskText = await todoPage.getTaskText(0);
    expect(taskText).toBe('Task with spaces');
  });
});