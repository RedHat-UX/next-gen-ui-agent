interface LinkProps {
  href: string;
  children: React.ReactNode;
}

const CustomLink: React.FC<LinkProps> = ({ href, children }) => {
  return (
    <a href={href} target="_blank">
      {children}
    </a>
  );
};

export default CustomLink;
