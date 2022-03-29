import React from 'react';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';

export default function AlertDialog(props) {
  return (
    <div>
      <Dialog
        open={props.open}
        onClose={props.handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">{'Delete company?'}</DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Are you sure you want to delete? Deleting this company means that
            you may permanently lose some information that Pursu has populated
            for you.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={props.handleCloseCancel} color="primary" autoFocus>
            Cancel
          </Button>
          <Button
            onClick={e => props.handleClose(e, props.card)}
            color="primary"
          >
            OK
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
