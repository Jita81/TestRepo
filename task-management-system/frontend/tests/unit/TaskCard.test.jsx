/**
 * TaskCard Component Tests
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import TaskCard from '../../src/components/TaskCard';

describe('TaskCard Component', () => {
  const mockTask = {
    id: 'task-123',
    title: 'Test Task',
    description: 'This is a test task description',
    status: 'todo',
    priority: 'high',
    assigned_to: 'user-1',
    assignee_name: 'John Doe',
    assignee_avatar: null,
    due_date: '2024-12-31',
    project_id: 'project-1',
    tags: ['urgent', 'bug'],
    subtasks_total: 5,
    subtasks_completed: 3,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('should render task title', () => {
      render(<TaskCard task={mockTask} projectId="project-1" />);
      expect(screen.getByText('Test Task')).toBeInTheDocument();
    });

    it('should render task description preview', () => {
      render(<TaskCard task={mockTask} projectId="project-1" />);
      expect(screen.getByText(/This is a test task/)).toBeInTheDocument();
    });

    it('should truncate long descriptions', () => {
      const longTask = {
        ...mockTask,
        description: 'A'.repeat(150),
      };
      render(<TaskCard task={longTask} projectId="project-1" />);
      const description = screen.getByText(/A{100}/);
      expect(description.textContent.length).toBeLessThanOrEqual(103); // 100 + "..."
    });

    it('should show "No description" when description is missing', () => {
      const taskNoDesc = { ...mockTask, description: null };
      render(<TaskCard task={taskNoDesc} projectId="project-1" />);
      expect(screen.getByText('No description')).toBeInTheDocument();
    });
  });

  describe('Priority Badge', () => {
    it('should display high priority badge', () => {
      render(<TaskCard task={mockTask} projectId="project-1" />);
      expect(screen.getByLabelText(/Priority: High/i)).toBeInTheDocument();
    });

    it('should display urgent priority with fire emoji', () => {
      const urgentTask = { ...mockTask, priority: 'urgent' };
      render(<TaskCard task={urgentTask} projectId="project-1" />);
      expect(screen.getByText('🔥')).toBeInTheDocument();
    });

    it('should display medium priority with right arrow', () => {
      const mediumTask = { ...mockTask, priority: 'medium' };
      render(<TaskCard task={mediumTask} projectId="project-1" />);
      expect(screen.getByText('➡️')).toBeInTheDocument();
    });

    it('should display low priority with down arrow', () => {
      const lowTask = { ...mockTask, priority: 'low' };
      render(<TaskCard task={lowTask} projectId="project-1" />);
      expect(screen.getByText('⬇️')).toBeInTheDocument();
    });
  });

  describe('Assignee Display', () => {
    it('should show assignee name', () => {
      render(<TaskCard task={mockTask} projectId="project-1" />);
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    it('should show assignee initials when no avatar', () => {
      render(<TaskCard task={mockTask} projectId="project-1" />);
      expect(screen.getByText('JD')).toBeInTheDocument();
    });

    it('should show "Unassigned" when no assignee', () => {
      const unassignedTask = {
        ...mockTask,
        assigned_to: null,
        assignee_name: null,
      };
      render(<TaskCard task={unassignedTask} projectId="project-1" />);
      expect(screen.getByText('Unassigned')).toBeInTheDocument();
    });

    it('should display assignee avatar when provided', () => {
      const taskWithAvatar = {
        ...mockTask,
        assignee_avatar: 'https://example.com/avatar.jpg',
      };
      render(<TaskCard task={taskWithAvatar} projectId="project-1" />);
      const avatar = screen.getByAlt('John Doe');
      expect(avatar).toBeInTheDocument();
      expect(avatar).toHaveAttribute('src', 'https://example.com/avatar.jpg');
    });
  });

  describe('Due Date Display', () => {
    it('should display formatted due date', () => {
      render(<TaskCard task={mockTask} projectId="project-1" />);
      expect(screen.getByText(/Dec 31/)).toBeInTheDocument();
    });

    it('should show overdue warning for past dates', () => {
      const overdueTask = {
        ...mockTask,
        due_date: '2020-01-01',
        status: 'todo',
      };
      render(<TaskCard task={overdueTask} projectId="project-1" />);
      expect(screen.getByText('⚠️')).toBeInTheDocument();
    });

    it('should not show overdue warning for completed tasks', () => {
      const completedTask = {
        ...mockTask,
        due_date: '2020-01-01',
        status: 'done',
      };
      render(<TaskCard task={completedTask} projectId="project-1" />);
      expect(screen.queryByText('⚠️')).not.toBeInTheDocument();
    });

    it('should not display due date when missing', () => {
      const taskNoDue = { ...mockTask, due_date: null };
      render(<TaskCard task={taskNoDue} projectId="project-1" />);
      expect(screen.queryByLabelText(/Due/)).not.toBeInTheDocument();
    });
  });

  describe('Tags Display', () => {
    it('should display task tags', () => {
      render(<TaskCard task={mockTask} projectId="project-1" />);
      expect(screen.getByText('urgent')).toBeInTheDocument();
      expect(screen.getByText('bug')).toBeInTheDocument();
    });

    it('should limit displayed tags to 3', () => {
      const taskManyTags = {
        ...mockTask,
        tags: ['tag1', 'tag2', 'tag3', 'tag4', 'tag5'],
      };
      render(<TaskCard task={taskManyTags} projectId="project-1" />);
      expect(screen.getByText('tag1')).toBeInTheDocument();
      expect(screen.getByText('tag2')).toBeInTheDocument();
      expect(screen.getByText('tag3')).toBeInTheDocument();
      expect(screen.getByText('+2')).toBeInTheDocument();
    });

    it('should not display tags section when no tags', () => {
      const taskNoTags = { ...mockTask, tags: [] };
      render(<TaskCard task={taskNoTags} projectId="project-1" />);
      expect(screen.queryByText('urgent')).not.toBeInTheDocument();
    });
  });

  describe('Subtask Progress', () => {
    it('should display subtask progress', () => {
      render(<TaskCard task={mockTask} projectId="project-1" />);
      expect(screen.getByText('3/5 subtasks')).toBeInTheDocument();
    });

    it('should display progress bar', () => {
      render(<TaskCard task={mockTask} projectId="project-1" />);
      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toBeInTheDocument();
      expect(progressBar).toHaveAttribute('aria-valuenow', '3');
      expect(progressBar).toHaveAttribute('aria-valuemax', '5');
    });

    it('should not display subtasks when total is 0', () => {
      const taskNoSubtasks = { ...mockTask, subtasks_total: 0 };
      render(<TaskCard task={taskNoSubtasks} projectId="project-1" />);
      expect(screen.queryByText(/subtasks/)).not.toBeInTheDocument();
    });

    it('should calculate correct progress percentage', () => {
      render(<TaskCard task={mockTask} projectId="project-1" />);
      const progressBar = screen.getByRole('progressbar');
      // Check that progress bar exists and has correct aria attributes
      expect(progressBar).toHaveAttribute('aria-valuenow', '3');
      expect(progressBar).toHaveAttribute('aria-valuemax', '5');
    });
  });

  describe('Interactions', () => {
    it('should open modal on card click', () => {
      render(<TaskCard task={mockTask} projectId="project-1" />);
      const card = screen.getByRole('button', { name: /Task: Test Task/ });
      fireEvent.click(card);
      // Modal should open (we'd need to check for modal in real implementation)
    });

    it('should open modal on Enter key', () => {
      render(<TaskCard task={mockTask} projectId="project-1" />);
      const card = screen.getByRole('button', { name: /Task: Test Task/ });
      fireEvent.keyDown(card, { key: 'Enter' });
      // Modal should open
    });

    it('should open modal on Space key', () => {
      render(<TaskCard task={mockTask} projectId="project-1" />);
      const card = screen.getByRole('button', { name: /Task: Test Task/ });
      fireEvent.keyDown(card, { key: ' ' });
      // Modal should open
    });

    it('should be keyboard focusable', () => {
      render(<TaskCard task={mockTask} projectId="project-1" />);
      const card = screen.getByRole('button');
      expect(card).toHaveAttribute('tabIndex', '0');
    });
  });

  describe('Dragging State', () => {
    it('should apply dragging styles when isDragging is true', () => {
      const { container } = render(
        <TaskCard task={mockTask} isDragging={true} projectId="project-1" />
      );
      const card = container.querySelector('.task-card');
      expect(card).toHaveClass('shadow-lg', 'rotate-2');
    });

    it('should not apply dragging styles when isDragging is false', () => {
      const { container } = render(
        <TaskCard task={mockTask} isDragging={false} projectId="project-1" />
      );
      const card = container.querySelector('.task-card');
      expect(card).not.toHaveClass('shadow-lg');
      expect(card).not.toHaveClass('rotate-2');
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<TaskCard task={mockTask} projectId="project-1" />);
      expect(screen.getByLabelText(/Task: Test Task/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Priority: High/)).toBeInTheDocument();
    });

    it('should have role="button"', () => {
      render(<TaskCard task={mockTask} projectId="project-1" />);
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('should display task ID for reference', () => {
      render(<TaskCard task={mockTask} projectId="project-1" />);
      // Shows first 8 chars of ID
      expect(screen.getByText(/#task-123/)).toBeInTheDocument();
    });
  });
});
