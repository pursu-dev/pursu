import React from 'react';
import {
  makeStyles,
  List,
  ListItem,
  ListItemText,
  Drawer,
} from '@material-ui/core';
import {
  Dashboard as DashboardIcon,
  Explore as ExploreIcon,
  Feedback as FeedbackIcon,
  Cancel as CancelIcon,
} from '@material-ui/icons';
import { NavLink } from 'react-router-dom';
import FeedbackModal from './FeedbackModal'

const useStyles = makeStyles({
  listIcon: {
    margin: '0px 8px',
  },
});

export default function HamburgerDrawer(props) {
  const classes = useStyles();
  const [open, setOpen] = React.useState(false);

  const handleOpenFeedback = () => {
    setOpen(true);
  };

  const handleCloseFeedback = () => {
    setOpen(false);
  };

  return (
    <Drawer open={props.open} onClose={props.onClose}>
      <List>
        <NavLink to="/">
          <ListItem button>
            <ListItemText>
              <DashboardIcon className={classes.listIcon} />
              Dashboard
            </ListItemText>
          </ListItem>
        </NavLink>

        <NavLink to="/explore">
          <ListItem button>
            <ListItemText>
              <ExploreIcon className={classes.listIcon} />
              Explore 
            </ListItemText>
          </ListItem>
        </NavLink>

        <button style={{outline: 0}} onClick={handleOpenFeedback}>
          <ListItem button>
            <ListItemText>
              <FeedbackIcon className={classes.listIcon} />
              Feedback 
            </ListItemText>
          </ListItem>
        </button>

        <ListItem button onClick={props.onClose}>
          <CancelIcon className={classes.listIcon} />
          <ListItemText primary="Close" />
        </ListItem>
      </List>
      <FeedbackModal
        open={open}
        email={props.email}
        handleClose={handleCloseFeedback}
      />
    </Drawer>
  );
}
