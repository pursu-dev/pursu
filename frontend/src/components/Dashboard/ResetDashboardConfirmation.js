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
  Typography
} from '@material-ui/core';
import { Close as CloseIcon, Check as CheckIcon, Refresh as RefreshIcon } from '@material-ui/icons';
import { blue } from '@material-ui/core/colors';
import { Redirect } from 'react-router-dom';

const useStyles = makeStyles({
  avatar: {
    backgroundColor: blue[100],
    color: blue[600],
  },
});

export default function ResetDashboardConfirmation(props) {
  const classes = useStyles();
  const { onClose, open, token } = props;

  const handleListItemClick = (value) => {
    handleResetAccount(value);
    window.location.reload();
    onClose();
  };

  const handleResetAccount = (value) => {
    let data = {
      token: token,
      reset_insights: value
    };
    let url = process.env.REACT_APP_USER_RESET;
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
      <Dialog
        onClose={props.handleClose}
        aria-labelledby="simple-dialog-title"
        open={open}
      >
        <DialogTitle style={{textAlign: "center"}}> <strong> Reset your dashboard and start fresh! </strong></DialogTitle>
        <DialogContent dividers>
        <Typography gutterBottom style={{textAlign: "center"}}> Once you reset your account, all data from your dashboard will be deleted.  </Typography>
        <Typography style={{textAlign: "center"}}> Are you sure you'd like to reset? </Typography>
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
          <ListItem button onClick={() => handleListItemClick(0)} key={'Yes'}>
            <ListItemAvatar>
              <Avatar className={classes.avatar}>
                <CheckIcon />
              </Avatar>
            </ListItemAvatar>
            <ListItemText primary={'Yes'} />
          </ListItem>
          <ListItem button onClick={() => handleListItemClick(1)} key={'Yes Plus Insights'}>
            <ListItemAvatar>
              <Avatar className={classes.avatar}>
                <RefreshIcon />
              </Avatar>
            </ListItemAvatar>
            <ListItemText primary={'Yes, and also reset my recommendations data'} />
          </ListItem>
        </List>
      </Dialog>
    </div>
  );
}

ResetDashboardConfirmation.propTypes = {
  onClose: PropTypes.func.isRequired,
  open: PropTypes.bool.isRequired,
  token: PropTypes.string.isRequired,
};
