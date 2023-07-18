import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import 'react-toastify/dist/ReactToastify.css'
import * as Sentry from '@sentry/react'

import { OpenAPI } from './client'

import { toastConfig } from './utils/toastConfig'

import App from './app'

if (import.meta.env.MODE !== 'development') {
  // Runs in staging and production
  Sentry.init({
    dsn: 'https://deb7a1791e004fd6887189c03b568e8c@o4505547874172928.ingest.sentry.io/4505547928109056',
    integrations: [
      new Sentry.BrowserTracing(),
      new Sentry.Replay()
    ],

    // Set tracesSampleRate to 1.0 to capture 100%
    // of transactions for performance monitoring.
    tracesSampleRate: 1.0,

    // Set `tracePropagationTargets` to control for which URLs distributed tracing should be enabled
    tracePropagationTargets: [
      /^https:\/\/mallastest\.ing\.uc\.cl\/api/,
      /^https:\/\/plan\.ing\.uc\.cl\/api/,
      /^https:\/\/mallastest\.tail6ca5c\.ts\.net\/api/
    ],

    // Capture Replay for 10% of all sessions,
    // plus for 100% of sessions with an error
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0
  })
}

toastConfig()

const baseUrl = import.meta.env.VITE_BASE_API_URL
if (typeof baseUrl !== 'string') {
  throw new Error('VITE_BASE_API_URL environment variable not set during build')
}
OpenAPI.BASE = baseUrl
OpenAPI.TOKEN = async () => {
  const token = localStorage.getItem('access-token')
  if (token != null) {
    return token
  }
  return ''
}

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
