# DocuHub Frontend

React + Vite + TypeScript frontend for the DocuHub document management system.

## Features

- 🔐 Authentication with JWT tokens
- 📊 Dashboard with project statistics
- 📁 Project management (CRUD operations)
- 📄 Drawing management
- 🔔 Real-time notifications
- 👥 Role-based access control
- 📱 Responsive design with Tailwind CSS

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Heroicons** - Icon library

## Prerequisites

- Node.js 18+ (recommended: 20+)
- npm or yarn

## Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Update environment variables in `.env`:
   ```
   VITE_API_BASE_URL=http://152.42.210.234
   ```

## Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`.

## Build

Build for production:
```bash
npm run build
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
