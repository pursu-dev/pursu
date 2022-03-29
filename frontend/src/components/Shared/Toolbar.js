import React from 'react';
import { fade, makeStyles, withStyles } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import IconButton from '@material-ui/core/IconButton';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';
import MenuItem from '@material-ui/core/MenuItem';
import Menu from '@material-ui/core/Menu';
import SearchIcon from '@material-ui/icons/Search';
import logo from '../../images/Pursu_long_900.png';
import Sidebar from './SidebarOpen';
import { NavLink } from 'react-router-dom';
import { Settings as SettingsIcon } from '@material-ui/icons';
import { Autocomplete } from '@material-ui/lab';
import { TextField } from '@material-ui/core';
import FeedbackModal from './FeedbackModal';
import { isMobile } from 'react-device-detect';
import { CopyToClipboard } from 'react-copy-to-clipboard';

const styles = theme => ({
  grow: {
    flexGrow: 1,
    background: '#ffffff',
  },
  settingsGrow: {
    flexGrow: 1,
  },
  logo: {
    paddingRight: theme.spacing(2),
    marginRight: theme.spacing(1),
    borderRightWidth: 'thin',
    borderRightColor: '#d3d3d3',
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
  search: {
    position: 'relative',
    borderRadius: theme.shape.borderRadius,
    //borderColor: '#3c0d99',
    borderLeftColor: '#3c0d99',
    backgroundColor: fade('rgb(0, 0, 0, 0.01)', 0.05),
    '&:hover': {
      backgroundColor: fade('rgba(0, 0, 0, 0.08)', 0.1),
    },
    marginRight: theme.spacing(2),
    marginLeft: 0,
    width: '25%',
    [theme.breakpoints.up('sm')]: {
      marginLeft: theme.spacing(5),
      //width: 'auto',
    },
  },
  searchMobile: {
    position: 'relative',
    borderRadius: theme.shape.borderRadius,
    //borderColor: '#3c0d99',
    borderLeftColor: '#3c0d99',
    backgroundColor: fade('rgb(0, 0, 0, 0.01)', 0.05),
    '&:hover': {
      backgroundColor: fade('rgba(0, 0, 0, 0.08)', 0.1),
    },
    width: '55%',
    [theme.breakpoints.up('sm')]: {
      marginLeft: theme.spacing(2),
    },
  },
  searchIcon: {
    width: theme.spacing(0),
    height: '100%',
    position: 'absolute',
    pointerEvents: 'none',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#3c0d99',
    marginLeft: '-25px',
  },
  searchIconMobile: {
    height: '100%',
    opacity: '0%',
    position: 'absolute',
    pointerEvents: 'none',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#3c0d99',
    marginLeft: '0px',
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

//takes in an array of lanes
function getCurrentCompanies(data, page) {
  let options = [];
  if (page == 'explore') {
    options = getCurrentCompaniesExplore(data);
    return options;
  }
  if (data && data !== undefined) {
    for (var l = 0; l < data.lanes.length; l++) {
      var lane = data.lanes[l];
      for (var c = 0; c < lane.cards.length; c++) {
        var card = lane.cards[c];
        card['stage'] = lane.title;
        options = [...options, card];
      }
    }
  }
  return options;
}

function getCurrentCompaniesExplore(data) {
  const companies = [];
  if (data && data !== undefined) {
    const seen = new Set();
    for (let i = 0; i < data.length; ++i) {
      const cid = data[i][0];
      const company_name = data[i][2];
      const logo = data[i][3];
      const duplicate = seen.has(cid);
      seen.add(cid);
      if (!duplicate && !!data[i][8]) {
        companies.push([cid, company_name, logo]);
      }
    }
    return companies;
  }
  return [];
}

class ToolbarComponent extends React.Component {
  state = {
    achorEl: false,
    MobileMoreAnchorEl: false,
    openFeedbackModal: false,
    value: null,
    copied: false,
  };

  handleOpenFeedback = () => {
    this.setState({
      openFeedbackModal: true,
    });
  };

  handleCloseFeedback = () => {
    this.setState({
      openFeedbackModal: false,
    });
  };

  handleProfileMenuOpen = event => {
    this.setState({
      achorEl: event.currentTarget,
    });
  };

  handleMobileMenuClose = () => {
    this.setState({
      mobileMoreAnchorEl: null,
    });
  };

  handleMenuClose = () => {
    this.setState({
      achorEl: null,
      mobileMoreAnchorEl: null,
    });
  };

  handleMobileMenuOpen = event => {
    this.setState({
      mobileMoreAnchorEl: event.currentTarget,
    });
  };

  handleOnChange = (e, value) => {
    this.setState({ value: value });
    if (value === null) {
      return;
    }
    if (this.props.page == 'dashboard') {
      if (value.cid) {
        this.props.handleCompanyModalOpen(value);
      }
      if (this.props.isDemo) {
        this.props.handleCompanyModalOpen(value);
      }
    } else {
      // since it's coming from explore, create a "card" company
      if (value[0]) {
        let company = this.props.filter(this.props.pipelines, value[0]);
        if (!company) {
          company = {};
          company['cid'] = value[0];
          company['title'] = value[1];
          company['logo'] = value[2];
        }
        this.props.handleCompanyModalOpen(company, company['cid']);
      }
    }
  };

  getFunctionLabel = option => {
    if (this.props.page == 'dashboard') {
      return option.title;
    } else {
      return option[1];
    }
  };

  componentDidUpdate = () => {
    if (this.state.value != null) {
      this.setState({ value: null });
    }
    if (this.state.copied === true) {
      setTimeout(() => {
        this.setState({ copied: false });
      }, 1000);
    }
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

    const options = getCurrentCompanies(this.props.data, this.props.page);
    return (
      <div className={classes.grow}>
        <AppBar position="static" elevation={0}>
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
            <div className={isMobile ? classes.searchMobile : classes.search}>
              <div
                className={
                  isMobile ? classes.searchIconMobile : classes.searchIcon
                }
              >
                <SearchIcon />
              </div>
              <Autocomplete
                clearOnEscape={true}
                value={this.state.value}
                className={classes.auto}
                options={options.map(option => option)}
                groupBy={option => option.stage}
                getOptionLabel={this.getFunctionLabel}
                onChange={this.handleOnChange}
                renderInput={params => (
                  <TextField
                    {...params}
                    label="Search..."
                    variant="outlined"
                    size="small"
                    classes={{
                      root: classes.inputRoot,
                      input: classes.inputInput,
                    }}
                  />
                )}
              />
            </div>
            <div className={classes.grow} />
            <div className={classes.sectionDesktop}>
              <NavLink to={this.props.isDemo ? '/demo' : '/'}>
                <Typography
                  component="h3"
                  variant="h6"
                  className={classes.navigation}
                >
                  Dashboard
                </Typography>
              </NavLink>
              <NavLink to="/explore">
                <Typography
                  component="h3"
                  variant="h6"
                  className={classes.navigation}
                >
                  Explore
                </Typography>
              </NavLink>

              {!this.props.isDemo && (
                <button
                  style={{ outline: 0 }}
                  onClick={this.handleOpenFeedback}
                >
                  <Typography
                    component="h3"
                    variant="h6"
                    className={classes.navigation}
                  >
                    Feedback
                  </Typography>
                </button>
              )}
              <CopyToClipboard
                onCopy={() => this.setState({ copied: true })}
                text={'https://pursu.dev/?ref=' + this.props.email}
              >
                <Tooltip
                  title={
                    <h1 style={{ fontSize: '16px', lineHeight: '20px' }}>
                      Get points by referring your friends! Points can be
                      redeemed for recruiter information in the company card!
                    </h1>
                  }
                  arrow
                >
                  <button style={{ outline: 0 }}>
                    <Typography
                      component="h3"
                      variant="h6"
                      className={classes.navigation}
                    >
                      {this.state.copied
                        ? 'Copied To Clipboard!'
                        : 'Copy Referral Link'}
                    </Typography>
                  </button>
                </Tooltip>
              </CopyToClipboard>
            </div>
            <div className={classes.settings}>
              <IconButton
                color="inherit"
                href="/"
                onClick={this.props.openSettings}
              >
                <Typography component="h1" variant="h6" color="primary" noWrap>
                  <SettingsIcon />
                </Typography>
              </IconButton>
            </div>
            <div className={classes.sectionMobile}></div>
          </Toolbar>
        </AppBar>
        {renderMenu}
        <FeedbackModal
          open={this.state.openFeedbackModal}
          email={this.props.email}
          handleClose={this.handleCloseFeedback}
        />
      </div>
    );
  }
}

export default withStyles(styles)(ToolbarComponent);
