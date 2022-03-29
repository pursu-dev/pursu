import React, { useEffect } from 'react';
import { makeStyles, Modal, Box } from '@material-ui/core';
import { isMobile } from 'react-device-detect';
import CloseIcon from '@material-ui/icons/Close';
import CodingChallengeCard from './CodingChallengeCard';
import NotesCard from './NotesCard';
import NextStageTime from './NextStageTime';
import LogoName from './LogoName';
import RecruiterCardInformation from './RecruiterCardInformation';
import RecruiterCardInsights from './RecruiterCardInsights';
import InsightsGraph from './InsightsGraph';
import SimilarCompanies from './SimilarCompanies';
import ButtonGrid from './ButtonGrid';
import { getQuery, getInsightsQuery } from '../../helpers/utils';

const useStyles = makeStyles({
  root: {
    flexGrow: 1,
    minHeight: 500,
  },
  limit: {
    width: '500px',
  },
  paper: {
    borderRadius: '25px',
  },
  modal: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  closeButton: {
    gridColumnStart: 'second-col',
    gridColumnEnd: 'second-col',
    gridRowStart: 'zero-row',
    gridRowEnd: 'zero-row',
    alignSelf: isMobile ? 'flex-end' : 'center',
    margin: isMobile ? '5px' : '0px',
    justifySelf: 'center',
  },
  box: {
    borderRadius: '20px',
    width: '55rem',
    height: '38rem',
    // width: '950px', keeping these here in case we need to revert to previous versions for some reason
    // height: '700px',
    backgroundColor: 'white',
    display: 'grid',
    gridTemplateColumns: '[zero-col] 47.5% [first-col] 47.5% [second-col] 5%',
    gridTemplateRows:
      '[zero-row] 5% [first-row] 20% [second-row] 20% [third-row] 55%',
    alignItems: 'center',
    outline: 0,
  },
  mobileBox: {
    width: '100%',
    height: '100%',
    backgroundColor: 'white',
    display: 'flex',
    alignItems: 'center',
    flexDirection: 'column',
    rowGap: '40px',
    overflowY: 'auto',
  },
  logoAndName: {
    gridColumnStart: 'zero-col',
    gridColumnEnd: 'zero-col',
    gridRowStart: 'first-row',
    gridRowEnd: 'second-row',
    justifySelf: 'start',
    marginLeft: '40px',
  },
  buttonGrid: {
    gridColumnStart: 'first-col',
    gridColumnEnd: 'first-col',
    gridRowStart: 'first-row',
    gridRowEnd: 'second-row',
    justifySelf: 'end',
  },
  nextStage: {
    gridColumnStart: 'zero-col',
    gridColumnEnd: 'zero-col',
    gridRowStart: 'second-row',
    gridRowEnd: 'third-row',
    marginLeft: '40px',
  },
  codingChallengeCard: {
    gridColumnStart: 'zero-col',
    gridColumnEnd: 'zero-col',
    gridRowStart: 'second-row',
    gridRowEnd: 'third-row',
    marginLeft: isMobile ? '-70px' : '40px',
  },
  horizontalLine: {
    borderTop: '1px solid #000000',
    opacity: '10%',
    gridColumnStart: 'zero-col',
    gridColumnEnd: 'none',
    gridRowStart: 'second-row',
    gridRowEnd: 'third-row',
    alignSelf: 'end',
    justifySelf: 'center',
    width: isMobile ? '100%' : '92%',
  },
  recruiterCard: {
    gridColumnStart: 'first-col',
    gridColumnEnd: 'first-col',
    gridRowStart: 'second-row',
    gridRowEnd: 'third-row',
    justifySelf: 'center',
  },
  insightsGraph: {
    gridColumnStart: 'first-col',
    gridColumnEnd: 'first-col',
    gridRowStart: 'third-row',
    gridRowEnd: 'end',
    justifySelf: 'center',
    marginBottom: '25px',
  },
  similarCompanies: {
    gridColumnStart: 'zero-col',
    gridColumnEnd: 'zero-col',
    gridRowStart: 'third-row',
    gridRowEnd: 'fourth-row',
    marginBottom: '10px',
    marginLeft: isMobile ? '-80px' : '40px',
  },
  notesCard: {
    gridColumnStart: 'zero-col',
    gridColumnEnd: 'second-col',
    gridRowStart: 'third-row',
    gridRowEnd: 'end',
    justifySelf: 'stretch',
    alignSelf: 'stretch',
    marginLeft: '40px',
    marginTop: '10px',
  },
});

export default function CompanyModal(props) {
  const classes = useStyles();

  // button
  const [isInsight, setInsight] = React.useState(props.page === 'insights');

  // recruiter redemption
  const [isRecruiterAvailable, setIsRecruiterAvailable] = React.useState();
  const [redeemedRecruiterInfo, setRedeemedRecruiterInfo] = React.useState();

  // insights
  const [insightsData, setInsightsData] = React.useState();
  const [similarCompanies, setSimilarCompanies] = React.useState();

  useEffect(() => {
    if (!!props.card && !props.isDemo) {
      getInsightsQuery(
        process.env.REACT_APP_GET_STAGE_INSIGHTS,
        props.token,
        props.card.cid,
        setInsightsData
      );
      getInsightsQuery(
        process.env.REACT_APP_GET_REDEEMED_RECRUITER_DATA,
        props.token,
        props.card.cid,
        setIsRecruiterAvailable
      ); // is any recruiter available to redeem?
      getQuery(
        'redeemed_recruiters',
        props.token,
        setRedeemedRecruiterInfo,
        props.card.cid
      ); // already redeemed recruiters
      getQuery(
        'similar_companies',
        props.token,
        setSimilarCompanies,
        props.card.cid
      );
    }
  }, [props.card]);

  // reset page to information on modal close
  useEffect(() => {
    if (!props.open) {
      setInsight(props.page === 'insights');
    }
  }, [props.open]);

  return (
    <Modal className={classes.modal} open={props.open} onClose={props.onClose}>
      <Box className={isMobile ? classes.mobileBox : classes.box}>
        <CloseIcon className={classes.closeButton} onClick={props.onClose} />
        <LogoName classes={classes} {...props} />
        {isMobile && <hr className={classes.horizontalLine} />}
        <ButtonGrid
          classes={classes}
          setInsight={setInsight}
          isInsight={isInsight}
          {...props}
        />
        {!isInsight && (
          <>
            {/* Information */}
            <RecruiterCardInformation
              classes={classes}
              {...props}
              isRecruiterAvailable={isRecruiterAvailable}
              redeemedRecruiterInfo={redeemedRecruiterInfo}
            />
            <CodingChallengeCard classes={classes} {...props} />
            <hr className={classes.horizontalLine} />
            <NotesCard classes={classes} {...props} />
          </>
        )}
        {isInsight && (!!insightsData || props.isDemo) && (
          <>
            {/* Insight */}
            <RecruiterCardInsights
              classes={classes}
              {...props}
              isRecruiterAvailable={isRecruiterAvailable}
              redeemedRecruiterInfo={redeemedRecruiterInfo}
              setRedeemedRecruiterInfo={setRedeemedRecruiterInfo}
            />
            <NextStageTime
              classes={classes}
              {...props}
              insightsData={insightsData}
            />
            <InsightsGraph
              classes={classes}
              insightsData={insightsData}
              {...props}
            />
            <SimilarCompanies
              classes={classes}
              {...props}
              similarCompanies={similarCompanies}
            />
          </>
        )}
      </Box>
    </Modal>
  );
}
