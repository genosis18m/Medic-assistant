import { useUser, UserButton } from '@clerk/clerk-react'
import { Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Chat from '../components/Chat'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function PatientPage() {
    const { user, isLoaded } = useUser()
    const [appointments, setAppointments] = useState([])
    const [loading, setLoading] = useState(false)

    // Fetch appointments
    useEffect(() => {
        if (user?.primaryEmailAddress?.emailAddress) {
            fetchAppointments()
        }
    }, [user])

    const fetchAppointments = async () => {
        try {
            setLoading(true)
            const email = user?.primaryEmailAddress?.emailAddress
            const response = await fetch(`${API_URL}/appointments?patient_email=${email}`)
            if (response.ok) {
                const data = await response.json()
                setAppointments(data.appointments || [])
            }
        } catch (error) {
            console.error('Failed to fetch appointments:', error)
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
        <div className="min-h-screen flex bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            {/* Sidebar - Previous Visits */}
            <div className="w-80 bg-white/5 border-r border-white/10 p-4 overflow-y-auto">
                <h2 className="text-white text-lg font-bold mb-4 flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Previous Visits
                </h2>
                {loading ? (
                    <p className="text-white/60 text-sm">Loading...</p>
                ) : appointments.length === 0 ? (
                    <p className="text-white/60 text-sm">No appointments yet</p>
                ) : (
                    <div className="space-y-2">
                        {appointments.map((apt) => (
                            <div
                                key={apt.id}
                                className="bg-white/5 p-3 rounded-lg border border-white/10 hover:bg-white/10 transition-colors cursor-pointer"
                            >
                                <p className="text-white font-medium text-sm">{apt.doctor_name || `Doctor ID ${apt.doctor_id}`}</p>
                                <p className="text-teal-300 text-xs">{apt.appointment_date} at {apt.appointment_time}</p>
                                <p className="text-white/60 text-xs mt-1">{apt.reason}</p>
                                <span className={`inline-block mt-1 px-2 py-0.5 rounded text-xs ${apt.status === 'confirmed' ? 'bg-green-500/20 text-green-300' :
                                        apt.status === 'cancelled' ? 'bg-red-500/20 text-red-300' :
                                            'bg-yellow-500/20 text-yellow-300'
                                    }`}>
                                    {apt.status}
                                </span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col">
                {/* Header */}
                <header className="py-4 px-6 shadow-lg bg-gradient-to-r from-teal-600 to-blue-600">
                    <div className="max-w-4xl mx-auto flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                        d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                                </svg>
                            </div>
                            <div>
                                <h1 className="text-xl font-bold text-white">Medical Assistant</h1>
                                <p className="text-teal-100 text-sm">🧑 Patient Mode</p>
                            </div>
                        </div>
                        <UserButton afterSignOutUrl="/sign-in" />
                    </div>
                </header>

                {/* Chat Component with proper props */}
                <main className="flex-1">
                    <Chat role="patient" userId={userId} userEmail={userEmail} />
                </main>
            </div>
        </div>
    )
}

export default PatientPage
