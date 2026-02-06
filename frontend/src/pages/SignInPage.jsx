import { useState } from 'react'
import { SignIn, SignedIn, SignedOut, useClerk } from '@clerk/clerk-react'
import { useNavigate } from 'react-router-dom'
import SimpleDoctorLogin from '../components/SimpleDoctorLogin'

function SignInPage() {
    const [isDoctorMode, setIsDoctorMode] = useState(false)
    const navigate = useNavigate()
    const { signOut } = useClerk()

    const handleDoctorLoginSuccess = (doctorData) => {
        // Store doctor data in localStorage for the app to use
        localStorage.setItem('simpleDoctorAuth', JSON.stringify(doctorData))
        // Redirect to main app
        navigate('/')
        window.location.reload() // Force reload to pick up auth
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-emerald-900 via-green-800 to-teal-900 flex items-center justify-center p-6">
            <div className="max-w-md w-full">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="flex items-center justify-center gap-3 mb-4">
                        <img src="/logo.svg" alt="Medical Assistant" className="w-16 h-16" />
                    </div>
                    <h1 className="text-4xl font-bold text-white mb-2">Medical Assistant</h1>
                    <p className="text-emerald-100/80 text-lg">AI-Powered Healthcare Platform</p>
                </div>

                {/* Check if already signed in */}
                <SignedIn>
                    <div className="bg-white/10 border border-white/20 rounded-xl p-6 backdrop-blur-sm text-center">
                        <p className="text-white mb-4">You're already signed in!</p>
                        <div className="flex gap-3">
                            <button
                                onClick={() => navigate('/patient')}
                                className="flex-1 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-colors"
                            >
                                Continue to App
                            </button>
                            <button
                                onClick={() => signOut()}
                                className="flex-1 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-200 border border-red-400/30 rounded-lg transition-colors"
                            >
                                Sign Out
                            </button>
                        </div>
                    </div>
                </SignedIn>

                {/* Show login forms only when signed out */}
                <SignedOut>
                    {/* Custom Toggle Switch */}
                    <div className="flex justify-center mb-8">
                        <div className="customCheckBoxHolder">
                            <input
                                type="checkbox"
                                id="roleSwitch"
                                className="customCheckBoxInput"
                                checked={isDoctorMode}
                                onChange={(e) => setIsDoctorMode(e.target.checked)}
                            />
                            <div className="customCheckBoxWrapper flex">
                                <div className="customCheckBox" onClick={() => setIsDoctorMode(false)}>
                                    <div className="inner">Patient Login</div>
                                </div>
                                <div className="customCheckBox" onClick={() => setIsDoctorMode(true)}>
                                    <div className="inner">Doctor Login</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Show either Clerk or Simple Doctor Login */}
                    {isDoctorMode ? (
                        <SimpleDoctorLogin onSuccess={handleDoctorLoginSuccess} />
                    ) : (
                        <SignIn
                            appearance={{
                                elements: {
                                    rootBox: 'mx-auto',
                                    card: 'bg-white/10 border border-white/20 shadow-xl backdrop-blur-sm',
                                    headerTitle: 'text-white',
                                    headerSubtitle: 'text-emerald-100/70',
                                    formButtonPrimary: 'bg-emerald-600 hover:bg-emerald-700',
                                    formFieldInput: 'bg-white/10 border-white/30 text-white placeholder-white/50',
                                    formFieldLabel: 'text-emerald-100',
                                    footerActionLink: 'text-emerald-300 hover:text-emerald-100'
                                }
                            }}
                            forceRedirectUrl="/patient"
                            signUpUrl="/sign-up"
                        />
                    )}
                </SignedOut>
            </div>
        </div>
    )
}

export default SignInPage
