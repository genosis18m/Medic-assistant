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

            {/* Enhanced Input Area with Glassmorphism */}
            <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="glass-effect-strong border-t border-white/20 p-4"
            >
                <form onSubmit={handleSubmit} className="flex gap-3">
                    <div className="flex-1 relative group">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder={role === 'doctor' ? "Ask about your patients or generate reports..." : "Describe your symptoms or ask a question..."}
                            className="input-field w-full text-white placeholder-white/40"
                            disabled={isLoading}
                        />
                        <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-teal-500/20 to-blue-500/20 opacity-0 group-focus-within:opacity-100 transition-opacity pointer-events-none blur-xl"></div>
                    </div>

                    <motion.button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        whileHover={{ scale: 1.05, y: -2 }}
                        whileTap={{ scale: 0.95 }}
                        className={`btn-primary relative overflow-hidden ${isLoading || !input.trim()
                            ? 'opacity-50 cursor-not-allowed'
                            : 'pulse-glow'
                            }`}
                    >
                        {isLoading ? (
                            <motion.svg
                                animate={{ rotate: 360 }}
                                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                className="h-5 w-5"
                                fill="none"
                                viewBox="0 0 24 24"
                            >
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </motion.svg>
                        ) : (
                            <span className="flex items-center gap-2">
                                Send
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                                </svg>
                            </span>
                        )}
                    </motion.button>
                </form>

                {/* Enhanced Quick Actions with Hover Effects */}
                <div className="mt-4 flex flex-wrap gap-2">
                    {quickActions.map((action, idx) => (
                        <motion.button
                            key={idx}
                            onClick={() => {
                                setInput(action)
                                setShowPreview(true)
                            }}
                            whileHover={{ scale: 1.05, y: -2 }}
                            whileTap={{ scale: 0.95 }}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.05 }}
                            className="text-sm px-4 py-2 rounded-lg glass-effect text-white/80 hover:text-white hover:glass-effect-strong transition-all border border-white/10 hover:border-teal-400/50 shimmer"
                        >
                            💡 {action}
                        </motion.button>
                    ))}
                </div>
            </motion.div>

            {/* Legacy input area removed - using enhanced version above */}
        </div>
    )
}

export default Chat
