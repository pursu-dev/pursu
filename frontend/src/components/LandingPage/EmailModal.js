import React from 'react';
import ReactGA from 'react-ga';
import { makeStyles, Box, Modal } from '@material-ui/core';
import { useHistory } from 'react-router-dom';
import LoginPopup from './LoginPopup';

const useStyles = makeStyles(theme => ({
  modal: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
}));

export default function TransitionsModal(props) {
  const classes = useStyles();
  const [openEmailModal, setOpenEmailModal] = React.useState(false);
  const history = useHistory();

  ReactGA.initialize(process.env.REACT_APP_GOOGLE_ANALYTICS_CODE);

  return (
    <Box>
      {props.message === 'Login' && (
        <button
          class="button button1"
          background="#008CBA"
          onClick={() => history.push('/demo')}
        >
          Try Our Demo!
        </button>
      )}
      <button
        class="button button1"
        background="#008CBA"
        onClick={() => setOpenEmailModal(true)}
      >
        Login
      </button>

      <Modal
        className={classes.modal}
        open={openEmailModal}
        onClose={() => setOpenEmailModal(false)}
      >
        <LoginPopup {...props} displayGreeting />
      </Modal>
    </Box>
  );
}
