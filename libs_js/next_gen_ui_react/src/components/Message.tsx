import Message from "@patternfly/chatbot/dist/dynamic/Message";

import DynamicComponent from "./DynamicComponents";

interface IProps {
  avatar?: string;
  name?: string;
  datetime: string;
  content: string;
  actions?: any;
  customProps?: any;
}

export default function MessageWrapper(props: IProps) {
  const { avatar, name, datetime, content, actions, customProps } = props;

  return (
    <Message
      avatar={
        avatar ||
        "https://www.patternfly.org/images/patternfly_avatar.9a60a33abd961931.jpg"
      }
      name={name}
      role="user"
      timestamp={new Date(datetime).toLocaleString()}
      extraContent={{
        beforeMainContent: (
          <DynamicComponent config={content} customProps={customProps} />
        ),
        afterMainContent: actions,
      }}
    />
  );
}
