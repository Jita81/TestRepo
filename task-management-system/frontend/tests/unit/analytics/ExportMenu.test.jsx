/**
 * Tests for ExportMenu Component
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ExportMenu from '../../../src/components/analytics/ExportMenu';

describe('ExportMenu', () => {
  const mockOnExport = vi.fn();
  
  beforeEach(() => {
    mockOnExport.mockClear();
  });
  
  it('should render export button', () => {
    render(<ExportMenu onExport={mockOnExport} exporting={false} />);
    
    expect(screen.getByText('Export Report')).toBeInTheDocument();
  });
  
  it('should show exporting state', () => {
    render(<ExportMenu onExport={mockOnExport} exporting={true} />);
    
    expect(screen.getByText('Exporting...')).toBeInTheDocument();
  });
  
  it('should disable button when exporting', () => {
    render(<ExportMenu onExport={mockOnExport} exporting={true} />);
    
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });
  
  it('should open menu when button clicked', async () => {
    render(<ExportMenu onExport={mockOnExport} exporting={false} />);
    
    const button = screen.getByText('Export Report');
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(screen.getByText('Export as PDF')).toBeInTheDocument();
    });
  });
  
  it('should display all export options', async () => {
    render(<ExportMenu onExport={mockOnExport} exporting={false} />);
    
    fireEvent.click(screen.getByText('Export Report'));
    
    await waitFor(() => {
      expect(screen.getByText('Export as PDF')).toBeInTheDocument();
      expect(screen.getByText('Export as CSV')).toBeInTheDocument();
      expect(screen.getByText('Export Both')).toBeInTheDocument();
      expect(screen.getByText('Velocity Report (CSV)')).toBeInTheDocument();
      expect(screen.getByText('Workload Report (CSV)')).toBeInTheDocument();
      expect(screen.getByText('Bottlenecks (CSV)')).toBeInTheDocument();
      expect(screen.getByText('Trends (CSV)')).toBeInTheDocument();
    });
  });
  
  it('should call onExport with PDF format', async () => {
    render(<ExportMenu onExport={mockOnExport} exporting={false} />);
    
    fireEvent.click(screen.getByText('Export Report'));
    
    await waitFor(() => {
      const pdfOption = screen.getByText('Export as PDF');
      fireEvent.click(pdfOption);
    });
    
    expect(mockOnExport).toHaveBeenCalledWith('pdf', 'summary');
  });
  
  it('should call onExport with CSV format', async () => {
    render(<ExportMenu onExport={mockOnExport} exporting={false} />);
    
    fireEvent.click(screen.getByText('Export Report'));
    
    await waitFor(() => {
      const csvOption = screen.getByText('Export as CSV');
      fireEvent.click(csvOption);
    });
    
    expect(mockOnExport).toHaveBeenCalledWith('csv', 'summary');
  });
  
  it('should call onExport with both formats', async () => {
    render(<ExportMenu onExport={mockOnExport} exporting={false} />);
    
    fireEvent.click(screen.getByText('Export Report'));
    
    await waitFor(() => {
      const bothOption = screen.getByText('Export Both');
      fireEvent.click(bothOption);
    });
    
    expect(mockOnExport).toHaveBeenCalledWith('both', 'summary');
  });
  
  it('should call onExport with velocity report type', async () => {
    render(<ExportMenu onExport={mockOnExport} exporting={false} />);
    
    fireEvent.click(screen.getByText('Export Report'));
    
    await waitFor(() => {
      const velocityOption = screen.getByText('Velocity Report (CSV)');
      fireEvent.click(velocityOption);
    });
    
    expect(mockOnExport).toHaveBeenCalledWith('csv', 'velocity');
  });
  
  it('should call onExport with workload report type', async () => {
    render(<ExportMenu onExport=<mockOnExport} exporting={false} />);
    
    fireEvent.click(screen.getByText('Export Report'));
    
    await waitFor(() => {
      const workloadOption = screen.getByText('Workload Report (CSV)');
      fireEvent.click(workloadOption);
    });
    
    expect(mockOnExport).toHaveBeenCalledWith('csv', 'workload');
  });
  
  it('should close menu after selection', async () => {
    render(<ExportMenu onExport={mockOnExport} exporting={false} />);
    
    fireEvent.click(screen.getByText('Export Report'));
    
    await waitFor(() => {
      const pdfOption = screen.getByText('Export as PDF');
      fireEvent.click(pdfOption);
    });
    
    await waitFor(() => {
      expect(screen.queryByText('Export as PDF')).not.toBeInTheDocument();
    });
  });
  
  it('should show helper text in menu', async () => {
    render(<ExportMenu onExport={mockOnExport} exporting={false} />);
    
    fireEvent.click(screen.getByText('Export Report'));
    
    await waitFor(() => {
      expect(screen.getByText('Reports include current date range')).toBeInTheDocument();
    });
  });
  
  it('should render export icons', async () => {
    const { container } = render(<ExportMenu onExport={mockOnExport} exporting={false} />);
    
    fireEvent.click(screen.getByText('Export Report'));
    
    await waitFor(() => {
      expect(container.textContent).toContain('📄'); // PDF
      expect(container.textContent).toContain('📊'); // CSV
      expect(container.textContent).toContain('📑'); // Both
      expect(container.textContent).toContain('📈'); // Velocity
      expect(container.textContent).toContain('👥'); // Workload
      expect(container.textContent).toContain('🚧'); // Bottlenecks
      expect(container.textContent).toContain('📉'); // Trends
    });
  });
});
