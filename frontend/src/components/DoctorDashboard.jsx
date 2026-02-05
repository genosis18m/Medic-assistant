import { useState, useEffect } from 'react'

const API_URL = 'http://localhost:8000'

function DoctorDashboard({ onBack }) {
    const [stats, setStats] = useState(null)
    const [doctors, setDoctors] = useState([])
    const [selectedDoctor, setSelectedDoctor] = useState(1)
    const [isLoading, setIsLoading] = useState(false)
    const [reportResult, setReportResult] = useState(null)

    // Fetch doctors on mount
    useEffect(() => {
        fetchDoctors()
        fetchStats()
    }, [])

    const fetchDoctors = async () => {
        try {
            const response = await fetch(`${API_URL}/doctors`)
            const data = await response.json()
            setDoctors(data.doctors || [])
        } catch (error) {
            console.error('Failed to fetch doctors:', error)
        }
    }

    const fetchStats = async () => {
        try {
            const response = await fetch(`${API_URL}/stats?doctor_id=${selectedDoctor}`)
            const data = await response.json()
            setStats(data)
        } catch (error) {
            console.error('Failed to fetch stats:', error)
        }
    }

    const generateReport = async (sendSlack = false) => {
        setIsLoading(true)
        setReportResult(null)

        try {
            const response = await fetch(`${API_URL}/doctor/report`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    doctor_id: selectedDoctor,
                    report_type: 'daily',
                    send_slack: sendSlack
                })
            })

            const data = await response.json()
            setReportResult(data)
        } catch (error) {
            setReportResult({ error: 'Failed to generate report' })
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-white mb-1">Doctor Dashboard</h1>
                        <p className="text-slate-400">View stats, generate reports, and manage notifications</p>
                    </div>
                    <button
                        onClick={onBack}
                        className="px-4 py-2 text-slate-300 hover:text-white transition-colors flex items-center gap-2"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                        </svg>
                        Back to Chat
                    </button>
                </div>

                {/* Doctor Selector */}
                <div className="bg-slate-800/50 rounded-xl p-4 mb-6 border border-slate-700/50">
                    <label className="block text-slate-400 text-sm mb-2">Select Doctor</label>
                    <select
                        value={selectedDoctor}
                        onChange={(e) => {
                            setSelectedDoctor(Number(e.target.value))
                            setTimeout(fetchStats, 100)
                        }}
                        className="w-full md:w-64 px-4 py-2 bg-slate-700 text-white rounded-lg border border-slate-600 focus:outline-none focus:border-purple-500"
                    >
                        {doctors.map((doc) => (
                            <option key={doc.id} value={doc.id}>
                                {doc.name} - {doc.specialization}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    <div className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-xl p-6 shadow-lg">
                        <div className="text-purple-200 text-sm mb-1">Total Today</div>
                        <div className="text-3xl font-bold text-white">{stats?.stats?.total || 0}</div>
                    </div>
                    <div className="bg-gradient-to-br from-green-600 to-green-800 rounded-xl p-6 shadow-lg">
                        <div className="text-green-200 text-sm mb-1">Completed</div>
                        <div className="text-3xl font-bold text-white">{stats?.stats?.completed || 0}</div>
                    </div>
                    <div className="bg-gradient-to-br from-yellow-600 to-yellow-800 rounded-xl p-6 shadow-lg">
                        <div className="text-yellow-200 text-sm mb-1">Pending</div>
                        <div className="text-3xl font-bold text-white">{(stats?.stats?.pending || 0) + (stats?.stats?.confirmed || 0)}</div>
                    </div>
                    <div className="bg-gradient-to-br from-red-600 to-red-800 rounded-xl p-6 shadow-lg">
                        <div className="text-red-200 text-sm mb-1">Cancelled</div>
                        <div className="text-3xl font-bold text-white">{stats?.stats?.cancelled || 0}</div>
                    </div>
                </div>

                {/* Action Buttons */}
                <div className="grid md:grid-cols-2 gap-6 mb-8">
                    <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
                        <h2 className="text-xl font-semibold text-white mb-4">Generate Report</h2>
                        <p className="text-slate-400 text-sm mb-4">
                            Create a summary of your appointments for today.
                        </p>
                        <div className="flex gap-3">
                            <button
                                onClick={() => generateReport(false)}
                                disabled={isLoading}
                                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors disabled:opacity-50"
                            >
                                {isLoading ? 'Generating...' : 'View Report'}
                            </button>
                            <button
                                onClick={() => generateReport(true)}
                                disabled={isLoading}
                                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
                            >
                                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zM17.688 8.834a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zM15.165 17.688a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z" />
                                </svg>
                                Send to Slack
                            </button>
                        </div>
                    </div>

                    <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
                        <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
                        <div className="space-y-2">
                            <a
                                href={`${API_URL}/appointments?doctor_id=${selectedDoctor}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors text-center"
                            >
                                View All Appointments (JSON)
                            </a>
                            <button
                                onClick={() => window.location.reload()}
                                className="w-full px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
                            >
                                Refresh Stats
                            </button>
                        </div>
                    </div>
                </div>

                {/* Report Result */}
                {reportResult && (
                    <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-xl font-semibold text-white">Generated Report</h2>
                            {reportResult.notification_sent && (
                                <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">
                                    ✓ Sent to Slack
                                </span>
                            )}
                        </div>
                        {reportResult.error ? (
                            <p className="text-red-400">{reportResult.error}</p>
                        ) : (
                            <pre className="bg-slate-900 p-4 rounded-lg text-slate-300 text-sm overflow-x-auto whitespace-pre-wrap font-mono">
                                {reportResult.summary}
                            </pre>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}

export default DoctorDashboard
