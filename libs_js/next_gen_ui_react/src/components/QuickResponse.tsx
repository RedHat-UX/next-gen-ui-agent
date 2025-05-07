import { Button, Flex, FlexItem, Card, CardBody } from "@patternfly/react-core";
import React from "react";

interface ActionButton {
  label: string;
  onClick: () => void;
}

interface QuickResponseProps {
  message: string;
  actions: ActionButton[];
}

const QuickResponse: React.FC<QuickResponseProps> = ({ message, actions }) => {
  console.log(actions);
  return (
    <Card>
      <CardBody>
        <p className="pf-v5-u-my-sm">{message}</p>
        <Flex gap={{ default: "gapMd" }}>
          {actions.map((action, index) => (
            <FlexItem key={index}>
              <Button onClick={action.onClick} size="sm">
                {action.label}
              </Button>
            </FlexItem>
          ))}
        </Flex>
      </CardBody>
    </Card>
  );
};

export default QuickResponse;
