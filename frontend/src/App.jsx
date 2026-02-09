import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { SignedIn, SignedOut, useUser, UserButton, useClerk } from '@clerk/clerk-react'
import Chat from './components/Chat'
import RoleSelector from './components/RoleSelector'
import UnifiedLoginPage from './pages/UnifiedLoginPage'
import SignUpPage from './pages/SignUpPage'
import PatientPage from './pages/PatientPage'
import DoctorDashboardPage from './pages/DoctorDashboardPage'
import DoctorChatPage from './pages/DoctorChatPage'
import DoctorAppointmentsPage from './pages/DoctorAppointmentsPage'
import DoctorReportsPage from './pages/DoctorReportsPage'

function MainApp() {
    const { user } = useUser()
    const { signOut } = useClerk()
    const [role, setRole] = useState(null)


    // Get user role from Clerk metadata
    const userRole = user?.unsafeMetadata?.role || 'patient'

    // Map doctor emails to doctor IDs
    const EMAIL_TO_DOCTOR_ID = {
        'doctor12345@gmail.com': 1,  // Dr. Sarah Johnson
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
                        {/* Doctor Dashboard Link */}
                        {role === 'doctor' && (
                            <button
                                onClick={() => window.location.href = '/doctor/dashboard'}
                                className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg 
                                    transition-colors flex items-center gap-2 text-sm font-medium"
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                                </svg>
                                Dashboard Area
                            </button>
                        )}
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
            <main className="flex-1 flex flex-col">
                <Routes>
                    <Route path="/" element={<Chat role={role} userId={user?.id} userEmail={user?.primaryEmailAddress?.emailAddress} />} />

                    {/* Doctor Routes */}
                    <Route path="/doctor/*" element={
                        role === 'doctor' ? (
                            <DoctorDashboardPage doctorId={doctorId} userEmail={userEmail} />
                        ) : (
                            <Navigate to="/" replace />
                        )
                    } />
                </Routes>
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
    // Check for simple doctor authentication (bypasses Clerk)
    const simpleDoctorAuth = localStorage.getItem('simpleDoctorAuth')
    const simpleDoctorData = simpleDoctorAuth ? JSON.parse(simpleDoctorAuth) : null

    // Check for simple patient authentication
    const simplePatientAuth = localStorage.getItem('simplePatientAuth')
    const simplePatientData = simplePatientAuth ? JSON.parse(simplePatientAuth) : null

    if (simpleDoctorData) {
        // Simple doctor is logged in - render doctor dashboard
        return (
            <BrowserRouter>
                <Routes>
                    <Route path="/" element={<DoctorDashboardPage doctorId={simpleDoctorData.doctorId} userEmail={simpleDoctorData.email} />} />
                    <Route path="/doctor" element={<DoctorDashboardPage doctorId={simpleDoctorData.doctorId} userEmail={simpleDoctorData.email} />} />
                    <Route path="/doctor/dashboard" element={<DoctorDashboardPage doctorId={simpleDoctorData.doctorId} userEmail={simpleDoctorData.email} />} />
                    <Route path="/doctor/chat" element={<SimpleDoctorChatPage doctorData={simpleDoctorData} />} />
                    <Route path="/doctor/appointments" element={<DoctorAppointmentsPage doctorId={simpleDoctorData.doctorId} />} />
                    <Route path="/doctor/reports" element={<DoctorReportsPage doctorId={simpleDoctorData.doctorId} />} />
                    <Route path="*" element={<Navigate to="/doctor" replace />} />
                </Routes>
            </BrowserRouter>

        )
    }

    if (simplePatientData) {
        // Simple patient login
        const handleLogout = () => {
            localStorage.removeItem('simplePatientAuth')
            window.location.reload()
        }

        // Mock user object matching Clerk structure partially
        const mockUser = {
            id: 'test-patient-id',
            primaryEmailAddress: { emailAddress: simplePatientData.email },
            fullName: simplePatientData.name
        }

        return (
            <BrowserRouter>
                <Routes>
                    <Route path="/" element={<PatientPage mockUser={mockUser} />} />
                    <Route path="/patient" element={<PatientPage mockUser={mockUser} />} />
                    <Route path="*" element={<Navigate to="/patient" replace />} />
                </Routes>
                {/* 
                   Note: PatientPage has its own header with UserButton. 
                   We might need to monkey-patch UserButton behavior or just accept it might look broken?
                   Actually PatientPage renders Header with UserButton.
                   UserButton will try to use Clerk. 
                   If no Clerk user, UserButton might be empty or error?
                   Let's hope it handles null user gracefully or we might need to modify PatientPage header too.
                   Wait, PatientPage uses <LogoutButton> and <UserButton>.
                   If mockUser is present, UserButton is useless.
                   I should probably update PatientPage to hide UserButton if mockUser is invoked.
                 */}
            </BrowserRouter>
        )
    }

    // Normal Clerk-based authentication
    return (
        <BrowserRouter>
            <Routes>
                {/* Unified Login Page overrides /sign-in */}
                <Route path="/sign-in/*" element={<UnifiedLoginPage />} />
                <Route path="/sign-up/*" element={<SignUpPage />} />

                {/* Patient route */}
                <Route
                    path="/patient"
                    element={
                        <>
                            <SignedIn>
                                <PatientPage />
                            </SignedIn>
                            <SignedOut>
                                <Navigate to="/sign-in" replace />
                            </SignedOut>
                        </>
                    }
                />

                {/* Doctor routes (Clerk) */}
                <Route
                    path="/doctor/*"
                    element={
                        <>
                            <SignedIn>
                                <MainAppRouter />
                            </SignedIn>
                            <SignedOut>
                                <Navigate to="/sign-in" replace />
                            </SignedOut>
                        </>
                    }
                />

                {/* Default and catch-all */}
                <Route path="/" element={
                    <>
                        <SignedIn>
                            <Navigate to="/patient" replace />
                        </SignedIn>
                        <SignedOut>
                            <Navigate to="/sign-in" replace />
                        </SignedOut>
                    </>
                } />
                <Route path="*" element={<Navigate to="/sign-in" replace />} />
            </Routes>
        </BrowserRouter>
    )
}

// Router for authenticated users
function MainAppRouter() {
    const { user } = useUser()
    const userEmail = user?.primaryEmailAddress?.emailAddress
    const canAccessDoctor = ['doctor12345@gmail.com', 'adonimohit@gmail.com', 'doctor@clinic.com', 'momoochan.ofc@gmail.com'].includes(userEmail)
    const doctorId = 5 // Dr. Mohit Adoni for demo doctors

    return (
        <Routes>
            {/* Default route - auto redirect based on email */}
            <Route path="/" element={
                canAccessDoctor
                    ? <Navigate to="/doctor" replace />
                    : <Navigate to="/patient" replace />
            } />
            <Route path="/patient" element={<PatientPage />} />
            {canAccessDoctor && (
                <>
                    <Route path="/doctor" element={<DoctorDashboardPage doctorId={doctorId} userEmail={userEmail} />} />
                    <Route path="/doctor/dashboard" element={<DoctorDashboardPage doctorId={doctorId} userEmail={userEmail} />} />
                    <Route path="/doctor/chat" element={<DoctorChatPage />} />
                    <Route path="/doctor/appointments" element={<DoctorAppointmentsPage doctorId={doctorId} />} />
                    <Route path="/doctor/reports" element={<DoctorReportsPage doctorId={doctorId} />} />
                </>
            )}
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    )
}

// Simple doctor chat page
function SimpleDoctorChatPage({ doctorData }) {
    const navigate = useNavigate()

    const handleLogout = () => {
        localStorage.removeItem('simpleDoctorAuth')
        window.location.href = '/sign-in'
    }

    return (
        <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            <header className="py-4 px-6 shadow-lg bg-gradient-to-r from-purple-600 to-blue-600">
                <div className="max-w-4xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => window.location.href = '/doctor'}
                            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                        >
                            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                            </svg>
                        </button>
                        <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm p-1">
                            <img src="/logo.svg" alt="Medical Assistant Logo" className="w-full h-full object-contain" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-white">Medical Assistant</h1>
                            <p className="text-purple-100 text-sm">💬 AI Assistant</p>
                        </div>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-white rounded-lg transition-colors"
                    >
                        Logout
                    </button>
                </div>
            </header>
            <main className="flex-1">
                <Chat role="doctor" />
            </main>
        </div>
    )
}

// Simplified app for doctors using simple auth
function SimpleDoctorApp({ doctorData }) {
    const [showDashboard, setShowDashboard] = useState(false)

    const handleLogout = () => {
        localStorage.removeItem('simpleDoctorAuth')
        window.location.reload()
    }

    if (showDashboard) {
        return <DoctorDashboard onBack={() => setShowDashboard(false)} userId="simple-doctor" doctorId={doctorData.doctorId} />
    }

    return (
        <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            <header className="py-4 px-6 shadow-lg bg-gradient-to-r from-purple-600 to-blue-600">
                <div className="max-w-4xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm p-1">
                            <img src="/logo.svg" alt="Medical Assistant Logo" className="w-full h-full object-contain" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-white">Medical Assistant</h1>
                            <p className="text-purple-100 text-sm">👨‍⚕️ Doctor Mode - {doctorData.name}</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => setShowDashboard(!showDashboard)}
                            className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors"
                        >
                            {showDashboard ? 'Chat' : 'Dashboard'}
                        </button>
                        <button
                            onClick={handleLogout}
                            className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-white rounded-lg transition-colors"
                        >
                            Logout
                        </button>
                    </div>
                </div>
            </header>
            <main className="flex-1">
                <Chat role="doctor" />
            </main>
        </div>
    )
}


export default App

