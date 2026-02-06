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
    const messagesEndRef = useRef(null)

    // Welcome message with initial actions
    useEffect(() => {
        const welcomeMsg = {
            role: 'assistant',
            content: role === 'doctor'
                ? "👨‍⚕️ Welcome, Doctor! How can I assist you today?"
                : "👋 Hello! I'm your Medical Assistant. I can help you:\n\n• Book appointments\n• Check availability\n• Cancel appointments\n• View your schedule\n\nHow can I help you today?"
        }
        setMessages([welcomeMsg])
        setSuggestedActions(INITIAL_ACTIONS)
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

    // Parse suggested actions from bot response - SMART DETECTION
    const parseSuggestedActions = (content) => {
        const lowerContent = content.toLowerCase()

        // Check for date selection
        if (lowerContent.includes('which date') || lowerContent.includes('what date') ||
            (lowerContent.includes('date') && lowerContent.includes('appointment'))) {
            const dates = getNextTwoDays()
            return dates.map(d => d.label)
        }

        // Check for time slots - EXTRACT FROM RESPONSE
        if (lowerContent.includes('available slots') || lowerContent.includes('available times') ||
            lowerContent.includes('what time') || lowerContent.includes('time works')) {
            const extractedSlots = extractTimeSlots(content)
            if (extractedSlots.length > 0) {
                return extractedSlots
            }
            // Fallback to default times if extraction fails
            return ['9:00 AM', '10:00 AM', '11:00 AM', '2:00 PM', '3:00 PM', '4:00 PM']
        }

        // Check for doctor selection questions
        if (lowerContent.includes('which doctor') || lowerContent.includes('what doctor') ||
            lowerContent.includes('see a doctor') || lowerContent.includes('which one') ||
            lowerContent.includes("i'd be happy") ||
            (lowerContent.includes('doctor') && (lowerContent.includes('like to see') || lowerContent.includes('want to see') || lowerContent.includes('book with'))) ||
            (lowerContent.includes('book') && lowerContent.includes('doctor'))) {
            return ['Dr. Mohit Adoni', 'Dr. Sarah Johnson', 'Dr. Michael Chen', 'Dr. Emily Williams', 'Dr. James Brown']
        }

        // Check for confirmation
        if (lowerContent.includes('confirm') || lowerContent.includes('is this correct') ||
            lowerContent.includes('yes or no')) {
            return ['Yes, confirm', 'No, cancel']
        }

        // Check for doctor list (fallback)
        if ((lowerContent.includes('doctor') || lowerContent.includes('available')) &&
            (content.includes('Sarah') || content.includes('Mohit') || content.includes('ID:'))) {
            return ['Dr. Mohit Adoni', 'Dr. Sarah Johnson', 'Dr. Michael Chen', 'Dr. Emily Williams', 'Dr. James Brown']
        }

        // Check for symptoms
        if (lowerContent.includes('symptom') || lowerContent.includes('issue') ||
            lowerContent.includes('brought you') || lowerContent.includes('reason for visit')) {
            return ['Fever', 'Headache', 'Cough', 'Back Pain', 'Stomach Ache', 'Other']
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
                    user_email: userEmail
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

                // Parse and set suggested actions
                const actions = parseSuggestedActions(data.response)
                setSuggestedActions(actions)
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
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[70%] p-4 rounded-lg ${msg.role === 'user'
                                ? 'bg-teal-600 text-white'
                                : 'bg-white/10 text-white border border-white/20'
                                }`}
                        >
                            <p className="whitespace-pre-wrap">{msg.content}</p>
                        </div>
                    </div>
                ))}

                {/* Suggested Actions */}
                {suggestedActions.length > 0 && !isLoading && (
                    <div className="flex justify-start">
                        <div className="max-w-[70%]">
                            <p className="text-white/60 text-sm mb-2">
                                {messages.length === 1 ? 'Quick actions:' : 'Choose an option:'}
                            </p>
                            <div className="flex flex-wrap gap-2">
                                {suggestedActions.map((action, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => handleQuickAction(action)}
                                        className="px-4 py-2 bg-teal-600/20 hover:bg-teal-600/40 border border-teal-500/50 text-teal-200 rounded-lg transition-colors text-sm font-medium"
                                    >
                                        {action}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-white/10 text-white border border-white/20 p-4 rounded-lg">
                            <div className="flex gap-2">
                                <div className="w-2 h-2 bg-teal-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                <div className="w-2 h-2 bg-teal-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                <div className="w-2 h-2 bg-teal-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-white/10 p-4 bg-slate-800/50">
                <form onSubmit={handleSubmit} className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your message..."
                        className="flex-1 px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-teal-500"
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        className="px-6 py-3 bg-teal-600 hover:bg-teal-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
                    >
                        Send
                    </button>
                </form>
            </div>
        </div>
    )
}

export default Chat
