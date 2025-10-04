/**
 * Tests for MetricsCards Component
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import MetricsCards from '../../../src/components/analytics/MetricsCards';

describe('MetricsCards', () => {
  const mockMetrics = {
    total_tasks: 100,
    completed_tasks: 75,
    in_progress_tasks: 15,
    overdue_tasks: 5,
    blocked_tasks: 2,
    completion_rate: 75.0,
    overdue_rate: 5.0,
    avg_completion_days: 3.5,
    avg_urgent_completion_days: 1.2,
    avg_high_completion_days: 2.5,
    avg_medium_completion_days: 4.0
  };
  
  const mockHealth = {
    score: 85,
    status: 'excellent',
    total_tasks: 100,
    completed_tasks: 75
  };
  
  const mockVelocity = {
    avg_weekly_velocity: 20,
    trend: 'increasing'
  };
  
  it('should render all metric cards', () => {
    render(
      <MetricsCards 
        metrics={mockMetrics}
        health={mockHealth}
        velocity={mockVelocity}
      />
    );
    
    // Check for all 8 metric cards
    expect(screen.getByText('Total Tasks')).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getByText('In Progress')).toBeInTheDocument();
    expect(screen.getByText('Overdue')).toBeInTheDocument();
    expect(screen.getByText('Weekly Velocity')).toBeInTheDocument();
    expect(screen.getByText('Avg Completion')).toBeInTheDocument();
    expect(screen.getByText('Blocked Tasks')).toBeInTheDocument();
    expect(screen.getByText('Health Score')).toBeInTheDocument();
  });
  
  it('should display correct metric values', () => {
    render(
      <MetricsCards 
        metrics={mockMetrics}
        health={mockHealth}
        velocity={mockVelocity}
      />
    );
    
    expect(screen.getByText('100')).toBeInTheDocument(); // Total tasks
    expect(screen.getByText('75')).toBeInTheDocument(); // Completed
    expect(screen.getByText('15')).toBeInTheDocument(); // In progress
    expect(screen.getByText('5')).toBeInTheDocument(); // Overdue
    expect(screen.getByText('20')).toBeInTheDocument(); // Velocity
    expect(screen.getByText('3.5d')).toBeInTheDocument(); // Avg completion
    expect(screen.getByText('2')).toBeInTheDocument(); // Blocked
    expect(screen.getByText('85')).toBeInTheDocument(); // Health score
  });
  
  it('should display completion rate subtitle', () => {
    render(
      <MetricsCards 
        metrics={mockMetrics}
        health={mockHealth}
        velocity={mockVelocity}
      />
    );
    
    expect(screen.getByText('75% rate')).toBeInTheDocument();
  });
  
  it('should display velocity trend', () => {
    render(
      <MetricsCards 
        metrics={mockMetrics}
        health={mockHealth}
        velocity={mockVelocity}
      />
    );
    
    expect(screen.getByText('increasing trend')).toBeInTheDocument();
  });
  
  it('should display health status', () => {
    render(
      <MetricsCards 
        metrics={mockMetrics}
        health={mockHealth}
        velocity={mockVelocity}
      />
    );
    
    expect(screen.getByText('excellent')).toBeInTheDocument();
  });
  
  it('should render with zero values', () => {
    const zeroMetrics = {
      total_tasks: 0,
      completed_tasks: 0,
      in_progress_tasks: 0,
      overdue_tasks: 0,
      blocked_tasks: 0,
      completion_rate: 0,
      overdue_rate: 0,
      avg_completion_days: 0
    };
    
    const zeroHealth = {
      score: 0,
      status: 'poor'
    };
    
    const zeroVelocity = {
      avg_weekly_velocity: 0,
      trend: 'stable'
    };
    
    render(
      <MetricsCards 
        metrics={zeroMetrics}
        health={zeroHealth}
        velocity={zeroVelocity}
      />
    );
    
    // Should render without crashing
    expect(screen.getByText('Total Tasks')).toBeInTheDocument();
  });
  
  it('should display overdue rate', () => {
    render(
      <MetricsCards 
        metrics={mockMetrics}
        health={mockHealth}
        velocity={mockVelocity}
      />
    );
    
    expect(screen.getByText('5% of total')).toBeInTheDocument();
  });
  
  it('should show decreasing trend when applicable', () => {
    const decreasingVelocity = {
      ...mockVelocity,
      trend: 'decreasing'
    };
    
    render(
      <MetricsCards 
        metrics={mockMetrics}
        health={mockHealth}
        velocity={decreasingVelocity}
      />
    );
    
    expect(screen.getByText('decreasing trend')).toBeInTheDocument();
  });
  
  it('should render icons for all cards', () => {
    const { container } = render(
      <MetricsCards 
        metrics={mockMetrics}
        health={mockHealth}
        velocity={mockVelocity}
      />
    );
    
    // Icons are rendered as text emojis
    expect(container.textContent).toContain('📋'); // Total tasks
    expect(container.textContent).toContain('✅'); // Completed
    expect(container.textContent).toContain('⚡'); // In progress
    expect(container.textContent).toContain('⚠️'); // Overdue
    expect(container.textContent).toContain('📈'); // Velocity
    expect(container.textContent).toContain('⏱️'); // Avg completion
    expect(container.textContent).toContain('🚫'); // Blocked
    expect(container.textContent).toContain('💚'); // Health
  });
});
