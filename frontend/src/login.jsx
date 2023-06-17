import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';


function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    document.title = 'Home'
  }, [])

  const handleSubmit = async event => {
    event.preventDefault();
    const regex = /^[a-z0-9\-]+$/i; // allows only alphanumeric and hyphen characters

    if (!regex.test(username) || !regex.test(password)) {
      setErrorMessage("Only alphanumeric characters and hyphens are allowed.");
      return;
    }

    const route = isLogin ? "/login" : "/signup";
    const response = await fetch(route, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    if (response.ok) {
      navigate('/content');
    } else {
      setErrorMessage(data.message || "An error occurred.");
    }
  };

  const switchMode = () => setIsLogin(!isLogin);

  return (
    <div className="LoginPage">
      <h2>{isLogin ? "Login" : "Sign Up"}</h2>
      {errorMessage && <p className="errorMessage">{errorMessage}</p>}
      <form onSubmit={handleSubmit}>
        <input type="text" placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} required/>
        <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required/>
        <input type="submit" value={isLogin ? "Login" : "Sign Up"} />
      </form>
      <button onClick={switchMode}>{isLogin ? "Switch to Sign Up" : "Switch to Login"}</button>
    </div>
  );
}

export default LoginPage;
