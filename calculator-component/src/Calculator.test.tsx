import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { Calculator } from './Calculator';

describe('Calculator Component', () => {
  describe('Rendering', () => {
    test('renders calculator with title', () => {
      render(<Calculator />);
      expect(screen.getByText('Simple Calculator')).toBeInTheDocument();
    });

    test('renders two number input fields', () => {
      render(<Calculator />);
      expect(screen.getByLabelText('First Number')).toBeInTheDocument();
      expect(screen.getByLabelText('Second Number')).toBeInTheDocument();
    });

    test('renders all operation radio buttons', () => {
      render(<Calculator />);
      expect(screen.getByLabelText('Addition')).toBeInTheDocument();
      expect(screen.getByLabelText('Subtraction')).toBeInTheDocument();
      expect(screen.getByLabelText('Multiplication')).toBeInTheDocument();
      expect(screen.getByLabelText('Division')).toBeInTheDocument();
    });

    test('renders Calculate and Clear buttons', () => {
      render(<Calculator />);
      expect(screen.getByRole('button', { name: /calculate result/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /clear calculator/i })).toBeInTheDocument();
    });

    test('addition is selected by default', () => {
      render(<Calculator />);
      const addRadio = screen.getByLabelText('Addition') as HTMLInputElement;
      expect(addRadio.checked).toBe(true);
    });
  });

  describe('Addition Operation', () => {
    test('adds two positive numbers correctly', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.type(screen.getByLabelText('First Number'), '5');
      await user.type(screen.getByLabelText('Second Number'), '3');
      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        expect(screen.getByRole('status')).toHaveTextContent('Result: 8');
      });
    });

    test('adds negative numbers correctly', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.type(screen.getByLabelText('First Number'), '-5');
      await user.type(screen.getByLabelText('Second Number'), '-3');
      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        expect(screen.getByRole('status')).toHaveTextContent('Result: -8');
      });
    });

    test('adds decimal numbers correctly', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.type(screen.getByLabelText('First Number'), '2.5');
      await user.type(screen.getByLabelText('Second Number'), '3.7');
      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        expect(screen.getByRole('status')).toHaveTextContent('Result: 6.2');
      });
    });
  });

  describe('Subtraction Operation', () => {
    test('subtracts two numbers correctly', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.type(screen.getByLabelText('First Number'), '10');
      await user.type(screen.getByLabelText('Second Number'), '3');
      await user.click(screen.getByLabelText('Subtraction'));
      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        expect(screen.getByRole('status')).toHaveTextContent('Result: 7');
      });
    });

    test('handles negative results', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.type(screen.getByLabelText('First Number'), '5');
      await user.type(screen.getByLabelText('Second Number'), '10');
      await user.click(screen.getByLabelText('Subtraction'));
      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        expect(screen.getByRole('status')).toHaveTextContent('Result: -5');
      });
    });
  });

  describe('Multiplication Operation', () => {
    test('multiplies two numbers correctly', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.type(screen.getByLabelText('First Number'), '4');
      await user.type(screen.getByLabelText('Second Number'), '5');
      await user.click(screen.getByLabelText('Multiplication'));
      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        expect(screen.getByRole('status')).toHaveTextContent('Result: 20');
      });
    });

    test('multiplication by zero returns zero', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.type(screen.getByLabelText('First Number'), '5');
      await user.type(screen.getByLabelText('Second Number'), '0');
      await user.click(screen.getByLabelText('Multiplication'));
      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        expect(screen.getByRole('status')).toHaveTextContent('Result: 0');
      });
    });

    test('multiplies decimal numbers correctly', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.type(screen.getByLabelText('First Number'), '2.5');
      await user.type(screen.getByLabelText('Second Number'), '4');
      await user.click(screen.getByLabelText('Multiplication'));
      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        expect(screen.getByRole('status')).toHaveTextContent('Result: 10');
      });
    });
  });

  describe('Division Operation', () => {
    test('divides two numbers correctly', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.type(screen.getByLabelText('First Number'), '20');
      await user.type(screen.getByLabelText('Second Number'), '4');
      await user.click(screen.getByLabelText('Division'));
      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        expect(screen.getByRole('status')).toHaveTextContent('Result: 5');
      });
    });

    test('handles division with decimal result', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.type(screen.getByLabelText('First Number'), '10');
      await user.type(screen.getByLabelText('Second Number'), '3');
      await user.click(screen.getByLabelText('Division'));
      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        const resultText = screen.getByRole('status').textContent;
        expect(resultText).toContain('3.3333333333');
      });
    });

    test('shows error when dividing by zero', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.type(screen.getByLabelText('First Number'), '10');
      await user.type(screen.getByLabelText('Second Number'), '0');
      await user.click(screen.getByLabelText('Division'));
      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent('Cannot divide by zero');
      });
    });
  });

  describe('Error Handling', () => {
    test('shows error when first number is empty', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.type(screen.getByLabelText('Second Number'), '5');
      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent('Please enter both numbers');
      });
    });

    test('shows error when second number is empty', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.type(screen.getByLabelText('First Number'), '5');
      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent('Please enter both numbers');
      });
    });

    test('shows error when both numbers are empty', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent('Please enter both numbers');
      });
    });

    test('clears error when user starts typing', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      // Trigger an error
      await user.click(screen.getByRole('button', { name: /calculate result/i }));
      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument();
      });

      // Start typing
      await user.type(screen.getByLabelText('First Number'), '5');

      // Error should be cleared
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });
  });

  describe('Clear Functionality', () => {
    test('clears all inputs and results', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.type(screen.getByLabelText('First Number'), '10');
      await user.type(screen.getByLabelText('Second Number'), '5');
      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        expect(screen.getByRole('status')).toBeInTheDocument();
      });

      await user.click(screen.getByRole('button', { name: /clear calculator/i }));

      expect(screen.getByLabelText('First Number')).toHaveValue(null);
      expect(screen.getByLabelText('Second Number')).toHaveValue(null);
      expect(screen.queryByRole('status')).not.toBeInTheDocument();
    });

    test('clears error messages', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.click(screen.getByRole('button', { name: /calculate result/i }));
      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument();
      });

      await user.click(screen.getByRole('button', { name: /clear calculator/i }));

      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('has proper ARIA labels for inputs', () => {
      render(<Calculator />);
      const firstInput = screen.getByLabelText('First Number');
      const secondInput = screen.getByLabelText('Second Number');

      expect(firstInput).toHaveAttribute('type', 'number');
      expect(secondInput).toHaveAttribute('type', 'number');
    });

    test('marks inputs as invalid when there is an error', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        const firstInput = screen.getByLabelText('First Number');
        const secondInput = screen.getByLabelText('Second Number');
        expect(firstInput).toHaveAttribute('aria-invalid', 'true');
        expect(secondInput).toHaveAttribute('aria-invalid', 'true');
      });
    });

    test('error message has role="alert"', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        const alert = screen.getByRole('alert');
        expect(alert).toBeInTheDocument();
        expect(alert).toHaveAttribute('aria-live', 'polite');
      });
    });

    test('result has role="status"', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.type(screen.getByLabelText('First Number'), '5');
      await user.type(screen.getByLabelText('Second Number'), '3');
      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        const status = screen.getByRole('status');
        expect(status).toBeInTheDocument();
        expect(status).toHaveAttribute('aria-live', 'polite');
      });
    });

    test('calculator has region role', () => {
      render(<Calculator />);
      const calculator = screen.getByRole('region', { name: 'Calculator' });
      expect(calculator).toBeInTheDocument();
    });
  });

  describe('Keyboard Interactions', () => {
    test('Enter key triggers calculation', async () => {
      render(<Calculator />);
      const firstInput = screen.getByLabelText('First Number');

      fireEvent.change(firstInput, { target: { value: '5' } });
      fireEvent.change(screen.getByLabelText('Second Number'), { target: { value: '3' } });
      fireEvent.keyDown(firstInput, { key: 'Enter', code: 'Enter' });

      await waitFor(() => {
        expect(screen.getByRole('status')).toHaveTextContent('Result: 8');
      });
    });

    test('Escape key clears calculator', async () => {
      render(<Calculator />);
      const firstInput = screen.getByLabelText('First Number');

      fireEvent.change(firstInput, { target: { value: '5' } });
      fireEvent.change(screen.getByLabelText('Second Number'), { target: { value: '3' } });
      fireEvent.keyDown(firstInput, { key: 'Escape', code: 'Escape' });

      expect(firstInput).toHaveValue(null);
      expect(screen.getByLabelText('Second Number')).toHaveValue(null);
    });
  });

  describe('Edge Cases', () => {
    test('handles very large numbers', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.type(screen.getByLabelText('First Number'), '999999999');
      await user.type(screen.getByLabelText('Second Number'), '1');
      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        expect(screen.getByRole('status')).toHaveTextContent('Result: 1000000000');
      });
    });

    test('handles very small decimal numbers', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.type(screen.getByLabelText('First Number'), '0.001');
      await user.type(screen.getByLabelText('Second Number'), '0.002');
      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        expect(screen.getByRole('status')).toHaveTextContent('Result: 0.003');
      });
    });

    test('rounds result to avoid floating point precision issues', async () => {
      const user = userEvent.setup();
      render(<Calculator />);

      await user.type(screen.getByLabelText('First Number'), '0.1');
      await user.type(screen.getByLabelText('Second Number'), '0.2');
      await user.click(screen.getByRole('button', { name: /calculate result/i }));

      await waitFor(() => {
        expect(screen.getByRole('status')).toHaveTextContent('Result: 0.3');
      });
    });
  });
});