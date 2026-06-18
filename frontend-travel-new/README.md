# Frontend Setup Guide

## Prerequisites
- Node.js (v18 or higher)
- npm (Node package manager)
- Angular CLI

## Installation Steps

### 1. Install Node.js
If not already installed:
- Download from [nodejs.org](https://nodejs.org/)
- Or use the pre-installed version in GenAI Lab

### 2. Install Angular CLI (Global)
```bash
npm install -g @angular/cli
```

### 3. Navigate to Frontend Directory
```bash
cd frontend
```

### 4. Install Dependencies
```bash
npm install
```

This will install:
- Angular framework and modules
- TypeScript
- RxJS
- Development tools

### 5. Verify Installation
```bash
ng version
```

You should see Angular CLI and project versions.

### 6. Configure Environment

Edit `src/environments/environment.ts` if backend is on different port:
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5000/api'
};
```

### 7. Start Development Server
```bash
npm start
# or
ng serve
```

The app will be available at: `http://localhost:4200`

### 8. Open in Browser
Navigate to `http://localhost:4200`

You should see the Travel Itinerary Assistant homepage.

## Development Commands

| Command | Description |
|---------|-------------|
| `npm start` | Start dev server |
| `ng serve` | Start dev server (alternative) |
| `ng build` | Build for production |
| `ng test` | Run unit tests |
| `ng lint` | Lint code |

## Project Structure

```
src/
├── app/
│   ├── components/          # UI components
│   │   ├── trip-form/       # Trip input form
│   │   ├── chat-interface/  # Chat UI
│   │   └── itinerary-display/ # Itinerary view
│   ├── services/            # API services
│   │   └── api.service.ts   # Backend API calls
│   ├── models/              # TypeScript interfaces
│   │   └── itinerary.model.ts
│   ├── app.component.ts     # Main app component
│   ├── app.module.ts        # App module
│   └── app.component.html   # Main template
├── environments/            # Environment configs
├── assets/                  # Static assets
├── styles.scss              # Global styles
└── index.html              # Main HTML file
```

## Configuration

### Change Backend URL
Edit `src/environments/environment.ts`:
```typescript
apiUrl: 'http://different-host:5000/api'
```

### Change Port
```bash
ng serve --port 4201
```

### Enable Production Mode
```bash
ng build --configuration production
```

## Component Overview

### Trip Form Component
- Collects user preferences
- Validates input
- Emits form data to parent

### Chat Interface Component
- Displays conversation history
- Handles user input
- Shows typing indicators

### Itinerary Display Component
- Renders generated itinerary
- Provides export options
- Print-friendly layout

### API Service
- Handles HTTP requests
- Manages backend communication
- Error handling

## Styling

### Global Styles
Located in `src/styles.scss`:
- CSS reset
- Utility classes
- Theme colors
- Responsive breakpoints

### Component Styles
Each component has its own `.scss` file:
- Scoped to component
- SCSS features (nesting, variables)
- Responsive design

### Color Palette
```scss
Primary: #667eea
Secondary: #764ba2
Success: #4caf50
Error: #f44336
```

## Development Tips

### Hot Module Replacement
Angular dev server automatically reloads on changes.

### Browser DevTools
Use Angular DevTools extension for Chrome/Edge for debugging.

### Debugging
Open browser console (F12) to see:
- API requests
- Console logs
- Network activity
- Component state

### TypeScript Strict Mode
Enabled by default for type safety.

## Troubleshooting

### Issue: Cannot connect to backend
**Solution:** 
1. Ensure backend is running on port 5000
2. Check `environment.ts` has correct API URL
3. Look for CORS errors in console

### Issue: Port 4200 already in use
**Solution:**
```bash
ng serve --port 4201
```

### Issue: Module not found
**Solution:**
```bash
npm install
```

### Issue: Compilation errors
**Solution:**
1. Check TypeScript syntax
2. Ensure all imports are correct
3. Run `npm install` to update dependencies

### Issue: Styles not loading
**Solution:**
1. Check `.scss` syntax
2. Restart dev server
3. Clear browser cache

## Building for Production

### Create Production Build
```bash
ng build --configuration production
```

Output in `dist/travel-itinerary-frontend/`

### Serve Production Build
```bash
# Install serve globally
npm install -g serve

# Serve the build
cd dist/travel-itinerary-frontend
serve -s .
```

## Testing

### Run Unit Tests
```bash
ng test
```

### Run E2E Tests
```bash
ng e2e
```

## Performance Optimization

- Lazy loading modules
- AOT compilation (enabled by default)
- Tree shaking in production builds
- Minification and uglification

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Edge (latest)
- Safari (latest)

## Next Steps

1. Ensure backend is running
2. Test form submission
3. Verify API integration
4. Customize styling if needed
5. Add features for hackathon
