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

const useStyles = makeStyles(theme => ({
  root: {
    display: 'inline-block',
    padding: theme.spacing(2),
    maxWidth: 450,
    width: 400,
    [theme.breakpoints.down('sm')]: {
      width: 325,
    },
    zIndex: 2,
    borderRadius: 3,
  },
  companyLogo: {
    objectFit: 'fill',
    width: 50,
    height: 50,
    marginTop: 15,
    marginLeft: 10,
  },
  companyContainer: {
    display: 'flex',
    justifyContent: 'flex-start',
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
    height: '15px',
    wordWrap: 'break-word',
  },
  companyTitle: {
    color: 'rgba(0, 0, 0, .4)',
    // fontSize: props => (props.companyName.length >= 16 ? 15 : 20),
    fontSize: 14,
    height: '20px',
    wordWrap: 'break-word',
    paddingBottom: '10px',
  },
  companyLocation: {
    color: 'rgba(0, 0, 0, .4)',
    // fontSize: props => (props.companyName.length >= 16 ? 15 : 20),
    fontSize: 14,
    height: '20px',
    wordWrap: 'break-word',
    paddingBottom: '10px',
  },
  posted: {
    float: 'left',
    color: 'rgba(0, 0, 0, .4)',
    fontSize: 12,
    marginTop: '10px',
  },
  applyButton: {
    float: 'right',
    backgroundColor: '#61289A',
    color: '#FFFFFF',
    marginBottom: '20px',
    textTransform: 'capitalize',
  },
  bottomCard: {
    paddingTop: '20px',
    paddingBottom: '15px',
  },
}));

export default function CompanyTile(props) {
  const [companyModal, setCompanyModal] = React.useState(false);
  const [modalOpenTime, setModalOpenTime] = React.useState(null);
  const handleCompanyModalOpen = () => {
    setCompanyModal(true);
    setModalOpenTime(moment());
  };

  const handleCompanyModalClose = () => {
    var time_diff = moment().diff(modalOpenTime, 'seconds');
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
  // if (props.companyName !== undefined){
  //     companyName = props.companyName.replace(/\W/g, '');
  // }
  // if (companyName == "Snap") { companyName = "Snapchat" }
  // let imageName = "//logo.clearbit.com/" + companyName + ".com?size=256"
  return (
    <div className={classes.root}>
      <Grow in={true} timeout={250 * ((props.index % 12) + 1)}>
        <Card onClick={handleCompanyModalOpen}>
          <CardActionArea>
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
                Software Engineer Intern/New Grad
              </Typography>
              <Typography variant="subtitle2" className={classes.companyTitle}>
                {props.companyName}
              </Typography>
              <Typography
                variant="subtitle2"
                className={classes.companyLocation}
              >
                Location
              </Typography>
              <div id="textbox" className={classes.bottomCard}>
                <p className={classes.posted}>Posted 2 days ago</p>
                <Button className={classes.applyButton}>Apply</Button>
              </div>
            </CardContent>
          </CardActionArea>
        </Card>
      </Grow>

      <CompanyModal
        open={companyModal}
        onClose={handleCompanyModalClose}
        cid={props.cid}
        companyName={companyName}
        tab={'insights'}
        token={props.token}
        card={props.card}
      />
    </div>
  );
}
