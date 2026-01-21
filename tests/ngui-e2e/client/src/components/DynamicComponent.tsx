import React from 'react';
import { Alert, EmptyState, EmptyStateBody, Title } from '@patternfly/react-core';
import { ExclamationTriangleIcon } from '@patternfly/react-icons';
import DynamicUILibrary from '@rhngui/patternfly-react-renderer';
import ErrorBoundary from './ErrorBoundary';

interface DynamicComponentProps {
  config: Record<string, unknown>;
  showRawConfig?: boolean; // For debugging
}

// Component validation functions
const validateConfig = (config: Record<string, unknown>): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];
  
  if (!config) {
    errors.push('Config is null or undefined');
    return { isValid: false, errors };
  }

  if (typeof config !== 'object') {
    errors.push('Config must be an object');
    return { isValid: false, errors };
  }

  if (!config.id && !config.component && !config.fields) {
    errors.push('Config missing required component definition (type, component, or components)');
  }

  if (Object.keys(config).length === 0) {
    errors.push('Config object is empty');
  }

  return { isValid: errors.length === 0, errors };
};

const ComponentNotAvailableMessage: React.FC<{ errors: string[]; config?: Record<string, unknown>; showRawConfig?: boolean }> = ({ 
  errors, 
  config, 
  showRawConfig 
}) => (
  <EmptyState variant="sm">
    <div className="dynamic-error-icon-container">
      <ExclamationTriangleIcon />
    </div>
    <Title headingLevel="h4" size="md">
      Component Not Available
    </Title>
    <EmptyStateBody>
      <p>The requested component could not be rendered.</p>
      <ul className="dynamic-error-list">
        {errors.map((error, index) => (
          <li key={index}>{error}</li>
        ))}
      </ul>
      
      {showRawConfig && config && (
        <details className="dynamic-debug-details">
          <summary>Raw Config (Debug)</summary>
          <pre className="dynamic-debug-pre">
            {JSON.stringify(config, null, 2)}
          </pre>
        </details>
      )}
    </EmptyStateBody>
  </EmptyState>
);

const DynamicComponent: React.FC<DynamicComponentProps> = ({ 
  config, 
  showRawConfig = false,
}) => {

  // Prepare config - map "table" to "data-view" for compatibility
  // Note: The renderer supports both, but "data-view" is the canonical name
  const preparedConfig = React.useMemo(() => {
    const componentType = typeof config.component === 'string' ? config.component : '';
    if (componentType === 'table') {
      return { ...config, component: 'data-view' };
    }
    return config;
  }, [config]);

  // Validate the config
  const { isValid, errors } = validateConfig(config);

  if (!isValid) {
    return (
      <ComponentNotAvailableMessage 
        errors={errors} 
        config={config} 
        showRawConfig={showRawConfig} 
      />
    );
  }

  // Custom error boundary fallback for DynamicComponent failures
  const DynamicComponentErrorFallback = (
    <Alert variant="warning" title="Component Rendering Failed">
      <p>The component could not be rendered due to an internal error.</p>
      <p>This might be due to:</p>
      <ul>
        <li>Invalid component configuration</li>
        <li>Missing component dependencies</li>
        <li>Component implementation issues</li>
      </ul>
      
      {showRawConfig && (
        <details className="dynamic-loading-details">
          <summary>Component Config</summary>
          <pre className="dynamic-loading-pre">
            {JSON.stringify(preparedConfig, null, 2)}
          </pre>
        </details>
      )}
    </Alert>
  );

  // Pass config to the renderer
  // The renderer (DataViewWrapper) automatically uses ComponentHandlerRegistry from context
  // if available, so no need to manually create handlerResolver
  const renderProps: Record<string, unknown> = { 
    config: preparedConfig,
  };

  return (
    <div className="dynamic-component-container">
      <ErrorBoundary 
        fallback={DynamicComponentErrorFallback}
        onError={(error, errorInfo) => {
          // Log error details for debugging
          console.error('SafeDynamicComponent Error:', {
            error: error.message,
            stack: error.stack,
            componentStack: errorInfo.componentStack,
            config: preparedConfig
          });
        }}
      >
        <DynamicUILibrary {...renderProps} />
      </ErrorBoundary>
    </div>
  );
};

export default DynamicComponent;
