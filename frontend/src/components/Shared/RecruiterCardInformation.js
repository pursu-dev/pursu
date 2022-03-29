import React, { useEffect } from 'react';
import { Typography, Button, Box, makeStyles } from '@material-ui/core';

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

export default function RecruiterCard(props) {
  const classes = useStyles();

  return (
    <Box className={props.classes.recruiterCard}>
      <Box className={classes.flexTest}>
        <Box className={classes.circle}>
          {getUppercaseLetters(props.card.recruiterName)}
        </Box>
        <Box className={classes.recruiterCard}>
          <Typography className={classes.yourRecruiter}>
            Your Recruiter
          </Typography>
          <Typography className={classes.recruiterName}>
            {!!props.card.recruiterName
              ? props.card.recruiterName
              : 'Currently Not Available'}
          </Typography>
          <Typography className={classes.recruiterEmail}>
            {!!props.card.recruiterEmail
              ? props.card.recruiterEmail
              : 'Come Back Later For Updates!'}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}
