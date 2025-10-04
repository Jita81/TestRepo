/**
 * TaskFilters Component Tests
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TaskFilters from '../../src/components/TaskFilters';
import api from '../../src/services/api';

vi.mock('../../src/services/api');

describe('TaskFilters Component', () => {
  const mockUsers = [
    { id: 'user-1', username: 'johndoe', email: 'john@example.com' },
    { id: 'user-2', username: 'janedoe', email: 'jane@example.com' },
  ];

  const defaultProps = {
    searchQuery: '',
    filters: {
      assignee: null,
      priority: null,
      dueDateStart: null,
      dueDateEnd: null,
    },
    onSearchChange: vi.fn(),
    onFilterChange: vi.fn(),
    onClearFilters: vi.fn(),
    projectId: 'project-1',
  };

  beforeEach(() => {
    vi.clearAllMocks();
    api.get.mockResolvedValue({
      data: {
        success: true,
        data: mockUsers,
      },
    });
  });

  describe('Search Functionality', () => {
    it('should render search input', () => {
      render(<TaskFilters {...defaultProps} />);
      expect(
        screen.getByPlaceholderText(/search tasks/i)
      ).toBeInTheDocument();
    });

    it('should call onSearchChange when typing', () => {
      render(<TaskFilters {...defaultProps} />);
      const input = screen.getByPlaceholderText(/search tasks/i);
      fireEvent.change(input, { target: { value: 'test query' } });
      expect(defaultProps.onSearchChange).toHaveBeenCalledWith('test query');
    });

    it('should display current search query', () => {
      const props = { ...defaultProps, searchQuery: 'existing search' };
      render(<TaskFilters {...props} />);
      const input = screen.getByPlaceholderText(/search tasks/i);
      expect(input).toHaveValue('existing search');
    });

    it('should show clear button when search has value', () => {
      const props = { ...defaultProps, searchQuery: 'test' };
      render(<TaskFilters {...props} />);
      expect(screen.getByLabelText(/clear search/i)).toBeInTheDocument();
    });

    it('should not show clear button when search is empty', () => {
      render(<TaskFilters {...defaultProps} />);
      expect(screen.queryByLabelText(/clear search/i)).not.toBeInTheDocument();
    });

    it('should clear search when clicking clear button', () => {
      const props = { ...defaultProps, searchQuery: 'test' };
      render(<TaskFilters {...props} />);
      const clearButton = screen.getByLabelText(/clear search/i);
      fireEvent.click(clearButton);
      expect(defaultProps.onSearchChange).toHaveBeenCalledWith('');
    });
  });

  describe('Assignee Filter', () => {
    it('should fetch and display project users', async () => {
      render(<TaskFilters {...defaultProps} />);

      await waitFor(() => {
        expect(api.get).toHaveBeenCalledWith('/projects/project-1/members');
      });

      await waitFor(() => {
        expect(screen.getByText('johndoe')).toBeInTheDocument();
        expect(screen.getByText('janedoe')).toBeInTheDocument();
      });
    });

    it('should include "All Assignees" option', async () => {
      render(<TaskFilters {...defaultProps} />);
      await waitFor(() => {
        expect(screen.getByText('All Assignees')).toBeInTheDocument();
      });
    });

    it('should call onFilterChange when selecting assignee', async () => {
      render(<TaskFilters {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('johndoe')).toBeInTheDocument();
      });

      const select = screen.getByLabelText(/filter by assignee/i);
      fireEvent.change(select, { target: { value: 'user-1' } });

      expect(defaultProps.onFilterChange).toHaveBeenCalledWith({
        ...defaultProps.filters,
        assignee: 'user-1',
      });
    });

    it('should display selected assignee', async () => {
      const props = {
        ...defaultProps,
        filters: { ...defaultProps.filters, assignee: 'user-1' },
      };
      render(<TaskFilters {...props} />);
      
      await waitFor(() => {
        const select = screen.getByLabelText(/filter by assignee/i);
        expect(select.value).toBe('user-1');
      });
    });
  });

  describe('Priority Filter', () => {
    it('should display all priority options', () => {
      render(<TaskFilters {...defaultProps} />);
      const select = screen.getByLabelText(/filter by priority/i);
      expect(select).toBeInTheDocument();

      const options = Array.from(select.querySelectorAll('option')).map(
        (o) => o.textContent
      );
      expect(options).toContain('All Priorities');
      expect(options).toContain('Low');
      expect(options).toContain('Medium');
      expect(options).toContain('High');
      expect(options).toContain('Urgent');
    });

    it('should call onFilterChange when selecting priority', () => {
      render(<TaskFilters {...defaultProps} />);
      const select = screen.getByLabelText(/filter by priority/i);
      fireEvent.change(select, { target: { value: 'high' } });

      expect(defaultProps.onFilterChange).toHaveBeenCalledWith({
        ...defaultProps.filters,
        priority: 'high',
      });
    });

    it('should display selected priority', () => {
      const props = {
        ...defaultProps,
        filters: { ...defaultProps.filters, priority: 'urgent' },
      };
      render(<TaskFilters {...props} />);
      const select = screen.getByLabelText(/filter by priority/i);
      expect(select).toHaveValue('urgent');
    });
  });

  describe('Advanced Filters', () => {
    it('should hide advanced filters by default', () => {
      render(<TaskFilters {...defaultProps} />);
      expect(screen.queryByText('Due Date Range')).not.toBeInTheDocument();
    });

    it('should show advanced filters when clicking toggle', () => {
      render(<TaskFilters {...defaultProps} />);
      const toggleButton = screen.getByLabelText(/toggle advanced filters/i);
      fireEvent.click(toggleButton);
      expect(screen.getByText('Due Date Range')).toBeInTheDocument();
    });

    it('should hide advanced filters when clicking toggle again', () => {
      render(<TaskFilters {...defaultProps} />);
      const toggleButton = screen.getByLabelText(/toggle advanced filters/i);
      
      fireEvent.click(toggleButton);
      expect(screen.getByText('Due Date Range')).toBeInTheDocument();
      
      fireEvent.click(toggleButton);
      expect(screen.queryByText('Due Date Range')).not.toBeInTheDocument();
    });

    it('should update button text when toggling', () => {
      render(<TaskFilters {...defaultProps} />);
      const toggleButton = screen.getByLabelText(/toggle advanced filters/i);
      
      expect(toggleButton).toHaveTextContent('More Filters');
      
      fireEvent.click(toggleButton);
      expect(toggleButton).toHaveTextContent('Less Filters');
    });
  });

  describe('Due Date Range Filters', () => {
    it('should render due date inputs in advanced filters', () => {
      render(<TaskFilters {...defaultProps} />);
      const toggleButton = screen.getByLabelText(/toggle advanced filters/i);
      fireEvent.click(toggleButton);

      expect(screen.getByLabelText(/filter by due date from/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/filter by due date to/i)).toBeInTheDocument();
    });

    it('should call onFilterChange for start date', () => {
      render(<TaskFilters {...defaultProps} />);
      const toggleButton = screen.getByLabelText(/toggle advanced filters/i);
      fireEvent.click(toggleButton);

      const startInput = screen.getByLabelText(/filter by due date from/i);
      fireEvent.change(startInput, { target: { value: '2024-01-01' } });

      expect(defaultProps.onFilterChange).toHaveBeenCalledWith({
        ...defaultProps.filters,
        dueDateStart: '2024-01-01',
      });
    });

    it('should call onFilterChange for end date', () => {
      render(<TaskFilters {...defaultProps} />);
      const toggleButton = screen.getByLabelText(/toggle advanced filters/i);
      fireEvent.click(toggleButton);

      const endInput = screen.getByLabelText(/filter by due date to/i);
      fireEvent.change(endInput, { target: { value: '2024-12-31' } });

      expect(defaultProps.onFilterChange).toHaveBeenCalledWith({
        ...defaultProps.filters,
        dueDateEnd: '2024-12-31',
      });
    });

    it('should display selected date range', () => {
      const props = {
        ...defaultProps,
        filters: {
          ...defaultProps.filters,
          dueDateStart: '2024-01-01',
          dueDateEnd: '2024-12-31',
        },
      };
      render(<TaskFilters {...props} />);
      const toggleButton = screen.getByLabelText(/toggle advanced filters/i);
      fireEvent.click(toggleButton);

      const startInput = screen.getByLabelText(/filter by due date from/i);
      const endInput = screen.getByLabelText(/filter by due date to/i);

      expect(startInput).toHaveValue('2024-01-01');
      expect(endInput).toHaveValue('2024-12-31');
    });
  });

  describe('Filter Clearing', () => {
    it('should clear individual filter by setting to empty value', () => {
      render(<TaskFilters {...defaultProps} />);
      const select = screen.getByLabelText(/filter by priority/i);
      
      fireEvent.change(select, { target: { value: 'high' } });
      fireEvent.change(select, { target: { value: '' } });

      expect(defaultProps.onFilterChange).toHaveBeenLastCalledWith({
        ...defaultProps.filters,
        priority: null,
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper labels for all inputs', () => {
      render(<TaskFilters {...defaultProps} />);
      expect(screen.getByLabelText(/search tasks/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/filter by assignee/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/filter by priority/i)).toBeInTheDocument();
    });

    it('should have proper aria-expanded on toggle button', () => {
      render(<TaskFilters {...defaultProps} />);
      const toggleButton = screen.getByLabelText(/toggle advanced filters/i);
      
      expect(toggleButton).toHaveAttribute('aria-expanded', 'false');
      
      fireEvent.click(toggleButton);
      expect(toggleButton).toHaveAttribute('aria-expanded', 'true');
    });
  });

  describe('Error Handling', () => {
    it('should handle API error gracefully when fetching users', async () => {
      api.get.mockRejectedValue(new Error('API Error'));
      
      render(<TaskFilters {...defaultProps} />);

      // Should still render the component
      expect(screen.getByPlaceholderText(/search tasks/i)).toBeInTheDocument();
      
      // Should show at least the "All Assignees" option
      await waitFor(() => {
        expect(screen.getByText('All Assignees')).toBeInTheDocument();
      });
    });
  });
});
