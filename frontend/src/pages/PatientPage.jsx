import { useUser, UserButton, useClerk } from '@clerk/clerk-react'
import LogoutButton from '../components/LogoutButton'
import { Navigate } from 'react-router-dom'
import { useState, useEffect, useRef } from 'react'
import Chat from '../components/Chat'

const API_URL = import.meta.env.DEV ? (import.meta.env.VITE_API_URL || '/api') : (import.meta.env.VITE_API_URL || 'http://localhost:8000')

function PatientPage() {
    const { user, isLoaded } = useUser()
    const { signOut } = useClerk()
    const [appointments, setAppointments] = useState([])
    const [loading, setLoading] = useState(false)
    const [integrationStatus, setIntegrationStatus] = useState(null)
    const chatRef = useRef(null)

    // ... (useEffect hooks remain same)
    // Fetch appointments
    useEffect(() => {
        if (user?.primaryEmailAddress?.emailAddress) {
            fetchAppointments()
        }
    }, [user])

    useEffect(() => {
        const fetchIntegrations = async () => {
            try {
                const res = await fetch(`${API_URL}/integrations/status`)
                if (res.ok) {
                    const data = await res.json()
                    setIntegrationStatus(data)
                }
            } catch (e) {
            }
        }
        fetchIntegrations()
    }, [])

    const fetchAppointments = async () => {
        try {
            setLoading(true)
            const email = user?.primaryEmailAddress?.emailAddress
            if (!email) {
                setAppointments([])
                return
            }
            const response = await fetch(`${API_URL}/appointments?patient_email=${encodeURIComponent(email)}`)
            const data = await response.json().catch(() => ({}))
            const list = data?.appointments
            setAppointments(Array.isArray(list) ? list : [])
        } catch (error) {
            console.error('Failed to fetch appointments:', error)
            setAppointments([])
        } finally {
            setLoading(false)
        }
    }

    // Loading
    if (!isLoaded) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
                <div className="text-white text-xl">Loading...</div>
            </div>
        )
    }

    // Not logged in
    if (!user) {
        return <Navigate to="/sign-in" replace />
    }

    // Get user data for Chat component
    const userId = user.id
    const userEmail = user.primaryEmailAddress?.emailAddress

    return (
        <div className="h-screen flex bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 overflow-hidden">
            {/* Sidebar - 25% width, independently scrollable */}
            <div className="w-1/4 min-w-[280px] max-w-[350px] bg-white/5 border-r border-white/10 flex flex-col">
                <div className="p-4 border-b border-white/10 flex-shrink-0">
                    <h2 className="text-white text-lg font-bold flex items-center gap-2">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Previous Visits
                    </h2>
                </div>
                <div className="flex-1 overflow-y-auto p-4">
                    {loading ? (
                        <p className="text-white/60 text-sm">Loading...</p>
                    ) : appointments.length === 0 ? (
                        <p className="text-white/60 text-sm">No appointments yet</p>
                    ) : (
                        <div className="space-y-2">
                            {appointments.map((apt, idx) => (
                                <div
                                    key={apt?.id ?? `apt-${idx}`}
                                    className="bg-white/5 p-3 rounded-lg border border-white/10 hover:bg-white/10 transition-colors cursor-pointer"
                                >
                                    <p className="text-white font-medium text-sm">{apt?.doctor_name || (apt?.doctor_id != null ? `Doctor ID ${apt.doctor_id}` : 'Appointment')}</p>
                                    <p className="text-teal-300 text-xs">{(apt?.appointment_date ?? '')} {(apt?.appointment_time) ? `at ${apt.appointment_time}` : ''}</p>
                                    <p className="text-white/60 text-xs mt-1">{apt?.reason ?? '—'}</p>
                                    <span className={`inline-block mt-1 px-2 py-0.5 rounded text-xs ${apt?.status === 'confirmed' ? 'bg-green-500/20 text-green-300' :
                                        apt?.status === 'cancelled' ? 'bg-red-500/20 text-red-300' :
                                            'bg-yellow-500/20 text-yellow-300'
                                        }`}>
                                        {apt?.status ?? 'scheduled'}
                                    </span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Main Chat Area - 75% width, fits entire screen height */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Header - Fixed height */}
                <header className="py-4 px-6 shadow-lg bg-gradient-to-r from-teal-600 to-blue-600 flex-shrink-0">
                    <div className="max-w-5xl mx-auto flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            {/* Logout moved to right. Logo and Title stay left */}
                            <img src="/logo.svg" alt="App Logo" className="w-10 h-10 object-contain drop-shadow-md" />
                            <div>
                                <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-teal-200 drop-shadow-[0_0_10px_rgba(255,255,255,0.5)] tracking-wide">
                                    Patient Mode
                                </h1>
                            </div>
                        </div>
                        <div className="flex items-center gap-4">
                            <LogoutButton onLogout={() => signOut()} />
                            <div className="transform scale-125 origin-right">
                                <UserButton afterSignOutUrl="/sign-in" />
                            </div>
                        </div>
                    </div>
                </header>

                {integrationStatus && (!integrationStatus.calendar_enabled || !integrationStatus.email_enabled) && (
                    <div className="px-6 py-3 bg-amber-500/10 border-b border-amber-400/40 text-amber-100 text-sm">
                        Email or calendar is not fully configured here. When enabled, booking will send you a confirmation email and a calendar invite.
                    </div>
                )}
                {integrationStatus && integrationStatus.calendar_enabled && integrationStatus.email_enabled && (
                    <div className="px-6 py-2 border-b border-white/10 text-emerald-200/90 text-sm flex items-center justify-between">
                        <span>When you book an appointment, you’ll receive a confirmation email and a calendar invite.</span>
                        <button
                            onClick={() => chatRef.current?.clearChat()}
                            className="text-xs bg-white/10 hover:bg-white/20 text-white px-3 py-1 rounded transition-colors"
                        >
                            Clear Chat
                        </button>
                    </div>
                )}

                {/* Chat Component - Takes remaining height, scrolls independently */}
                <div className="flex-1 min-h-0">
                    <Chat ref={chatRef} role="patient" userId={userId} userEmail={userEmail} />
                </div>
            </div>
        </div>
    )
}

export default PatientPage
