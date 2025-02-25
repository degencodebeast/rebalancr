# Rebalancr Frontend

AI-powered portfolio rebalancing for DeFi investors. This frontend application provides an intuitive interface for portfolio management, AI-assisted trading, and yield optimization.

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Features

- Portfolio visualization and management
- AI-powered trading recommendations
- Real-time market updates via WebSockets
- DeFi yield optimization

## Development

- Built with Next.js 14 using the App Router
- TypeScript for type safety
- Tailwind CSS for styling
- WebSocket integration for real-time data

## Project Structure

The project follows a feature-based organization:

- `src/app/*` - Next.js pages using App Router
- `src/components/*` - Reusable React components
- `src/hooks/*` - Custom React hooks
- `src/lib/*` - Utility functions and services

## Testing WebSocket Connection

Visit the `/dashboard` page to test WebSocket connectivity with the backend server.
