import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
} from '@material-ui/core';

const styles = theme => ({
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
});

export default function CustomizedDialogs(props) {
  return (
    <div>
      <Dialog
        onClose={props.close}
        aria-labelledby="customized-dialog-title"
        open={props.info}
      >
        <DialogTitle id="customized-dialog-title" onClose={props.close}>
          New Company
        </DialogTitle>
        <DialogContent dividers>
          <Typography gutterBottom>
            You have discovered a new company for our database! We have added
            this company to our list, but in the meantime please manually keep
            track of this company and your recruiting process.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button autoFocus onClick={props.close} color="primary">
            OK
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
