# Real-Time Web Dashboard

## Overview
Browser-based interface for monitoring test calls as they happen.

## Core Features

### 1. Live Call Monitor
- List of active calls with status indicators
- Real-time transcript updates (<2s latency)
- Current turn counter
- Conversation state display
- End call button

### 2. Call History
- Searchable list of past calls
- Filter by date, scenario, outcome
- Download transcripts and audio
- View evaluation scores
- Export reports

### 3. Audio Playback
- In-browser audio player
- Synchronized with transcript
- Speaker labels (bot/user)
- Playback speed control
- Download options

### 4. Quick Actions
- Start new test call
- Select scenario from dropdown
- Enter target phone number
- View running tests

## Technical Stack
- Frontend: React + Tailwind CSS
- Backend: Extend `core/server.py` with WebSocket support
- Real-time: Server-Sent Events (SSE) or WebSockets
- State: SQLite for call metadata

## API Endpoints Needed
```
GET  /api/calls              - List all calls
GET  /api/calls/{id}         - Get call details
GET  /api/calls/{id}/stream  - Real-time updates (SSE)
POST /api/calls/start        - Initiate new call
POST /api/calls/{id}/stop    - End active call
GET  /api/scenarios          - List available scenarios
```

## Success Criteria
- Transcripts appear in UI within 2 seconds of call completion
- Dashboard loads in <3 seconds
- Supports 50+ concurrent viewers
- Works on mobile and desktop

## Files to Modify
- `core/server.py` - Add API routes and WebSocket handlers
- `main.py` - Start dashboard alongside call server
- Create `web/` folder for frontend code
