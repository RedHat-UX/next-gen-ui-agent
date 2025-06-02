import {
  Accordion,
  AccordionItem,
  AccordionContent,
  AccordionToggle,
} from "@patternfly/react-core";
import map from "lodash/map";
import React, { useState } from "react";

interface AccordionWrapperProps {
  items: {
    id: string;
    title: string;
    content: string | React.ReactNode;
  }[];
}

const AccordionWrapper: React.FC<AccordionWrapperProps> = ({ items }) => {
  console.log(items);
  const [expanded, setExpanded] = useState<string | null>(null);

  const onToggle = (id: string) => {
    setExpanded((prev) => (prev === id ? null : id));
  };

  return (
    <Accordion asDefinitionList>
      {map(items, (item) => (
        <AccordionItem key={item.id} isExpanded={expanded === item.id}>
          <AccordionToggle
            onClick={() => {
              onToggle(item.id);
            }}
            id={item.id}
          >
            {item.title}
          </AccordionToggle>
          <AccordionContent id="def-list-expand1">
            {item.content}
          </AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  );
};

export default AccordionWrapper;
