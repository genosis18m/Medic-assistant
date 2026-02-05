import { useState } from 'react'

function RoleSelector({ onSelectRole, currentRole }) {
    const [hoveredRole, setHoveredRole] = useState(null)

    const roles = [
        {
            id: 'patient',
            title: 'Patient',
            description: 'Book appointments, check availability, and manage your healthcare schedule',
            icon: (
                <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
            ),
            gradient: 'from-teal-500 to-cyan-500',
            hoverGradient: 'from-teal-400 to-cyan-400'
        },
        {
            id: 'doctor',
            title: 'Doctor',
            description: 'View patient stats, generate reports, and receive notifications',
            icon: (
                <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                        d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                        d="M12 8v4m0 0v4m0-4h4m-4 0H8" />
                </svg>
            ),
            gradient: 'from-purple-500 to-blue-500',
            hoverGradient: 'from-purple-400 to-blue-400'
        }
    ]

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-6">
            <div className="max-w-4xl w-full">
                {/* Header */}
                <div className="text-center mb-12">
                    <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-r from-teal-500 to-blue-500 mb-6 shadow-lg shadow-teal-500/20">
                        <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                        </svg>
                    </div>
                    <h1 className="text-4xl font-bold text-white mb-3">
                        Medical Assistant
                    </h1>
                    <p className="text-slate-400 text-lg">
                        AI-Powered Doctor Appointment & Reporting System
                    </p>
                </div>

                {/* Role Cards */}
                <div className="grid md:grid-cols-2 gap-6">
                    {roles.map((role) => (
                        <button
                            key={role.id}
                            onClick={() => onSelectRole(role.id)}
                            onMouseEnter={() => setHoveredRole(role.id)}
                            onMouseLeave={() => setHoveredRole(null)}
                            className={`relative group p-8 rounded-2xl border transition-all duration-300 text-left
                                ${currentRole === role.id
                                    ? `border-transparent bg-gradient-to-br ${role.gradient} shadow-xl`
                                    : 'border-slate-700/50 bg-slate-800/50 hover:border-slate-600/50 hover:bg-slate-800/80'}
                                ${hoveredRole === role.id && currentRole !== role.id ? 'transform scale-[1.02]' : ''}`}
                        >
                            {/* Icon */}
                            <div className={`inline-flex items-center justify-center w-16 h-16 rounded-xl mb-4 transition-colors
                                ${currentRole === role.id
                                    ? 'bg-white/20 text-white'
                                    : `bg-gradient-to-br ${role.gradient} text-white`}`}>
                                {role.icon}
                            </div>

                            {/* Title */}
                            <h2 className={`text-2xl font-bold mb-2 transition-colors
                                ${currentRole === role.id ? 'text-white' : 'text-slate-100'}`}>
                                {role.title}
                            </h2>

                            {/* Description */}
                            <p className={`transition-colors
                                ${currentRole === role.id ? 'text-white/80' : 'text-slate-400'}`}>
                                {role.description}
                            </p>

                            {/* Selected indicator */}
                            {currentRole === role.id && (
                                <div className="absolute top-4 right-4">
                                    <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                                        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                        </svg>
                                    </div>
                                </div>
                            )}

                            {/* Hover arrow */}
                            <div className={`absolute bottom-4 right-4 transition-all duration-300
                                ${hoveredRole === role.id && currentRole !== role.id ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-2'}`}>
                                <svg className="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                                </svg>
                            </div>
                        </button>
                    ))}
                </div>

                {/* Continue Button */}
                {currentRole && (
                    <div className="mt-8 text-center">
                        <p className="text-slate-400 text-sm">
                            Click on your role card again or chat will appear above
                        </p>
                    </div>
                )}

                {/* Features */}
                <div className="mt-12 grid grid-cols-3 gap-6 text-center">
                    <div className="p-4">
                        <div className="text-2xl mb-2">🤖</div>
                        <h3 className="text-slate-300 font-medium">AI-Powered</h3>
                        <p className="text-slate-500 text-sm">Natural language understanding</p>
                    </div>
                    <div className="p-4">
                        <div className="text-2xl mb-2">📅</div>
                        <h3 className="text-slate-300 font-medium">Calendar Sync</h3>
                        <p className="text-slate-500 text-sm">Google Calendar integration</p>
                    </div>
                    <div className="p-4">
                        <div className="text-2xl mb-2">🔔</div>
                        <h3 className="text-slate-300 font-medium">Notifications</h3>
                        <p className="text-slate-500 text-sm">Email & Slack alerts</p>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default RoleSelector
