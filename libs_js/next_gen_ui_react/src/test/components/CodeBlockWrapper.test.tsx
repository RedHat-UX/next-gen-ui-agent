import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { CodeBlockWrapper } from '../../components/CodeBloackWrapper';

describe('CodeBlockWrapper', () => {
  const codeSnippet = `console.log("Hello, World!");`;

  beforeEach(() => {
    // Mock clipboard API
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn(),
      },
    });
  });

  it('renders code content', () => {
    render(<CodeBlockWrapper>{codeSnippet}</CodeBlockWrapper>);
    expect(screen.getByText(/console\.log\("Hello, World!"\);/)).toBeInTheDocument();
  });

  it('copies text to clipboard when button is clicked', async () => {
    render(<CodeBlockWrapper>{codeSnippet}</CodeBlockWrapper>);

    const button = screen.getByRole('button', { name: /copy/i });
    await userEvent.click(button);

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(codeSnippet);
  });
});
