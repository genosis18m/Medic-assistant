import { useState, useRef, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function Chat({ role = 'patient', userId, userEmail }) {
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [sessionId, setSessionId] = useState(null)
    const [suggestedActions, setSuggestedActions] = useState([])
    const messagesEndRef = useRef(null)

    // Welcome message
    useEffect(() => {
        const welcomeMsg = {
            role: 'assistant',
            content: role === 'doctor'
                ? "👨‍⚕️ Welcome, Doctor! How can I assist you today?"
                : "👋 Hello! I'm your Medical Assistant. I can help you:\n\n• Book appointments\n• Check availability\n• Cancel appointments\n• View your schedule\n\nHow can I help you today?"
        }
        setMessages([welcomeMsg])
    }, [role])

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    // Parse suggested actions from bot response
    const parseSuggestedActions = (content) => {
        // Look for lists or options in the message
        if (content.includes('9:00 AM') || content.includes('time')) {
            return ['9:00 AM', '10:00 AM', '11:00 AM', '2:00 PM', '3:00 PM', '4:00 PM']
        }
        if (content.toLowerCase().includes('confirm') || content.toLowerCase().includes('yes or no')) {
            return ['Yes, confirm', 'No, cancel']
        }
        if (content.toLowerCase().includes('doctor') && content.includes('Sarah')) {
            return ['Dr. Mohit Adoni', 'Dr. Sarah Johnson', 'Dr. Michael Chen', 'Dr. Emily Williams', 'Dr. James Brown']
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
                throw new Error('Failed to get response')
            }
        } catch (error) {
            console.error('Chat error:', error)
            const errorMessage = {
                role: 'assistant',
                content: '❌ Sorry, I encountered an error. Please try again.'
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
                            <p className="text-white/60 text-sm mb-2">Quick options:</p>
                            <div className="flex flex-wrap gap-2">
                                {suggestedActions.map((action, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => handleQuickAction(action)}
                                        className="px-4 py-2 bg-white/10 hover:bg-white/20 border border-white/20 text-white rounded-lg transition-colors text-sm"
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
