/**
 * Tests for InsightsList Component
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import InsightsList from '../../../src/components/analytics/InsightsList';

describe('InsightsList', () => {
  const mockInsights = [
    {
      type: 'positive',
      category: 'velocity',
      message: 'Team velocity increased by 20% this week',
      action: null
    },
    {
      type: 'warning',
      category: 'overdue',
      message: '15% of tasks are overdue',
      action: 'Review due dates and prioritize overdue tasks'
    },
    {
      type: 'critical',
      category: 'blocked',
      message: '5 tasks are blocked',
      action: 'Address blocking issues immediately'
    },
    {
      type: 'info',
      category: 'completion_time',
      message: 'Tasks take an average of 5 days to complete',
      action: 'Consider breaking down tasks into smaller chunks'
    }
  ];
  
  it('should render all insights', () => {
    render(<InsightsList insights={mockInsights} />);
    
    expect(screen.getByText('Insights & Recommendations')).toBeInTheDocument();
    expect(screen.getByText('Team velocity increased by 20% this week')).toBeInTheDocument();
    expect(screen.getByText('15% of tasks are overdue')).toBeInTheDocument();
    expect(screen.getByText('5 tasks are blocked')).toBeInTheDocument();
    expect(screen.getByText('Tasks take an average of 5 days to complete')).toBeInTheDocument();
  });
  
  it('should display actions when provided', () => {
    render(<InsightsList insights={mockInsights} />);
    
    expect(screen.getByText(/Review due dates and prioritize overdue tasks/)).toBeInTheDocument();
    expect(screen.getByText(/Address blocking issues immediately/)).toBeInTheDocument();
    expect(screen.getByText(/Consider breaking down tasks into smaller chunks/)).toBeInTheDocument();
  });
  
  it('should display category badges', () => {
    render(<InsightsList insights={mockInsights} />);
    
    expect(screen.getByText('velocity')).toBeInTheDocument();
    expect(screen.getByText('overdue')).toBeInTheDocument();
    expect(screen.getByText('blocked')).toBeInTheDocument();
    expect(screen.getByText('completion_time')).toBeInTheDocument();
  });
  
  it('should render correct icons for each type', () => {
    const { container } = render(<InsightsList insights={mockInsights} />);
    
    expect(container.textContent).toContain('✅'); // Positive
    expect(container.textContent).toContain('⚠️'); // Warning
    expect(container.textContent).toContain('🚨'); // Critical
    expect(container.textContent).toContain('ℹ️'); // Info
  });
  
  it('should render with empty insights array', () => {
    render(<InsightsList insights={[]} />);
    
    expect(screen.getByText('Insights & Recommendations')).toBeInTheDocument();
  });
  
  it('should render insight without action', () => {
    const insightsNoAction = [{
      type: 'positive',
      category: 'velocity',
      message: 'Great progress!',
      action: null
    }];
    
    render(<InsightsList insights={insightsNoAction} />);
    
    expect(screen.getByText('Great progress!')).toBeInTheDocument();
    expect(screen.queryByText(/Action:/)).not.toBeInTheDocument();
  });
  
  it('should apply correct styling for positive insights', () => {
    const positiveInsight = [{
      type: 'positive',
      category: 'test',
      message: 'Good job!',
      action: null
    }];
    
    const { container } = render(<InsightsList insights={positiveInsight} />);
    
    const insightCard = container.querySelector('.bg-green-50');
    expect(insightCard).toBeInTheDocument();
  });
  
  it('should apply correct styling for warning insights', () => {
    const warningInsight = [{
      type: 'warning',
      category: 'test',
      message: 'Warning message',
      action: 'Take action'
    }];
    
    const { container } = render(<InsightsList insights={warningInsight} />);
    
    const insightCard = container.querySelector('.bg-amber-50');
    expect(insightCard).toBeInTheDocument();
  });
  
  it('should apply correct styling for critical insights', () => {
    const criticalInsight = [{
      type: 'critical',
      category: 'test',
      message: 'Critical issue',
      action: 'Urgent action needed'
    }];
    
    const { container } = render(<InsightsList insights={criticalInsight} />);
    
    const insightCard = container.querySelector('.bg-red-50');
    expect(insightCard).toBeInTheDocument();
  });
  
  it('should render multiple insights of the same type', () => {
    const multipleWarnings = [
      {
        type: 'warning',
        category: 'overdue',
        message: 'First warning',
        action: 'Action 1'
      },
      {
        type: 'warning',
        category: 'workload',
        message: 'Second warning',
        action: 'Action 2'
      }
    ];
    
    render(<InsightsList insights={multipleWarnings} />);
    
    expect(screen.getByText('First warning')).toBeInTheDocument();
    expect(screen.getByText('Second warning')).toBeInTheDocument();
  });
});
