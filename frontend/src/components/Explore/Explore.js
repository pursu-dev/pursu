import React, { useEffect } from 'react';
import ReactGA from 'react-ga';
import '../Shared/fonts.css';
import clsx from 'clsx';
import {
  makeStyles,
  CssBaseline,
  AppBar,
  Typography,
  Grid,
  Button,
  Popover,
  Menu,
  MenuItem,
  Switch,
} from '@material-ui/core';
import { pipToIndex, getQuery } from '../../helpers/utils';
import BugsBanner from '../Dashboard/BugsBanner';
import SimpleDialog from '../Dashboard/SimpleDialog';
import HamburgerDrawer from '../Shared/HamburgerDrawer';
import InfiniteScroll from 'react-infinite-scroll-component';
import Navbar from '../Shared/Navbar';
import CompanyModal from '../Shared/CompanyModal';
import RecCompanyTile from './RecCompanyTile';
import ExploreCompanyTile from './ExploreCompanyTile';
import moment from 'moment';

const useStyles = makeStyles(theme => ({
  toolbar: {
    paddingRight: 24, // keep right padding when drawer closed
    background: '#fcfaff',
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
  },
  appBarShift: {
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  menuButton: {
    marginRight: 36,
  },
  menuButtonHidden: {
    display: 'none',
  },
  title: {
    flexGrow: 1,
    background: '#fcfaff',
  },
  curtain: {
    display: 'flex',
    width: '100%',
    opacity: 100,
    zIndex: -3,
  },

  exploreBackground: {
    display: 'flex',
    background: '#f0f1f3',
    zIndex: -4,
  },

  header: {
    marginTop: 5,
    color: '#61289A',
    fontFamily: 'Lato',
  },
  banner: {
    margin: theme.spacing(2),
  },
  companyList: {
    margin: theme.spacing(2),
    color: 'rgb(0,0,0, .66)',
    fontFamily: 'Lato',
    paddingLeft: '65px',
  },
  exploreSearch: {
    margin: theme.spacing(2),
    paddingLeft: '65px',
  },
  exploreButton: {
    textTransform: 'capitalize',
    marginRight: theme.spacing(2),
    color: '#61289A',
    borderColor: '#61289A',
    fontFamily: 'Lato',
  },
  recommendedContainer: {
    background: 'rgba(196, 196, 196, 0.21)',
    borderRadius: 12,
    marginLeft: '6vw',
    marginRight: '6vw',
    display: 'flex',
    flexWrap: 'wrap',
    flexDirection: 'row',
    boxSizing: 'border-box',
    paddingLeft: '0px',
    paddingRight: '0px',
  },
  popoverList: {
    textTransform: 'capitalize',
    color: '#61289A',
    borderColor: '#61289A',
    fontFamily: 'Lato',
  },
}));

export default function Explore(props) {
  let token = props.token;
  const classes = useStyles();

  //components for modal popup for new company suggestion
  const [openSettings, setOpenSettings] = React.useState(false);
  const [companyIDs, setCompanyIDs] = React.useState([]);
  const [companyModal, setCompanyModal] = React.useState(false);
  const [openDrawer, setOpenDrawer] = React.useState(false);
  const [companiesList, setCompaniesList] = React.useState([]);
  const [pipelines, setPipelines] = React.useState(null);
  const [infiniteScrollData, setInfiniteScrollData] = React.useState([]);
  const [filteredCompanies, setFilteredCompanies] = React.useState([]);
  const [cardInfo, setCardInfo] = React.useState(null);
  const [exploreCompanies, setExploreCompanies] = React.useState([]);
  const [userInfo, setUserInfo] = React.useState(null);
  const [newGradChecked, setNewGradChecked] = React.useState(false);

  // job type filters
  const [jobTypePopoverRef, setjobTypePopoverRef] = React.useState(null);
  const [jobTypeFilter, setjobTypeFilter] = React.useState(null);

  // sort by filters
  const [sortByPopoverRef, setsortByPopoverRef] = React.useState(null);
  const [sortByFilter, setsortByFilter] = React.useState(null);

  const [modalOpenTime, setModalOpenTime] = React.useState(null);
  const [redemptionPoints, setRedemptionPoints] = React.useState(null);

  const handleCompanyModalOpen = (card, cid) => {
    setModalOpenTime(moment());

    const exploreCard = exploreCompanies.filter(item => {
      return item[0] === cid;
    })[0];

    // if not in pipeline
    if (!card && !!cid) {
      card = {
        cid: cid,
        title: exploreCard[2],
      };
    }
    setCardInfo(card);
  };

  const handleCompanyModalClose = () => {
    getQuery('pipeline_uid', props.token, setPipelines);
    const time_diff = moment().diff(modalOpenTime, 'seconds');
    ReactGA.event({
      category: 'Company Modal',
      action: 'Viewed',
      label: cardInfo.cid,
      value: time_diff,
    });
    setCompanyModal(false);
  };

  const handleOpenSettings = e => {
    e.preventDefault();
    setOpenSettings(true);
  };

  const handleCloseSettings = () => {
    setOpenSettings(false);
  };

  const handleDrawerClose = () => {
    setOpenDrawer(false);
  };

  function updateLogin(tokenToUse) {
    // make sure its after the first successful data query
    const backendData = {
      token: tokenToUse,
    };
    const url = process.env.REACT_APP_USER_LOGIN;
    fetch(url, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backendData),
    });
  }

  // token to use is props.token
  function getRecommendedCompanies(tokenToUse) {
    let backendData = {
      token: tokenToUse,
    };
    let url = process.env.REACT_APP_EXPLORE_RECOMMENDATIONS;
    fetch(url, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backendData),
    }).then(response => {
      response.json().then(data => {
        if (
          data.recommendations !== null &&
          data.recommendations !== undefined
        ) {
          setCompanyIDs(data.recommendations);
        }
      });
    });
  }

  const loadMoreCompanies = () => {
    if (exploreCompanies.length <= 0) {
      return;
    }
    let companies = [];
    const length = infiniteScrollData.length;
    for (let i = 0; i < length; ++i) {
      companies.push(infiniteScrollData[i]);
    }

    for (let i = length; i < length + 12; ++i) {
      let cid = exploreCompanies[i][0];
      let company_name = exploreCompanies[i][1];
      let logo = exploreCompanies[i][2];
      let obj = {
        name: company_name,
        cid: cid,
        logo: logo,
      };
      companies.push(obj);
    }
    setInfiniteScrollData(companies);
  };

  function filterByCID(array, cid) {
    return array.filter(item => {
      return item[0] === cid;
    })[0][2];
  }

  function filterByNodeCid(jsonObject, match) {
    return jsonObject.filter(function(jsonObject) {
      return jsonObject[0] == match;
    })[0];
  }

  function filterByIdArr(jsonObject, cid) {
    let match = jsonObject.filter(pipeline => pipeline[pipToIndex.cid] === cid);
    let card;
    if (match.length > 0 && match[0][pipToIndex.active]) {
      card = {
        description: match[0][pipToIndex.notes],
        draggable: true,
        title: match[0][pipToIndex.company_name],
        pid: match[0][pipToIndex.pid],
        recruiterName: match[0][pipToIndex.recruiter_name],
        recruiterEmail: match[0][pipToIndex.recruiter_email],
        link: match[0][pipToIndex.challenge_link],
        cid: match[0][pipToIndex.cid],
        timestamp: match[0][pipToIndex.timestamp],
        laneId: String(match[0][pipToIndex.stage]),
      };
      return card;
    } else {
      return null;
    }
  }

  const setInitialInfinite = () => {
    let companies = [];
    exploreCompanies.sort((a, b) => (a[2] > b[2] ? 1 : -1));
    for (let i = 0; i < exploreCompanies.length; ++i) {
      let cid = exploreCompanies[i][0];
      let trending =
        exploreCompanies[i][1] != null ? exploreCompanies[i][1] : 0;
      let companyName = exploreCompanies[i][2];
      let logo = exploreCompanies[i][3];
      let applicationLink = exploreCompanies[i][4];
      let location =
        exploreCompanies[i][5] != null ? exploreCompanies[i][5] : 'Various';
      let isInternship = exploreCompanies[i][6];
      let timestamp = exploreCompanies[i][7];
      let hasInsights = exploreCompanies[i][8];
      let obj = {
        name: companyName,
        cid: cid,
        trending: trending,
        logo: logo,
        appLink: applicationLink,
        location: location,
        isInternship: isInternship,
        timePosted: timestamp,
        hasInsights: hasInsights,
      };
      if (isInternship) {
        companies.push(obj);
      }
    }
    setInfiniteScrollData(companies);
  };

  const setJobFilteredData = () => {
    let companies = [];
    // infiniteScrollData.sort((a, b) => (a['name'] > b['name'] ? 1 : -1));
    for (let i = 0; i < exploreCompanies.length; ++i) {
      let cid = exploreCompanies[i][0];
      let trending =
        exploreCompanies[i][1] != null ? exploreCompanies[i][1] : 0;
      let companyName = exploreCompanies[i][2];
      let logo = exploreCompanies[i][3];
      let applicationLink = exploreCompanies[i][4];
      let location =
        exploreCompanies[i][5] != null ? exploreCompanies[i][5] : 'Various';
      let isInternship = exploreCompanies[i][6];
      let timestamp = exploreCompanies[i][7];
      let hasInsights = exploreCompanies[i][8];
      let obj = {
        name: companyName,
        cid: cid,
        trending: trending,
        logo: logo,
        appLink: applicationLink,
        location: location,
        isInternship: isInternship,
        timePosted: timestamp,
        hasInsights: hasInsights,
      };
      //job type filter
      if (jobTypeFilter === 'Internship' && isInternship) {
        companies.push(obj);
      } else if (jobTypeFilter === 'New Grad' && !isInternship) {
        companies.push(obj);
      } else if (jobTypeFilter === null) {
        companies.push(obj);
      }

      //check for sort by filter
      if (sortByFilter == 'Trending') {
        companies.sort((a, b) => (a['trending'] < b['trending'] ? 1 : -1));
      } else if (sortByFilter == 'Most Recent') {
        companies.sort((a, b) => (a['timePosted'] < b['timePosted'] ? 1 : -1));
      }
    }
    setInfiniteScrollData(companies);
  };

  const setSortedData = () => {
    let companies = [];
    // exploreCompanies.sort((a, b) => (a[2] > b[2] ? 1 : -1));
    for (let i = 0; i < infiniteScrollData.length; ++i) {
      let cid = infiniteScrollData[i]['cid'];
      let trending =
        infiniteScrollData[i]['trending'] != null
          ? infiniteScrollData[i]['trending']
          : 0;
      let companyName = infiniteScrollData[i]['name'];
      let logo = infiniteScrollData[i]['logo'];
      let applicationLink = infiniteScrollData[i]['appLink'];
      let location =
        infiniteScrollData[i]['location'] != null
          ? infiniteScrollData[i]['location']
          : 'Various';
      let isInternship = infiniteScrollData[i]['isInternship'];
      let timestamp = infiniteScrollData[i]['timePosted'];
      let hasInsights = infiniteScrollData[i]['hasInsights'];
      let obj = {
        name: companyName,
        cid: cid,
        trending: trending,
        logo: logo,
        appLink: applicationLink,
        location: location,
        isInternship: isInternship,
        timePosted: timestamp,
        hasInsights,
      };
      companies.push(obj);
    }
    if (sortByFilter == 'Trending') {
      companies.sort((a, b) => (a['trending'] < b['trending'] ? 1 : -1));
    } else if (sortByFilter == 'Most Recent') {
      companies.sort((a, b) => (a['timePosted'] < b['timePosted'] ? 1 : -1));
    }
    setInfiniteScrollData(companies);
  };

  const filterIDs = () => {
    if (companiesList.length <= 0) {
      return;
    }
    let companies = [];
    for (let i = 0; i < 3; ++i) {
      let companyByCidObject = filterByNodeCid(companiesList, companyIDs[i]);
      let company_name = companyByCidObject[1];
      let cid = companyByCidObject[0];
      let logo = companyByCidObject[2];

      let obj = {
        name: company_name,
        cid: cid,
        logo: logo,
      };
      companies.push(obj);
    }
    setFilteredCompanies(companies);
    companies = [];
    companiesList.sort((a, b) => (a[1] > b[1] ? 1 : -1));
    for (let i = 0; i < 144; ++i) {
      let company_name = companiesList[i][1];
      let cid = companiesList[i][0];
      let logo = companiesList[i][2];
      let obj = {
        name: company_name,
        cid: cid,
        logo: logo,
      };
      companies.push(obj);
    }
    setInfiniteScrollData(companies);
  };

  useEffect(() => {
    getQuery('companies', props.token, setCompaniesList);
    getQuery('explore', props.token, setExploreCompanies);
    getQuery('pipeline_uid', props.token, setPipelines);
    getQuery('user_info', props.token, setUserInfo);
    getRecommendedCompanies(token);
    // setCompanyIDs([708, 59, 18, 55, 672]); // dev
  }, []);

  useEffect(() => {
    if (cardInfo !== null) {
      setCompanyModal(true);
    }
  }, [cardInfo]);

  // filter companies useEffect
  useEffect(() => {
    if (companyIDs.length == 5) {
      filterIDs();
    } else if (exploreCompanies.length > 0) {
      setInitialInfinite();
    }
  }, [exploreCompanies]);

  useEffect(() => {
    if (newGradChecked) {
      setjobTypeFilter('New Grad');
    } else {
      setjobTypeFilter('Internship');
    }
  }, [newGradChecked]);

  useEffect(() => {
    if (jobTypeFilter !== null) {
      setJobFilteredData();
    } else {
      setInitialInfinite();
    }
  }, [jobTypeFilter]);

  useEffect(() => {
    if (sortByFilter !== null) {
      setSortedData();
    } else {
      setInitialInfinite();
    }
  }, [sortByFilter]);

  useEffect(() => {
    updateLogin(props.token);
    getQuery('user_info', props.token, setUserInfo);
  }, []);

  useEffect(() => {
    if (!!userInfo) {
      setRedemptionPoints(!!userInfo[0][8] ? userInfo[0][8] : 0);
    }
  }, [userInfo]);

  useEffect(() => {
    if (!!userInfo && userInfo[0][1] !== null) {
      ReactGA.initialize(process.env.REACT_APP_GOOGLE_ANALYTICS_CODE);
      ReactGA.set({
        userId: userInfo[0][0],
      });
      ReactGA.pageview('explore');
    }
  }, [userInfo]);

  return (
    <div>
      <CssBaseline />
      <AppBar
        position="flex"
        className={clsx(classes.appBar, openDrawer && classes.appBarShift)}
      >
        <Navbar
          handleCompanyModalOpen={handleCompanyModalOpen}
          page={'explore'}
          filter={filterByIdArr}
          pipelines={pipelines}
          data={exploreCompanies}
          openSettings={handleOpenSettings}
          email={!!userInfo ? userInfo[0][7] : ''}
        />
      </AppBar>
      <BugsBanner token={token} />
      {/* Recommended Companies Section Commented Out */}
      {/* <Grid
        direction="row"
        justify="center"
        alignItems="center"
        className={classes.recommendedContainer}
      >
        {pipelines !== null &&
          filteredCompanies.map((company, index) => (
            <Grid item xs={2.4}>
              <RecCompanyTile
                companyName={company.name}
                cid={company.cid}
                logo={company.logo}
                companyModal={companyModal}
                index={index}
                card={filterByIdArr(pipelines, company.cid)}
                token={token}
              />
            </Grid>
          ))}
      </Grid> */}
      <Typography
        variant="h5"
        className={classes.companyList}
        color="textSecondary"
      >
        Explore
      </Typography>
      <div className={classes.exploreSearch}>
        <Button variant="outlined" className={classes.exploreButton}>
          {/* {jobTypeFilter ? 'Job Type: ' + jobTypeFilter : 'Job Type'} */}
          Internship
          <Switch
            checked={newGradChecked}
            onChange={event => {
              setNewGradChecked(event.target.checked);
            }}
            color="default"
            inputProps={{ 'aria-label': 'checkbox with default color' }}
            size="small"
          />
          New Grad
        </Button>
        {/* <Menu
          id="long-menu"
          anchorEl={jobTypePopoverRef}
          keepMounted
          open={jobTypePopoverRef}
          onClose={() => setjobTypePopoverRef(false)}
          PaperProps={{
            style: {
              maxHeight: 48 * 4.5,
              width: '20ch',
            },
          }}
        >
          <MenuItem
            className={classes.popoverList}
            onClick={event => {
              setjobTypeFilter(event.currentTarget.textContent);
              setjobTypePopoverRef(false);
            }}
          >
            Internship
          </MenuItem>
          <MenuItem
            className={classes.popoverList}
            onClick={event => {
              setjobTypeFilter(event.currentTarget.textContent);
              setjobTypePopoverRef(false);
            }}
          >
            New Grad
          </MenuItem>
          <MenuItem
            className={classes.popoverList}
            onClick={event => {
              setjobTypeFilter(null);
              setjobTypePopoverRef(false);
            }}
          >
            All
          </MenuItem>
        </Menu> */}
        <Button
          variant="outlined"
          className={classes.exploreButton}
          onClick={event => setsortByPopoverRef(event.currentTarget)}
        >
          {sortByFilter ? 'Sort By: ' + sortByFilter : 'Sort By'}
          {/* Sort By */}
        </Button>
        <Menu
          id="long-menu"
          anchorEl={sortByPopoverRef}
          keepMounted
          open={sortByPopoverRef}
          onClose={() => setsortByPopoverRef(false)}
          PaperProps={{
            style: {
              maxHeight: 48 * 4.5,
              width: '20ch',
            },
          }}
        >
          <MenuItem
            className={classes.popoverList}
            onClick={event => {
              setsortByFilter(event.currentTarget.textContent);
              setsortByPopoverRef(false);
            }}
          >
            Trending
          </MenuItem>
          <MenuItem
            className={classes.popoverList}
            onClick={event => {
              setsortByFilter(event.currentTarget.textContent);
              setsortByPopoverRef(false);
            }}
          >
            Most Recent
          </MenuItem>
          <MenuItem
            className={classes.popoverList}
            onClick={event => {
              setsortByFilter(null);
              setsortByPopoverRef(false);
            }}
          >
            Clear
          </MenuItem>
        </Menu>
      </div>
      {infiniteScrollData.length > 0 ? (
        <InfiniteScroll
          style={{
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'center',
            flexWrap: 'wrap',
          }}
          // height={450} //potential better future option? need to test more
          dataLength={infiniteScrollData.length}
          // next={loadMoreCompanies}
          // hasMore={infiniteScrollData.length <= companiesList.length}
          hasMore={false}
          // endMessage={
          //   <p style={{ textAlign: 'center' }}>
          //     <b>No more companies to display</b>
          //   </p>
          // }
        >
          {pipelines !== null &&
            infiniteScrollData.map((company, index) => (
              <ExploreCompanyTile
                token={token}
                userInfo={userInfo}
                companyName={company.name}
                cid={company.cid}
                trending={company.trending}
                logo={company.logo}
                appLink={company.appLink}
                trending={company.trending}
                location={company.location}
                isInternship={company.isInternship}
                timePosted={company.timePosted}
                hasInsights={company.hasInsights}
                companyModal={companyModal}
                index={index}
                card={filterByIdArr(pipelines, company.cid)}
                handleCompanyModalOpen={handleCompanyModalOpen}
              />
            ))}
        </InfiniteScroll>
      ) : (
        <p style={{ textAlign: 'center' }}>
          <b>No more companies! Clear your filters to see more.</b>
        </p>
      )}

      <HamburgerDrawer open={openDrawer} onClose={handleDrawerClose} />
      <SimpleDialog
        open={openSettings}
        onClose={handleCloseSettings}
        token={token}
      />
      {companyModal && (
        <CompanyModal
          userInfo={userInfo}
          open={companyModal}
          onClose={handleCompanyModalClose}
          card={cardInfo}
          token={props.token}
          logo={filterByCID(companiesList, cardInfo.cid)}
          page="insights"
          isPipeline={!!filterByIdArr(pipelines, cardInfo.cid)}
          setRedemptionPoints={setRedemptionPoints}
          redemptionPoints={redemptionPoints}
        />
      )}
    </div>
  );
}
