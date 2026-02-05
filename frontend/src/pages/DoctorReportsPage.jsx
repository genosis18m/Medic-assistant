import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { UserButton } from '@clerk/clerk-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function DoctorReportsPage({ doctorId = 5 }) {
    const navigate = useNavigate()
    const [selectedDoctor, setSelectedDoctor] = useState(doctorId)
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)

    const doctors = [
        { id: 1, name: 'Dr. Sarah Johnson', specialty: 'General Practice' },
        { id: 2, name: 'Dr. Michael Chen', specialty: 'Cardiology' },
        { id: 3, name: 'Dr. Emily Williams', specialty: 'Dermatology' },
        { id: 4, name: 'Dr. James Brown', specialty: 'Neurology' },
        { id: 5, name: 'Dr. Mohit Adoni', specialty: 'General Practice' }
    ]

    useEffect(() => {
        fetchStats()
    }, [selectedDoctor])

    const fetchStats = async () => {
        try {
            setLoading(true)
            const response = await fetch(`${API_URL}/appointments?doctor_id=${selectedDoctor}`)
            if (response.ok) {
                const data = await response.json()
                const appointments = data.appointments || []

                // Calculate stats
                const today = new Date().toISOString().split('T')[0]
                const thisWeekStart = new Date()
                thisWeekStart.setDate(thisWeekStart.getDate() - thisWeekStart.getDay())
                const weekStart = thisWeekStart.toISOString().split('T')[0]

                const todayCount = appointments.filter(apt => apt.appointment_date === today).length
                const weekCount = appointments.filter(apt => apt.appointment_date >= weekStart).length
                const confirmedCount = appointments.filter(apt => apt.status === 'confirmed').length
                const cancelledCount = appointments.filter(apt => apt.status === 'cancelled').length

                // Common reasons
                const reasonCounts = {}
                appointments.forEach(apt => {
                    const reason = apt.reason || 'Not specified'
                    reasonCounts[reason] = (reasonCounts[reason] || 0) + 1
                })
                const topReasons = Object.entries(reasonCounts)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 5)

                setStats({
                    total: appointments.length,
                    today: todayCount,
                    thisWeek: weekCount,
                    confirmed: confirmedCount,
                    cancelled: cancelledCount,
                    topReasons
                })
            }
        } catch (error) {
            console.error('Failed to fetch stats:', error)
        } finally {
            setLoading(false)
        }
    }

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
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-white">Reports & Analytics</h1>
                            <p className="text-purple-100 text-sm">View practice statistics</p>
                        </div>
                    </div>
                    <UserButton afterSignOutUrl="/sign-in" />
                </div>
            </header>

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

                {loading ? (
                    <p className="text-white/60">Loading statistics...</p>
                ) : stats ? (
                    <>
                        {/* Stats Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                            <div className="bg-white/10 border border-white/20 rounded-2xl p-6 backdrop-blur-sm">
                                <h3 className="text-purple-300 text-sm font-medium mb-2">Total Appointments</h3>
                                <p className="text-5xl font-bold text-white">{stats.total}</p>
                            </div>
                            <div className="bg-white/10 border border-white/20 rounded-2xl p-6 backdrop-blur-sm">
                                <h3 className="text-purple-300 text-sm font-medium mb-2">Today</h3>
                                <p className="text-5xl font-bold text-white">{stats.today}</p>
                            </div>
                            <div className="bg-white/10 border border-white/20 rounded-2xl p-6 backdrop-blur-sm">
                                <h3 className="text-purple-300 text-sm font-medium mb-2">This Week</h3>
                                <p className="text-5xl font-bold text-white">{stats.thisWeek}</p>
                            </div>
                            <div className="bg-white/10 border border-white/20 rounded-2xl p-6 backdrop-blur-sm">
                                <h3 className="text-purple-300 text-sm font-medium mb-2">Confirmed</h3>
                                <p className="text-5xl font-bold text-green-400">{stats.confirmed}</p>
                            </div>
                        </div>

                        {/* Status Breakdown */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            <div className="bg-white/10 border border-white/20 rounded-2xl p-6 backdrop-blur-sm">
                                <h2 className="text-white text-xl font-bold mb-4">Status Breakdown</h2>
                                <div className="space-y-3">
                                    <div className="flex justify-between items-center">
                                        <span className="text-white/80">Confirmed</span>
                                        <span className="text-green-400 font-bold">{stats.confirmed}</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-white/80">Cancelled</span>
                                        <span className="text-red-400 font-bold">{stats.cancelled}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Top Reasons */}
                            <div className="bg-white/10 border border-white/20 rounded-2xl p-6 backdrop-blur-sm">
                                <h2 className="text-white text-xl font-bold mb-4">Top Visit Reasons</h2>
                                {stats.topReasons.length === 0 ? (
                                    <p className="text-white/60">No data available</p>
                                ) : (
                                    <div className="space-y-3">
                                        {stats.topReasons.map(([reason, count], index) => (
                                            <div key={reason} className="flex justify-between items-center">
                                                <div className="flex items-center gap-2">
                                                    <span className="text-purple-400 font-bold">#{index + 1}</span>
                                                    <span className="text-white/80">{reason}</span>
                                                </div>
                                                <span className="text-white font-bold">{count}</span>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    </>
                ) : (
                    <p className="text-white/60">No statistics available</p>
                )}
            </main>
        </div>
    )
}

export default DoctorReportsPage
