import { useUser } from '@clerk/clerk-react'
import { Navigate } from 'react-router-dom'
import Chat from '../components/Chat'
import { UserButton } from '@clerk/clerk-react'

function PatientPage() {
    const { user, isLoaded } = useUser()

    // Loading state
    if (!isLoaded) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
                <div className="text-white text-xl">Loading...</div>
            </div>
        )
    }

    // Not authenticated
    if (!user) {
        return <Navigate to="/sign-in" replace />
    }

    // Authenticated - show patient page
    return (
        <div className="min-h-screen flex bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            {/* Sidebar */}
            <div className="w-80 bg-white/5 border-r border-white/10 p-4">
                <h2 className="text-white text-lg font-bold mb-4">Previous Visits</h2>
                <p className="text-white/60 text-sm">No appointments found</p>
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col">
                {/* Header */}
                <header className="py-4 px-6 shadow-lg bg-gradient-to-r from-teal-600 to-blue-600">
                    <div className="max-w-4xl mx-auto flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
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

                {/* Chat */}
                <main className="flex-1">
                    <Chat role="patient" />
                </main>
            </div>
        </div>
    )
}

export default PatientPage
