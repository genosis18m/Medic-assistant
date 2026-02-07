import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { UserButton } from '@clerk/clerk-react'

import Loader from '../components/Loader'
import LogoutButton from '../components/LogoutButton'

const API_URL = import.meta.env.DEV ? (import.meta.env.VITE_API_URL || '/api') : (import.meta.env.VITE_API_URL || 'http://localhost:8000')

function DoctorDashboardPage({ doctorId = 5, userEmail }) {
    const navigate = useNavigate()
    const location = useLocation()
    const [selectedDoctor, setSelectedDoctor] = useState(doctorId)
    const [appointments, setAppointments] = useState([])
    const [stats, setStats] = useState({ today: 0, thisWeek: 0, total: 0 })
    const [loading, setLoading] = useState(true)
    const [integrationStatus, setIntegrationStatus] = useState(null)

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
            const response = await fetch(`${API_URL}/appointments?doctor_id=${selectedDoctor}`)
            if (response.ok) {
                const data = await response.json()
                console.log("Fetched appointments for doctor", selectedDoctor, ":", data)
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
        <div className="min-h-screen bg-slate-50">
            {/* Header */}
            <header className="py-4 px-8 shadow-md bg-teal-700">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="bg-white p-1.5 rounded-full shadow-sm">
                            <img src="/logo.svg" alt="App Logo" className="w-10 h-10 object-contain" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-white tracking-wide">
                                Doctor Mode
                            </h1>
                            <p className="text-teal-100 text-sm font-medium">Professional Dashboard</p>
                        </div>
                    </div>

                    {/* Navigation Tabs */}
                    <div className="flex items-center gap-6 ml-8">
                        <div className="radio-inputs bg-teal-800/50 p-1 rounded-lg">
                            <label className="radio">
                                <input
                                    type="radio"
                                    name="radio"
                                    defaultChecked={location.pathname === '/doctor/dashboard' || location.pathname === '/doctor'}
                                    onClick={() => navigate('/doctor/dashboard')}
                                />
                                <span className="name text-teal-100 hover:text-white">Dashboard</span>
                            </label>
                            <label className="radio">
                                <input
                                    type="radio"
                                    name="radio"
                                    defaultChecked={location.pathname === '/doctor/appointments'}
                                    onClick={() => navigate('/doctor/appointments')}
                                />
                                <span className="name text-teal-100 hover:text-white">Appointments</span>
                            </label>
                            <label className="radio">
                                <input
                                    type="radio"
                                    name="radio"
                                    defaultChecked={location.pathname === '/doctor/reports'}
                                    onClick={() => navigate('/doctor/reports')}
                                />
                                <span className="name text-teal-100 hover:text-white">Reports</span>
                            </label>
                        </div>

                        {/* Special AI Assistant Button */}
                        <button
                            className="ai-assistant-btn"
                            onClick={() => navigate('/doctor/chat')}
                        >
                            <span>AI Assistant</span>
                            <div className="star-1">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 784.11 815.53">
                                    <path className="fil0" d="M392.05 0c-20.9,210.08 -184.06,378.41 -392.05,407.78 207.96,29.37 371.12,197.68 392.05,407.74 20.93,-210.06 184.09,-378.37 392.05,-407.74 -207.98,-29.38 -371.16,-197.69 -392.06,-407.78z"></path>
                                </svg>
                            </div>
                            <div className="star-2">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 784.11 815.53">
                                    <path className="fil0" d="M392.05 0c-20.9,210.08 -184.06,378.41 -392.05,407.78 207.96,29.37 371.12,197.68 392.05,407.74 20.93,-210.06 184.09,-378.37 392.05,-407.74 -207.98,-29.38 -371.16,-197.69 -392.06,-407.78z"></path>
                                </svg>
                            </div>
                            <div className="star-3">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 784.11 815.53">
                                    <path className="fil0" d="M392.05 0c-20.9,210.08 -184.06,378.41 -392.05,407.78 207.96,29.37 371.12,197.68 392.05,407.74 20.93,-210.06 184.09,-378.37 392.05,-407.74 -207.98,-29.38 -371.16,-197.69 -392.06,-407.78z"></path>
                                </svg>
                            </div>
                            <div className="star-4">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 784.11 815.53">
                                    <path className="fil0" d="M392.05 0c-20.9,210.08 -184.06,378.41 -392.05,407.78 207.96,29.37 371.12,197.68 392.05,407.74 20.93,-210.06 184.09,-378.37 392.05,-407.74 -207.98,-29.38 -371.16,-197.69 -392.06,-407.78z"></path>
                                </svg>
                            </div>
                            <div className="star-5">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 784.11 815.53">
                                    <path className="fil0" d="M392.05 0c-20.9,210.08 -184.06,378.41 -392.05,407.78 207.96,29.37 371.12,197.68 392.05,407.74 20.93,-210.06 184.09,-378.37 392.05,-407.74 -207.98,-29.38 -371.16,-197.69 -392.06,-407.78z"></path>
                                </svg>
                            </div>
                            <div className="star-6">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 784.11 815.53">
                                    <path className="fil0" d="M392.05 0c-20.9,210.08 -184.06,378.41 -392.05,407.78 207.96,29.37 371.12,197.68 392.05,407.74 20.93,-210.06 184.09,-378.37 392.05,-407.74 -207.98,-29.38 -371.16,-197.69 -392.06,-407.78z"></path>
                                </svg>
                            </div>
                        </button>

                        <div className="flex items-center gap-3 border-l border-teal-500/30 pl-6">
                            <LogoutButton
                                onLogout={() => {
                                    localStorage.removeItem('doctorAuth');
                                    localStorage.removeItem('simpleDoctorAuth');
                                    window.location.href = '/sign-in';
                                }}
                            />
                            <UserButton afterSignOutUrl="/sign-in" />
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-6 py-8">
                {integrationStatus && (!integrationStatus.calendar_enabled || !integrationStatus.slack_enabled || !integrationStatus.telegram_enabled) && (
                    <div className="mb-4 px-4 py-3 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 text-sm">
                        Some reporting integrations (Calendar, Slack, or Telegram) are not fully configured. You can still see
                        local stats and appointments, but external notifications or reports may be skipped.
                    </div>
                )}
                {/* Doctor Selector */}
                <div className="mb-8 bg-white p-4 rounded-xl shadow-sm border border-slate-100 flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-bold text-slate-800">Welcome back, Dr. Adoni</h2>
                        <p className="text-slate-500 text-sm">Here's your schedule for today</p>
                    </div>
                    <div className="flex items-center gap-3">
                        <label className="text-slate-600 font-medium text-sm">Viewing as:</label>
                        <select
                            value={selectedDoctor}
                            onChange={(e) => setSelectedDoctor(Number(e.target.value))}
                            className="px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:ring-2 focus:ring-teal-500 outline-none"
                        >
                            {doctors.map(doc => (
                                <option key={doc.id} value={doc.id}>
                                    {doc.name} - {doc.specialty}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div className="bg-white rounded-xl p-6 shadow-sm border-l-4 border-teal-500 hover:shadow-md transition-shadow">
                        <h3 className="text-slate-500 text-sm font-medium uppercase tracking-wider">Today's Appointments</h3>
                        <div className="flex items-end justify-between mt-2">
                            <p className="text-4xl font-bold text-slate-800">{stats.today}</p>
                            <span className="text-teal-600 bg-teal-50 px-2 py-1 rounded text-xs font-semibold">+0% from yesterday</span>
                        </div>
                    </div>
                    <div className="bg-white rounded-xl p-6 shadow-sm border-l-4 border-blue-500 hover:shadow-md transition-shadow">
                        <h3 className="text-slate-500 text-sm font-medium uppercase tracking-wider">This Week</h3>
                        <div className="flex items-end justify-between mt-2">
                            <p className="text-4xl font-bold text-slate-800">{stats.thisWeek}</p>
                            <span className="text-blue-600 bg-blue-50 px-2 py-1 rounded text-xs font-semibold">Scheduled</span>
                        </div>
                    </div>
                    <div className="bg-white rounded-xl p-6 shadow-sm border-l-4 border-purple-500 hover:shadow-md transition-shadow">
                        <h3 className="text-slate-500 text-sm font-medium uppercase tracking-wider">Total Patients</h3>
                        <div className="flex items-end justify-between mt-2">
                            <p className="text-4xl font-bold text-slate-800">{stats.total}</p>
                            <span className="text-purple-600 bg-purple-50 px-2 py-1 rounded text-xs font-semibold">Lifetime</span>
                        </div>
                    </div>
                </div>

                {/* Appointments List */}
                <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
                    <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                        <h2 className="text-slate-800 text-lg font-bold">Recent Appointments</h2>
                        <button className="text-teal-600 text-sm font-medium hover:text-teal-700">View All</button>
                    </div>

                    <div className="p-0">
                        {loading ? (
                            <div className="flex justify-center py-12">
                                <Loader />
                            </div>
                        ) : appointments.length === 0 ? (
                            <div className="p-12 text-center">
                                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-100 mb-4">
                                    <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                    </svg>
                                </div>
                                <p className="text-slate-500">No appointments found for the selected timeline.</p>
                            </div>
                        ) : (
                            <div className="divide-y divide-slate-100">
                                {appointments.slice(0, 10).map(apt => (
                                    <div key={apt.id} className="p-4 hover:bg-slate-50 transition-colors flex items-center justify-between group">
                                        <div className="flex items-center gap-4">
                                            <div className="w-10 h-10 rounded-full bg-teal-100 flex items-center justify-center text-teal-700 font-bold text-sm">
                                                {apt.patient_name.charAt(0)}
                                            </div>
                                            <div>
                                                <p className="text-slate-800 font-medium group-hover:text-teal-700 transition-colors">{apt.patient_name}</p>
                                                <p className="text-slate-500 text-xs">{apt.patient_email}</p>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-8">
                                            <div className="text-right">
                                                <p className="text-slate-800 font-medium text-sm">{apt.appointment_time}</p>
                                                <p className="text-slate-500 text-xs">{apt.appointment_date}</p>
                                            </div>

                                            <div className="w-24 text-right">
                                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${apt.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                                                    apt.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                                                        'bg-yellow-100 text-yellow-800'
                                                    }`}>
                                                    {apt.status === 'confirmed' && <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-1.5"></span>}
                                                    {apt.status}
                                                </span>
                                            </div>

                                            <div className="w-32 text-right hidden md:block">
                                                <p className="text-slate-600 text-sm truncate max-w-[120px]">{apt.reason}</p>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    )
}

export default DoctorDashboardPage
