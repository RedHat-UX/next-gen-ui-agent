import {
  Avatar,
  TextContent,
  TextVariants,
  Text,
} from "@patternfly/react-core";

import DynamicComponent from "./DynamicComponents";

interface IProps {
  avatar?: string;
  name?: string;
  datetime: string;
  content: string;
  actions?: any;
  customProps?: any;
}

export default function Message(props: IProps) {
  const { avatar, name, datetime, content, actions, customProps } = props;

  return (
    <div
      className="message"
      style={{ display: "flex", alignItems: "flex-start" }}
    >
      <Avatar
        size="md"
        src={
          avatar ||
          "https://www.patternfly.org/images/patternfly_avatar.9a60a33abd961931.jpg"
        }
        alt={name || "Bot"}
        className="pf-v5-u-mr-md"
      />
      <div style={{ flex: 1 }}>
        <TextContent>
          <div style={{ display: "flex", alignItems: "center" }}>
            <Text component={TextVariants.p}>
              <span className="message-sender pf-v5-u-mr-md">
                {name || "Bot"}
              </span>
              <span className="message-datetime">
                {new Date(datetime).toLocaleString()}
              </span>
            </Text>
          </div>
          <div className="pf-v5-u-my-sm">
            <DynamicComponent config={content} customProps={customProps} />
          </div>
          {actions}
        </TextContent>
      </div>
    </div>
  );
}
