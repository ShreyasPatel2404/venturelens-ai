// frontend/src/components/ErrorBoundary.jsx
import { Component } from "react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error("VentureLens Error:", error, info);
  }

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center px-6"
           style={{ fontFamily: "'DM Mono', monospace" }}>
        <div className="max-w-md text-center space-y-4">
          <div className="text-5xl">⚠️</div>
          <h2 className="text-xl font-bold text-red-400">Something went wrong</h2>
          <p className="text-gray-500 text-sm">
            {this.state.error?.message || "An unexpected error occurred."}
          </p>
          <button
            onClick={() => { this.setState({ hasError: false, error: null }); window.location.href = "/"; }}
            className="border border-amber-400/40 hover:border-amber-400 text-amber-400 px-6 py-2 rounded-lg text-sm transition-all"
          >
            ← Go back to home
          </button>
        </div>
      </div>
    );
  }
}