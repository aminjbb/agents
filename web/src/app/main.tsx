import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ControlRoom } from '@/pages/control-room';
import './theme.css';

const client = new QueryClient({ defaultOptions: { mutations: { retry: false } } });
const root = document.getElementById('root');
if (!root) throw new Error('Application root is missing');
ReactDOM.createRoot(root).render(
  <React.StrictMode><QueryClientProvider client={client}><ControlRoom /></QueryClientProvider></React.StrictMode>,
);
