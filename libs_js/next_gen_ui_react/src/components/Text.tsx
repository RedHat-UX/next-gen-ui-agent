import { JSX } from "react";

type TextProps = {
  component: keyof JSX.IntrinsicElements; // 'h1', 'h2', 'p', etc.
  children: React.ReactNode;
  className?: string;
};

const Text: React.FC<TextProps> = ({
  component: Component = "p",
  children,
  className,
}) => {
  return <Component className={className}>{children}</Component>;
};

export default Text;
