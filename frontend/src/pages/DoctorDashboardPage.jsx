import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { UserButton } from '@clerk/clerk-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function DoctorDashboardPage({ doctorId = 5, userEmail }) {
    const navigate = useNavigate()
    const [selectedDoctor, setSelectedDoctor] = useState(doctorId)
    const [appointments, setAppointments] = useState([])
    const [stats, setStats] = useState({ today: 0, thisWeek: 0, total: 0 })
    const [loading, setLoading] = useState(true)

    const doctors = [
        { id: 1, name: 'Dr. Sarah Johnson', specialty: 'General Practice' },
        { id: 2, name: 'Dr. Michael Chen', specialty: 'Cardiology' },
        { id: 3, name: 'Dr. Emily Williams', specialty: 'Dermatology' },
        { id: 4, name: 'Dr. James Brown', specialty: 'Neurology' },
        { id: 5, name: 'Dr. Mohit Adoni', specialty: 'General Practice' }
    ]

    useEffect(() => {
        fetchAppointments()
    }, [selectedDoctor])

    const fetchAppointments = async () => {
        try {
            setLoading(true)
            const response = await fetch(`${API_URL}/appointments?doctor_id=${selectedDoctor}`)
            if (response.ok) {
                const data = await response.json()
                setAppointments(data.appointments || [])
                // Calculate stats
                const today = new Date().toISOString().split('T')[0]
                const todayCount = data.appointments?.filter(apt => apt.appointment_date === today).length || 0
                setStats({
                    today: todayCount,
                    thisWeek: data.appointments?.length || 0,
                    total: data.appointments?.length || 0
                })
            }
        } catch (error) {
            console.error('Failed to fetch appointments:', error)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            {/* Header */}
            <header className="py-4 px-6 shadow-lg bg-gradient-to-r from-purple-600 to-blue-600">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                    d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                            </svg>
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-white">Medical Assistant</h1>
                            <p className="text-purple-100 text-sm">👨‍⚕️ Doctor Dashboard</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => navigate('/doctor/appointments')}
                            className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors flex items-center gap-2"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            Appointments
                        </button>
                        <button
                            onClick={() => navigate('/doctor/reports')}
                            className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors flex items-center gap-2"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                            Reports
                        </button>
                        <button
                            onClick={() => navigate('/doctor/chat')}
                            className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors"
                        >
                            💬 AI Assistant
                        </button>
                        <UserButton afterSignOutUrl="/sign-in" />
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-6 py-8">
                {/* Doctor Selector */}
                <div className="mb-6">
                    <label className="block text-white text-sm font-medium mb-2">Select Doctor</label>
                    <select
                        value={selectedDoctor}
                        onChange={(e) => setSelectedDoctor(Number(e.target.value))}
                        className="px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
                    >
                        {doctors.map(doc => (
                            <option key={doc.id} value={doc.id} className="bg-slate-800">
                                {doc.name} - {doc.specialty}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div className="bg-white/10 border border-white/20 rounded-2xl p-6 backdrop-blur-sm">
                        <h3 className="text-purple-300 text-sm font-medium">Today's Appointments</h3>
                        <p className="text-4xl font-bold text-white mt-2">{stats.today}</p>
                    </div>
                    <div className="bg-white/10 border border-white/20 rounded-2xl p-6 backdrop-blur-sm">
                        <h3 className="text-purple-300 text-sm font-medium">This Week</h3>
                        <p className="text-4xl font-bold text-white mt-2">{stats.thisWeek}</p>
                    </div>
                    <div className="bg-white/10 border border-white/20 rounded-2xl p-6 backdrop-blur-sm">
                        <h3 className="text-purple-300 text-sm font-medium">Total Appointments</h3>
                        <p className="text-4xl font-bold text-white mt-2">{stats.total}</p>
                    </div>
                </div>

                {/* Appointments List */}
                <div className="bg-white/10 border border-white/20 rounded-2xl p-6 backdrop-blur-sm">
                    <h2 className="text-white text-xl font-bold mb-4">Recent Appointments</h2>
                    {loading ? (
                        <p className="text-white/60">Loading appointments...</p>
                    ) : appointments.length === 0 ? (
                        <p className="text-white/60">No appointments found</p>
                    ) : (
                        <div className="space-y-3">
                            {appointments.slice(0, 10).map(apt => (
                                <div key={apt.id} className="bg-white/5 p-4 rounded-lg border border-white/10">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <p className="text-white font-medium">{apt.patient_name}</p>
                                            <p className="text-white/60 text-sm">{apt.patient_email}</p>
                                            <p className="text-purple-300 text-sm mt-1">{apt.reason}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-white font-medium">{apt.appointment_time}</p>
                                            <p className="text-white/60 text-sm">{apt.appointment_date}</p>
                                            <span className={`inline-block mt-1 px-2 py-1 rounded text-xs ${apt.status === 'confirmed' ? 'bg-green-500/20 text-green-300' :
                                                apt.status === 'cancelled' ? 'bg-red-500/20 text-red-300' :
                                                    'bg-yellow-500/20 text-yellow-300'
                                                }`}>
                                                {apt.status}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </main>
        </div>
    )
}

export default DoctorDashboardPage
