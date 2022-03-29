import React, { useState, useEffect } from 'react';
import LandingPage from '../LandingPage/LandingPage';
import UserInfo from '../UserInfo/UserInfo';
import { Redirect } from 'react-router-dom';
import { bake_cookie, read_cookie } from 'sfcookies';

function App(props) {
  let localuserStatus = {
    token:
      read_cookie('userToken').length == 0 ? null : read_cookie('userToken')[0],
    status: null,
  };

  const [userStatus, setUserStatus] = useState(localuserStatus);
  const [goToUserInfo, setGoToUserInfo] = useState(false);
  const [isReady, setIsReady] = useState(false);
  const [isBadLogin, setIsBadLogin] = useState(false);
  const [clientID, setClientID] = useState('');

  useEffect(() => {
    if (userStatus['token'] !== null) {
      checkUserData();
    }
  }, [userStatus]);

  const checkUserData = () => {
    const backendData = {
      query_name: 'user_info',
      token: userStatus['token'],
    };

    let url = process.env.REACT_APP_QUERIES;
    fetch(url, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backendData),
    })
      .then(response => {
        return response.json();
      })
      .then(data => {
        // length - 1 because points can be null
        for (let i = 0; i < data[0].length - 1; ++i) {
          if (data[0][i] === null) {
            setGoToUserInfo(true);
            break;
          }
        }
        setIsReady(true);
      });
  };

  const responseGoogleSuccess = authResult => {
    if (authResult['code']) {
      let data = {
        client_id: clientID,
        token: authResult['code'],
      };
      const url = process.env.REACT_APP_USER_CREDS;

      if (process.env.REACT_APP_DEVELOPMENT_MODE === 'true') {
        console.log('WOWZA data', data);
      }

      fetch(url, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      }).then(response => {
        if (process.env.REACT_APP_DEVELOPMENT_MODE === 'true') {
          console.log('WOWZA response', response);
        }
        const status = response.status;
        if (status === 401) {
          setIsBadLogin(true);
          return;
        } else if (status === 200 || status === 201) {
          response.json().then(res => {
            if (process.env.REACT_APP_DEVELOPMENT_MODE === 'true') {
              console.log('WOWZA res', res);
            }
            bake_cookie('userToken', [res['token'].replace(/^"|"$/g, '')]);
            const newLocalUserStatus = {
              token: res['token'],
              status: status,
            };
            setUserStatus(newLocalUserStatus);
          });
        }
      });
    }
  };

  const responseGoogleFailure = authResult => {
    if (process.env.REACT_APP_DEVELOPMENT_MODE === 'true') {
      console.log('WOWZA authresult', authResult);
    }
  };

  if ((userStatus['status'] === 201 || goToUserInfo) && isReady) {
    // new account created or UserInfo not filled out properly
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const ref = urlParams.get('ref');
    return <UserInfo token={userStatus['token']} referral={ref} />;
  } else if (userStatus['token'] !== null && isReady) {
    // userToken is available, use it to go to dashboard
    return (
      <Redirect
        push
        to={{
          pathname: '/dashboard',
          state: { userToken: userStatus['token'] },
        }}
      />
    );
  } else {
    return (
      <LandingPage
        setClientID={setClientID}
        func={responseGoogleSuccess}
        failure={responseGoogleFailure}
        alert={isBadLogin}
      />
    );
  }
}

export default App;
