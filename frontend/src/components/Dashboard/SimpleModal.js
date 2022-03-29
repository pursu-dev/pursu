import React from 'react';
import {
  makeStyles,
  Modal,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
} from '@material-ui/core';

const useStyles = makeStyles(theme => ({
  root: {
    margin: 0,
    padding: theme.spacing(2),
  },
  closeButton: {
    position: 'absolute',
    right: theme.spacing(1),
    top: theme.spacing(1),
    color: theme.palette.grey[500],
  },
  welcomeFont: {
    fontFamily: 'Poppins',
  },
}));

export default function SimpleModal(props) {
  const classes = useStyles();

  const body = (
    <div>
      <h2 className={classes.welcomeFont} id="simple-modal-title">
        {props.name} has been rewarded a referral point. By referring your
        friends, you can gain referral points to redeem company recruiters!
        Click on <strong> Copy Referral Link </strong> in the navbar to generate
        your link.
      </h2>
    </div>
  );

  return (
    <div>
      <Dialog
        open={props.open}
        onClose={props.handleClose}
        aria-labelledby="customized-dialog-title"
      >
        <DialogTitle id="customized-dialog-title" onClose={props.close}>
          Thanks for signing up for Pursu!
        </DialogTitle>
        <DialogContent dividers>
          <Typography gutterBottom>{body}</Typography>
        </DialogContent>
        <DialogActions>
          <Button autoFocus onClick={props.handleClose} color="primary">
            OK
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
