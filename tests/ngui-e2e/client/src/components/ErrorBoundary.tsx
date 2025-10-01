import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Alert, AlertActionCloseButton } from '@patternfly/react-core';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });
    
    // Call optional error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  private handleClose = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  public render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <Alert 
          variant="danger" 
          title="Component Error" 
          actionClose={<AlertActionCloseButton onClose={this.handleClose} />}
        >
          <p>
            <strong>Something went wrong with this component.</strong>
          </p>
          <p>
            {this.state.error?.message || 'Unknown error occurred'}
          </p>
          <details style={{ marginTop: '10px' }}>
            <summary>Technical Details (for developers)</summary>
            <pre style={{ fontSize: '12px', marginTop: '8px', whiteSpace: 'pre-wrap' }}>
              {this.state.error?.stack}
            </pre>
          </details>
        </Alert>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
