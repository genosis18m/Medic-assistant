import React, { useState } from 'react';
import { useSignIn } from '@clerk/clerk-react';
import { useNavigate } from 'react-router-dom';
import './UnifiedLoginPage.css';

const UnifiedLoginPage = () => {
    const [isChecked, setIsChecked] = useState(false); // false = Doctor (Front), true = Patient (Back)
    const navigate = useNavigate();

    // -- DOCTOR LOGIN STATE --
    const [doctorEmail, setDoctorEmail] = useState('');
    const [doctorPassword, setDoctorPassword] = useState('');
    const [doctorError, setDoctorError] = useState('');

    // -- PATIENT LOGIN STATE --
    const { isLoaded, signIn, setActive } = useSignIn();
    const [patientEmail, setPatientEmail] = useState('');
    const [patientPassword, setPatientPassword] = useState('');
    const [patientError, setPatientError] = useState('');

    // --- DOCTOR LOGIN HANDLER ---
    const handleDoctorLogin = (e) => {
        e.preventDefault();
        setDoctorError('');

        // Simple mock authentication for demo
        const validDoctors = {
            'sarah@clinic.com': { id: 1, name: 'Dr. Sarah Johnson' },
            'michael@clinic.com': { id: 2, name: 'Dr. Michael Chen' },
            'emily@clinic.com': { id: 3, name: 'Dr. Emily Williams' },
            'james@clinic.com': { id: 4, name: 'Dr. James Brown' },
            'adonimohit@gmail.com': { id: 5, name: 'Dr. Mohit Adoni' },
            // Allow generic for testing
            'doctor@clinic.com': { id: 5, name: 'Dr. Mohit Adoni' }
        };

        if (validDoctors[doctorEmail] && doctorPassword === 'password') {
            const doctorData = {
                email: doctorEmail,
                doctorId: validDoctors[doctorEmail].id,
                name: validDoctors[doctorEmail].name,
                role: 'doctor'
            };
            localStorage.setItem('simpleDoctorAuth', JSON.stringify(doctorData));
            window.location.href = '/doctor/dashboard';
        } else {
            setDoctorError('Invalid credentials. Try doctor@clinic.com / password');
        }
    };

    // --- PATIENT LOGIN HANDLER ---
    const handlePatientLogin = async (e) => {
        e.preventDefault();
        if (!isLoaded) return;
        setPatientError('');

        try {
            const result = await signIn.create({
                identifier: patientEmail,
                password: patientPassword,
            });

            if (result.status === "complete") {
                await setActive({ session: result.createdSessionId });
                navigate('/patient');
            } else {
                console.log(result);
                setPatientError('Login incomplete. Multi-factor needed?');
            }
        } catch (err) {
            console.error(err);
            setPatientError(err.errors?.[0]?.message || 'Invalid email or password');
        }
    };

    return (
        <div className="wrapper bg-slate-900">
            <div className="card-switch">
                <label className="switch">
                    {/* Checkbox controls the flip: Checked = Patient (Back), Unchecked = Doctor (Front) */}
                    <input
                        type="checkbox"
                        className="toggle"
                        checked={isChecked}
                        onChange={(e) => setIsChecked(e.target.checked)}
                    />
                    <span className="slider"></span>
                    <span className="card-side"></span>

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
                            <span className="helper-link">
                                Tech Support? <a href="#">Contact Admin</a>
                            </span>
                        </div>

                        {/* BACK: PATIENT LOGIN */}
                        <div className="flip-card__back">
                            <div className="logo-container">
                                <svg className="w-10 h-10 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                                </svg>
                            </div>
                            <div className="title">Patient Login</div>
                            <form className="flip-card__form" onSubmit={handlePatientLogin}>
                                <input
                                    className="flip-card__input"
                                    name="email"
                                    placeholder="Your Email"
                                    type="email"
                                    value={patientEmail}
                                    onChange={(e) => setPatientEmail(e.target.value)}
                                    required
                                />
                                <input
                                    className="flip-card__input"
                                    name="password"
                                    placeholder="Password"
                                    type="password"
                                    value={patientPassword}
                                    onChange={(e) => setPatientPassword(e.target.value)}
                                    required
                                />
                                {patientError && <p className="error-message">{patientError}</p>}
                                <button className="flip-card__btn">Log in</button>
                            </form>
                            <span className="helper-link">
                                New Patient? <a href="/sign-up">Create Account</a>
                            </span>
                        </div>
                    </div>
                </label>
            </div>
        </div>
    );
};

export default UnifiedLoginPage;
