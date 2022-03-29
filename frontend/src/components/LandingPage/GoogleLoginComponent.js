import React, { useEffect } from 'react';
import GoogleLogin from 'react-google-login';

export default function GoogleLoginComponent(props) {
  return (
    <GoogleLogin
      clientId={props.clientID}
      fetchBasicProfile={false}
      render={renderProps => (
        <button
          class="button button1"
          background="#008CBA"
          onClick={() => renderProps.onClick()}
          disabled={renderProps.disabled}
        >
          {props.message}
        </button>
      )}
      autoLoad={true}
      buttonText="Login"
      onSuccess={props.func}
      onFailure={props.failure}
      scope={
        'profile email https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.labels https://www.googleapis.com/auth/gmail.settings.basic'
      }
      cookiePolicy={'single_host_origin'}
      accessType={'offline'}
      responseType={'code'}
      className="loginBtn loginBtn--google"
    />
  );
}
