import React from 'react';
import { useNavigate } from 'react-router-dom';


const LogoutBar = () => {
    const navigate = useNavigate();

    const handleLogout = async () => {
        console.log('logging out...')
        
        const response = await fetch('/logout', {
            method: 'POST',
            credentials: "include",
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'message': 'user logged out' })
          });
        
        console.log(response.status)

        var cookies = document.cookie.split(";");

        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i];
            var eqPos = cookie.indexOf("=");
            var name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
            document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
        }
        navigate('/');
    };
    

    return (
        <div className="logout-bar">
            <button className="logout-button" onClick={handleLogout}>
                Logout
            </button>
        </div>
    );
}

export default LogoutBar;
