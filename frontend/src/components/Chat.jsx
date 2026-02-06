import { useState, useRef, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Initial welcome quick actions
const INITIAL_ACTIONS = ['Book Appointment', 'Check Availability', 'View My Appointments', 'Cancel Appointment']

// Get next 2 days for date selection (tomorrow and day after)
const getNextTwoDays = () => {
    const today = new Date()
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    const dayAfter = new Date(today)
    dayAfter.setDate(dayAfter.getDate() + 2)

    const formatDate = (date) => {
        const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return `${days[date.getDay()]}, ${months[date.getMonth()]} ${date.getDate()}`
    }

    return [
        { label: `Today (${formatDate(today)})`, value: today.toISOString().split('T')[0] },
        { label: `Tomorrow (${formatDate(tomorrow)})`, value: tomorrow.toISOString().split('T')[0] },
        { label: `${formatDate(dayAfter)}`, value: dayAfter.toISOString().split('T')[0] }
    ]
}

function Chat({ role = 'patient', userId, userEmail }) {
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [sessionId, setSessionId] = useState(null)
    const [suggestedActions, setSuggestedActions] = useState(INITIAL_ACTIONS)
    const [selectedDoctorId, setSelectedDoctorId] = useState(null)
    const messagesEndRef = useRef(null)

    const doctors = [
        { id: 1, name: 'Dr. Sarah Johnson (General)' },
        { id: 2, name: 'Dr. Michael Chen (Cardiology)' },
        { id: 3, name: 'Dr. Emily Williams (Dermatology)' },
        { id: 4, name: 'Dr. James Brown (Neurology)' },
        { id: 5, name: 'Dr. Mohit Adoni (General)' }
    ]

    // Initialize messages based on role
    // Initialize messages and session
    useEffect(() => {
        const loadChat = async () => {
            // Try to recover session from local storage
            let currentSessionId = localStorage.getItem('chat_session_id')

            // If we have a session, try to fetch history
            if (currentSessionId) {
                try {
                    const response = await fetch(`${API_URL}/chat/history?session_id=${currentSessionId}`)
                    if (response.ok) {
                        const data = await response.json()
                        if (data.history && data.history.length > 0) {
                            setSessionId(currentSessionId)
                            // Transform backend history format to frontend messages
                            // Backend: [{role: 'user', parts: [...]}, ...]
                            // Frontend: [{role: 'user', content: '...'}, ...]
                            const formattedMessages = data.history.map(msg => ({
                                role: msg.role,
                                content: typeof msg.parts[0] === 'string' ? msg.parts[0] : msg.parts[0].text
                            }))
                            setMessages(formattedMessages)
                            return // Exit if history loaded
                        }
                    }
                } catch (e) {
                    console.error("Failed to load history:", e)
                }
            }

            // Fallback: Start New Chat
            if (messages.length === 0) {
                const initialMsg = role === 'doctor'
                    ? "👨‍⚕️ Welcome! I can help you with reports, schedules, and patient stats. Who are you assisting?"
                    : "👋 Hello! I'm your Medical Assistant. How can I help you today?"

                setMessages([{ role: 'assistant', content: initialMsg }])
            }

            if (role === 'doctor') {
                setSuggestedActions(['Today\'s Schedule', 'Weekly Report', 'Patient Stats'])
            } else {
                setSuggestedActions(['Book Appointment', 'Check Availability'])
            }
        }

        loadChat()
    }, [role])

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    // Extract time slots from text (e.g., "9:00 AM", "10:30", "4:00 PM")
    const extractTimeSlots = (text) => {
        const timeRegex = /\b(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)?\b/g
        const matches = [...text.matchAll(timeRegex)]
        const uniqueTimes = new Set()

        matches.forEach(match => {
            let [, hourStr, minuteStr, meridiem] = match
            let hour = parseInt(hourStr)
            const minute = minuteStr // Keep as string, already has 2 digits from regex

            // Convert to 12-hour format with AM/PM if not present
            if (!meridiem) {
                meridiem = hour >= 12 ? 'PM' : 'AM'
                if (hour > 12) hour -= 12
                if (hour === 0) hour = 12
            }

            uniqueTimes.add(`${hour}:${minute} ${meridiem.toUpperCase()}`)
        })

        return Array.from(uniqueTimes)
    }

    const parseSuggestedActions = (response) => {
        if (!response) return []
        const content = response
        const lowerContent = content.toLowerCase()

        // DOCTOR MODE SUGGESTIONS
        if (role === 'doctor') {
            return [
                'Today\'s Schedule',
                'Tomorrow\'s Schedule',
                'Day After Tomorrow',
                'Weekly Report',
                'Patient Stats'
            ]
        }

        // PATIENT MODE SUGGESTIONS

        // 1. Date Selection
        if (lowerContent.includes('which date') || lowerContent.includes('what date') ||
            lowerContent.includes('when would you like')) {
            const dates = getNextTwoDays()
            return dates.map(d => d.label)
        }

        // 2. Time Slots
        if (lowerContent.includes('available slots') || lowerContent.includes('what time')) {
            const extractedSlots = extractTimeSlots(content)
            return extractedSlots.length > 0 ? extractedSlots : ['9:00 AM', '10:00 AM', '2:00 PM']
        }

        // 3. Confirmations
        if (lowerContent.includes('confirm') || lowerContent.includes('is this correct')) {
            return ['Yes, confirm', 'No, cancel']
        }

        // 4. Doctor Selection (Patient)
        if (lowerContent.includes('which doctor') || lowerContent.includes('like to see')) {
            return ['Dr. Mohit Adoni', 'Dr. Sarah Johnson', 'Dr. Michael Chen']
        }

        return []
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        if (!input.trim()) return
        sendMessage(input)
    }

    const sendMessage = async (messageText) => {
        const userMessage = { role: 'user', content: messageText }
        setMessages(prev => [...prev, userMessage])
        setInput('')
        setIsLoading(true)
        setSuggestedActions([])

        try {
            const response = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: messageText,
                    session_id: sessionId,
                    role: role,
                    user_id: userId,
                    user_email: userEmail,
                    doctor_id: selectedDoctorId // Send override if selected
                })
            })

            if (response.ok) {
                const data = await response.json()
                const assistantMessage = {
                    role: 'assistant',
                    content: data.response || 'I received your message.'
                }
                setMessages(prev => [...prev, assistantMessage])
                setSessionId(data.session_id)
                localStorage.setItem('chat_session_id', data.session_id)

                // Parse and set suggested actions
                if (data.suggested_actions && data.suggested_actions.length > 0) {
                    setSuggestedActions(data.suggested_actions)
                } else {
                    // Fallback to local parsing logic if backend doesn't provide
                    const actions = parseSuggestedActions(data.response)
                    setSuggestedActions(actions)
                }
            } else {
                const errorText = await response.text()
                console.error('API Error Response:', response.status, errorText)
                throw new Error(`Backend returned ${response.status}`)
            }
        } catch (error) {
            console.error('Chat error:', error)
            const errorMessage = {
                role: 'assistant',
                content: `❌ Backend error: ${error.message}. Make sure backend is running on ${API_URL}`
            }
            setMessages(prev => [...prev, errorMessage])
        } finally {
            setIsLoading(false)
        }
    }

    const handleQuickAction = (action) => {
        sendMessage(action)
    }

    return (
        <div className="flex flex-col h-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            {/* Doctor Context Switcher */}
            {role === 'doctor' && (
                <div className="glass-panel border-b border-white/10 p-2 px-4 flex items-center justify-between backdrop-blur-md z-10">
                    <span className="text-teal-200 text-xs font-medium uppercase tracking-wider">Viewing as</span>
                    <select
                        className="bg-slate-800/80 text-white text-xs border border-white/20 rounded px-3 py-1.5 focus:ring-1 focus:ring-teal-500 outline-none cursor-pointer hover:bg-slate-700/80 transition-colors"
                        onChange={(e) => {
                            const id = Number(e.target.value)
                            setSelectedDoctorId(id)
                            setMessages(prev => [...prev, {
                                role: 'assistant',
                                content: `Switched context to ${doctors.find(d => d.id === id)?.name}. How can I help?`
                            }])
                        }}
                        value={selectedDoctorId || ''}
                    >
                        <option value="">Select Doctor Context...</option>
                        {doctors.map(doc => (
                            <option key={doc.id} value={doc.id}>{doc.name}</option>
                        ))}
                    </select>
                </div>
            )}

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages
                    .filter(msg => {
                        // Filter out tool messages and internal function artifacts
                        if (msg.role === 'tool') return false;
                        if (typeof msg.content === 'string' && (
                            msg.content.includes('(function=') ||
                            msg.content.trim().startsWith('{') && msg.content.trim().endsWith('}')
                        )) return false;
                        return true;
                    })
                    .map((msg, idx) => (
                        <div
                            key={idx}
                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div className={`message-bubble ${msg.role === 'user' ? 'message-user' : 'message-ai'}`}>
                                <p className="whitespace-pre-wrap">{msg.content}</p>
                            </div>
                        </div>
                    ))}

                {/* Suggested Actions */}
                {suggestedActions.length > 0 && !isLoading && (
                    <div className="flex justify-start">
                        <div className="max-w-[85%]">
                            <p className="text-white/60 text-sm mb-2 px-2">
                                {messages.length === 1 ? 'Quick actions:' : 'Choose an option:'}
                            </p>
                            <div className="flex flex-wrap gap-2">
                                {suggestedActions.map((action, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => handleQuickAction(action)}
                                        className="chip"
                                    >
                                        {typeof action === 'object' ? action.label : action}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {isLoading && (
                    <div className="flex justify-start px-4 py-2">
                        <div className="ai-profile-loader">
                            <div className="jolly-loader-small"></div>
                            <span className="loading-text">Generating...</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-white/5 p-4 glass-panel bg-slate-900/40 backdrop-blur-xl flex justify-center">
                <form onSubmit={handleSubmit} className="w-full max-w-2xl">
                    <div className="searchBox">
                        <input
                            className="searchInput"
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type to chat..."
                            disabled={isLoading}
                        />
                        <button
                            className="searchButton"
                            type="submit"
                            disabled={isLoading || !input.trim()}
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                            </svg>
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}

export default Chat
