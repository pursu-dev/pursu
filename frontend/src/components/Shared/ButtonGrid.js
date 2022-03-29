import React, { useEffect } from 'react';
import { makeStyles, Box, Button } from '@material-ui/core';

const useStyles = makeStyles({
  activeButton: {
    backgroundColor: '#B49BD4',
    color: 'white',
  },
  inactiveButton: {
    backgroundColor: 'white',
    color: '#B49BD4',
  },
});

export default function ButtonGrid(props) {
  const classes = useStyles();

  return (
    <Box className={props.classes.buttonGrid}>
      <Button
        disabled={!props.isPipeline}
        className={
          props.isInsight ? classes.inactiveButton : classes.activeButton
        }
        variant="contained"
        onClick={() => props.setInsight(false)}
      >
        Information
      </Button>
      <Button
        disabled={props.logo === -1}
        className={
          props.isInsight ? classes.activeButton : classes.inactiveButton
        }
        variant="contained"
        onClick={() => props.setInsight(true)}
      >
        Insights
      </Button>
    </Box>
  );
}
