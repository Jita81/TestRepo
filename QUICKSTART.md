# Quick Start Guide 🚀

Get your Todo List app running in 60 seconds!

## Option 1: Double-Click (Easiest)

1. Navigate to the project folder
2. Double-click `index.html`
3. Your default browser opens the app
4. ✅ Done!

## Option 2: Local Server (Recommended)

### Using Python
```bash
cd /workspace
python3 -m http.server 8080
```
Then open: http://localhost:8080

### Using Node.js
```bash
cd /workspace
npx http-server -p 8080
```
Then open: http://localhost:8080

### Using PHP
```bash
cd /workspace
php -S localhost:8080
```
Then open: http://localhost:8080

## First Steps

1. **Add a Task**
   - Type "Buy groceries" in the input
   - Press Enter or click "Add Task"
   - See your task appear! ✅

2. **Complete a Task**
   - Click the ✓ button
   - Task gets strikethrough style

3. **Delete a Task**
   - Click the × button
   - Task smoothly disappears

4. **Test Persistence**
   - Add a few tasks
   - Refresh the page (F5)
   - Your tasks are still there! 💾

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Add task |
| `Escape` | Clear input |
| `Ctrl/Cmd + K` | Focus input |
| `Ctrl/Cmd + Shift + C` | Clear completed |

## File Structure

```
/workspace/
├── index.html          ← Open this in browser
├── css/
│   ├── normalize.css
│   └── styles.css
├── js/
│   ├── utils.js
│   ├── TaskManager.js
│   ├── TaskView.js
│   └── app.js
├── README.md           ← Full documentation
├── TESTING_GUIDE.md    ← Testing instructions
└── QUICKSTART.md       ← You are here!
```

## Troubleshooting

### Tasks not saving?
- Check if localStorage is enabled in browser
- Open DevTools → Console for errors

### Styles not loading?
- Use a local server (Option 2 above)
- Check file paths are correct

### App not working?
- Open browser console (F12)
- Look for error messages
- Verify all files are present

## Next Steps

- 📖 Read the full [README.md](README.md)
- 🧪 Follow the [TESTING_GUIDE.md](TESTING_GUIDE.md)
- 🔧 Customize CSS variables in `css/styles.css`
- 🎨 Adjust config in `js/utils.js`

## Browser Compatibility

✅ Chrome 90+
✅ Firefox 88+
✅ Safari 14+
✅ Edge 90+

## Features at a Glance

- ✨ Add, complete, and delete tasks
- 💾 Automatic saving to localStorage
- 📱 Fully responsive design
- ⌨️ Keyboard shortcuts
- ♿ Accessible
- 🔒 XSS protection
- 🎨 Beautiful UI
- ⚡ Fast and lightweight

## Developer Tools

Open browser console and try:

```javascript
// View app statistics
window.todoApp.taskManager.getStats()

// Export tasks
window.todoApp.exportData()

// Get all tasks
window.todoApp.taskManager.getAllTasks()
```

## Support

Having issues? Check:
1. Browser console for errors
2. localStorage is enabled
3. All files are present
4. Using a modern browser

---

**Ready to get organized? Let's go! 🎯**

Server running at: http://localhost:8080