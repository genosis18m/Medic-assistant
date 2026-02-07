import React, { useState } from 'react';
import { SignIn, useUser } from '@clerk/clerk-react';
import { useNavigate } from 'react-router-dom';
import './UnifiedLoginPage.css';

const UnifiedLoginPage = () => {
    // isChecked = true -> Patient (Back), false -> Doctor (Front)
    const [isChecked, setIsChecked] = useState(false);
    const navigate = useNavigate();
    const { isSignedIn, user, isLoaded } = useUser();

    // Auto-redirect if already signed in
    React.useEffect(() => {
        if (isLoaded && isSignedIn) {
            // Check if user is a doctor
            const email = user?.primaryEmailAddress?.emailAddress;
            const isDoctor = ['doctor12345@gmail.com', 'adonimohit@gmail.com', 'doctor@clinic.com'].includes(email);
            if (isDoctor) {
                navigate('/doctor/dashboard');
            } else {
                navigate('/patient');
            }
        }
    }, [isLoaded, isSignedIn, user, navigate]);

    // -- DOCTOR LOGIN STATE --
    const [doctorEmail, setDoctorEmail] = useState('');
    const [doctorPassword, setDoctorPassword] = useState('');
    const [doctorError, setDoctorError] = useState('');

    // --- DOCTOR LOGIN HANDLER ---
    const handleDoctorLogin = (e) => {
        e.preventDefault();
        setDoctorError('');

        // Simple mock authentication demo logic
        const validDoctors = {
            'sarah@clinic.com': { id: 1, name: 'Dr. Sarah Johnson' },
            'michael@clinic.com': { id: 2, name: 'Dr. Michael Chen' },
            'emily@clinic.com': { id: 3, name: 'Dr. Emily Williams' },
            'james@clinic.com': { id: 4, name: 'Dr. James Brown' },
            'adonimohit@gmail.com': { id: 5, name: 'Dr. Mohit Adoni' },
            'doctor@clinic.com': { id: 5, name: 'Dr. Mohit Adoni' },
            'momoochan.ofc@gmail.com': { id: 5, name: 'Dr. Mohit Adoni' } // Added user email for easier testing
        };

        // Normalize input: remove spaces, lowercase email
        const normalizedEmail = doctorEmail.trim().toLowerCase();
        const normalizedPassword = doctorPassword.trim(); // Optional: allow spaces in password if needed, but 'password' has none

        // Check against valid doctors
        if (validDoctors[normalizedEmail] && normalizedPassword === 'password') {
            const doctorData = {
                email: normalizedEmail,
                doctorId: validDoctors[normalizedEmail].id,
                name: validDoctors[normalizedEmail].name,
                role: 'doctor'
            };
            localStorage.setItem('simpleDoctorAuth', JSON.stringify(doctorData));
            window.location.href = '/doctor/dashboard';
        } else {
            setDoctorError('Invalid credentials. Try doctor@clinic.com / password');
        }
    };

    return (
        <div className="wrapper">
            <div className="card-switch">
                <label className="switch">
                    {/* Accessibly hidden toggle input */}
                    <input
                        type="checkbox"
                        className="toggle"
                        checked={isChecked}
                        onChange={(e) => setIsChecked(e.target.checked)}
                    />

                    {/* The "Button of Change" - Visible Toggle Switch */}
                    <div className="toggle-label" onClick={(e) => e.stopPropagation()}>
                        {/* We stop propagation so clicking the label doesn't double-toggle, 
                             control is handled by the parent label wrapping the input or manual state */}
                        <span className={`toggle-text ${!isChecked ? 'active' : ''}`}>Doctor</span>
                        <div className="toggle-slider" onClick={() => setIsChecked(!isChecked)}>
                            <div className="toggle-knob"></div>
                        </div>
                        <span className={`toggle-text ${isChecked ? 'active' : ''}`}>Patient</span>
                    </div>

                    <div className="flip-card__inner">
                        {/* FRONT: DOCTOR LOGIN */}
                        <div className="flip-card__front">
                            <div className="logo-container">
                                <svg className="w-10 h-10 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                                </svg>
                            </div>
                            <div className="title">Doctor Portal</div>
                            <form className="flip-card__form" onSubmit={handleDoctorLogin}>
                                <input
                                    className="flip-card__input"
                                    name="email"
                                    placeholder="Doctor Email"
                                    type="email"
                                    value={doctorEmail}
                                    onChange={(e) => setDoctorEmail(e.target.value)}
                                    required
                                />
                                <input
                                    className="flip-card__input"
                                    name="password"
                                    placeholder="Password"
                                    type="password"
                                    value={doctorPassword}
                                    onChange={(e) => setDoctorPassword(e.target.value)}
                                    required
                                />
                                {doctorError && <p className="error-message">{doctorError}</p>}
                                <button className="flip-card__btn">Access Portal</button>
                            </form>
                        </div>

                        {/* BACK: PATIENT LOGIN (CLERK) */}
                        <div className="flip-card__back">
                            <div className="w-full flex justify-center">
                                <SignIn
                                    appearance={{
                                        elements: {
                                            rootBox: 'w-full',
                                            card: 'bg-transparent shadow-none p-0 w-full',
                                            headerTitle: 'text-white text-2xl font-bold mb-4',
                                            headerSubtitle: 'text-slate-400 mb-6',
                                            formButtonPrimary: 'bg-gradient-to-r from-teal-500 to-teal-700 hover:from-teal-600 hover:to-teal-800 shadow-lg shadow-teal-500/30 border-0',
                                            socialButtonsBlockButton: 'bg-slate-900 border border-slate-700 hover:bg-slate-800 text-white',
                                            socialButtonsBlockButtonText: 'text-white font-medium',
                                            formFieldLabel: 'text-slate-300',
                                            formFieldInput: 'bg-slate-900 border-slate-700 text-white placeholder-slate-500 focus:border-teal-500 focus:ring-teal-500/20',
                                            footerActionLink: 'text-teal-400 hover:text-teal-300',
                                            dividerLine: 'bg-slate-700',
                                            dividerText: 'text-slate-500'
                                        },
                                        variables: {
                                            colorPrimary: '#2dd4bf',
                                            colorText: '#f8fafc',
                                            colorTextSecondary: '#94a3b8',
                                            colorBackground: 'transparent',
                                            colorInputBackground: '#0f172a',
                                            colorInputText: '#f8fafc',
                                            colorInputBorder: '#334155'
                                        }
                                    }}
                                    routing="path"
                                    path="/sign-in"
                                    signUpUrl="/sign-up"
                                    forceRedirectUrl="/patient"
                                />
                            </div>
                        </div>
                    </div>
                </label>
            </div>
        </div>
    );
};

export default UnifiedLoginPage;
