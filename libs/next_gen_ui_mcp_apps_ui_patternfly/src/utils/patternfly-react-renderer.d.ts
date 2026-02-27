declare module "@rhngui/patternfly-react-renderer" {
  import { ComponentType } from "react";

  interface DynamicComponentProps {
    config: any;
  }

  const DynamicComponent: ComponentType<DynamicComponentProps>;
  export default DynamicComponent;
  export { ComponentHandlerRegistryProvider, useComponentHandlerRegistry, type AutoFormatterIdOption, type AutoFormatterProviderOptions, type ComponentHandlerRegistry, type HandlerResolver, type FormatterContext, type FormatterContextMatcher, type CellFormatter, type ItemClickHandler, type ItemClickPayload, type ItemDataFieldValue, } from './components/ComponentHandlerRegistry';
}
