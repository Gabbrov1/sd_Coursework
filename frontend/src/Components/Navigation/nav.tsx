import { useEffect, useState } from "react";
import '../../styles/navbar.scss';

type User = {
  ID: number;
  Username: string;
  isAdmin: boolean;
};

type AuthStatus = {
  logged_in: boolean;
  user?: User;
};

export default function NavBar() {
  const [authStatus, setAuthStatus] = useState<AuthStatus>({
    logged_in: false,
  });

  useEffect(() => {
    fetch("http://localhost:5000/auth/status", {
      method: "GET",
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data: AuthStatus) => {
        setAuthStatus(data);
      })
      .catch((err) => console.error("Error fetching auth status:", err));
  }, []);

  return (
    <nav className="navbar">
      <ul className="nav-logo">
        <li>
          <a href="/">Home</a>
        </li>
        <li>
          <a href="/games">Games</a>
        </li>
      </ul>

      <ul className="nav-links">
        {authStatus.logged_in ? (
          <>
            <li>
              <a href="/auth/Account">Profile | {authStatus.user?.Username}</a>
            </li>

            {authStatus.user?.isAdmin && (
              <li>
                <a href="/admin">Admin</a>
              </li>
            )}

            <li>
              <a href="/auth/logout">Logout</a>
            </li>
          </>
        ) : (
          <li>
            <a href="/auth/login">Login / Register</a>
          </li>
        )}
      </ul>
    </nav>
  );
}
