import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Box, Typography } from '@material-ui/core';
import useAnimateNumber from 'use-animate-number';

const useStyles = makeStyles({
  number: {
    fontFamily: 'Poppins',
    fontWeight: '600',
    marginRight: '24px',
  },
  text: {
    fontFamily: 'Poppins',
    fontWeight: 400,
    fontSize: '20px',
  },
  restrict: {
    width: '90%',
    display: 'flex',
    alignItems: 'center',
  },
});

export default function NextStageTime(props) {
  const classes = useStyles();
  const options = {
    duration: 1500,
    enterance: true,
    direct: false,
    disabled: false,
    decimals: 0,
  };
  const [daysToNextStage, setDaysToNextStage] = useAnimateNumber(0, options);
  const [displayText, setDisplayText] = useState('');
  const [isFinished, setIsFinished] = useState('');

  const getNextStageData = (laneID, insightsData) => {
    // if no laneId
    // default: time to move to interview
    if (!laneID) {
      laneID = '2';
    }

    const ID = laneID.substr(-1);

    const sorted = [...insightsData].sort((left, right) => {
      if (left[0] < right[0]) {
        return -1;
      }
      if (left[0] > right[0]) {
        return 1;
      }
      return 0;
    });

    const insightsTimes = [-1, -1, -1, -1, -1, -1];

    for (let i = 0; i < sorted.length; i++) {
      if (sorted[i][0] == i) {
        insightsTimes[i] = sorted[i][1];
      }
    }

    if (!!laneID) {
      if (ID === '0') {
        // application
        setDisplayText('Days on average to move forward from application');
        return insightsTimes[0];
      } else if (ID === '1') {
        // referral
        setDisplayText('Days on average to move forward from referral');
        return insightsTimes[1];
      } else if (ID === '2') {
        // Coding Challenge
        setDisplayText('Days on average to move to an interview');
        return insightsTimes[2];
      } else if (ID === '3') {
        // Interview
        setDisplayText('Days on average to hear back after your interview');
        return insightsTimes[3];
      } else if (ID === '5') {
        // Offer
        setDisplayText('Congratulations on your offer!');
        return -2;
      } else if (ID === '6') {
        setDisplayText("Don't give up -- try again next cycle!");
        return -3;
      }
    }
  };

  useEffect(() => {
    if (props.isDemo) {
      setIsFinished(true);
      setDisplayText('Pursu will display estimated time to next stage');
      setDaysToNextStage(30);
      return;
    }
    if (!!props.insightsData) {
      const stageTime = getNextStageData(props.card.laneId, props.insightsData);

      let ID;
      if (!!props.card.laneId) {
        ID = props.card.laneId.substr(-1);
      } else {
        ID = '2';
      }
      setIsFinished(parseInt(ID) < 5 && stageTime !== -1);
      if (stageTime === -1) {
        setDisplayText(
          'Pursu is currently collecting data for this company/stage combination'
        );
      } else {
        setTimeout(() => {
          setDaysToNextStage(stageTime);
        }, 250);
      }
    }
  }, [props.insightsData]);

  return (
    <Box className={props.classes.nextStage}>
      <div className={classes.restrict}>
        <Typography display="inline" className={classes.number} variant="h2">
          {isFinished && daysToNextStage}
        </Typography>
        <Typography display="inline" className={classes.text} variant="body1">
          {displayText}
        </Typography>
      </div>
    </Box>
  );
}
//
