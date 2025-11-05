# Code Review Agent - Frontend

Next.js frontend for the AWS Bedrock Code Review Agent.

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

```bash
npm run build
npm start
```

## Features

- **Code Input**: Paste code directly for review
- **File Upload**: Upload code files or diff files
- **Real-time Analysis**: Get instant code review results
- **Issue Detection**: See bugs, style issues, and documentation gaps
- **Auto-fix Suggestions**: Apply fixes with one click
- **Beautiful UI**: Modern, responsive design with Tailwind CSS

## Project Structure

```
frontend/
├── app/
│   ├── components/      # React components
│   ├── lib/            # API utilities
│   ├── layout.tsx      # Root layout
│   ├── page.tsx        # Main page
│   └── globals.css     # Global styles
├── public/             # Static assets
└── package.json        # Dependencies
```

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000`.

Key endpoints:
- `POST /api/review/code` - Review code from text
- `POST /api/review/file` - Review uploaded file
- `POST /api/fix/apply` - Apply a fix to a file
- `GET /api/results` - Get recent review results

