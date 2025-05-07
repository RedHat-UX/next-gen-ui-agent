import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionToggle,
} from "@patternfly/react-core";
import React, { createContext, useContext, useState } from "react";

// Create Context to share state
const AccordionContext = createContext<{
  expanded: string | null;
  onToggle: (id: string) => void;
} | null>(null);

const AccordionWrapper: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [expanded, setExpanded] = useState<string | null>(null);

  const onToggle = (id: string) => {
    setExpanded((prev) => (prev === id ? null : id));
  };

  return (
    <AccordionContext.Provider value={{ expanded, onToggle }}>
      <Accordion asDefinitionList>{children}</Accordion>
    </AccordionContext.Provider>
  );
};

const AccordionItemWrapper: React.FC<{
  id: string;
  title: string;
  children: React.ReactNode;
}> = ({ id, title, children }) => {
  const context = useContext(AccordionContext);
  if (!context)
    throw new Error(
      "AccordionItemWrapper must be used within an AccordionWrapper"
    );

  const { expanded, onToggle } = context;

  return (
    <AccordionItem>
      <AccordionToggle
        onClick={() => onToggle(id)}
        isExpanded={expanded === id}
        id={id}
      >
        {title}
      </AccordionToggle>
      <AccordionContent id={`${id}-content`} isHidden={expanded !== id}>
        {children}
      </AccordionContent>
    </AccordionItem>
  );
};

export { AccordionWrapper, AccordionItemWrapper };
