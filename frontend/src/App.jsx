import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { SignedIn, SignedOut, useUser, UserButton } from '@clerk/clerk-react'
import Chat from './components/Chat'
import RoleSelector from './components/RoleSelector'
import DoctorDashboard from './components/DoctorDashboard'
import SignInPage from './pages/SignInPage'
import SignUpPage from './pages/SignUpPage'

function MainApp() {
    const { user } = useUser()
    const [role, setRole] = useState(null)
    const [showDashboard, setShowDashboard] = useState(false)

    // Get user role from Clerk metadata
    const userRole = user?.unsafeMetadata?.role || 'patient'

    // Map doctor emails to doctor IDs
    const EMAIL_TO_DOCTOR_ID = {
        'doctor12345@gmail.com': 5,  // Dr. Mohit Adoni
        'adonimohit@gmail.com': 5     // Dr. Mohit Adoni
    }

    const userEmail = user?.primaryEmailAddress?.emailAddress
    const doctorId = EMAIL_TO_DOCTOR_ID[userEmail] || 1

    // Auto-set role from Clerk user metadata
    if (!role && user) {
        setRole(userRole)
    }

    // Show role selector if no role selected
    if (!role) {
        return <RoleSelector onSelectRole={setRole} currentRole={role} userEmail={userEmail} />
    }

    // Show doctor dashboard
    if (role === 'doctor' && showDashboard) {
        return <DoctorDashboard onBack={() => setShowDashboard(false)} userId={user?.id} doctorId={doctorId} />
    }

    return (
        <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            {/* Header */}
            <header className={`py-4 px-6 shadow-lg ${role === 'doctor'
                ? 'bg-gradient-to-r from-purple-600 to-blue-600'
                : 'bg-gradient-to-r from-medical-teal to-medical-blue'}`}>
                <div className="max-w-4xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                            {role === 'doctor' ? (
                                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                </svg>
                            ) : (
                                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                        d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                                </svg>
                            )}
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-white">
                                {role === 'doctor' ? 'Doctor Portal' : 'Medical Assistant'}
                            </h1>
                            <p className="text-white/70 text-sm">
                                {role === 'doctor' ? 'Manage patients & reports' : 'AI-Powered Appointment Booking'}
                            </p>
                        </div>
                    </div>

                    {/* Right side controls */}
                    <div className="flex items-center gap-3">
                        {/* Dashboard toggle for doctors */}
                        {role === 'doctor' && (
                            <button
                                onClick={() => setShowDashboard(true)}
                                className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg 
                                    transition-colors flex items-center gap-2 text-sm"
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                </svg>
                                Dashboard
                            </button>
                        )}

                        {/* Role badge */}
                        <span className={`px-3 py-1 rounded-full text-xs font-medium
                            ${role === 'doctor' ? 'bg-purple-900/50 text-purple-200' : 'bg-teal-900/50 text-teal-200'}`}>
                            {role === 'doctor' ? '👨‍⚕️ Doctor' : '🧑 Patient'}
                        </span>

                        {/* User button (Clerk profile/sign out) */}
                        <UserButton
                            appearance={{
                                elements: {
                                    avatarBox: 'w-10 h-10'
                                }
                            }}
                        />

                        {/* Switch role button */}
                        <button
                            onClick={() => setRole(null)}
                            className="p-2 text-white/70 hover:text-white transition-colors"
                            title="Switch Role"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                    d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                            </svg>
                        </button>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 flex">
                <Chat role={role} userId={user?.id} userEmail={user?.primaryEmailAddress?.emailAddress} />
            </main>

            {/* Footer */}
            <footer className="py-4 text-center text-slate-500 text-sm border-t border-slate-800/50">
                <p>
                    🏥 Medical Assistant • Agentic AI with MCP •
                    <span className="text-slate-400"> Powered by Groq</span>
                </p>
            </footer>
        </div>
    )
}

function App() {
    return (
        <BrowserRouter>
            <Routes>
                {/* Public routes */}
                <Route path="/sign-in/*" element={<SignInPage />} />
                <Route path="/sign-up/*" element={<SignUpPage />} />

                {/* Protected routes */}
                <Route
                    path="/"
                    element={
                        <>
                            <SignedIn>
                                <MainApp />
                            </SignedIn>
                            <SignedOut>
                                <Navigate to="/sign-in" replace />
                            </SignedOut>
                        </>
                    }
                />
            </Routes>
        </BrowserRouter>
    )
}

export default App
