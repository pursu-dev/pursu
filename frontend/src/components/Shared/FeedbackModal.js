import React from 'react';
import {
  makeStyles,
  Modal,
  Typography,
  TextField,
  Button,
  Grid,
  Divider,
  Fab,
} from '@material-ui/core';
import { Comment as CommentIcon } from '@material-ui/icons';
import { Alert } from '@material-ui/lab';

const useStyles = makeStyles(theme => ({
  paper: {
    position: 'absolute',
    width: 500,
    border: '2px solid #3f51b5',
    backgroundColor: theme.palette.background.paper,
    boxShadow: theme.shadows[3],
    padding: theme.spacing(2, 4, 3),
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'column',
  },
  icon: {
    marginRight: theme.spacing(1),
  },
}));

export default function FeedbackModal(props) {
  const classes = useStyles();
  const [open, setOpen] = React.useState(false);
  const [sent, setSent] = React.useState(false);
  const [feedback, setFeedback] = React.useState('');

  const sendFeedback = () => {
    let body = { email: props.email, comment: feedback };
    let feedbackURL = process.env.REACT_APP_FEEDBACK_BETA;
    fetch(feedbackURL, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
      .then(() => {
        setFeedback('');
        setSent(true);
      })
      .then(() => {
        return new Promise(resolve => {
          setTimeout(() => {
            setSent(false);
            resolve();
          }, 3000);
        });
      });
  };

  const body = (
    <div className={classes.paper}>
      <Typography variant="h5" align="center">
        <strong>Send us your feedback!</strong>
      </Typography>
      {/* This divider doesn't work tried a bunch of stuff with it I think it has to do with the modal */}
      <Divider flexitem />
      <br />
      {sent && (
        <Alert>
          Your feedback was sent successfully! Thanks for using Pursu!
        </Alert>
      )}
      <TextField
        multiline
        variant="filled"
        placeholder="Feedback"
        fullWidth
        rows={5}
        onChange={event => setFeedback(event.target.value)}
        value={feedback}
      />
      <br />
      <Grid
        container
        spacing={1}
        direction="row"
        justify="flex-end"
        alignItems="center"
      >
        <Grid item>
          <Button onClick={props.handleClose} variant="contained" color="primary">
            Cancel
          </Button>
        </Grid>
        <Grid item>
          <Button
            onClick={sendFeedback}
            variant="contained"
            color="primary"
            disabled={feedback === ''}
          >
            Submit
          </Button>
        </Grid>
      </Grid>
    </div>
  );

  return (
    <div>
      <Modal
        open={props.open}
        onClose={props.handleClose}
        aria-labelledby="simple-modal-title"
        aria-describedby="simple-modal-description"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {body}
      </Modal>
    </div>
  );
}
