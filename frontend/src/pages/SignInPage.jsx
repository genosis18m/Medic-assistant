import { SignIn } from '@clerk/clerk-react'

function SignInPage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-emerald-900 via-green-800 to-teal-900 flex items-center justify-center p-6">
            <div className="max-w-md w-full">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-white mb-4 shadow-lg shadow-emerald-500/30">
                        <svg className="w-8 h-8 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                        </svg>
                    </div>
                    <h1 className="text-3xl font-bold text-white mb-2">Medical Assistant</h1>
                    <p className="text-emerald-100/80">Sign in to continue</p>
                </div>

                {/* Clerk Sign In Component */}
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
                    routing="path"
                    path="/sign-in"
                    signUpUrl="/sign-up"
                />
            </div>
        </div>
    )
}

export default SignInPage
