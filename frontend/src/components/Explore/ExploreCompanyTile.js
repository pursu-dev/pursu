import React from 'react';
import ReactGA from 'react-ga';
import CompanyModal from '../Shared/CompanyModal';
import fallback from '../../images/Pursu_Truena_Small.png';
import {
  makeStyles,
  Card,
  CardActionArea,
  CardContent,
  CardMedia,
  Typography,
  Grow,
  Button,
} from '@material-ui/core';
import moment from 'moment';
import Divider from '@material-ui/core/Divider';
import Grid from '@material-ui/core/Grid';

const emoji = require('emoji-dictionary');

const useStyles = makeStyles(theme => ({
  root: {
    display: 'inline-block',
    padding: theme.spacing(2),
    maxWidth: 500,
    width: 325,
    zIndex: 2,
    borderRadius: 3,
  },
  companyLogo: {
    objectFit: 'fill',
    width: 100,
    height: 100,
    marginTop: 15,
  },
  companyContainer: {
    display: 'flex',
    justifyContent: 'center',
  },
  minimum: {
    minHeight: 200,
  },
  wrap: {
    backgroundColor: '#ffffff',
  },
  companyPosition: {
    color: '#000000',
    fontWeight: 'bold',
    fontSize: props => (props.companyName.length >= 16 ? 12 : 14),
    height: '60px',
    wordWrap: 'break-word',
    paddingTop: '15px',
    fontFamily: 'Lato',
  },
  companyTitle: {
    color: 'rgba(0, 0, 0, .4)',
    // fontSize: props => (props.companyName.length >= 16 ? 15 : 20),
    fontSize: 14,
    height: '20px',
    wordWrap: 'break-word',
    paddingBottom: '10px',
    fontFamily: 'Lato',
  },
  companyLocation: {
    color: 'rgba(0, 0, 0, .4)',
    // fontSize: props => (props.companyName.length >= 16 ? 15 : 20),
    fontSize: 14,
    height: '35px',
    wordWrap: 'break-word',
    paddingBottom: '10px',
    fontFamily: 'Lato',
  },
  posted: {
    float: 'right',
    color: 'rgba(0, 0, 0, .4)',
    fontSize: 12,
    marginTop: '3vh',
    fontFamily: 'Lato',
  },
  info: {
    float: 'left',
  },
  applyButton: {
    backgroundColor: '#61289A',
    color: '#FFFFFF',
    textTransform: 'capitalize',
    width: '100%',
    fontFamily: 'Lato',
  },
  insightsButton: {
    backgroundColor: 'white',
    borderStyle: 'solid',
    borderColor: '#61289A',
    color: '#61289A',
    textTransform: 'capitalize',
    width: '100%',
    fontFamily: 'Lato',
  },
  bottomCard: {
    paddingTop: '15px',
    paddingBottom: '10px',
  },
  divider: {
    marginTop: '65px',
  },
}));

export default function CompanyTile(props) {
  const [companyModal, setCompanyModal] = React.useState(false);
  const [modalOpenTime, setModalOpenTime] = React.useState(null);
  const handleCompanyModalOpen = () => {
    props.handleCompanyModalOpen(props.card, props.cid);
    setCompanyModal(true);
    setModalOpenTime(moment());
  };

  const handleCompanyModalClose = () => {
    const time_diff = moment().diff(modalOpenTime, 'seconds');
    ReactGA.event({
      category: 'Company Modal',
      action: 'Viewed',
      label: props.cid,
      value: time_diff,
    });
    setCompanyModal(false);
  };

  const classes = useStyles(props);
  let companyName = 'default';

  // needed for dev:
  // if (props.companyName !== undefined) {
  //   companyName = props.companyName.replace(/\W/g, '');
  // }
  // if (companyName == 'Snap') {
  //   companyName = 'Snapchat';
  // }
  // let imageName = '//logo.clearbit.com/' + companyName + '.com?size=256';
  return (
    <div className={classes.root}>
      <Grow in={true} timeout={250 * ((props.index % 12) + 1)}>
        <Card raised>
          <div className={classes.companyContainer}>
            <CardMedia
              onError={e => {
                e.target.src = fallback;
              }}
              component="img"
              alt={props.companyName + ' logo'}
              image={props.logo !== null ? props.logo : fallback}
              // image={imageName} // dev
              title={props.companyName + ' logo'}
              className={classes.companyLogo}
            />
          </div>
          <CardContent className={classes.wrap}>
            <Typography
              gutterBottom
              variant="subtitle2"
              className={classes.companyPosition}
            >
              {props.companyName}{' '}
              {props.trending ? emoji.getUnicode('fire') : null}
            </Typography>
            <div>
              <div className={classes.info}>
                <Typography
                  variant="subtitle2"
                  className={classes.companyTitle}
                >
                  {props.isInternship ? 'Internship' : 'New Grad'}
                </Typography>
                <Typography
                  variant="subtitle2"
                  className={classes.companyLocation}
                >
                  {props.location}
                </Typography>
              </div>
              <p className={classes.posted}>
                {props.timePosted ? moment(props.timePosted).fromNow() : null}
              </p>
            </div>
            <Divider className={classes.divider} variant="middle" />
            <div id="textbox" className={classes.bottomCard}>
              <Grid container spacing={2}>
                {!!props.hasInsights && (
                  <Grid item xs={!!props.appLink ? 6 : 12}>
                    <Button
                      variant="outlined"
                      onClick={handleCompanyModalOpen}
                      className={classes.insightsButton}
                    >
                      Insights
                    </Button>
                  </Grid>
                )}
                {!!props.appLink && (
                  <Grid item xs={!!props.hasInsights ? 6 : 12}>
                    <Button
                      className={classes.applyButton}
                      href={props.appLink}
                      target="_blank"
                    >
                      Apply
                    </Button>
                  </Grid>
                )}
              </Grid>
            </div>
          </CardContent>
        </Card>
      </Grow>

      {/* <CompanyModal
        userInfo={props.userInfo}
        open={companyModal}
        onClose={handleCompanyModalClose}
        cid={props.cid}
        companyName={companyName}
        token={props.token}
        card={props.card}
      /> */}
    </div>
  );
}
