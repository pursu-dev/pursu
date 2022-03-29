import React from 'react';
import { Typography, Box, makeStyles } from '@material-ui/core';
import Stepper from '@material-ui/core/Stepper';
import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';
import StepConnector from '@material-ui/core/StepConnector';

const useStyles = makeStyles({
  logoAndName: {
    display: 'flex',
    alignItems: 'center',
  },
  logo: {
    width: '63px',
    height: '63px',
  },
  title: {
    fontSize: '28px',
    fontFamily: 'Poppins',
    fontWeight: 500,
    marginLeft: '24px',
  },
  connector: {
    // borderColor: "red" ,
    borderLeft: '1px grey dashed',
    marginTop: '8px',
  },
});

export default function CompanyStepper(props) {
  const classes = useStyles();

  return (
    <Box>
      <Typography variant="h5" className={classes.title}>
        Standard Recruiting Process for{' '}
        {!!props.companyName ? props.companyName : 'AirBnb'}
      </Typography>
      <Stepper
        orientation="vertical"
        connector={
          <StepConnector
            classes={{
              line: classes.connector,
            }}
            // classes={
            //     orientation="vertical",
            //     lineVertical={classes.connector}
            // }
          />
        }
      >
        <Step active={true}>
          <StepLabel>APPLICATION</StepLabel>
        </Step>
        <Step active={true}>
          <StepLabel>CODING CHALLENGE</StepLabel>
        </Step>
        <Step active={true}>
          <StepLabel>INTERVIEW</StepLabel>
        </Step>
        <Step active={true}>
          <StepLabel>OFFER</StepLabel>
        </Step>
      </Stepper>
    </Box>
  );
}
