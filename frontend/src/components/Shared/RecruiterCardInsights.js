import React, { useEffect } from 'react';
import {
  Typography,
  Tooltip,
  Button,
  Box,
  makeStyles,
} from '@material-ui/core';
import LockIcon from '@material-ui/icons/Lock';

const useStyles = makeStyles({
  flexTest: {
    display: 'flex',
    alignItems: 'start',
    flexDirection: 'row',
    gap: '30px 20px',
  },
  recruiterCard: {
    display: 'flex',
    alignItems: 'start',
    flexDirection: 'column',
  },
  yourRecruiter: {
    fontSize: '16px',
    fontFamily: 'Poppins',
    fontWeight: 600,
  },
  recruiterName: {
    fontSize: '15px',
    fontFamily: 'Poppins',
    fontWeight: 400,
  },
  recruiterEmail: {
    fontSize: '15px',
    fontFamily: 'Poppins',
    fontWeight: 400,
    opacity: '35%',
  },
  circle: {
    width: '70px',
    height: '70px',
    lineHeight: '70px',
    borderRadius: '50%',
    fontFamily: 'Poppins',
    fontSize: '35px',
    textAlign: 'center',
    color: 'white',
    backgroundColor: '#B49BD4',
  },
  redeemButton: {
    backgroundColor: '#21A0DF',
    color: '#FFFFFF',
    fontFamily: 'Poppins',
    fontWeight: 400,
    fontSize: '18px',
    textTransform: 'none',
  },
  lockIcon: {
    marginRight: '10px',
  },
});

const getUppercaseLetters = recruiterName => {
  if (!!recruiterName) {
    return recruiterName
      .split(' ')
      .map(c => c.charAt(0))
      .join('')
      .toUpperCase(); //Uppercase each letter
  }
  return '??';
};

export default function RecruiterCardInformation(props) {
  const classes = useStyles();

  const [displayRecruiterName, setDisplayRecruiterName] = React.useState();
  const [displayRecruiterEmail, setDisplayRecruiterEmail] = React.useState();
  const [recruiterExists, setRecruiterExists] = React.useState(
    !!props.redeemedRecruiterInfo && props.redeemedRecruiterInfo.length > 0
  );

  const getDisplayAvailablePoints = () => {
    return props.isRecruiterAvailable
      ? 'Your total points: ' + (!props.isDemo ? props.redemptionPoints : 0)
      : 'Come Back Later For Updates!';
  };

  const [displayAvailablePoints, setDisplayAvailablePoints] = React.useState(
    getDisplayAvailablePoints()
  );

  useEffect(() => {
    if (
      !!props.redeemedRecruiterInfo &&
      props.redeemedRecruiterInfo.length > 0
    ) {
      setRecruiterExists(true);
      setDisplayRecruiterName(props.redeemedRecruiterInfo[0][0]);
      setDisplayRecruiterEmail(props.redeemedRecruiterInfo[0][1]);
    }
  }, [props.redeemedRecruiterInfo]);

  useEffect(() => {
    setDisplayAvailablePoints(getDisplayAvailablePoints());
  }, [props.isRecruiterAvailable]);

  const redeemRecruiter = (token, cid) => {
    let backendData = {
      token,
      cid,
    };

    fetch(process.env.REACT_APP_REDEEM_RECRUITER, {
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
        setRecruiterExists(true);
        setDisplayRecruiterName(data.name);
        setDisplayRecruiterEmail(data.email);
        props.setRedeemedRecruiterInfo([[data.name, data.email]]);
        props.setRedemptionPoints(props.redemptionPoints - 1);
        setDisplayAvailablePoints(getDisplayAvailablePoints());
      });
  };

  const displayRecruiterAvailable = props.isRecruiterAvailable ? (
    <Tooltip
      title={
        !props.redemptionPoints ? (
          <h1 style={{ fontSize: '16px', lineHeight: '20px' }}>
            Get more points by referring your friends! Click the{' '}
            <strong>COPY REFERRAL LINK</strong> button in the navigation bar to
            copy your referral link!
          </h1>
        ) : (
          ''
        )
      }
      arrow
    >
      <span>
        <Button
          disabled={!props.redemptionPoints}
          onClick={() => redeemRecruiter(props.token, props.card.cid)}
          className={classes.redeemButton}
        >
          {' '}
          <LockIcon className={classes.lockIcon} /> Unlock (1 pt){' '}
        </Button>
      </span>
    </Tooltip>
  ) : (
    'Currently Not Available'
  );
  return (
    <Box className={props.classes.recruiterCard}>
      <Box className={classes.flexTest}>
        <Box className={classes.circle}>
          {getUppercaseLetters(displayRecruiterName)}
        </Box>
        <Box className={classes.recruiterCard}>
          <Typography className={classes.yourRecruiter}>
            Redeemed Recruiter
          </Typography>
          <Typography className={classes.recruiterName}>
            {recruiterExists ? displayRecruiterName : displayRecruiterAvailable}
          </Typography>
          <Typography className={classes.recruiterEmail}>
            {recruiterExists ? displayRecruiterEmail : displayAvailablePoints}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}
