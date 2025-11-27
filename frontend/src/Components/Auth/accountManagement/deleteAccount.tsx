import React, { useState } from 'react';
import './deleteAccount.css';

const DeleteAccount: React.FC = () => {
    const [isConfirming, setIsConfirming] = useState(false);
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleDeleteClick = () => {
        setIsConfirming(true);
    };

    const handleCancel = () => {
        setIsConfirming(false);
        setPassword('');
        setError('');
    };

    const handleConfirmDelete = async () => {
        if (!password.trim()) {
            setError('Password is required');
            return;
        }

        setLoading(true);
        try {
            const response = await fetch('/api/auth/delete-account', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password }),
            });

            if (!response.ok) {
                throw new Error('Failed to delete account');
            }

            // Redirect to login or home page
            window.location.href = '/login';
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="delete-account-container">
            <h2>Delete Account</h2>
            
            {!isConfirming ? (
                <div>
                    <p>This action cannot be undone. All your data will be permanently deleted.</p>
                    <button onClick={handleDeleteClick} className="btn-danger">
                        Delete My Account
                    </button>
                </div>
            ) : (
                <div className="confirmation-form">
                    <p>Enter your password to confirm account deletion:</p>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Enter your password"
                        disabled={loading}
                    />
                    {error && <p className="error">{error}</p>}
                    
                    <div className="button-group">
                        <button 
                            onClick={handleConfirmDelete} 
                            className="btn-danger"
                            disabled={loading}
                        >
                            {loading ? 'Deleting...' : 'Confirm Delete'}
                        </button>
                        <button 
                            onClick={handleCancel} 
                            className="btn-secondary"
                            disabled={loading}
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default DeleteAccount;