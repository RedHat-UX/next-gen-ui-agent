import isArray from "lodash/isArray";
import isEmpty from "lodash/isEmpty";
import map from "lodash/map";
import { cloneElement, isValidElement, useState } from "react";

import { componentsMap } from "../constants/componentsMap";

const FragmentWrapper = ({ children }: { children?: React.ReactNode }) => (
  <>{children}</>
);

interface IProps {
  config: any;
  customProps?: Record<
    string,
    Record<string, any | ((...args: any[]) => void)>
  >;
}

const DynamicComponent = ({ config, customProps = {} }: IProps) => {
  const [customData, setCustomData] = useState(null);

  if (isEmpty(config)) {
    console.error("Config is empty");
    return null;
  }

  const componentKey = config?.key || config?.component;

  const parseProps = (props?: Record<string, any>) => {
    const newProps = { ...props };

    if (componentKey && customProps[componentKey]) {
      Object.entries(customProps[componentKey]).forEach(([key, value]) => {
        if (typeof value === "function") {
          newProps[key] = (...args: any[]) =>
            value(...args, {
              componentKey,
              // config,
              customData,
            });
        } else if (isValidElement(value)) {
          newProps[key] = cloneElement(value, {
            onClick: (event: any) =>
              value.props.onClick?.(event, {
                componentKey,
                // config,
                customData,
              }),
          });
        } else if (Array.isArray(value) && value.every(isValidElement)) {
          newProps[key] = value.map((element) =>
            cloneElement(element, {
              onClick: (event: any) =>
                element.props.onClick?.(event, {
                  componentKey,
                  // config,
                  customData,
                }),
            })
          );
        } else {
          newProps[key] = value;
        }
      });
    }

    newProps.customProps = customProps;
    newProps.setCustomData = setCustomData;

    if (Array.isArray(newProps.actions)) {
      newProps.actions = newProps.actions.map((action) => ({
        ...action,
        onClick:
          typeof action.onClick === "string"
            ? new Function("event", action.onClick)
            : action.onClick,
      }));
    }

    if (typeof newProps.onRowSelect === "string") {
      newProps.onRowSelect = new Function("data", newProps.onRowSelect);
    }

    return newProps;
  };

  const Component = componentsMap[config?.component] || FragmentWrapper;
  const newProps = parseProps(config?.props);

  return (
    <Component {...newProps}>
      {isArray(config?.children)
        ? map(config?.children, (child, index) => (
            <DynamicComponent
              config={child}
              key={(child.key || child.component || index) + index}
              customProps={customProps}
            />
          ))
        : config?.children}
    </Component>
  );
};

export default DynamicComponent;
