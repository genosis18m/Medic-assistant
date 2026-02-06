import React, { useState } from 'react';
import { useSignIn } from '@clerk/clerk-react';
import { useNavigate, Link } from 'react-router-dom';
import './UnifiedLoginPage.css';

const UnifiedLoginPage = () => {
    // Role state: 'doctor' or 'patient'
    const [role, setRole] = useState('doctor');
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
        <div className="login-wrapper">
            <div className="login-card">
                {/* Header */}
                <div className="login-header">
                    <svg className="logo-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                            d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                    </svg>
                    <h1 className="login-title">Welcome back</h1>
                    <p className="login-subtitle">Sign in to your account</p>
                </div>

                {/* Role Tabs */}
                <div className="role-tabs">
                    <button
                        className={`role-tab ${role === 'doctor' ? 'active' : ''}`}
                        onClick={() => setRole('doctor')}
                    >
                        Doctor Portal
                    </button>
                    <button
                        className={`role-tab ${role === 'patient' ? 'active' : ''}`}
                        onClick={() => setRole('patient')}
                    >
                        Patient Login
                    </button>
                </div>

                {/* Forms */}
                {role === 'doctor' ? (
                    <form className="login-form" onSubmit={handleDoctorLogin}>
                        <div className="input-group">
                            <label className="input-label">Email Address</label>
                            <input
                                className="custom-input"
                                type="email"
                                placeholder="name@clinic.com"
                                value={doctorEmail}
                                onChange={(e) => setDoctorEmail(e.target.value)}
                                required
                            />
                        </div>
                        <div className="input-group">
                            <label className="input-label">Password</label>
                            <input
                                className="custom-input"
                                type="password"
                                placeholder="••••••••"
                                value={doctorPassword}
                                onChange={(e) => setDoctorPassword(e.target.value)}
                                required
                            />
                        </div>
                        {doctorError && <div className="error-text">{doctorError}</div>}
                        <button type="submit" className="login-btn">Sign In as Doctor</button>
                    </form>
                ) : (
                    <form className="login-form" onSubmit={handlePatientLogin}>
                        <div className="input-group">
                            <label className="input-label">Email Address</label>
                            <input
                                className="custom-input"
                                type="email"
                                placeholder="you@example.com"
                                value={patientEmail}
                                onChange={(e) => setPatientEmail(e.target.value)}
                                required
                            />
                        </div>
                        <div className="input-group">
                            <label className="input-label">Password</label>
                            <input
                                className="custom-input"
                                type="password"
                                placeholder="••••••••"
                                value={patientPassword}
                                onChange={(e) => setPatientPassword(e.target.value)}
                                required
                            />
                        </div>
                        {patientError && <div className="error-text">{patientError}</div>}
                        <button type="submit" className="login-btn">Sign In</button>
                    </form>
                )}

                {/* Footer */}
                <div className="login-footer">
                    {role === 'patient' && (
                        <div>
                            Don't have an account?{' '}
                            <Link to="/sign-up" className="footer-link">Sign up</Link>
                        </div>
                    )}
                    {role === 'doctor' && (
                        <div>
                            <span className="text-slate-500">Need help? </span>
                            <a href="#" className="footer-link">Contact IT Support</a>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default UnifiedLoginPage;
