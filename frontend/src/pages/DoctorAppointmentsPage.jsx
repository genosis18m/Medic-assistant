import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { UserButton } from '@clerk/clerk-react'

const API_URL = import.meta.env.DEV ? (import.meta.env.VITE_API_URL || '/api') : (import.meta.env.VITE_API_URL || 'http://localhost:8000')

function DoctorAppointmentsPage({ doctorId = 5 }) {
    const navigate = useNavigate()
    const [selectedDoctor, setSelectedDoctor] = useState(doctorId)
    const [appointments, setAppointments] = useState([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState('all') // all, today, upcoming, past

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
            }
        } catch (error) {
            console.error('Failed to fetch appointments:', error)
        } finally {
            setLoading(false)
        }
    }

    const filterAppointments = () => {
        const today = new Date().toISOString().split('T')[0]

        if (filter === 'all') return appointments
        if (filter === 'today') return appointments.filter(apt => apt.appointment_date === today)
        if (filter === 'upcoming') return appointments.filter(apt => apt.appointment_date >= today && apt.status === 'confirmed')
        if (filter === 'past') return appointments.filter(apt => apt.appointment_date < today)

        return appointments
    }

    const filteredAppointments = filterAppointments()

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            <header className="py-4 px-6 shadow-lg bg-gradient-to-r from-purple-600 to-blue-600">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => navigate('/doctor')}
                            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                        >
                            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                            </svg>
                        </button>
                        <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-white">Appointments</h1>
                            <p className="text-purple-100 text-sm">Manage patient appointments</p>
                        </div>
                    </div>
                    <UserButton afterSignOutUrl="/sign-in" />
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-6 py-8">
                {/* Filters and Doctor Selector */}
                <div className="flex gap-4 mb-6">
                    <div className="flex-1">
                        <label className="block text-white text-sm font-medium mb-2">Select Doctor</label>
                        <select
                            value={selectedDoctor}
                            onChange={(e) => setSelectedDoctor(Number(e.target.value))}
                            className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
                        >
                            {doctors.map(doc => (
                                <option key={doc.id} value={doc.id} className="bg-slate-800">
                                    {doc.name} - {doc.specialty}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div className="flex-1">
                        <label className="block text-white text-sm font-medium mb-2">Filter</label>
                        <div className="flex gap-2">
                            {['all', 'today', 'upcoming', 'past'].map(f => (
                                <button
                                    key={f}
                                    onClick={() => setFilter(f)}
                                    className={`px-4 py-2 rounded-lg capitalize transition-colors ${filter === f
                                            ? 'bg-purple-600 text-white'
                                            : 'bg-white/10 text-white/70 hover:bg-white/20'
                                        }`}
                                >
                                    {f}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Appointments List */}
                <div className="bg-white/10 border border-white/20 rounded-2xl p-6 backdrop-blur-sm">
                    <h2 className="text-white text-xl font-bold mb-4">
                        {filteredAppointments.length} Appointment{filteredAppointments.length !== 1 ? 's' : ''}
                    </h2>
                    {loading ? (
                        <p className="text-white/60">Loading appointments...</p>
                    ) : filteredAppointments.length === 0 ? (
                        <p className="text-white/60">No appointments found</p>
                    ) : (
                        <div className="space-y-3">
                            {filteredAppointments.map(apt => (
                                <div key={apt.id} className="bg-white/5 p-4 rounded-lg border border-white/10 hover:bg-white/10 transition-colors">
                                    <div className="flex justify-between items-start">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-3 mb-2">
                                                <h3 className="text-white font-bold text-lg">{apt.patient_name}</h3>
                                                <span className={`px-2 py-1 rounded text-xs ${apt.status === 'confirmed' ? 'bg-green-500/20 text-green-300' :
                                                        apt.status === 'cancelled' ? 'bg-red-500/20 text-red-300' :
                                                            'bg-yellow-500/20 text-yellow-300'
                                                    }`}>
                                                    {apt.status}
                                                </span>
                                            </div>
                                            <p className="text-white/60 text-sm mb-1">📧 {apt.patient_email}</p>
                                            <p className="text-purple-300 text-sm">📋 {apt.reason}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-white font-bold text-lg">{apt.appointment_time}</p>
                                            <p className="text-white/60 text-sm">{apt.appointment_date}</p>
                                            <p className="text-purple-300 text-xs mt-1">ID: {apt.id}</p>
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

export default DoctorAppointmentsPage
