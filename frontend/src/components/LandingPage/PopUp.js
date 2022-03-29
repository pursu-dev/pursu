import React from 'react';
import ReactGA from 'react-ga';
import { makeStyles, Modal, Backdrop, Fade, Button } from '@material-ui/core';

import tw from 'twin.macro';
import PopupImage from '../../images/popupImg.jpg';
import LoginPopup from './LoginPopup';
import { withOrientationChange } from 'react-device-detect';
const PopupHeading = tw.h3`font-bold text-lg md:text-xl lg:text-2xl xl:text-2xl text-gray-900 leading-tight`;
const PopupParagraph = tw.p`text-xs md:text-sm lg:text-base xl:text-base`;

const useStyles = makeStyles(theme => ({
  modal: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    maxWidth: '650px',
    margin: 'auto',
    padding: '10px',
  },
  paper: {
    backgroundColor: theme.palette.background.paper,
    boxShadow: theme.shadows[5],
    padding: theme.spacing(2, 4, 3),
    outline: 0,
  },
  getStartedButton: {
    outline: 'none',
    '&:focus': {
      outline: 0,
    },
    fontSize: '20px',
    fontWeight: 'bold',
    backgroundColor: 'rgba(60, 4, 156, 0.75)',
    color: 'white',
    paddingLeft: '20px',
    paddingRight: '20px',
    textAlign: 'center',
    textTransform: 'capitalize',
  },
}));

export default function PopUp(props) {
  const classes = useStyles();
  const [open, setOpen] = React.useState(false);

  ReactGA.initialize(process.env.REACT_APP_GOOGLE_ANALYTICS_CODE);

  const handleOpen = () => {
    ReactGA.event({
      category: 'Get Started',
      action: 'Viewed',
      value: 1,
    });
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  return (
    <div>
      <Button
        className={classes.getStartedButton}
        variant="contained"
        background="#008CBA"
        onClick={handleOpen}
      >
        Get Started
      </Button>
      <Modal
        className={classes.modal}
        open={open}
        onClose={handleClose}
        closeAfterTransition
        BackdropComponent={Backdrop}
        BackdropProps={{
          timeout: 500,
        }}
      >
        <Fade in={open}>
          <div className={classes.paper}>
            <div className="modal">
              <div className="header">
                <PopupHeading>
                  We're so excited that you have chosen to sign up for Pursu!
                </PopupHeading>
              </div>
              <div className="content">
                <PopupParagraph>
                  You're just a couple clicks away from creating your account!
                  Pursu is built by students and we do not currently have the
                  funding yet to pay for Google’s verification process, thus you
                  will be shown this security message before you are able to get
                  started:
                </PopupParagraph>
                <div class="popup-image">
                  <img src={PopupImage} alt="Security Message" />
                </div>

                <PopupParagraph>
                  In order to continue signing up, click on the "Advanced"
                  button in the lower left hand corner. For more details about
                  how we handle your data, take a look at our
                  <a
                    style={{ color: 'blue' }}
                    href="https://bit.ly/32yM3Rv"
                    target="_blank"
                  >
                    {' '}
                    privacy policy.
                  </a>{' '}
                  Get started by entering your email!
                </PopupParagraph>
              </div>
              <div className="actions">
                <LoginPopup {...props} />
              </div>
            </div>
          </div>
        </Fade>
      </Modal>
    </div>
  );
}
