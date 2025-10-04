/**
 * Tests for DateRangePicker Component
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import DateRangePicker from '../../../src/components/analytics/DateRangePicker';
import { format } from 'date-fns';

describe('DateRangePicker', () => {
  const mockOnChange = vi.fn();
  const mockOnQuickRange = vi.fn();
  
  const defaultProps = {
    startDate: '2024-01-01',
    endDate: '2024-12-31',
    onChange: mockOnChange,
    onQuickRange: mockOnQuickRange
  };
  
  beforeEach(() => {
    mockOnChange.mockClear();
    mockOnQuickRange.mockClear();
  });
  
  it('should render date inputs', () => {
    render(<DateRangePicker {...defaultProps} />);
    
    expect(screen.getByLabelText('From:')).toBeInTheDocument();
    expect(screen.getByLabelText('To:')).toBeInTheDocument();
  });
  
  it('should display current date values', () => {
    render(<DateRangePicker {...defaultProps} />);
    
    const startInput = screen.getByLabelText('From:');
    const endInput = screen.getByLabelText('To:');
    
    expect(startInput.value).toBe('2024-01-01');
    expect(endInput.value).toBe('2024-12-31');
  });
  
  it('should call onChange when start date changes', () => {
    render(<DateRangePicker {...defaultProps} />);
    
    const startInput = screen.getByLabelText('From:');
    fireEvent.change(startInput, { target: { value: '2024-02-01' } });
    
    expect(mockOnChange).toHaveBeenCalledWith({
      startDate: '2024-02-01',
      endDate: '2024-12-31'
    });
  });
  
  it('should call onChange when end date changes', () => {
    render(<DateRangePicker {...defaultProps} />);
    
    const endInput = screen.getByLabelText('To:');
    fireEvent.change(endInput, { target: { value: '2024-11-30' } });
    
    expect(mockOnChange).toHaveBeenCalledWith({
      startDate: '2024-01-01',
      endDate: '2024-11-30'
    });
  });
  
  it('should render all quick range buttons', () => {
    render(<DateRangePicker {...defaultProps} />);
    
    expect(screen.getByText('Last 7 Days')).toBeInTheDocument();
    expect(screen.getByText('Last 30 Days')).toBeInTheDocument();
    expect(screen.getByText('Last 90 Days')).toBeInTheDocument();
    expect(screen.getByText('Last 180 Days')).toBeInTheDocument();
    expect(screen.getByText('Last Year')).toBeInTheDocument();
  });
  
  it('should call onQuickRange when clicking quick range button', () => {
    render(<DateRangePicker {...defaultProps} />);
    
    const button = screen.getByText('Last 7 Days');
    fireEvent.click(button);
    
    expect(mockOnQuickRange).toHaveBeenCalledWith(7);
  });
  
  it('should call onQuickRange with correct days for each button', () => {
    render(<DateRangePicker {...defaultProps} />);
    
    fireEvent.click(screen.getByText('Last 7 Days'));
    expect(mockOnQuickRange).toHaveBeenCalledWith(7);
    
    fireEvent.click(screen.getByText('Last 30 Days'));
    expect(mockOnQuickRange).toHaveBeenCalledWith(30);
    
    fireEvent.click(screen.getByText('Last 90 Days'));
    expect(mockOnQuickRange).toHaveBeenCalledWith(90);
    
    fireEvent.click(screen.getByText('Last 180 Days'));
    expect(mockOnQuickRange).toHaveBeenCalledWith(180);
    
    fireEvent.click(screen.getByText('Last Year'));
    expect(mockOnQuickRange).toHaveBeenCalledWith(365);
  });
  
  it('should set max date on start input to end date', () => {
    render(<DateRangePicker {...defaultProps} />);
    
    const startInput = screen.getByLabelText('From:');
    expect(startInput).toHaveAttribute('max', '2024-12-31');
  });
  
  it('should set min date on end input to start date', () => {
    render(<DateRangePicker {...defaultProps} />);
    
    const endInput = screen.getByLabelText('To:');
    expect(endInput).toHaveAttribute('min', '2024-01-01');
  });
  
  it('should set max date on end input to today', () => {
    render(<DateRangePicker {...defaultProps} />);
    
    const endInput = screen.getByLabelText('To:');
    const today = format(new Date(), 'yyyy-MM-dd');
    expect(endInput).toHaveAttribute('max', today);
  });
  
  it('should have proper input types', () => {
    render(<DateRangePicker {...defaultProps} />);
    
    const startInput = screen.getByLabelText('From:');
    const endInput = screen.getByLabelText('To:');
    
    expect(startInput).toHaveAttribute('type', 'date');
    expect(endInput).toHaveAttribute('type', 'date');
  });
  
  it('should render with custom date range', () => {
    const customProps = {
      ...defaultProps,
      startDate: '2024-06-01',
      endDate: '2024-06-30'
    };
    
    render(<DateRangePicker {...customProps} />);
    
    const startInput = screen.getByLabelText('From:');
    const endInput = screen.getByLabelText('To:');
    
    expect(startInput.value).toBe('2024-06-01');
    expect(endInput.value).toBe('2024-06-30');
  });
});
