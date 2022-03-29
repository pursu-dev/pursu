import React from 'react';
import tw from 'twin.macro';
import LeftExploreImage from '../../images/explore-page.png';
import { makeStyles, Typography } from '@material-ui/core';

const useStyles = makeStyles({
  containerLeftText: {
    display: 'flex',
    flexDirection: 'column',
    flexWrap: 'wrap',
    padding: '75px',
    width: '70%',
    marginTop: '30px',
  },
  containerRightText: {
    width: '30%',
    paddingTop: '55px',
    paddingBottom: '55px',
    textAlign: 'right',
    paddingRight: '55px',
    display: 'table',
  },
  textBox: {
    margin: '20px',
    marginBottom: '100px',
    display: 'table-cell',
    verticalAlign: 'middle',
    paddingRight: '20px',
  },
  textTitle: {
    fontFamily: 'Poppins',
    fontWeight: 'bold',
    marginBottom: '5px',
  },
  container: {
    display: 'flex',
    flexDirection: 'row-wrap',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    fontFamily: 'Poppins',
  },
  exploreImg: {
    maxWidth: '100%',
    maxHeight: '100%',
    objectFit: 'contain',
  },
});

const Container = tw.div`relative`;

export default () => {
  const classes = useStyles();
  return (
    <Container className={classes.container}>
      <div className={classes.containerLeftText}>
        <img className={classes.exploreImg} src={LeftExploreImage} />
      </div>
      <div className={classes.containerRightText}>
        <div className={classes.textBox}>
          <Typography variant="h6" className={classes.textTitle}>
            Customized Insights
          </Typography>
          Your personal dashboard gives you a bird’s eye view of your recruiting
          progress and deadlines with different companies.
        </div>
      </div>
    </Container>
  );
};
