import { useState, useRef, useEffect } from 'react'

const API_URL = 'http://localhost:8000'

function Chat() {
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            content: "👋 Hello! I'm your Medical Appointment Assistant. I can help you:\n\n• Check doctor availability\n• Book appointments\n• Cancel existing appointments\n• View your scheduled appointments\n\nHow can I help you today?"
        }
    ])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [sessionId, setSessionId] = useState(null)
    const messagesEndRef = useRef(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const sendMessage = async (e) => {
        e.preventDefault()
        if (!input.trim() || isLoading) return

        const userMessage = input.trim()
        setInput('')
        setMessages(prev => [...prev, { role: 'user', content: userMessage }])
        setIsLoading(true)

        try {
            const response = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage,
                    session_id: sessionId
                })
            })

            if (!response.ok) {
                throw new Error('Failed to get response')
            }

            const data = await response.json()
            setSessionId(data.session_id)
            setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
        } catch (error) {
            console.error('Chat error:', error)
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: '❌ Sorry, I encountered an error. Please make sure the backend server is running on port 8000 and you have set your OPENAI_API_KEY.'
            }])
        } finally {
            setIsLoading(false)
        }
    }

    const quickActions = [
        "Show me available doctors",
        "I need a cardiology appointment",
        "What times are available tomorrow?",
        "Book an appointment"
    ]

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
                                    ? 'bg-gradient-to-r from-medical-teal to-medical-blue text-white'
                                    : 'bg-slate-800/80 text-slate-100 border border-slate-700/50 backdrop-blur-sm'
                                }`}
                        >
                            <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-slate-800/80 rounded-2xl px-4 py-3 border border-slate-700/50">
                            <div className="flex items-center gap-2">
                                <div className="flex gap-1">
                                    <span className="w-2 h-2 rounded-full bg-medical-teal animate-bounce" style={{ animationDelay: '0ms' }}></span>
                                    <span className="w-2 h-2 rounded-full bg-medical-teal animate-bounce" style={{ animationDelay: '150ms' }}></span>
                                    <span className="w-2 h-2 rounded-full bg-medical-teal animate-bounce" style={{ animationDelay: '300ms' }}></span>
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
                            className="px-3 py-2 text-sm bg-slate-800/50 hover:bg-slate-700/50 text-slate-300 
                       rounded-xl border border-slate-700/50 transition-all duration-200 
                       hover:border-medical-teal/50 hover:text-medical-teal"
                        >
                            {action}
                        </button>
                    ))}
                </div>
            )}

            {/* Input Form */}
            <form onSubmit={sendMessage} className="flex gap-3">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your message..."
                    disabled={isLoading}
                    className="flex-1 px-4 py-3 rounded-xl bg-slate-800/70 border border-slate-700/50 
                   text-white placeholder-slate-500 focus:outline-none focus:border-medical-teal
                   focus:ring-2 focus:ring-medical-teal/20 transition-all duration-200"
                />
                <button
                    type="submit"
                    disabled={isLoading || !input.trim()}
                    className="px-6 py-3 bg-gradient-to-r from-medical-teal to-medical-blue text-white 
                   rounded-xl font-medium hover:opacity-90 disabled:opacity-50 
                   disabled:cursor-not-allowed transition-all duration-200
                   hover:shadow-lg hover:shadow-medical-teal/20"
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                </button>
            </form>
        </div>
    )
}

export default Chat
