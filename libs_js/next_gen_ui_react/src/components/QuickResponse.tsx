import Message from "@patternfly/chatbot/dist/dynamic/Message";
import { isEmpty } from "lodash";
import map from "lodash/map";
import React from "react";

interface QuickResponse {
  id: string;
  content: string;
  onClick: string;
}

interface QuickResponseProps {
  message: string;
  actions: QuickResponse[];
}

const QuickResponse: React.FC<QuickResponseProps> = ({ message, actions }) => {
  const processedActions = !isEmpty(actions)
    ? map(actions, (action) => ({
        ...action,
        onClick:
          typeof action.onClick === "string"
            ? new Function("event", action.onClick)
            : action.onClick,
      }))
    : [];

  return (
    <Message
      name="Bot"
      role="bot"
      avatar="https://www.patternfly.org/images/patternfly_avatar.9a60a33abd961931.jpg"
      content={message}
      quickResponses={processedActions}
    />
  );
};

export default QuickResponse;
