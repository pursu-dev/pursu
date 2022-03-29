import React from 'react';
import { makeStyles, Typography, Box, TextField } from '@material-ui/core';
import GoogleLoginComponent from './GoogleLoginComponent';

const useStyles = makeStyles(theme => ({
  box: {
    borderRadius: '20px',
    padding: '10px 50px 10px 50px',
    backgroundColor: 'white',
    display: 'flex',
    flexDirection: 'column',
    alignContent: 'center',
    justifyContent: 'center',
    alignItems: 'center',
  },
  text: {
    marginTop: '9px',
    marginBottom: '9px',
  },
  validateButton: {
    border: 'solid',
    color: '#5012cc',
    backgroundColor: 'white',
    padding: '10px 24px',
    textAlign: 'center',
    textDecoration: 'none',
    display: 'inline-block',
    fontSize: '20px',
    fontWeight: 'bold',
    justifyContent: 'center',
    verticalAlign: 'middle',
    margin: '4px 2px',
    paddingTop: '10px',
    cursor: 'pointer',
  },
}));

export default function LoginPopup(props) {
  const classes = useStyles();
  const [inputEmail, setInputEmail] = React.useState('');
  const [clientID, setClientID] = React.useState('');
  const [attemptedEmail, setAttemptedEmail] = React.useState(false);
  const emailRegex = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

  const getClientID = () => {
    if (!emailRegex.test(inputEmail)) {
      setAttemptedEmail(true);
      return;
    }
    const url = process.env.REACT_APP_GET_GOOGLE_CLIENT_ID;
    let backendData = {
      email: inputEmail,
    };
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
      .then(results => {
        setClientID(results.client_id);
        props.setClientID(results.client_id);
      });
  };

  return (
    <Box className={classes.box}>
      {props.displayGreeting && (
        <Typography variant="h6">Welcome to Pursu!</Typography>
      )}
      <TextField
        label="Email"
        className={classes.text}
        variant="filled"
        placeholder="Enter your email"
        onChange={e => setInputEmail(e.target.value)}
        value={inputEmail}
        error={attemptedEmail && !emailRegex.test(inputEmail)}
        helperText={
          attemptedEmail && !emailRegex.test(inputEmail)
            ? 'Please enter a valid email'
            : ''
        }
        onKeyPress={e => {
          if (e.key === 'Enter') getClientID();
        }}
      />
      {!!clientID ? (
        <GoogleLoginComponent {...props} clientID={clientID} />
      ) : (
        <button className={classes.validateButton} onClick={getClientID}>
          Continue
        </button>
      )}
    </Box>
  );
}
