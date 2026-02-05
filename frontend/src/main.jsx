import React from 'react'
import ReactDOM from 'react-dom/client'
import { ClerkProvider } from '@clerk/clerk-react'
import App from './App.jsx'
import './index.css'

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!PUBLISHABLE_KEY) {
    console.warn('Missing Clerk Publishable Key. Add VITE_CLERK_PUBLISHABLE_KEY to your .env file')
}

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <ClerkProvider
            publishableKey={PUBLISHABLE_KEY}
            appearance={{
                layout: {
                    unsafe_disableDevelopmentModeWarnings: true,
                }
            }}
            signUpOptions={{
                unsafeMetadata: {
                    phoneNumberRequired: true
                }
            }}
        >
            <App />
        </ClerkProvider>
    </React.StrictMode>,
)
