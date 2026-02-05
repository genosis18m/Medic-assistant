import { useUser, UserButton } from '@clerk/clerk-react'
import { Navigate } from 'react-router-dom'

function PatientPage() {
    const { user, isLoaded } = useUser()

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

    // SUCCESS! Show patient page WITHOUT Chat for now
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
                <p className="text-white/60 text-sm">No appointments yet</p>
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

                {/* Temporary Chat Placeholder - Chat component has bugs */}
                <main className="flex-1 p-8">
                    <div className="max-w-3xl mx-auto">
                        <div className="bg-yellow-900/20 border border-yellow-500 text-yellow-300 p-6 rounded-lg mb-6">
                            <h3 className="text-xl font-bold mb-2">⚠️ Chat Temporarily Disabled</h3>
                            <p>The Chat component is being fixed. For now, you can book appointments using the doctor dashboard.</p>
                        </div>

                        <div className="bg-white/10 p-6 rounded-lg">
                            <h2 className="text-2xl font-bold text-white mb-4">Welcome, {user.firstName || 'Patient'}!</h2>
                            <p className="text-white/80 mb-4">
                                You're logged in as: <span className="text-teal-300">{user.primaryEmailAddress?.emailAddress}</span>
                            </p>

                            <div className="space-y-4 mt-6">
                                <h3 className="text-xl font-semibold text-white">Quick Actions:</h3>
                                <div className="grid gap-4">
                                    <div className="bg-white/5 p-4 rounded-lg border border-white/10 hover:bg-white/10 transition cursor-pointer">
                                        <div className="flex items-center gap-3">
                                            <div className="w-12 h-12 bg-teal-500/20 rounded-lg flex items-center justify-center">
                                                <svg className="w-6 h-6 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                                </svg>
                                            </div>
                                            <div>
                                                <h4 className="font-semibold text-white">Book Appointment</h4>
                                                <p className="text-sm text-white/60">Schedule with our AI doctor</p>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="bg-white/5 p-4 rounded-lg border border-white/10 hover:bg-white/10 transition cursor-pointer">
                                        <div className="flex items-center gap-3">
                                            <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                                                <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                                </svg>
                                            </div>
                                            <div>
                                                <h4 className="font-semibold text-white">View Medical History</h4>
                                                <p className="text-sm text-white/60">Access your health records</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    )
}

export default PatientPage
