# Testing Guide - Todo List Application

## Quick Verification Checklist

Use this guide to verify all features are working correctly.

## 🧪 Manual Testing Steps

### 1. Basic Task Operations

#### Test 1.1: Add Valid Task
1. Open the application in browser
2. Type "Buy groceries" in the input field
3. Click "Add Task" or press Enter
4. **Expected**: Task appears at the bottom of the list
5. **Expected**: Input field clears
6. **Expected**: Success message shown
7. **Expected**: Counter updates to "1 task"

#### Test 1.2: Add Multiple Tasks
1. Add "Finish project report"
2. Add "Call dentist"
3. Add "Exercise for 30 minutes"
4. **Expected**: All tasks appear in order added
5. **Expected**: Counter shows "4 tasks remaining"

#### Test 1.3: Empty Task Prevention
1. Clear input field (press Escape)
2. Try to submit empty field
3. Try to submit only spaces "   "
4. **Expected**: Error message "Task cannot be empty"
5. **Expected**: No task added

#### Test 1.4: Character Limit
1. Type or paste 281+ characters
2. **Expected**: Warning appears at 252 characters (90% of 280)
3. **Expected**: Error appears after 280 characters
4. **Expected**: Cannot submit task over limit

### 2. Task Completion

#### Test 2.1: Complete Task
1. Click the ✓ button on "Buy groceries"
2. **Expected**: Text shows strikethrough
3. **Expected**: Task background changes to gray
4. **Expected**: Success message shown
5. **Expected**: Counter updates to "3 of 4 tasks remaining"

#### Test 2.2: Uncomplete Task
1. Click the ✓ button again on completed task
2. **Expected**: Strikethrough removed
3. **Expected**: Task returns to normal appearance
4. **Expected**: Counter updates back

#### Test 2.3: Multiple Completions
1. Complete all tasks
2. **Expected**: Counter shows "All 4 tasks completed! 🎉"
3. **Expected**: All tasks have strikethrough

### 3. Task Deletion

#### Test 3.1: Delete Single Task
1. Click the × button on any task
2. **Expected**: Smooth slide-out animation
3. **Expected**: Task removed from list
4. **Expected**: Counter updates
5. **Expected**: Success message shown

#### Test 3.2: Delete All Tasks
1. Delete each task one by one
2. **Expected**: Empty state appears when last task deleted
3. **Expected**: Message: "No tasks yet. Add one to get started!"
4. **Expected**: Counter shows "0 tasks"

### 4. Data Persistence

#### Test 4.1: Basic Persistence
1. Add 3 tasks: "Task A", "Task B", "Task C"
2. Complete "Task B"
3. Refresh the page (F5)
4. **Expected**: All 3 tasks still present
5. **Expected**: "Task B" still marked as completed
6. **Expected**: Task order preserved

#### Test 4.2: Long-term Persistence
1. Add several tasks
2. Close the browser tab
3. Reopen browser and navigate to app
4. **Expected**: All tasks restored
5. **Expected**: All states preserved

#### Test 4.3: localStorage Verification
1. Open Browser DevTools
2. Go to Application/Storage → Local Storage
3. Find key `todo_tasks`
4. **Expected**: JSON array of tasks visible
5. Verify structure matches expected format

### 5. Input Validation

#### Test 5.1: Whitespace Handling
1. Type "   Task with spaces   "
2. Submit
3. **Expected**: Task added as "Task with spaces" (trimmed)

#### Test 5.2: Special Characters
1. Add task with emojis: "🎉 Party planning 🎊"
2. Add task with symbols: "Buy <groceries> & supplies"
3. **Expected**: Both tasks display correctly
4. **Expected**: No JavaScript errors

#### Test 5.3: XSS Prevention
1. Try to add: `<script>alert('XSS')</script>`
2. Try to add: `<img src=x onerror=alert('XSS')>`
3. **Expected**: Text is sanitized and displayed as plain text
4. **Expected**: No script execution

### 6. Responsive Design

#### Test 6.1: Desktop (1920x1080)
1. Open on desktop resolution
2. **Expected**: Centered card layout (max 800px width)
3. **Expected**: Input and button side-by-side
4. **Expected**: Large, readable text

#### Test 6.2: Tablet (768x1024)
1. Resize browser to tablet size
2. **Expected**: Layout adjusts smoothly
3. **Expected**: Touch-friendly button sizes
4. **Expected**: No horizontal scrolling

#### Test 6.3: Mobile (375x667)
1. Resize to mobile or use device emulation
2. **Expected**: Input and button stack vertically
3. **Expected**: Full-width button
4. **Expected**: Adequate spacing for touch
5. **Expected**: No overlapping elements

### 7. Keyboard Navigation

