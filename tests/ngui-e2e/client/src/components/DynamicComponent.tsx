import React from 'react';
import { Alert, EmptyState, EmptyStateBody, Title } from '@patternfly/react-core';
import { ExclamationTriangleIcon } from '@patternfly/react-icons';
// @ts-ignore - dynamicui module doesn't have type definitions
// import DynamicUILibrary from 'dynamicui';
import ErrorBoundary from './ErrorBoundary';

interface DynamicComponentProps {
  config: any;
  showRawConfig?: boolean; // For debugging
}

// Component validation functions
const validateConfig = (config: any): { isValid: boolean; errors: string[] } => {
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

const ComponentNotAvailableMessage: React.FC<{ errors: string[]; config?: any; showRawConfig?: boolean }> = ({ 
  errors, 
  config, 
  showRawConfig 
}) => (
  <EmptyState variant="sm">
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      marginBottom: '16px',
      color: 'var(--pf-v6-global--warning-color--100)'
    }}>
      <ExclamationTriangleIcon size={48} />
    </div>
    <Title headingLevel="h4" size="md">
      Component Not Available
    </Title>
    <EmptyStateBody>
      <p>The requested component could not be rendered.</p>
      <ul style={{ textAlign: 'left', marginTop: '10px' }}>
        {errors.map((error, index) => (
          <li key={index}>{error}</li>
        ))}
      </ul>
      
      {showRawConfig && config && (
        <details style={{ marginTop: '15px', textAlign: 'left' }}>
          <summary>Raw Config (Debug)</summary>
          <pre style={{ 
            fontSize: '12px', 
            background: 'var(--pf-v6-global--BackgroundColor--light-300)',
            padding: '10px',
            borderRadius: '4px',
            marginTop: '8px',
            maxHeight: '200px',
            overflow: 'auto'
          }}>
            {JSON.stringify(config, null, 2)}
          </pre>
        </details>
      )}
    </EmptyStateBody>
  </EmptyState>
);

const DynamicComponent: React.FC<DynamicComponentProps> = ({ 
  config, 
  showRawConfig = false 
}) => {
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
        <details style={{ marginTop: '10px' }}>
          <summary>Component Config</summary>
          <pre style={{ 
            fontSize: '12px', 
            marginTop: '8px',
            maxHeight: '150px',
            overflow: 'auto'
          }}>
            {JSON.stringify(config, null, 2)}
          </pre>
        </details>
      )}
    </Alert>
  );

  return (
    <ErrorBoundary
      fallback={DynamicComponentErrorFallback}
      onError={(error, errorInfo) => {
        // Log error details for debugging
        console.error('SafeDynamicComponent Error:', {
          error: error.message,
          stack: error.stack,
          componentStack: errorInfo.componentStack,
          config: config
        });
      }}
    >
      {/* <DynamicUILibrary config={config} /> */}
      <div>DynamicUI component placeholder (not needed for web components PoC)</div>
    </ErrorBoundary>
  );
};

export default DynamicComponent;
