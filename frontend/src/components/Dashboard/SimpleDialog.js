import React from 'react';
import PropTypes from 'prop-types';
import { makeStyles } from '@material-ui/core/styles';
import {
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  DialogTitle,
  Dialog,
} from '@material-ui/core';
import {
  Delete as DeleteIcon,
  Close as CloseIcon,
  ExitToApp as ExitToAppIcon,
  Refresh as RefreshIcon,
} from '@material-ui/icons';
import { blue } from '@material-ui/core/colors';
import { Redirect } from 'react-router-dom';
import ConfirmationDialog from './ConfirmationDialog';
import ResetDashboardConfirmation from './ResetDashboardConfirmation';
import { delete_cookie } from 'sfcookies';

const options = ['Logout', 'Reset Dashboard', 'Delete Account'];
const iconArray = [<ExitToAppIcon />, <RefreshIcon />, <DeleteIcon />];

const useStyles = makeStyles({
  avatar: {
    backgroundColor: blue[100],
    color: blue[600],
  },
});

export default function SimpleDialog(props) {
  const classes = useStyles();
  const { onClose, open, token } = props;
  const [openConfirmation, setOpenConfirmation] = React.useState(false);
  const [resetConfirmation, setResetConfirmation] = React.useState(false);
  const [isLoggedOut, setIsLoggedOut] = React.useState(false);

  const handleOpenConfirmation = () => {
    setOpenConfirmation(true);
  };

  const handleCloseConfirmation = () => {
    setOpenConfirmation(false);
  };

  const handleResetConfirmationOpen = () => {
    setResetConfirmation(true);
  };

  const handleResetConfirmationClose = () => {
    setResetConfirmation(false);
  };

  const handleListItemClick = value => {
    if (value === 'Delete Account') {
      handleOpenConfirmation(true);
    } else if (value === 'Logout') {
      onClose();
      handleSignOut();
      setIsLoggedOut(true);
    } else if (value === 'Reset Dashboard') {
      handleResetConfirmationOpen();
    }
  };

  const handleSignOut = () => {
    delete_cookie('userToken');
  };

  return (
    <div>
      {isLoggedOut && (
        <Redirect
          push
          to={{
            pathname: '/',
          }}
        />
      )}
      <Dialog
        onClose={props.handleClose}
        aria-labelledby="simple-dialog-title"
        open={open}
      >
        <DialogTitle id="simple-dialog-title">Account Settings</DialogTitle>
        <List>
          {options.map((option, index) => (
            <ListItem
              button
              onClick={() => handleListItemClick(option)}
              key={option}
            >
              <ListItemAvatar>
                <Avatar className={classes.avatar}>{iconArray[index]}</Avatar>
              </ListItemAvatar>
              <ListItemText primary={option} />
            </ListItem>
          ))}
          <ListItem button onClick={onClose} key={'Close'}>
            <ListItemAvatar>
              <Avatar className={classes.avatar}>
                <CloseIcon />
              </Avatar>
            </ListItemAvatar>
            <ListItemText primary={'Close Dialog'} />
          </ListItem>
        </List>
      </Dialog>
      <ConfirmationDialog
        open={openConfirmation}
        onClose={handleCloseConfirmation}
        token={token}
      />
      <ResetDashboardConfirmation
        open={resetConfirmation}
        onClose={handleResetConfirmationClose}
        token={token}
      />
    </div>
  );
}

SimpleDialog.propTypes = {
  onClose: PropTypes.func.isRequired,
  open: PropTypes.bool.isRequired,
  token: PropTypes.string.isRequired,
};
