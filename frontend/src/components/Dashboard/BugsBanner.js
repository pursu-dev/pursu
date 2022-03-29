import React, { useState, useEffect } from 'react';
import { Alert, AlertTitle } from '@material-ui/lab';
import { Button } from '@material-ui/core';
import { PropTypes } from 'prop-types';

export default function BugsBanner(props) {
  const [bugs, setBugs] = useState([]);

  useEffect(() => {
    getBugs();
  }, []);

  const getBugs = () => {
    const url = process.env.REACT_APP_QUERIES;
    const body = {
      query_name: 'bugs',
      token: props.token,
    };
    fetch(url, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
      .then(response => {
        return response.json();
      })
      .then(data => {
        setBugs(data);
      });
  };

  const clearBanner = bug => {
    setBugs(bugs.filter(item => item !== bug));
  };

  return (
    <div>
      {bugs &&
        bugs.map((bug, index) => (
          <div key={index}>
            <Alert
              severity="info"
              action={
                <Button
                  color="inherit"
                  size="small"
                  onClick={() => clearBanner(bug)}
                >
                  CLOSE
                </Button>
              }
            >
              <AlertTitle>Bug Alert</AlertTitle>
              {bug[0]}
            </Alert>
          </div>
        ))}
    </div>
  );
}

BugsBanner.propTypes = {
  token: PropTypes.string.isRequired,
};
