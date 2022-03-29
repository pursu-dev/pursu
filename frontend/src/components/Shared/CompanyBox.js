import React, { useState, useEffect } from 'react';
import { Typography, Box, makeStyles } from '@material-ui/core';
import { isMobile } from 'react-device-detect';
import fallback from '../../images/Pursu_Truena_Small.png';

const useStyles = makeStyles({
  logoAndName: {
    display: 'flex',
    alignItems: 'center',
  },
  logo: {
    width: '63px',
    height: '63px',
    marginLeft: '15px',
  },
  title: {
    fontSize: '18px',
    fontFamily: 'Poppins',
    fontWeight: 500,
    marginLeft: '24px',
  },
  location: {
    fontSize: '14px',
    fontFamily: 'Poppins',
    fontWeight: 300,
    marginLeft: '24px',
    color: 'grey',
  },
  box: {
    borderRadius: '5px',
    width: isMobile ? '130%' : '80%',
    height: '86px',
    backgroundColor: '#E9E9E9',
    justifyItems: 'center',
    alignItems: 'center',
    display: 'flex',
    marginBottom: '10px',
  },
  text: {
    flexDirection: 'column',
  },
});

export default function CompanyBox(props) {
  const classes = useStyles();
  const [logo, setLogo] = useState(
    !!props.similarCompanyLogo ? props.similarCompanyLogo : ''
  );

  useEffect(() => {
    if (
      process.env.REACT_APP_DEVELOPMENT_MODE === 'true' &&
      !!props.similarCompanyName
    ) {
      const title = props.similarCompanyName.replace(/[^0-9a-zA-Z]/g, '');
      setLogo('https://logo.clearbit.com/' + title + '.com');
    }
  }, []);

  return (
    <Box className={classes.box}>
      <img
        className={classes.logo}
        src={!!logo ? logo : fallback}
        onError={e => {
          setLogo(fallback);
        }}
      />
      <Box className={classes.text}>
        <Typography className={classes.title}>
          {!!props.similarCompanyName ? props.similarCompanyName : 'Company'}
        </Typography>
        <Typography className={classes.location}>
          {!!props.similarCompanySector ? props.similarCompanySector : 'Sector'}
        </Typography>
      </Box>
    </Box>
  );
}
