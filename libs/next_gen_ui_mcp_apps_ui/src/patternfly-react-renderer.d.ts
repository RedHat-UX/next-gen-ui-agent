declare module "@rhngui/patternfly-react-renderer" {
  import { ComponentType } from "react";

  interface DynamicComponentProps {
    config: any;
  }

  const DynamicComponent: ComponentType<DynamicComponentProps>;
  export default DynamicComponent;
}
