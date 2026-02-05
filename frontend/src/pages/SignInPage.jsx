import { useState } from 'react'
import { SignIn } from '@clerk/clerk-react'
import { useNavigate } from 'react-router-dom'
import SimpleDoctorLogin from '../components/SimpleDoctorLogin'

function SignInPage() {
    const [isDoctorMode, setIsDoctorMode] = useState(false)
    const navigate = useNavigate()

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

                {/* Toggle between Clerk and Doctor Login */}
                <div className="flex gap-2 mb-6">
                    <button
                        onClick={() => setIsDoctorMode(false)}
                        className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${!isDoctorMode
                            ? 'bg-white text-emerald-900'
                            : 'bg-white/10 text-white hover:bg-white/20'
                            }`}
                    >
                        Patient Login
                    </button>
                    <button
                        onClick={() => setIsDoctorMode(true)}
                        className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${isDoctorMode
                            ? 'bg-white text-emerald-900'
                            : 'bg-white/10 text-white hover:bg-white/20'
                            }`}
                    >
                        👨‍⚕️ Doctor Login
                    </button>
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
                        redirectUrl="/patient"
                        signUpUrl="/sign-up"
                    />
                )}
            </div>
        </div>
    )
}

export default SignInPage
