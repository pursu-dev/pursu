import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Typography,
} from '@material-ui/core';
import { CloseIcon } from '@material-ui/icons/Close';

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

export default function DuplicateCustomizedDialogs(props) {
  return (
    <div>
      <Dialog
        onClose={props.close}
        aria-labelledby="customized-dialog-title"
        open={props.info}
      >
        <DialogTitle id="customized-dialog-title" onClose={props.close}>
          Duplicate Company
        </DialogTitle>
        <DialogContent dividers>
          <Typography gutterBottom>
            This company is already in your board! Try dragging that company to
            a new stage if you would like to update any information.
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
