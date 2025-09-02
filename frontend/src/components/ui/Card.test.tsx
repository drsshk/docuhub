import React from 'react';
import { render, screen } from '@testing-library/react';
import { Card } from './Card';

describe('Card', () => {
  it('renders with children content', () => {
    render(
      <Card>
        <h2>Test Title</h2>
        <p>Test content</p>
      </Card>
    );
    
    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <Card className="custom-class">
        <p>Test content</p>
      </Card>
    );
    
    expect(container.firstChild).toHaveClass('custom-class');
  });
});