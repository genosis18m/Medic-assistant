import Chat from './components/Chat'

function App() {
    return (
        <div className="min-h-screen flex flex-col">
            {/* Header */}
            <header className="bg-gradient-to-r from-medical-teal to-medical-blue py-4 px-6 shadow-lg">
                <div className="max-w-4xl mx-auto flex items-center gap-3">
                    <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                        </svg>
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-white">Medical Assistant</h1>
                        <p className="text-white/70 text-sm">AI-Powered Appointment Booking</p>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 flex">
                <Chat />
            </main>

            {/* Footer */}
            <footer className="py-4 text-center text-slate-500 text-sm">
                <p>© 2024 Medical Assistant. Powered by AI.</p>
            </footer>
        </div>
    )
}

export default App
