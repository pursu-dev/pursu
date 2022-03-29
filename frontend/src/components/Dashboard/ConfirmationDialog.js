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
  DialogContent,
  Typography,
} from '@material-ui/core';
import { Close as CloseIcon, Check as CheckIcon } from '@material-ui/icons';
import { blue } from '@material-ui/core/colors';
import { Redirect } from 'react-router-dom';
import { delete_cookie } from 'sfcookies';

const useStyles = makeStyles({
  avatar: {
    backgroundColor: blue[100],
    color: blue[600],
  },
});

export default function ConfirmationDialog(props) {
  const classes = useStyles();
  const { onClose, open, token } = props;
  const [goIndex, setGoIndex] = React.useState(false);

  const handleListItemClick = value => {
    delete_cookie('userToken');
    handleDeleteAccount();
    setGoIndex(true);
    onClose();
  };

  const handleDeleteAccount = () => {
    let data = {
      token: token,
    };
    let url = process.env.REACT_APP_USER_DELETE;
    fetch(url, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
  };

  return (
    <div>
      {goIndex && (
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
        <DialogTitle style={{ textAlign: 'center' }}>
          {' '}
          <strong> Delete your Account </strong>
        </DialogTitle>
        <DialogContent dividers>
          <Typography
            gutterBottom
            style={{ textAlign: 'center' }}
            id="simple-dialog-title"
          >
            We're sorry to see you go!
          </Typography>
          <Typography style={{ textAlign: 'center' }} id="simple-dialog-title">
            Once you delete your account, you will permanently lose access to
            all information on Pursu. We also will no longer track incoming
            emails and will delete all associated user information. Are you sure
            you want to delete your account?
          </Typography>
        </DialogContent>
        <List>
          <ListItem button onClick={onClose} key={'Close'}>
            <ListItemAvatar>
              <Avatar className={classes.avatar}>
                <CloseIcon />
              </Avatar>
            </ListItemAvatar>
            <ListItemText primary={'No'} />
          </ListItem>
          <ListItem button onClick={handleListItemClick} key={'Close'}>
            <ListItemAvatar>
              <Avatar className={classes.avatar}>
                <CheckIcon />
              </Avatar>
            </ListItemAvatar>
            <ListItemText primary={'Yes'} />
          </ListItem>
        </List>
      </Dialog>
    </div>
  );
}

ConfirmationDialog.propTypes = {
  onClose: PropTypes.func.isRequired,
  open: PropTypes.bool.isRequired,
  token: PropTypes.string.isRequired,
};
