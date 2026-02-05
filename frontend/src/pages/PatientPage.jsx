import { useUser, UserButton } from '@clerk/clerk-react'
import { Navigate } from 'react-router-dom'

function PatientPage() {
    const { user, isLoaded } = useUser()

    // Loading
    if (!isLoaded) {
        return (
            <div className="min-h-screen bg-slate-900 flex items-center justify-center">
                <div className="text-white text-2xl">Loading...</div>
            </div>
        )
    }

    // Not logged in
    if (!user) {
        return <Navigate to="/sign-in" replace />
    }

    // SUCCESS! Show patient page
    return (
        <div className="min-h-screen bg-slate-900 text-white">
            <div className="p-8">
                <div className="max-w-4xl mx-auto">
                    <div className="bg-slate-800 p-6 rounded-lg">
                        <div className="flex justify-between items-center mb-6">
                            <h1 className="text-3xl font-bold">✅ Patient Page Works!</h1>
                            <UserButton afterSignOutUrl="/sign-in" />
                        </div>

                        <div className="bg-green-900/20 border border-green-500 text-green-300 p-4 rounded mb-4">
                            🎉 SUCCESS! You're logged in as: {user.primaryEmailAddress?.emailAddress}
                        </div>

                        <div className="space-y-4">
                            <h2 className="text-xl font-semibold">Welcome to Medical Assistant</h2>
                            <p>This is your patient dashboard. The chat will be added back once we confirm this works.</p>

                            <div className="bg-slate-700 p-4 rounded">
                                <h3 className="font-bold mb-2">Quick Actions:</h3>
                                <ul className="list-disc list-inside space-y-1">
                                    <li>Book an appointment</li>
                                    <li>View medical history</li>
                                    <li>Chat with AI assistant</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default PatientPage
