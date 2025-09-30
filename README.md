# Todo List Application

A clean, modern, and production-ready todo list application built with vanilla JavaScript. Features persistent storage, responsive design, and comprehensive error handling.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![JavaScript](https://img.shields.io/badge/javascript-ES6+-yellow)

## ✨ Features

- ✅ **Add Tasks**: Create new tasks with validation and character limits
- ✅ **Complete Tasks**: Toggle task completion with visual feedback
- ✅ **Delete Tasks**: Remove tasks with smooth animations
- ✅ **Persistent Storage**: Tasks automatically save to localStorage
- ✅ **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- ✅ **Accessibility**: Full keyboard navigation and ARIA support
- ✅ **Input Validation**: Prevents empty tasks and enforces character limits
- ✅ **Visual Feedback**: Real-time feedback for all user actions
- ✅ **Task Statistics**: Track completion progress
- ✅ **Empty State**: Helpful message when no tasks exist
- ✅ **Keyboard Shortcuts**: Quick actions via keyboard
- ✅ **XSS Protection**: Input sanitization for security
- ✅ **Error Handling**: Graceful degradation and error recovery

## 🚀 Getting Started

### Prerequisites

- A modern web browser (Chrome, Firefox, Safari, Edge)
- No build tools or dependencies required!

### Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd todo-app
   ```

2. **Open in browser**
   ```bash
   # Simply open index.html in your browser
   # Or use a local server:
   python -m http.server 8000
   # Then visit http://localhost:8000
   ```

That's it! No npm install, no build process needed.

## 📖 Usage

### Basic Operations

**Adding a Task:**
1. Type your task in the input field
2. Press `Enter` or click the "Add Task" button
3. Task appears at the bottom of the list

**Completing a Task:**
1. Click the ✓ button on any task
2. Task gets marked with strikethrough styling
3. Click again to mark as incomplete

**Deleting a Task:**
1. Click the × button on any task
2. Task is removed with a smooth animation

### Keyboard Shortcuts

- `Enter` - Add a new task
- `Escape` - Clear the input field
- `Ctrl/Cmd + K` - Focus the input field
- `Ctrl/Cmd + Shift + C` - Clear all completed tasks

### Task Constraints

- **Minimum length**: 1 character (excluding whitespace)
- **Maximum length**: 280 characters
- **Maximum tasks**: 1000 tasks
- **Character warning**: Shows when 90% of limit is reached

## 🏗️ Architecture

This application follows the **Model-View** architectural pattern for clean separation of concerns.

### Project Structure

```
todo-app/
├── index.html              # Main HTML structure
├── css/
│   ├── normalize.css       # CSS reset for cross-browser consistency
│   └── styles.css          # Application styles and theme
├── js/
│   ├── utils.js           # Utility functions and helpers
│   ├── TaskManager.js     # Data model and business logic
│   ├── TaskView.js        # UI rendering and interactions
│   └── app.js             # Application initialization
└── README.md              # This file
```

### Component Overview

#### **TaskManager** (Model)
Manages all task data and business logic:
- CRUD operations for tasks
- Data validation and sanitization
- localStorage persistence
- Observer pattern for state changes
- Task statistics and filtering

#### **TaskView** (View)
Handles all UI rendering and user interactions:
- DOM manipulation
- Event handling
- Visual feedback
- Accessibility features
- Animation and transitions

#### **Utils**
Provides shared utilities:
- Input validation
- XSS sanitization
- Storage management
- Debouncing and throttling
- Helper functions

## 🔒 Security

This application implements several security best practices:

1. **XSS Protection**: All user input is sanitized before rendering
2. **Content Security Policy**: CSP headers prevent injection attacks
3. **Input Validation**: Strict validation on all user input
4. **Safe DOM Manipulation**: Uses textContent instead of innerHTML where possible
5. **localStorage Safety**: Error handling for storage quota and availability

## ♿ Accessibility

Built with accessibility in mind:

- **Semantic HTML**: Proper use of semantic elements
- **ARIA Labels**: Screen reader support for all interactive elements
- **Keyboard Navigation**: Full keyboard support
- **Focus Management**: Visible focus indicators
- **Color Contrast**: WCAG AA compliant color ratios
- **Reduced Motion**: Respects `prefers-reduced-motion` setting

## 📱 Responsive Design

The application is fully responsive with breakpoints at:

- **Desktop**: 769px and above
- **Tablet**: 481px - 768px
- **Mobile**: 480px and below

Features adapt including:
- Flexible layouts
- Touch-friendly button sizes
- Optimized typography
- Adjusted spacing

## 🎨 Customization

### Theming

Edit CSS variables in `css/styles.css`:

```css
:root {
    --primary-color: #4CAF50;
    --danger-color: #f44336;
    --text-color: #333333;
    /* ... and more */
}
```

### Configuration

Modify constants in `js/utils.js`:

```javascript
const CONFIG = {
    MAX_TASK_LENGTH: 280,
    MAX_TASKS: 1000,
    STORAGE_KEY: 'todo_tasks',
    // ... and more
};
```

## 🧪 Testing

### Manual Testing Checklist

- [ ] Add a task with valid text
- [ ] Try to add an empty task (should show error)
- [ ] Try to add a task exceeding 280 characters (should show error)
- [ ] Complete a task
- [ ] Uncomplete a completed task
- [ ] Delete a task
- [ ] Refresh page and verify tasks persist
- [ ] Test on mobile device
- [ ] Test keyboard shortcuts
- [ ] Test with JavaScript console for errors

### Browser Compatibility

Tested and working on:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 🐛 Error Handling

The application handles various error scenarios:

- **Storage Full**: Alerts user when localStorage quota is exceeded
- **Storage Unavailable**: Gracefully degrades when localStorage is disabled
- **Invalid Input**: Shows user-friendly validation messages
- **Task Limit**: Prevents adding tasks beyond the limit
- **Missing Elements**: Fails gracefully if DOM elements are missing
- **Script Errors**: Global error handler catches unhandled exceptions

## 📊 Features Roadmap

Potential future enhancements:

- [ ] Task categories/tags
- [ ] Task priorities
- [ ] Due dates and reminders
- [ ] Search and filter functionality
- [ ] Task editing (double-click to edit)
- [ ] Drag and drop reordering
- [ ] Export/import tasks (JSON/CSV)
- [ ] Dark mode toggle
- [ ] Multiple task lists
- [ ] Sync across devices
- [ ] Progressive Web App (PWA) support
- [ ] Service Worker for offline support

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Standards

- Use ES6+ JavaScript features
- Follow existing code style
- Add JSDoc comments for new functions
- Ensure responsive design
- Test on multiple browsers
- Maintain accessibility standards

## 📝 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2025 Todo List App

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 👨‍💻 Developer Guide

### Console Commands

The application exposes some useful methods for debugging:

```javascript
// Access the app instance
window.todoApp

// Get task statistics
window.todoApp.taskManager.getStats()

// Export tasks as JSON
window.todoApp.exportData()

// Import tasks from JSON
window.todoApp.importData('[{"text":"Task 1","completed":false}]')

// Clear all completed tasks
window.todoApp.clearCompletedTasks()

// Access TaskManager directly
window.todoApp.taskManager.getAllTasks()
```

### Storage Structure

Tasks are stored in localStorage with the following structure:

```json
[
  {
    "id": "uuid-v4-string",
    "text": "Task description",
    "completed": false,
    "timestamp": 1234567890000
  }
]
```

### Event Flow

1. User interacts with UI (TaskView)
2. TaskView validates input and calls TaskManager
3. TaskManager updates data and notifies subscribers
4. TaskView receives notification and re-renders UI
5. TaskManager saves to localStorage

## 📞 Support

If you encounter any issues:

1. Check the browser console for errors
2. Verify localStorage is enabled in your browser
3. Try clearing localStorage and refreshing
4. Test in a different browser
5. Check browser compatibility

## 🙏 Acknowledgments

- Icons: Unicode characters for cross-browser compatibility
- Fonts: System font stack for optimal performance
- CSS Reset: normalize.css for consistency
- Inspiration: Modern todo applications and best practices

## 📈 Performance

The application is optimized for performance:

- **Minimal Dependencies**: Pure vanilla JavaScript, no frameworks
- **Debounced Operations**: Prevents excessive localStorage writes
- **Event Delegation**: Efficient event handling for dynamic content
- **CSS Animations**: Hardware-accelerated transitions
- **Lazy Rendering**: Only re-renders changed elements
- **Optimized Bundle**: ~15KB total (HTML + CSS + JS)

## 🌐 Browser Storage

- Uses localStorage (5-10MB typically available)
- Handles quota exceeded errors gracefully
- Provides fallback when storage is unavailable
- Automatically saves on every change
- Validates data on load

---

**Built with ❤️ using Vanilla JavaScript**

Last updated: 2025-09-30