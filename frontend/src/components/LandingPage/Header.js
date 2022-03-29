import React from 'react';
import { fade, makeStyles, withStyles } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import MenuItem from '@material-ui/core/MenuItem';
import Menu from '@material-ui/core/Menu';
import logo from '../../images/Pursu_long_900.png';
import Sidebar from '../Shared/SidebarOpen';
import { NavLink } from 'react-router-dom';
import EmailModal from './EmailModal';

const styles = theme => ({
  grow: {
    flexGrow: 1,
    background: 'none',
    opacity: 1,
    paddingLeft: '30px',
  },
  logo: {
    paddingRight: theme.spacing(2),
    marginRight: theme.spacing(1),
  },
  menuButton: {
    marginRight: theme.spacing(1),
  },
  title: {
    display: 'none',
    [theme.breakpoints.up('sm')]: {
      display: 'block',
    },
  },
  auto: {
    borderRadius: theme.spacing.borderRadius,
    borderColor: '#3c0d99',
  },
  navigation: {
    margin: theme.spacing(2),
    fontFamily: 'Lato',
    color: '#3c0d99',
  },
  inputRoot: {
    color: '#3c0d99',
  },
  inputInput: {
    // padding: theme.spacing(1, 1, 1, 4),
    padding: '5px',
    transition: theme.transitions.create('width'),
    width: '100%',
    [theme.breakpoints.up('md')]: {
      width: 200,
    },
    color: '#3c0d99',
    fontFamily: 'Lato',
  },
  sectionDesktop: {
    display: 'none',
    [theme.breakpoints.up('md')]: {
      alignItems: 'center',
      justifyContent: 'center',
      display: 'flex',
    },
  },
  sectionMobile: {
    display: 'flex',
    marginRight: -35,
    [theme.breakpoints.up('md')]: {
      display: 'none',
    },
  },
  settings: {
    marginRight: 20,
  },
});

class ToolbarComponent extends React.Component {
  state = {
    achorEl: false,
    MobileMoreAnchorEl: false,
    openFeedbackModal: false,
    value: null,
    copied: false,
  };

  render() {
    const { classes } = this.props;
    const isMenuOpen = Boolean(this.state.anchorEl);
    const isMobileMenuOpen = Boolean(this.state.mobileMoreAnchorEl);

    const menuId = 'primary-search-account-menu';
    const renderMenu = (
      <Menu
        anchorEl={this.state.anchorEl}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        id={menuId}
        keepMounted
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        open={isMenuOpen}
        onClose={this.handleMenuClose}
      >
        <MenuItem onClick={this.handleMenuClose}>Profile</MenuItem>
        <MenuItem onClick={this.handleMenuClose}>My account</MenuItem>
      </Menu>
    );

    return (
      <div className={classes.grow}>
        <AppBar
          position="static"
          elevation={0}
          style={{ backgroundColor: 'rgba(119, 54, 207, 0.0)' }}
        >
          <Toolbar elevation={0} className={classes.grow}>
            <div className={classes.sectionMobile}>
              <Sidebar onClick={this.props.openDrawer} />
            </div>
            <div className={classes.logo}>
              <NavLink
                push
                to={{
                  pathname: '/',
                }}
              >
                <img
                  style={{
                    maxHeight: 100,
                    maxWidth: 100,
                    objectFit: 'contain',
                  }}
                  src={logo}
                  alt="logo"
                />
              </NavLink>
            </div>
            <div className={classes.grow} />
            <div className={classes.sectionDesktop}>
              <EmailModal
                func={this.props.func}
                message={'Login'}
                caller={'Landing'}
                setClientID={this.props.setClientID}
              />
            </div>
            <div className={classes.sectionMobile}></div>
          </Toolbar>
        </AppBar>
        {renderMenu}
      </div>
    );
  }
}

export default withStyles(styles)(ToolbarComponent);
