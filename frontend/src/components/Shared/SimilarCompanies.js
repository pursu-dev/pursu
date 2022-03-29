import React, { useState, useEffect } from 'react';
import { Typography, Box, makeStyles } from '@material-ui/core';
import CompanyBox from './CompanyBox';
import Fade from '@material-ui/core/Collapse';

const useStyles = makeStyles({
  title: {
    fontSize: '24px',
    fontFamily: 'Poppins',
    fontWeight: 500,
    marginBottom: '10px',
  },
  box: {
    borderRadius: '5px',
    width: '100%',
    height: '10%',
    backgroundColor: 'white',
    alignItems: 'center',
    marginBottom: '24px',
  },
});

export default function SimilarCompanies(props) {
  const classes = useStyles();
  const [animate, setAnimate] = useState(false);

  useEffect(() => {
    setTimeout(() => {
      setAnimate(true);
    }, 250);
  }, [props]);

  return (
    <Box className={props.classes.similarCompanies}>
      <Typography variant="h5" className={classes.title}>
        Similar Companies
      </Typography>
      {!props.isDemo ? (
        <Box className={classes.box}>
          {!!props.similarCompanies &&
            props.similarCompanies.map((company, i) => (
              <Fade in={animate}>
                <CompanyBox
                  {...props}
                  key={i}
                  similarCompanyName={company[0]}
                  similarCompanySector={company[1]}
                  similarCompanyLogo={company[2]}
                />
              </Fade>
            ))}
        </Box>
      ) : (
        <Box className={classes.box}>
          <Fade in={animate}>
            <CompanyBox
              {...props}
              key={1}
              similarCompanyName={'Slack'}
              similarCompanySector={'Communication'}
              similarCompanyLogo={'https://logo.clearbit.com/slack.com'}
            />
            <CompanyBox
              {...props}
              key={2}
              similarCompanyName={'Facebook'}
              similarCompanySector={'Communication'}
              similarCompanyLogo={'https://logo.clearbit.com/facebook.com'}
            />
            <CompanyBox
              {...props}
              key={3}
              similarCompanyName={'Redfin'}
              similarCompanySector={'Housing'}
              similarCompanyLogo={'https://logo.clearbit.com/redfin.com'}
            />
          </Fade>
        </Box>
      )}
    </Box>
  );
}
