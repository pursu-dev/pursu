import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Box, Typography } from '@material-ui/core';
import CodeIcon from '@material-ui/icons/Code';

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
  logo: {
    width: '63px',
    height: '63px',
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
  greenBox: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '160px',
    height: '35px',
    backgroundColor: '#44CB51',
    marginTop: '10px',
    borderRadius: '2px',
  },
  greyBox: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '160px',
    height: '35px',
    backgroundColor: 'grey',
    marginTop: '10px',
    borderRadius: '2px',
  },
  startButtonText: {
    fontSize: '15px',
    fontFamily: 'Poppins',
    color: 'white',
    fontWeight: 500,
  },
});

const websiteConversion = {
  'hackerrank.com': 'Hackerrank',
  'app.codility.com': 'Codility',
  'codevue.com': 'CodeVue',
  'app.codesignal.com': 'CodeSignal',
  'app.coderpad.io': 'Coderpad',
};

export default function CodingChallengeCard(props) {
  const classes = useStyles();

  const websiteConverter = () => {
    if (!props.card.link) {
      return '';
    }
    const splitted = props.card.link.split('/');
    if (splitted[2] in websiteConversion) {
      return websiteConversion[splitted[2]];
    }
    return '';
  };

  return (
    <Box className={props.classes.codingChallengeCard}>
      <Box className={classes.flexTest}>
        <Box className={classes.circle}>
          <CodeIcon />
        </Box>
        <Box className={classes.recruiterCard}>
          <Typography className={classes.yourRecruiter}>
            Coding Challenge
          </Typography>
          <a href={props.card.link} target="_blank">
            <Box
              className={!!props.card.link ? classes.greenBox : classes.greyBox}
            >
              <Typography className={classes.startButtonText}>
                {!!props.card.link ? 'Start ' + websiteConverter() : 'N/A'}
              </Typography>
            </Box>
          </a>
        </Box>
      </Box>
    </Box>
  );
}
