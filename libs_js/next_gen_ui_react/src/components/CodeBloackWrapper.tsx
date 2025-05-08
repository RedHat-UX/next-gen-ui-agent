import {
  CodeBlock,
  CodeBlockAction,
  CodeBlockCode,
  ClipboardCopyButton,
} from "@patternfly/react-core";
import React, { useState } from "react";

const CodeBlockWrapper: React.FC<{ children: string }> = ({ children }) => {
  const [copied, setCopied] = useState(false);

  const onCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const actions = (
    <CodeBlockAction>
      <ClipboardCopyButton
        id="copy-button"
        textId="code-content"
        aria-label="Copy to clipboard"
        onClick={() => onCopy(children)}
        exitDelay={copied ? 1500 : 600}
        maxWidth="110px"
        variant="plain"
      >
        {copied ? "Copied!" : "Copy"}
      </ClipboardCopyButton>
    </CodeBlockAction>
  );

  return (
    <CodeBlock actions={actions}>
      <CodeBlockCode id="code-content">{children}</CodeBlockCode>
    </CodeBlock>
  );
};

export { CodeBlockWrapper };
