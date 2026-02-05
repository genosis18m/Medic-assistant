import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Quick action suggestions
const COMMON_SYMPTOMS = [
    "Fever", "Headache", "Cough", "Cold",
    "Back Pain", "Stomach Ache", "Fatigue", "Other"
]

const VISIT_REASONS = [
    "General Checkup", "Follow-up Visit",
    "Emergency", "Consultation",
    "Prescription Refill", "Test Results"
]

const TIME_SLOTS = [
    "9:00 AM", "10:00 AM", "11:00 AM",
    "2:00 PM", "3:00 PM", "4:00 PM"
]

const CONFIRMATIONS = ["Yes", "No"]

function Chat({ role = 'patient', userId, userEmail }) {
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [sessionId, setSessionId] = useState(null)
    const [showPreview, setShowPreview] = useState(false)
    const messagesEndRef = useRef(null)
    const textareaRef = useRef(null)

    // Role-specific welcome messages
    const getWelcomeMessage = () => {
        if (role === 'doctor') {
            return {
                role: 'assistant',
                content: "👨‍⚕️ Welcome, Doctor! I can help you with:\n\n• View today's appointment stats\n• Check patient records by symptoms\n•Generate daily/weekly reports\n• Send summaries to Slack/WhatsApp\n\nWhat would you like to know?"
            }
        }
        return {
            role: 'assistant',
            content: "👋 Hello! I'm your Medical Appointment Assistant. I can help you:\n\n• Check doctor availability\n• Book appointments (with email confirmation)\n• Cancel existing appointments\n• View your scheduled appointments\n\nHow can I help you today?"
        }
    }

    // Reset messages when role changes
    useEffect(() => {
        setMessages([getWelcomeMessage()])
        setSessionId(null)
    }, [role])

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto'
            textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px'
        }
    }, [input])

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return

        const userMessage = input.trim()
        setInput('')
        setMessages(prev => [...prev, { role: 'user', content: userMessage }])
        setIsLoading(true)
        setShowPreview(true)

        try {
            const response = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage,
                    session_id: sessionId,
                    role: role
                })
            })

            if (!response.ok) {
                throw new Error('Failed to get response')
            }

            const data = await response.json()
            setSessionId(data.session_id)
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: data.response,
                timestamp: new Date().toISOString()
            }])
        } catch (error) {
            console.error('Chat error:', error)
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: '❌ Sorry, I encountered an error. Please make sure the backend server is running.'
            }])
        } finally {
            setIsLoading(false)
            setShowPreview(false)
        }
    }

    // Handle Enter key (send) vs Shift+Enter (new line)
    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            sendMessage()
        }
    }

    // Role-specific quick actions
    const quickActions = role === 'doctor'
        ? [
            "How many patients today?",
            "Show me appointments with fever",
            "Generate my daily report",
            "Send summary to WhatsApp"
        ]
        : [
            "Show me available doctors",
            "I need a cardiology appointment",
            "What times are available tomorrow?",
            "Book an appointment"
        ]

    // Expected response preview
    const getExpectedResponse = () => {
        if (role === 'doctor') {
            return "📊 I'm checking your patient records and stats..."
        }
        return "🔍 Let me check available appointments for you..."
    }

    return (
        <div className="flex-1 max-w-4xl mx-auto w-full flex flex-col p-4">
            {/* Messages Container */}
            <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2 scrollbar-thin scrollbar-thumb-slate-600">
                {messages.map((message, index) => (
                    <div
                        key={index}
                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[80%] rounded-2xl px-4 py-3 ${message.role === 'user'
                                ? role === 'doctor'
                                    ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
                                    : 'bg-gradient-to-r from-medical-teal to-medical-blue text-white'
                                : 'bg-slate-800/80 text-slate-100 border border-slate-700/50 backdrop-blur-sm'
                                }`}
                        >
                            <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
                            {message.timestamp && message.role === 'assistant' && (
                                <p className="text-xs text-slate-400 mt-2">
                                    {new Date(message.timestamp).toLocaleTimeString()}
                                </p>
                            )}
                        </div>
                    </div>
                ))}

                {/* Loading indicator */}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-slate-800/80 rounded-2xl px-4 py-3 border border-slate-700/50">
                            <div className="flex items-center gap-2">
                                <div className="flex gap-1">
                                    <span className={`w-2 h-2 rounded-full animate-bounce ${role === 'doctor' ? 'bg-purple-500' : 'bg-medical-teal'}`} style={{ animationDelay: '0ms' }}></span>
                                    <span className={`w-2 h-2 rounded-full animate-bounce ${role === 'doctor' ? 'bg-purple-500' : 'bg-medical-teal'}`} style={{ animationDelay: '150ms' }}></span>
                                    <span className={`w-2 h-2 rounded-full animate-bounce ${role === 'doctor' ? 'bg-purple-500' : 'bg-medical-teal'}`} style={{ animationDelay: '300ms' }}></span>
                                </div>
                                <span className="text-slate-400 text-sm">Thinking...</span>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Quick Actions */}
            {messages.length <= 1 && (
                <div className="flex flex-wrap gap-2 mb-4">
                    {quickActions.map((action, index) => (
                        <button
                            key={index}
                            onClick={() => setInput(action)}
                            className={`px-3 py-2 text-sm bg-slate-800/50 hover:bg-slate-700/50 text-slate-300 
                       rounded-xl border border-slate-700/50 transition-all duration-200 
                       ${role === 'doctor'
                                    ? 'hover:border-purple-500/50 hover:text-purple-400'
                                    : 'hover:border-medical-teal/50 hover:text-medical-teal'}`}
                        >
                            {action}
                        </button>
                    ))}
                </div>
            )}

            {/* Input Form */}
            <div className="relative">
                <textarea
                    ref={textareaRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={role === 'doctor' ? "Ask about your patients... (Shift+Enter for new line)" : "Type your message... (Shift+Enter for new line)"}
                    disabled={isLoading}
                    rows={1}
                    className={`w-full px-4 py-3 pr-14 rounded-xl bg-slate-800/70 border border-slate-700/50 
                   text-white placeholder-slate-500 focus:outline-none transition-all duration-200 resize-none
                   ${role === 'doctor'
                            ? 'focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20'
                            : 'focus:border-medical-teal focus:ring-2 focus:ring-medical-teal/20'}`}
                />
                <button
                    onClick={sendMessage}
                    disabled={isLoading || !input.trim()}
                    className={`absolute right-2 bottom-2 p-2 text-white rounded-lg transition-all duration-200
                   disabled:opacity-50 disabled:cursor-not-allowed ${role === 'doctor'
                            ? 'bg-gradient-to-r from-purple-600 to-blue-600 hover:opacity-90'
                            : 'bg-gradient-to-r from-medical-teal to-medical-blue hover:opacity-90'}`}
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                </button>
            </div>

            {/* Helper text */}
            <p className="text-xs text-slate-500 mt-2 text-center">
                Press <kbd className="px-1 py-0.5 bg-slate-700 rounded">Enter</kbd> to send •
                <kbd className="px-1 py-0.5 bg-slate-700 rounded ml-1">Shift + Enter</kbd> for new line
            </p>
        </div>
    )
}

export default Chat
