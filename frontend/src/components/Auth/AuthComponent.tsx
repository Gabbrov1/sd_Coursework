import { useState } from "react";
import '../../styles/login.scss'

export default function AuthComponent() {
    const [stateRegister, setStateRegister] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault(); // always stop normal form submit
        setError(null);

        const form = e.currentTarget;

        // If we're in "Register" mode, check passwords match
        if (stateRegister) {
            const password = (form.elements.namedItem("password") as HTMLInputElement)?.value;
            const confirm = (form.elements.namedItem("confirmPassword") as HTMLInputElement)?.value;

            if (password !== confirm) {
                setError("Passwords do not match");
                return;
            }
        }

        const formData = new FormData(form);

        const url = stateRegister
            ? "http://localhost:5000/auth/register"
            : "http://localhost:5000/auth/login";

        try {
            const res = await fetch(url, {
                method: "POST",
                body: formData,
            });

            let data: any = {};
            try {
                data = await res.json();
            } catch {
            }

            if (!res.ok) {
                setError(data?.error || "Something went wrong. Please try again.");
                return;
            }

            // Success handling
            if (stateRegister) {
                window.location.href = "/auth/login";
            } else {
                window.location.href = "/";
            }

        } catch (err) {
            console.error(err);
            setError("Cannot reach server. Please try again later.");
        }
    };

    return (
        <div className="content">
            <div className="content-secondary">
                <div className="auth-nav">
                    <button type="button" onClick={() => { setStateRegister(false); setError(null); }}>
                        Sign In
                    </button>
                    <button type="button" onClick={() => { setStateRegister(true); setError(null); }}>
                        Sign Up
                    </button>
                </div>

                <div className={`auth-container ${stateRegister ? 'register' : 'login'}`}>
                    <h1>{stateRegister ? "Register" : "Login"}</h1>

                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label htmlFor="username">Username</label>
                            <input type="text" id="username" name="username" required />
                        </div>

                        <div className="form-group">
                            <label htmlFor="password">Password</label>
                            <input type="password" id="password" name="password" required />

                            {stateRegister && (
                                <>
                                    <label htmlFor="confirmPassword">Re-type Password</label>
                                    <input
                                        type="password"
                                        id="confirmPassword"
                                        name="confirmPassword"
                                        required
                                    />
                                </>
                            )}
                        </div>

                        {error && (
                            <p className="error-text">{error}</p>
                        )}

                        <button type="submit">
                            {stateRegister ? "Register" : "Sign In"}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}
