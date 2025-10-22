# NGUI End-to-End Testing Application

This directory contains a complete end-to-end testing application for the Next Gen UI (NGUI) system, demonstrating AI-driven UI component generation with a split server/client architecture.

## Structure

```
ngui-e2e/
├── server/           # FastAPI backend with NGUI agent
└── client/           # React frontend application
```

## Components

- **`server/`** - FastAPI backend that provides AI-powered UI generation APIs using LangGraph integration
- **`client/`** - React frontend application that consumes the backend APIs and renders dynamic UI components

## Getting Started

Each subfolder contains its own README with detailed setup, installation, configuration, and running instructions:

- See [`server/README.md`](server/README.md) for backend setup and configuration
- See [`client/README.md`](client/README.md) for frontend setup and configuration

## Purpose

This application serves as a comprehensive testing and demonstration platform for the NGUI system, allowing contributors to understand the complete workflow from AI model inference to dynamic UI component rendering.
