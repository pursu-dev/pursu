import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Box, Button, Typography, CircularProgress } from '@material-ui/core';

const useStyles = makeStyles({
  title: {
    fontSize: '25px',
    fontFamily: 'Poppins',
    color: 'black',
    fontWeight: 500,
  },
  textArea: {
    width: '100%',
    height: '80%',
    fontSize: '18px',
    fontFamily: 'Poppins',
    color: 'black',
    fontWeight: 400,
    resize: 'none',
    outline: 'none',
    marginTop: '10px',
  },
  flex: {
    display: 'flex',
    gap: '30px 20px',
  },
  saveButton: {
    backgroundColor: '#B49BD4',
    color: 'white',
  },
});

export default function NotesCard(props) {
  const classes = useStyles();
  const [notesLoadingIcon, setNotesLoadingIcon] = React.useState(false);
  const [notes, setNotes] = React.useState(props.card.description);

  const handleSubmit = () => {
    setNotesLoadingIcon(true);
    let backendData = {
      token: props.token,
      pid: props.card.pid,
      notes,
    };
    let url = process.env.REACT_APP_DASHBOARD_EDIT;
    fetch(url, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backendData),
    }).then(() => {
      setTimeout(() => setNotesLoadingIcon(false), 1000);
    });
  };

  return (
    <Box className={props.classes.notesCard}>
      <Box className={classes.flex}>
        <Typography className={classes.title}>Notes</Typography>
        <Button
          size="small"
          variant="contained"
          className={classes.saveButton}
          onClick={() => handleSubmit()}
        >
          {notesLoadingIcon ? <CircularProgress size={25} /> : 'Save'}
        </Button>
      </Box>
      <textarea
        value={notes}
        className={classes.textArea}
        onChange={e => setNotes(e.target.value)}
        placeholder={'Type your notes here...'}
      />
    </Box>
  );
}
