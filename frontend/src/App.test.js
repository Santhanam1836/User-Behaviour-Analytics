import { render, screen } from '@testing-library/react';
import App from './App';

// Mock socket.io-client so it doesn't try to open a real WebSocket in tests.
// App.js uses `import { io } from 'socket.io-client'` so we mock the named export.
jest.mock('socket.io-client', () => {
  const mockSocket = {
    on: jest.fn(),
    off: jest.fn(),
    emit: jest.fn(),
    disconnect: jest.fn(),
  };
  return {
    __esModule: true,
    io: jest.fn(() => mockSocket),
  };
});

test('renders the login page without crashing', () => {
  render(<App />);
  // The app shows a login form on initial load (unauthenticated state)
  const loginButton = screen.getByRole('button', { name: /login/i });
  expect(loginButton).toBeInTheDocument();
});
