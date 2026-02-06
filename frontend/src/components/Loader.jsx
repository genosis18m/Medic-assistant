import React from 'react';
import './Loader.css';

const Loader = () => {
    return (
        <div className="flex items-center justify-center min-h-[50vh] w-full">
            <div className="card">
                <div className="loader">
                    <p>loading</p>
                    <div className="words">
                        <span className="word">appointments</span>
                        <span className="word">sessions</span>
                        <span className="word">patient</span>
                        <span className="word">appointments</span>
                        <span className="word">sessions</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Loader;
