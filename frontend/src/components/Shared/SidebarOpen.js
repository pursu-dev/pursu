import React from 'react';
import { makeStyles, IconButton } from '@material-ui/core';
import { Menu as MenuIcon } from '@material-ui/icons';

const useStyles = makeStyles(theme => ({
  menuButton: {
    marginRight: 36,
  },
}));

export default function SidebarOpen(props) {
  const classes = useStyles();
  return (
    <IconButton
      edge="start"
      aria-label="open drawer"
      onClick={props.onClick}
      className={classes.menuButton}
    >
      <MenuIcon />
    </IconButton>
  );
}
