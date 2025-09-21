import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error: error };
  }

  componentDidCatch(error, errorInfo) {
    // You can also log the error to an error reporting service
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return (
        <div className="p-4 rounded-lg bg-red-800/50 border border-red-500 text-red-300">
          <h4 className="font-bold mb-2">Something went wrong</h4>
          <p className="text-sm">This component failed to render. Please try a different query.</p>
          <details className="text-xs mt-2">
            <summary>Error Details</summary>
            <pre className="mt-2 whitespace-pre-wrap">
              {this.state.error && this.state.error.toString()}
            </pre>
          </details>
        </div>
      );
    }

    return this.props.children; 
  }
}

export default ErrorBoundary;