#### Test 7.1: Tab Navigation
1. Press Tab repeatedly
2. **Expected**: Can navigate through all interactive elements
3. **Expected**: Visible focus indicators
4. **Expected**: Logical tab order

#### Test 7.2: Keyboard Shortcuts
1. Press `Ctrl+K` (or `Cmd+K` on Mac)
2. **Expected**: Input field gets focus
3. Add and complete several tasks
4. Press `Ctrl+Shift+C`
5. **Expected**: All completed tasks cleared
6. Press `Escape` in input field
7. **Expected**: Input field cleared

#### Test 7.3: Enter Key
1. Type task text
2. Press Enter
3. **Expected**: Task added
4. **Expected**: Focus remains on input

### 8. User Feedback

#### Test 8.1: Success Messages
1. Add a task
2. **Expected**: Green success message
3. Complete a task
4. **Expected**: Appropriate success message
5. Delete a task
6. **Expected**: Confirmation message

#### Test 8.2: Error Messages
1. Try empty task
2. **Expected**: Red error message
3. Try task over 280 characters
4. **Expected**: Clear error message

#### Test 8.3: Auto-dismiss
1. Add a task
2. Wait 3 seconds
3. **Expected**: Success message disappears automatically

### 9. Performance

#### Test 9.1: Many Tasks
1. Add 50+ tasks quickly
2. **Expected**: App remains responsive
3. **Expected**: No lag in UI
4. Scroll through list
5. **Expected**: Smooth scrolling

#### Test 9.2: Rapid Actions
1. Click complete button rapidly 10 times
2. **Expected**: Toggle works correctly
3. **Expected**: No errors in console
4. Click delete button multiple times rapidly
5. **Expected**: Deletes only once

### 10. Browser Compatibility

#### Test 10.1: Chrome
- Open in Chrome
- Run all basic tests
- Check console for errors

#### Test 10.2: Firefox
- Open in Firefox
- Run all basic tests
- Check console for errors

#### Test 10.3: Safari
- Open in Safari
- Run all basic tests
- Check console for errors

#### Test 10.4: Edge
- Open in Edge
- Run all basic tests
- Check console for errors

## 🔍 Console Testing

Open browser console and run these commands:

```javascript
// Get app instance
window.todoApp

// Add tasks programmatically
window.todoApp.taskManager.addTask("Test task 1")
window.todoApp.taskManager.addTask("Test task 2")

// Get statistics
window.todoApp.taskManager.getStats()
// Expected: { total: X, completed: Y, pending: Z, completionRate: % }

// Get all tasks
window.todoApp.taskManager.getAllTasks()
// Expected: Array of task objects

// Export tasks
window.todoApp.exportData()
// Expected: JSON string

// Import tasks
const testData = '[{"id":"test","text":"Imported task","completed":false,"timestamp":1234567890}]'
window.todoApp.importData(testData)

// Clear completed
window.todoApp.clearCompletedTasks()
```

## 🚨 Error Scenarios

### Test E1: localStorage Disabled
1. Disable localStorage in browser settings
2. Open application
3. **Expected**: App still functions
4. **Expected**: Warning in console
5. Add tasks
6. **Expected**: Tasks work but don't persist

### Test E2: localStorage Full
1. Fill localStorage to quota
2. Add many tasks
3. **Expected**: Error handled gracefully
4. **Expected**: User-friendly message

### Test E3: Network Disconnected
1. Open app
2. Disconnect network
3. Use application
4. **Expected**: All features still work (offline-capable)

## ✅ Success Criteria

All tests should pass with:
- ✓ No JavaScript errors in console
- ✓ All features working as expected
- ✓ Smooth animations and transitions
- ✓ Responsive on all screen sizes
- ✓ Accessible via keyboard
- ✓ Data persists correctly
- ✓ Error messages are user-friendly
- ✓ Performance is smooth

## 📊 Test Results Template

```
Date: _____________
Browser: _____________
Version: _____________
OS: _____________

Basic Operations:      [ ] Pass [ ] Fail
Task Completion:       [ ] Pass [ ] Fail
Task Deletion:         [ ] Pass [ ] Fail
Data Persistence:      [ ] Pass [ ] Fail
Input Validation:      [ ] Pass [ ] Fail
Responsive Design:     [ ] Pass [ ] Fail
Keyboard Navigation:   [ ] Pass [ ] Fail
User Feedback:         [ ] Pass [ ] Fail
Performance:           [ ] Pass [ ] Fail
Browser Compatibility: [ ] Pass [ ] Fail

Notes:
_____________________________________
_____________________________________
```

## 🐛 Known Issues

None - All features working as expected!

## 📝 Testing Notes

- Always test with DevTools console open
- Check for any warnings or errors
- Verify localStorage in Application tab
- Test with realistic data amounts
- Try edge cases and unusual inputs
- Test on actual mobile devices when possible

---

**Happy Testing!** 🎉