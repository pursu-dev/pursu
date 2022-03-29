import React, { useEffect, useState } from 'react';
import { Typography, Box, makeStyles } from '@material-ui/core';
import fallback from '../../images/Pursu_Truena_Small.png';

const useStyles = makeStyles({
  logoAndNameFlex: {
    display: 'flex',
    alignItems: 'center',
  },
  logo: {
    width: '63px',
    height: '63px',
    marginRight: '20px',
  },
  companyName: {
    fontSize: '30px',
    fontFamily: 'Poppins',
    fontWeight: 500,
    marginRight: '24px',
  },
});

export default function LogoName(props) {
  const classes = useStyles();
  const [logo, setLogo] = useState(props.logo);

  useEffect(() => {
    if (process.env.REACT_APP_DEVELOPMENT_MODE === 'true') {
      const title = props.card.title.replace(/[^0-9a-zA-Z]/g, '');
      setLogo('https://logo.clearbit.com/' + title + '.com');
    }
  }, []);

  return (
    <Box className={props.classes.logoAndName}>
      <Box className={classes.logoAndNameFlex}>
        <img
          className={classes.logo}
          src={!!logo ? logo : fallback}
          onError={e => {
            setLogo(fallback);
          }}
        />
        <Typography className={classes.companyName}>
          {!!props.card.title ? props.card.title : 'Company_Name_Error'}
        </Typography>
      </Box>
    </Box>
  );
}
