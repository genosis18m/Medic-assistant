import { useState } from 'react'

const DOCTOR_CREDENTIALS = {
    'doctor12345@gmail.com': { password: 'doctor', doctorId: 5, name: 'Dr. Mohit Adoni' },
    'adonimohit@gmail.com': { password: 'doctor', doctorId: 5, name: 'Dr. Mohit Adoni' }
}

function SimpleDoctorLogin({ onSuccess }) {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const handleLogin = (e) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        setTimeout(() => {
            const credentials = DOCTOR_CREDENTIALS[email]

            if (!credentials) {
                setError('Doctor account not found')
                setLoading(false)
                return
            }

            if (credentials.password !== password) {
                setError('Incorrect password')
                setLoading(false)
                return
            }

            // Success!
            onSuccess({
                email,
                doctorId: credentials.doctorId,
                name: credentials.name
            })
            setLoading(false)
        }, 500)
    }

    return (
        <div className="w-full max-w-md">
            <div className="bg-white/10 border border-white/20 rounded-2xl p-8 backdrop-blur-sm">
                <div className="flex justify-center mb-6">
                    <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center p-2 backdrop-blur-md shadow-lg">
                        <img src="/logo.svg" alt="Medical Assistant Logo" className="w-full h-full object-contain" />
                    </div>
                </div>
                <h2 className="text-2xl font-bold text-white mb-6 text-center">Doctor Login</h2>

                <form onSubmit={handleLogin} className="space-y-4">
                    <div>
                        <label className="block text-emerald-100 text-sm font-medium mb-2">
                            Email Address
                        </label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-emerald-400 focus:ring-2 focus:ring-emerald-400/20"
                            placeholder="doctor12345@gmail.com"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-emerald-100 text-sm font-medium mb-2">
                            Password
                        </label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-emerald-400 focus:ring-2 focus:ring-emerald-400/20"
                            placeholder="Enter password"
                            required
                        />
                    </div>

                    {error && (
                        <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200 text-sm">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Signing in...' : 'Sign In'}
                    </button>
                </form>

                <div className="mt-6 p-4 bg-white/5 rounded-lg">
                    <p className="text-emerald-100/60 text-xs text-center">
                        Demo Credentials:<br />
                        <strong className="text-emerald-200">doctor12345@gmail.com</strong> / <strong className="text-emerald-200">doctor</strong>
                    </p>
                </div>
            </div>
        </div>
    )
}

export default SimpleDoctorLogin
