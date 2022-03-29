export const pipToIndex = {
  login_time: 0,
  pid: 1,
  cid: 2,
  timestamp: 3,
  stage: 4,
  recruiter_name: 5,
  recruiter_email: 6,
  challenge_link: 7,
  notes: 8,
  deadline: 9,
  active: 10,
  company_name: 11,
  user_email: 12,
  user_uid: 13,
};

// piptoindex for userinfo as well

export const lookupStage = {
  0: 'APPLICATION', // 2863ff
  1: 'REFERRAL', //bf00ff
  2: 'CODING CHALLENGE', //
  3: 'INTERVIEW', //fb6240
  5: 'OFFER', //2ece89
  6: 'REJECTION', //f62d51
};

// takes a query_name, user_token, and sets the data in the appropriate setState hook
export const getQuery = (query_name, token, setState, cid) => {
  let backendData = {
    query_name,
    token,
    cid,
  };

  fetch(process.env.REACT_APP_QUERIES, {
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
      setState(data);
    });
};

// takes a query_name, user_token, and sets the data in the appropriate setState hook
export const getInsightsQuery = (url, token, cid, setState) => {
  let backendData = {
    token,
    cid,
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
    .then(data => {
      setState(data);
    });
};
