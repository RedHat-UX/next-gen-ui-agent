import { render, screen } from '@testing-library/react';

import CustomLink from '../../components/CustomLink';

describe('CustomLink', () => {
  const linkText = 'Visit OpenAI';
  const linkHref = 'https://www.openai.com';

  it('renders the link with correct text', () => {
    render(<CustomLink href={linkHref}>{linkText}</CustomLink>);
    expect(screen.getByText(linkText)).toBeInTheDocument();
  });

  it('renders the link with correct href', () => {
    render(<CustomLink href={linkHref}>{linkText}</CustomLink>);
    const link = screen.getByRole('link', { name: linkText });
    expect(link).toHaveAttribute('href', linkHref);
  });

  it('opens link in new tab with target="_blank"', () => {
    render(<CustomLink href={linkHref}>{linkText}</CustomLink>);
    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('target', '_blank');
  });
});
